# Schema Exploration — Tier-2 fallback when no curated KQL exists

> The vm-kusto-query skill prefers curated KQL from `catalogs/` → playbook deep files → dashboard IGs. When all three yield nothing — typically a new symptom or a cluster not yet in `catalogs/` — this workflow describes how to **enumerate**, **sample**, and **construct** a one-off query, then **promote** it so the next case finds it in Tier 1.
>
> Lives in the **S5 EXPAND** state of [`investigation-loop.md`](investigation-loop.md). Always preceded by an attempt at the three curated tiers; never the first thing you do.

---

## Step 0 — Pick the right cluster

Use this map (only domains not already exhaustively routed in SKILL.md):

| Investigation domain | Candidate cluster(s) | Default database |
|---|---|---|
| Host compute fabric (lifecycle, SH, LM, NMAgent) | `Azcsupfollower.kusto.windows.net` | `AzureCM` |
| Hyper-V / RDOS / guest KVP / WindowsEventTable | `azcore.centralus.kusto.windows.net` | `Fa`, `SharedWorkspace`, `acccvmtmgeneva` |
| ASAP / Boost storage (PF/VF/NQE/UMED) | `storageclient.eastus.kusto.windows.net` | `Fa`, `Fc` |
| Hardware inventory / SEL / WHEA / decom | `AzureDCM.AzureDCMDb`, `Sparkle.kusto.windows.net` | (per-cluster) |
| PCIe / 7U Server topology | `Sparkle.kusto.windows.net`, `PartnerRAS` | (per-cluster) |
| Maintenance / Air / AzPE / SSM | `vmainsight.kusto.windows.net`, `azpe.azpe`, `icmcluster.ACM` | `Air`, `azpe`, `Publisher` |
| Disks RP (managed disk lifecycle) | `disks.kusto.windows.net` | `Disks` |
| CRP control plane | `azcrp.kusto.windows.net`, `azcsupfollower2.centralus`, `crp.kusto.windows.net` | `crp_allprod`, `CrpService` |
| CRP BI / Snapshots | `azcrpbifollower.kusto.windows.net` | `bi_allprod` |
| ARM ingress / Policy / EventService | `armprodgbl.<region>.kusto.windows.net` | `ARMProd` |
| Capacity / Allocator | `azureallocator.<region>.kusto.windows.net`, `azcrpeus.kusto.windows.net` | `AzureAllocator`, `casprod` |
| RSM (extension rollout) | `azmc2.centralus.kusto.windows.net` | `rsm_Prod` |
| Networking (NRP, AznwSdn, AzSlb, Hybrid) | `nrp.nrpmds`, `aznwsdn.aznwmds`, `azslb.azslb`, `hybridnetworking.kusto.windows.net` | (per-cluster) |
| Storage Account (XStore properties, billing, perf) | `xstore.xdataanalytics`, `xargus.centralus.kusto.windows.net`, `xlivesite.kusto.windows.net`, `accprod.kusto.windows.net`, `pav2data.eastus.kusto.windows.net`, `hdmprod.kusto.windows.net` | `xstore`, `Production`, `xlivesite`, `aipusageaudit` |
| Azure Files / AFS (KailaniSVC namespace) | Jarvis DGrep MDM `KailaniSVC`, plus `xstore.kusto.windows.net` for backend | (Jarvis MDM) |
| Managed Identity RP | `azmsicl.kusto.windows.net` | `azmsidb` (CoreIdentity-restricted) |
| ICM / Hawkeye / ASW | `icmcluster.kusto.windows.net`, `Hawkeye.hawkeyedb`, `AzureSupportData` | `IcMDataWarehouse`, etc. |

If your symptom doesn't map to any row above, **ask the user** — guessing wastes a JIT request.

---

## Step 1 — Enumerate

Once you have a cluster + database, use ADX management commands. These work with both Azure MCP `kusto` tool and `scripts/kusto_runner.py`. They count as queries against your S5 budget — limit to ~5.

```kusto
// List databases in a cluster
.show databases

// List tables (and materialized views) in a database
.show tables

// Filter table list by name pattern
.show tables | where TableName contains "Container"

// Get schema for one table
.show table <TableName> schema as json
// or, lighter:
<TableName> | getschema

// Get table folder/hierarchy (Microsoft internal tables are folder-grouped)
.show tables | summarize tableCount=count() by Folder

// List functions (incl. cross-database functions)
.show functions
.show functions | where Name contains "VMAvailability"
```

**Heuristics for choosing tables**:
- Names containing `Snapshot` → periodic state (good for "what state was X at time T")
- Names containing `Event` / `Log` → discrete events
- Names ending in `Etl` / `EtwTable` → raw ETW from host
- Names containing `Qos` / `Operation` → QoS / API metrics
- Names containing `Daily` / `5M` / `1H` / `1D` → pre-aggregated rollups

---

## Step 2 — Sample 1 row

**Always sample before writing the real query.** Saves you 3 failed runs to learn that a column you assumed exists is actually nested in `properties.foo`.

