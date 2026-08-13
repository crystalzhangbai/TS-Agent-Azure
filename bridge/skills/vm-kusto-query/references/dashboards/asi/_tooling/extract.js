// Extract ASI page query library.
// Uses a Bearer token captured from the user's browser session.
//
// Usage:
//   node extract.js --token <token-file> --service <svc> --page <page> --out <dir>
//
// Example:
//   node extract.js --token token.txt --service "EEE RDOS" --page "WF Unexpected Restart" --out ../pages/wf-unexpected-restart/raw

const fs = require('fs');
const path = require('path');

const ASI = 'https://asi.azure.ms';

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--token') out.token = argv[++i];
    else if (a === '--service') out.service = argv[++i];
    else if (a === '--page') out.page = argv[++i];
    else if (a === '--out') out.out = argv[++i];
  }
  return out;
}

const args = parseArgs(process.argv);
if (!args.token || !args.service || !args.page) {
  console.error('usage: node extract.js --token <file> --service "<svc>" --page "<page>" [--out <dir>]');
  process.exit(2);
}
const SERVICE = args.service;
const PAGE = args.page;
const TOKEN = fs.readFileSync(args.token, 'utf8').trim();
const outDir = args.out || '.';
fs.mkdirSync(outDir, { recursive: true });

const headers = {
  'Authorization': `Bearer ${TOKEN}`,
  'Accept': 'application/json',
  'Content-Type': 'application/json',
};

async function getJson(url) {
  const r = await fetch(url, { headers });
  if (!r.ok) throw new Error(`GET ${url} -> ${r.status}`);
  return r.json();
}
async function postJson(url, body) {
  const r = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`POST ${url} -> ${r.status} ${await r.text()}`);
  return r.json();
}

function walk(node, panelPath, queryRefs, cwgIds) {
  if (!node || typeof node !== 'object') return;
  const title = node.props?.title || '';
  const myPath = title ? [...panelPath, title] : panelPath;

  if (node.type === 'CompoundWidgetContainer' && node.widgetProperties?.compoundWidgetId) {
    cwgIds.push({ id: node.widgetProperties.compoundWidgetId, panelPath: myPath });
  }
  if (Array.isArray(node.queries)) {
    for (const q of node.queries) {
      if (q.groupId) queryRefs.push({
        groupId: q.groupId, majorVersion: q.majorVersion, minorVersion: q.minorVersion,
        panelPath: myPath, widgetType: node.type, widgetTitle: title,
        queryId: q.id, inputMappings: q.inputMappings || [],
      });
    }
  }
  if (Array.isArray(node.selectedProperties)) {
    for (const sp of node.selectedProperties) {
      const m = sp.mapping;
      if (m?.groupId) queryRefs.push({
        groupId: m.groupId, majorVersion: m.majorVersion, minorVersion: m.minorVersion,
        panelPath: myPath, widgetType: node.type, widgetTitle: title,
        via: 'selectedProperty', propertyName: sp.paramName || sp.friendlyName,
      });
    }
  }
  if (Array.isArray(node.mapping)) {
    for (const m of node.mapping) {
      if (m.groupId) queryRefs.push({
        groupId: m.groupId, majorVersion: m.majorVersion, minorVersion: m.minorVersion,
        panelPath: myPath, widgetType: node.type, widgetTitle: title,
        via: 'mapping', propertyName: m.internalDestinationName || m.externalSourceName,
      });
    }
  }
  if (Array.isArray(node.children)) for (const c of node.children) walk(c, myPath, queryRefs, cwgIds);
}

