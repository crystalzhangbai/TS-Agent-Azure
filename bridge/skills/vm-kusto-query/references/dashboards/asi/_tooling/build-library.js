// Build a panel-organized library.json + library.md for an ASI page.
//
// Input:  <raw-dir>/queries.json + <raw-dir>/query-refs.json (from extract.js)
// Output: <out-dir>/library.json + <out-dir>/library.md + <out-dir>/meta.json
//
// Usage:
//   node build-library.js \
//     --raw   ../pages/<page-slug>/raw \
//     --out   ../pages/<page-slug> \
//     --service "EEE RDOS" \
//     --page  "WF Unexpected Restart" \
//     [--page-input cluster=...,containerid=...,...]   (optional, describes URL inputs)

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--raw') out.raw = argv[++i];
    else if (a === '--out') out.out = argv[++i];
    else if (a === '--service') out.service = argv[++i];
    else if (a === '--page') out.page = argv[++i];
    else if (a === '--page-input') out.pageInput = argv[++i];
  }
  return out;
}

const args = parseArgs(process.argv);
if (!args.raw || !args.out || !args.service || !args.page) {
  console.error('usage: node build-library.js --raw <dir> --out <dir> --service "<svc>" --page "<page>"');
  process.exit(2);
}

const queries = JSON.parse(fs.readFileSync(path.join(args.raw, 'queries.json'), 'utf8'));
const refs    = JSON.parse(fs.readFileSync(path.join(args.raw, 'query-refs.json'), 'utf8'));
const summary = JSON.parse(fs.readFileSync(path.join(args.raw, 'extraction-summary.json'), 'utf8'));

// Index queries by groupId+majorVersion
const byKey = {};
for (const q of queries) byKey[`${q.groupId}__${q.majorVersion}`] = q;

// Keep only true widget→query refs
const widgetRefs = refs.filter(r => !r.via);

// Build panels: panelPath[1:].join(' > ') (skip page title prefix).
// Skip any segment that starts with a known page-prefix like "Start Hub -" or "WF -".
const PAGE_PREFIX_RE = /^(Start Hub - |WF Unexpected Restart - |WF Resource Health - |VM Availability - )/;
const panels = {};
for (const r of widgetRefs) {
  const trimmed = (r.panelPath || []).slice(1)
    .filter(t => t && !PAGE_PREFIX_RE.test(t));
  const panelKey = trimmed.length ? trimmed.join(' > ') : '(top-level)';
  panels[panelKey] ??= { panelPath: trimmed, queries: [] };

  const seen = new Set(panels[panelKey].queries.map(x => `${x.groupId}__${x.majorVersion}`));
  const k = `${r.groupId}__${r.majorVersion}`;
  if (seen.has(k)) continue;

  const q = byKey[k];
  if (!q) continue;

  panels[panelKey].queries.push({
    id: q.id,
    name: q.name,
    groupId: q.groupId,
    majorVersion: q.majorVersion,
    minorVersion: q.minorVersion,
    cluster: q.cluster,
    database: q.database,
    type: q.type,
    widgetType: r.widgetType,
    widgetTitle: r.widgetTitle,
    params: q.params?.map(p => ({ name: p.name, type: p.type, optional: p.optional })),
    schema: q.schema,
    inputMappings: r.inputMappings,
    kustoQuery: q.kustoQuery,
    panelPath: trimmed,
  });
}

const sortedPanels = Object.fromEntries(
  Object.entries(panels).sort((a, b) => a[0].localeCompare(b[0]))
);

// Determine page URL inputs.
// If --page-input provided as "k1=desc1,k2=desc2,...", use that. Otherwise harvest
// from raw page.json root mapping if available.
let pageInputs = {};
if (args.pageInput) {
  for (const part of args.pageInput.split(',')) {
    const [k, ...rest] = part.split('=');
    if (k) pageInputs[k.trim()] = rest.join('=').trim() || '';
  }
}
// Default: harvest from page.json's root mapping
const pageJson = JSON.parse(fs.readFileSync(path.join(args.raw, 'page.json'), 'utf8'));
if (!Object.keys(pageInputs).length && Array.isArray(pageJson.root?.mapping)) {
  for (const m of pageJson.root.mapping) {
    const name = m.internalDestinationName || m.externalSourceName;
    if (name) pageInputs[name] = m.description || '';
  }
}