**CRITICAL: Do NOT project, filter, summarize, or extend any column until you have confirmed it exists in the table** — either via `take 1` output or `getschema`. This is the SEM0100 gate (full rule: [SKILL.md § Step 2.5](../../SKILL.md#step-25--verify-query-before-sharing-mandatory--the-sem0100-gate)).

```kusto
cluster('<host>').database('<db>').<TableName>
| where PreciseTimeStamp > ago(2h)   // narrow time first
| take 1
```

Inspect every column. Pay attention to:
- `properties` / `parameters` / `details` columns — usually `dynamic` (JSON). Extract with `tostring(props.foo)` / `toint(props.bar)`.
- `subscriptionId` casing — some tables have `SubscriptionId`, some `subscriptionId`, some `subId`.
- Time column name — most use `PreciseTimeStamp` but some (XStore) use `TimeStamp` / `Timestamp`.
- VM identity column — `roleInstanceName`, `vmName`, `resourceName`, `VMUniqueId` all exist in various tables.

> **For the 6 high-hallucination tables** (`LogContainerSnapshot`, `LogNodeSnapshot`, `DiskManagerApiQoSEvent`, `DiskManagerContextActivityEvent`, `ApiQosEvent`, `LiveMigrationSessionCompleteLog`) and the phantom-table blacklist, the verified correct/wrong column names live in **[`operational-discipline.md` § Known Schema Pitfalls](operational-discipline.md#known-schema-pitfalls--the-sem0100-blacklist-single-source-of-truth)** — the single source of truth. Don't re-list them here.

---

## Step 3 — Construct with guardrails

Build the query around the standard variable convention ([`conventions.md`](conventions.md#variable-convention)) and the guardrails from [`operational-discipline.md`](operational-discipline.md#query-guardrails):

```kusto
let _t1 = datetime({StartTime}) - 1h;
let _t2 = datetime({EndTime})   + 1h;
let _sub = "{SubscriptionId}";
let _vm  = "{VMName}";
cluster('<host>').database('<db>').<TableName>
| where PreciseTimeStamp between (_t1 .. _t2)
| where subscriptionId =~ _sub          // case-insensitive
| where roleInstanceName has _vm        // partial OK for VMSS
| project PreciseTimeStamp, ... , properties_FaultCode = tostring(properties.faultCode)
| order by PreciseTimeStamp asc
| take 1000                              // hard cap, raise consciously
```

**Mandatory rules**:
1. Time window first — every chatty table needs `between(_t1 .. _t2)`. Default ≤ 6h.
2. `cluster('<host>').database('<db>').<TableName>` form — never bare `<TableName>`.
3. `| take 1000` at the end. Raise to 5000 only if you've confirmed the table is small.
4. Use `=~` for case-insensitive equality, `has` for tokenized substring; avoid `contains` on huge tables (slow).
5. Don't `summarize` until you've inspected raw rows.

---

## Step 4 — Verify

Run the query. If:
- **0 rows** → widen time window 4x; if still 0, the table doesn't carry this signal — pick another table from Step 1 (don't iterate more than 3 tables, see stop conditions in [`investigation-loop.md`](investigation-loop.md))
- **Way too many rows** → tighten by adding more `where` filters from the sample row's columns
- **Just right** → continue to Step 5

---

## Step 5 — Decide whether to catalog

**Default**: quote the KQL inline in the case write-up with a one-line provenance note:

```
Source: ad-hoc schema exploration — cluster('<host>').database('<db>').<Table>
```

Then move on. Most schema-exploration queries are one-offs and should NOT be added to `catalogs/`.

**Exception** — add a catalog entry only when **any one** of these is true:

| # | Trigger | Why |
|---|---|---|
| 1 | The `cluster('...')` is not in any existing catalog file and not in SKILL.md Scenario Routing | New cluster.db means the next case can't even find it |
| 2 | The table is new on a cluster.db that IS already catalogued | One missing entry on a familiar cluster — cheap to add |
| 3 | This same question has come up in **another case within the past 7 days** | Two hits in a week = recurring; promote before it becomes "I keep forgetting this query" |
| 4 | The query is **pivot-quality** — its result determines the next anchor query (like the 15 entries in [`result-interpretation.md`](result-interpretation.md)) | Pivots are the highest-value entries in the skill; never skip |

If none of those apply, **don't add it**. Don't bulk-curate; that's how catalogs accumulate stale entries no one trusts.

### How to add (when an exception fires)

Follow [`conventions.md`](conventions.md#cataloging-new-queries) — that section is the single source of truth for:
- picking the target file from the catalog matrix
- entry format + required metadata
- the rule "if it's a new cluster.db, also add a Scenario Routing row to SKILL.md"

Additional: if the trigger was #4 (pivot-quality), also add a row to [`result-interpretation.md`](result-interpretation.md) — the catalog tells the next agent the KQL; result-interpretation tells them what each result value means and where to branch.

---

## Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `Sem0001: 'foo' is not recognized as a table` | Wrong database or table is in a follower cluster | Try `<TableName>_DSV1` / `_DSV` suffix, or check follower cluster (e.g., `azcsupfollower2` not `azcsupfollower`) |
| `Sem0011: column 'foo' does not exist` | Schema differs from sample (column nested in `properties`) | Re-run Step 2 sample; use `getschema` |
| `Request is throttled` | Cluster-side QPS cap | Backoff 30 s, retry once, otherwise switch to `scripts/kusto_runner.py` (different throttle pool) |
| `403 Forbidden` | Not in JIT group | See [`operational-discipline.md`](operational-discipline.md#cluster-permission-matrix) |
| `Query exceeds memory limit` | No time filter / `take` / hot partition | Add stricter time bounds; `summarize` early; avoid `join` on full tables |
| Query worked yesterday, empty today | Table partition rolled (some tables have 7d retention) | Check `.show table T extents` for available time range |
