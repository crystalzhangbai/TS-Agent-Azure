# Conventions — Variables, ADX Deep Links, Catalog Maintenance

> Universal conventions for the vm-kusto-query skill: standard variable names used in
> every KQL template, how to open queries in Azure Data Explorer from a script, and
> rules for cataloging new queries into this `references/` folder.

---

## Variable Convention

All query templates use these standardized placeholders. When you take a query from this
catalog, substitute these `{...}` tokens with real values before executing.

### VM / Container identity
- `{NodeId}` — physical host node GUID/name
- `{ContainerId}` — container GUID on the node
- `{VMName}` — VM resource name (also seen as `roleInstanceName`)
- `{VMId}` — `virtualMachineUniqueId` (preferred for cross-table joins)
- `{TenantName}` — fabric tenant for the VM
- `{Cluster}` — physical cluster name (e.g., `XYZ12PrdApp30`)

### Subscription / Resource
- `{SubscriptionId}` — Azure subscription GUID
- `{ResourceGroupName}` — resource group
- `{ResourceId}` — full ARM resource ID (`/subscriptions/.../resourceGroups/.../providers/...`)
- `{StorageAccountName}` — storage account name
- `{DiskName}` — managed disk name
- `{DiskRPInternalId}` — internal Disks RP ID

### Time window
- `{StartTime}` / `{EndTime}` — incident window, format `2026-06-01 14:30:00Z`
- Or `{BeginTime}` / `{EndTime}` in older queries (treat as synonyms)
- **Rule of thumb**: subtract 1–2h from the reported start time for context; add 30–60min after end time to catch recovery actions

### Operation tracing
- `{LMSessionId}` — Live Migration session GUID
- `{CorrelationId}` / `{CorrelationRequestId}` — ARM / CRP correlation request ID
- `{ActivityId}` — CRP / azcrp activity ID
- `{IncidentId}` — ICM incident number

### Networking
- `{GatewayId}` — VPN/ExR gateway resource ID
- `{ExRServiceKey}` — ExpressRoute service key

### Decompose `{ResourceId}` into Sub/RG/VMName
```kusto
let MyResourceID = "{ResourceId}";
let SubID       = tostring(split(MyResourceID, "/")[2]);
let ResourceGrp = tostring(split(MyResourceID, "/")[4]);
let VMName      = tostring(split(MyResourceID, "/")[-1]);
```

> See also: `_shared-vm-identification.md` Q0 for the canonical version of this snippet.

---

## Query Lookup Order

> Clarification: **IG = Investigation Guide**. In this repo, IG files are the chapterized KQL guides under `dashboards/asi/pages/<slug>/investigation-guide/`, reverse-engineered from ASI dashboard pages and then curated for troubleshooting.

When the [`investigation-loop.md`](investigation-loop.md) state machine enters **S2 FIND-AND-RUN**,
search for KQL in this priority order. Stop at the first tier that yields a query covering
the question — do not skip ahead. Only fall through to the next tier when the current
tier has nothing applicable.

| Priority | Source | When to use | Authority |
|---|---|---|---|
| 1 | `catalogs/*.md` (15 topical catalogs) | Default — every well-trodden investigation is here. Curated, parameterized, with `Interpretation:` notes | Highest. Stable signatures, RCA-context-verified |
| 2 | `playbooks/<X>-<topic>-deep.md` (24 deep playbooks) | When the question matches a playbook scenario but the exact query is inline in a section rather than promoted to a catalog | High. Workflow-correct but may be sub-optimal as standalone snippets |
| 3 | `dashboards/asi/pages/<slug>/investigation-guide/*.md` (162 ASI IG pages — **IG = Investigation Guide**, the curated symptom-keyed chapter files under each dashboard page) | When the question targets a specific ASI dashboard page (charts, alerts, metric drill-downs) | Medium. Page-scoped; not always parameterized |
| 4 | Schema exploration ([`schema-exploration-workflow.md`](schema-exploration-workflow.md)) | Only when tiers 1–3 yield nothing. Tier-2 of the loop's S5 EXPAND state | Low. One-off; must be promoted to tier 1 if it works |

### Decision rules
1. **Don't browse all 163 IG pages** — IG search is text-grep on the `slug` and `investigation-guide/*.md` content; if the slug doesn't obviously match, skip to tier 4.
2. **Catalog hit is enough** — if `catalogs/<topic>.md` has a query that answers the question, do not also check the playbook. Catalogs are normalized; playbooks may have stale versions.
3. **IG queries need parameterization** — IG snippets often inline a specific subscription / resource ID. Before running, substitute with this file's Variable Convention placeholders.
4. **Dashboard KQL stays in `dashboards/`** — do not copy it into `catalogs/`. The dashboards tree is the curated home for page-scoped queries; running them inline from the IG is the intended pattern.
5. **Tier-4 outputs are exploratory** — quote a schema-exploration query in the case write-up with a `Source: ad-hoc schema exploration` note. If the cluster.db or table is new, document it per `Cataloging New Queries` below.
6. **Jarvis/Geneva requests route to `dgrep`** — do not create new `dashboards/jarvis/` reverse-engineered pages; use the `dgrep` skill for Jarvis MDM/Geneva telemetry lookups.