// Standard param aliases observed in widget queries across ASI pages.
const paramAliases = {
  startTime: ['starttime', 'StartTime', 'queryFrom', 'startTimeFilter', 'queryStart', 'query_startTime'],
  endTime:   ['endtime',   'EndTime',   'queryTo',   'endTimeFilter',  'queryEnd',   'query_endTime'],
  containerId: ['containerid', 'queryContainerid', 'queryContainerId', 'ContainerId', 'query_ContainerId'],
  nodeId:    ['nodeid', 'NodeId', 'queryNodeId', 'query_NodeId'],
  vmId:      ['vmid', 'VmId', 'virtualMachineUniqueId', 'vmUniqueId', 'queryVmId', 'query_vmId'],
  cluster:   ['Tenant', 'Cluster', 'tenant', 'clusterName', 'queryCluster', 'query_cluster', 'queryTenant'],
  roleInstanceName: ['queryRoleInstanceName', 'RoleInstanceName', 'query_VMName', 'queryroleInstanceName'],
  tenantName: ['tenantname', 'tenantNameId', 'queryTenantName', 'query_TenantName', 'querytenantName'],
  subscriptionId: ['SubscriptionId', 'querySubscription', 'query_SubscriptionId', 'querySubscriptionId'],
};

const library = {
  service: args.service,
  page: args.page,
  pageId: pageJson.id,
  pageInputs,
  paramAliases,
  panels: sortedPanels,
  meta: {
    extractedAt: new Date().toISOString(),
    totalPanels: Object.keys(sortedPanels).length,
    totalUniqueQueries: queries.length,
    totalWidgetRefs: widgetRefs.length,
  },
};

fs.mkdirSync(args.out, { recursive: true });
fs.writeFileSync(path.join(args.out, 'library.json'),
  JSON.stringify(library, null, 2));

// meta.json (small)
fs.writeFileSync(path.join(args.out, 'meta.json'), JSON.stringify({
  service: library.service,
  page: library.page,
  pageId: library.pageId,
  pageInputs: library.pageInputs,
  totals: library.meta,
  asiPageUrl: `https://asi.azure.ms/services/${encodeURIComponent(args.service)}/pages/${encodeURIComponent(args.page)}`,
}, null, 2));

// library.md
const md = [];
md.push(`# ${args.service} — ${args.page}: KQL Query Library\n`);
md.push(`> Auto-extracted from ASI on ${library.meta.extractedAt}.`);
md.push(`> Total: ${library.meta.totalUniqueQueries} unique KQL queries across ${library.meta.totalPanels} panels (${library.meta.totalWidgetRefs} widget refs).\n`);
md.push('## Page inputs (URL params)\n');
for (const [k, v] of Object.entries(library.pageInputs)) md.push(`- \`${k}\` — ${v || '(no description)'}`);
md.push('\n## Panels\n');
for (const [panel, info] of Object.entries(sortedPanels)) {
  md.push(`### ${panel}`);
  md.push(`Path: \`${info.panelPath.join(' > ') || '(top-level)'}\`  ·  Queries: ${info.queries.length}\n`);
  md.push('| # | Name | Type | Cluster | Database | Params |');
  md.push('|---|------|------|---------|----------|--------|');
  info.queries.forEach((q, i) => {
    const cl = (q.cluster || '?').replace('.kusto.windows.net', '');
    const params = (q.params || []).map(p => p.name).join(', ') || '-';
    md.push(`| ${i + 1} | ${q.name || '(unnamed)'} | ${q.type || '?'} | ${cl} | ${q.database || '?'} | ${params} |`);
  });
  md.push('');
}
fs.writeFileSync(path.join(args.out, 'library.md'), md.join('\n'));

console.log(`Wrote:
  ${path.join(args.out, 'library.json')}
  ${path.join(args.out, 'library.md')}
  ${path.join(args.out, 'meta.json')}

Stats:
  panels:    ${library.meta.totalPanels}
  queries:   ${library.meta.totalUniqueQueries}
  refs:      ${library.meta.totalWidgetRefs}
`);