(async () => {
  console.log(`Fetching page: ${SERVICE}/${PAGE}`);
  const page = await getJson(`${ASI}/api/services/${encodeURIComponent(SERVICE)}/pages/${encodeURIComponent(PAGE)}`);
  fs.writeFileSync(path.join(outDir, 'page.json'), JSON.stringify(page, null, 2));
  console.log(`Page id=${page.id}`);

  const queryRefs = [];
  const cwgIds = [];
  walk(page.root, [], queryRefs, cwgIds);
  console.log(`Initial walk: ${queryRefs.length} query refs, ${cwgIds.length} compound-widget refs`);

  const fetchedCwgs = {};
  const queue = [...cwgIds];
  while (queue.length) {
    const { id, panelPath } = queue.shift();
    if (fetchedCwgs[id]) continue;
    let doc;
    try {
      doc = await getJson(`${ASI}/api/services/${encodeURIComponent(SERVICE)}/compoundWidgetGroups/${id}`);
    } catch (e1) {
      try {
        doc = await getJson(`${ASI}/api/compoundWidgetGroups/${id}`);
      } catch (e2) {
        console.warn(`  CWG ${id} fetch failed: ${e2.message}`);
        fetchedCwgs[id] = { error: e2.message, panelPath };
        continue;
      }
    }
    fetchedCwgs[id] = { doc, panelPath };
    const subRefs = [], subCwgs = [];
    walk(doc.root, panelPath, subRefs, subCwgs);
    queryRefs.push(...subRefs);
    for (const c of subCwgs) if (!fetchedCwgs[c.id]) queue.push(c);
    console.log(`  CWG ${id} (${panelPath.join(' > ') || '(root)'}): +${subRefs.length} refs, +${subCwgs.length} sub-cwgs`);
  }
  fs.writeFileSync(path.join(outDir, 'compound-widget-groups.json'), JSON.stringify(fetchedCwgs, null, 2));
  console.log(`Fetched ${Object.keys(fetchedCwgs).length} compound widget groups. Total refs: ${queryRefs.length}`);

  // Dedupe by (groupId, majorVersion)
  const seen = new Set();
  const selectors = [];
  for (const r of queryRefs) {
    const k = `${r.groupId}__${r.majorVersion}`;
    if (!seen.has(k)) { seen.add(k); selectors.push({ groupId: r.groupId, majorVersion: r.majorVersion, searchType: 'ByGroupId' }); }
  }
  console.log(`Unique queries: ${selectors.length}`);

  const queries = [];
  for (let i = 0; i < selectors.length; i += 25) {
    const batch = selectors.slice(i, i + 25);
    try {
      const arr = await postJson(`${ASI}/api/queries/search`, { selectors: batch });
      queries.push(...arr);
      console.log(`  Batch ${i}-${i + batch.length - 1}: got ${arr.length} queries`);
    } catch (e) {
      console.warn(`  Batch ${i} failed: ${e.message}`);
    }
  }
  console.log(`Got ${queries.length} query bodies`);

  // Keep latest minor for each (groupId, majorVersion)
  const byKey = {};
  for (const q of queries) {
    const k = `${q.groupId}__${q.majorVersion}`;
    if (!byKey[k] || (q.minorVersion ?? 0) > (byKey[k].minorVersion ?? 0)) byKey[k] = q;
  }

  // Build refs-with-KQL
  const refsWithKql = queryRefs.map(r => {
    const q = byKey[`${r.groupId}__${r.majorVersion}`];
    return {
      ...r,
      name: q?.name, cluster: q?.cluster, database: q?.database, type: q?.type,
      params: q?.params?.map(p => ({ name: p.name, type: p.type, optional: p.optional })),
      schema: q?.schema?.map(s => ({ name: s.name, type: s.type })),
      missing: !q,
    };
  });

  fs.writeFileSync(path.join(outDir, 'queries.json'),
    JSON.stringify(Object.values(byKey).map(q => ({
      id: q.id, name: q.name, groupId: q.groupId,
      majorVersion: q.majorVersion, minorVersion: q.minorVersion,
      cluster: q.cluster, database: q.database, type: q.type,
      dataSource: q.dataSource, language: q.language,
      kustoQuery: q.kustoQuery,
      params: q.params,
      schema: q.schema?.map(s => ({ name: s.name, type: s.type })),
      serviceId: q.serviceId,
    })), null, 2));

  fs.writeFileSync(path.join(outDir, 'query-refs.json'), JSON.stringify(refsWithKql, null, 2));

  fs.writeFileSync(path.join(outDir, 'extraction-summary.json'), JSON.stringify({
    serviceId: SERVICE, pageName: PAGE, pageId: page.id,
    pageRootMapping: page.root?.mapping || [],
    totalRefs: queryRefs.length,
    uniqueQueries: queries.length,
    compoundWidgetGroupCount: Object.keys(fetchedCwgs).length,
  }, null, 2));

  console.log(`\nDone. Output in ${outDir}/`);
  console.log(`  page.json                      - raw page definition`);
  console.log(`  compound-widget-groups.json    - all CWG definitions`);
  console.log(`  queries.json                   - unique KQL queries (${queries.length})`);
  console.log(`  query-refs.json                - all widget→query references (${refsWithKql.length})`);
  console.log(`  extraction-summary.json        - summary`);
})().catch(e => { console.error(e); process.exit(1); });