### Routing entry points
- Symptom-to-playbook mapping: **SKILL.md → Scenario Routing table**
- Cluster-to-catalog mapping: **`Pick the right reference file`** table further down in this file
- Pivot query result interpretation: [`result-interpretation.md`](result-interpretation.md)

---

## Opening Queries in Azure Data Explorer (deep link)

When the user asks to "open this query in ADX" / "在 ADX 里跑一下" — build a URL-encoded
deep link and open it in the default browser. Use URL encoding (`urllib.parse.quote`),
**not** base64.

### Deep link format
```
https://dataexplorer.azure.com/clusters/{cluster_host}/databases/{database}?query={url_encoded_query}
```

- `{cluster_host}` — FQDN without `https://`, e.g., `azurecm.kusto.windows.net`
- `{database}` — database name, e.g., `AzureCM`
- `{url_encoded_query}` — KQL query encoded with `urllib.parse.quote(...)`

### Open it from PowerShell
```powershell
$env:PYTHONIOENCODING='utf-8'; python -c "
import urllib.parse, webbrowser

query = '''<KQL_QUERY_HERE>'''
encoded = urllib.parse.quote(query)
url = f'https://dataexplorer.azure.com/clusters/<cluster_host>/databases/<database>?query={encoded}'
webbrowser.open(url)
print('Opened in browser.')
"
```

### Notes
- Use **URL encoding** (`urllib.parse.quote`), NOT base64 — base64 does not decode reliably in ADX deep links
- Inside the Python string use **single-quoted** KQL string literals (`== '...'`) to avoid escaping
- The link opens in **Protected Mode**; the user can click **Run** or the pencil to switch to edit mode
- If opening multiple queries, open each one separately so the user gets multiple tabs

---

## Cataloging New Queries

> **IMPORTANT:** Whenever you execute or receive a KQL query — from the user, a portal, or
> any other source — check whether it touches clusters/databases/tables not yet documented
> in this `references/` folder. If yes, **document the query before moving on**.

### When to trigger
After running any query, scan it for:
1. **New cluster URI** — any `cluster('...')` not in the SKILL.md Scenario Routing / Clusters table
2. **New database** — any `database('...')` not associated with a known cluster
3. **New table or function** — any name not already in any `references/*.md` file

### Pick the right reference file

| Reference file | Scope |
|---|---|
| `_shared-vm-identification.md` | The 8-10 universal queries every playbook needs (VM identity, container/node snapshot, VMA RCA, signature→KB) |
| `azurecm-queries.md` | AzureCM cluster tables (container, node, fault, recovery, SH, LM) |
| `azcore-queries.md` | AzCore/RDOS tables (HyperV, VM health, node service, OS logs, NVMe) |
| `disks-queries.md` | Disks RP tables (managed disk lifecycle, existence) |
| `hardware-queries.md` | AzureDCM + Sparkle tables (HW inventory, WHEA/SEL) |
| `operations-queries.md` | Hawkeye, ICM, Watson, AzPE, Resource Health, ASW, IcMDataWarehouse |
| `vmainsight-queries.md` | VMInsight (VMA, Air, Vmadiag, host CPU, Windows events, PHU) |
| `vm-properties-queries.md` | EEE-style VM properties & disk surface queries (cross-cluster) |
| `crp-queries.md` | CRP operations, allocation, container ops, ARM API, azcrp QoS, AZ mapping |
| `networking-queries.md` | Azure Networking (NRP, VPN, ExR, AppGW, vWAN, SLB, CDN, DDoS) |
| `storage-account-queries.md` | XStore / Azure Files storage account investigations |
| `asap-storage-queries.md` | ASAP / Azure Boost NVMe storage |
| `pcie-failure-queries.md` | PCIe AER / link errors, C2789 7U server BDF mapping |
| `kql-language.md` | KQL syntax patterns & best practices |
| **Create new file** | If the query targets a cluster/domain not covered above |

### Format for an entry in an existing file

```markdown
### {Title — what this query retrieves}

Cluster: `<host>` (if different from file default)
Database: `<db>` (if different from file default)
Key columns: `col1`, `col2`, `col3`

```kusto
let SubId="{SubscriptionId}";
cluster('<host>').database('<db>').<TableName>
| where ...
```

Interpretation: {what the results mean, common filter values}
```

### Format for a brand-new file (template)

```markdown
# {Title} — {Short description}

Cluster: `{cluster_uri}`
Database: `{database_name}`

---

## {Query Section Title}

Key columns: `col1`, `col2`, `col3`

```kusto
{parameterized query with {Placeholders}}
```

Interpretation: {what the results mean}
```

### Mandatory rules
1. Every query MUST use `cluster('<host>').database('<db>').<Table>` form — never bare `<Table>` (see SKILL.md Workflow Step 2 rule 3)
2. Parameterize — replace hardcoded subs/VM names/timestamps/GUIDs with placeholders from the Variable Convention above
3. If a new cluster or database is introduced, ALSO update SKILL.md:
   - Add a row to the **Scenario Routing** table
   - Add to the Clusters quick reference inside `_shared-vm-identification.md` if it's a frequently-touched cluster

### Required metadata per entry

| Item | Required | Example |
|---|---|---|
| Query purpose / title | Yes | "VM disk surface details" |
| Cluster URI | Yes | `storageclient.eastus.kusto.windows.net` |
| Database | Yes | `Fa` |
| Table(s) / function(s) | Yes | `OsXIOSurfaceCounterTable`, `AsapMapVmToDiskOVL1()` |
| Input variables | Yes | `_containerId`, `_nodeId`, `_startTime`, `_endTime` |
| Output fields + descriptions | Yes | `CachePolicy` — None/ReadOnly/ReadWrite/LocalDisk |
| Full KQL (parameterized) | Yes | The complete query with `{Placeholder}` variables |
| Cross-cluster references | If any | Which other clusters/databases are joined |
| How to run | Recommended | `kusto_runner.py` command line example |

---

## Catalog Maintenance

### Add a new entry manually
Edit the right `references/*.md` per the matrix above; follow the format conventions.

### Rebuild catalog from ADO wiki
```bash
# Rebuild AzureIaaSVM catalog
python scripts/kusto_catalog_builder.py --wiki-project AzureIaaSVM

# Add a second project (e.g., AzureNetworking)
python scripts/kusto_catalog_builder.py --wiki-project AzureNetworking
# → creates references/catalog-<project>.md
```

### When to rebuild
- New clusters/tables appear in the ADO wiki
- Access instructions have changed
- You onboard to a new ADO wiki project


---

## RCA Report Template

When wrapping up a Kusto-driven investigation (Step 5 of the SKILL.md workflow), use this skeleton in the chat reply to the user. Keep it factual — every claim must trace back to one of the queries you ran.

```markdown
### Issue
- **Resource**: {VMName} / {SubscriptionId} / {ResourceGroupName}
- **Symptom**: {one-sentence customer-perceived problem}
- **Window**: {StartTime} – {EndTime} UTC ({duration})

### Investigation
| # | Cluster.db / Table | Finding |
|---|---|---|
| 1 | `azurecm.AzureCM` / `LogContainerHealthSnapshot` | Container Healthy throughout window, no faultInfo |
| 2 | `vmainsight.vmadb` / `VMA` | RCALevel1 = `<value>`, RCALevel2 = `<value>` at {timestamp} |
| 3 | `vmainsight.Air` / `AirDiskIOBlipEvents` | `<finding>` |
| … | … | … |

### Root cause
{One paragraph naming the fault tier (platform / host hardware / storage / network / guest OS), citing the table(s) above that prove it. If inconclusive, say so explicitly and list the missing telemetry.}

### Customer impact
- Downtime: {minutes} ({HH:MM:SS – HH:MM:SS} UTC)
- Scope: {single VM / all VMs on node / region-wide / etc.}
- Recovery: {auto-recovered via SH / customer restart / etc.}

### Next actions
- [ ] {follow-up KQL or handoff (e.g., "engage EEE Storage via Ava")}
- [ ] {customer-facing note (e.g., "FQR sent / RCA pending hardware team")}
```

**Rules:**
1. **Every Finding row must link to a query you actually ran** — never list a table without evidence. If the table returned 0 rows, write `rowCount=0; per result-interpretation.md this means <X>`.
2. **No speculation in Root cause** — if `VMA` is empty AND `AirDiskIOBlipEvents` is empty AND `KronoxVmOperationEvent` is empty, the honest conclusion is "no platform fault found in the queried clusters" — escalate per `operational-discipline.md` rather than guess.
3. **Customer impact comes from `LogContainerHealthSnapshot` `ContainerState` transitions**, not from the customer's report (their clock may be off by hours).
4. **Draft the customer-facing email manually** (FQR / LQR / RCA — keep internal identifiers out) — this template is the *internal* RCA only.
