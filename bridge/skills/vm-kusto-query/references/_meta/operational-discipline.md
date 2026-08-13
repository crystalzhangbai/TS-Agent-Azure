# Operational Discipline — permission, budget, error handling, MCP vs Python

> Rules the agent must follow when running KQL during an investigation. Without these the loop in [`investigation-loop.md`](investigation-loop.md) can silently burn through expensive cluster time, hit permission walls without recovering gracefully, or run forever without reporting.

---

## Cluster Permission Matrix

Three permission tiers across all internal Kusto clusters used by this skill.

| Tier | Meaning | What to do on `401`/`403` |
|---|---|---|
| **Default** | Tenant-wide access for any Microsoft Corp engineer in the right security group (e.g., Azure-Tools Read, AzureSupportEng) | Re-login (`az login --tenant 72f988bf-86f1-41af-91ab-2d7cd011db47`); if still blocked, request standard SG via `aka.ms/myaccess` |
| **JIT** | Requires Just-In-Time elevation through CoreIdentity (`aka.ms/oneidentity`) | Stop the loop; surface the JIT link + business justification template; resume after grant |
| **PG-only** | Restricted to Product Group on-calls; CSS cannot access | Stop and pivot — escalate to the platform PG by opening an ICM manually via ASC (Escalate ticket); if the root cause is networking, file a collab to the Azure Networking team (ANP) instead |

### Per-cluster classification

| Cluster | Tier | Notes |
|---|---|---|
| `Azcsupfollower.AzureCM` | Default | Most-used. Follower of `AzureCM` |
| `Azcsupfollower2.centralus.crp_allprod` | Default | CRP follower |
| `azurecm.AzureCM` | Default | Mirror; prefer follower for read |
| `azcore.centralus.Fa` / `SharedWorkspace` | Default | RDOS / Hyper-V |
| `azcore.centralus.acccvmtmgeneva` | Default | VM Type Manager |
| `vmainsight.vmadb` / `Air` / `Vmadiag` | Default | VMA RCA + maintenance |
| `disks.Disks` | Default | Disks RP |
| `Cirrus.Cirrus` | Default | Disks BI |
| `crp.CrpService` | Default | CRP QoS |
| `azcrp.crp_allprod` | Default | CRP allprod |
| `azcrpbifollower.bi_allprod` | Default | CRP BI |
| `armprodgbl.<region>.ARMProd` | Default | ARM ingress; per-region |
| `hardware-queries.md` clusters (AzureDCM, Sparkle, Partner_RAS) | Default | HW inventory + SEL |
| `Hawkeye.hawkeyedb` | Default | Failure signatures |
| `Watson.WatsonDB` | Default | Dump analysis |
| `azpe.azpe` | Default | Platform events / SE |
| `IcMDataWarehouse.IcmDataWarehouse` | Default | ICM analytics |
| `aplat.westcentralus.APlat` | Default | Kyber availability |
| `nrp.nrpmds` + networking clusters | Default | NRP / VPN / ExR / AppGW / SLB |
| `xstore.xdataanalytics` | Default | XStore billing / properties |
| `xargus.centralus.Production` | **JIT** | XArgus latency. Request `XArgusKustoAccess` + `XStorePartnersKusto Viewer` + `XP_AllDB_ReadOnly` via `aka.ms/CoreIdentity`. **24h propagation, 48h SLA**, business justification required |
| `xlivesite.xlivesite` | Default | XStore live site |
| `accprod.accprod` | Default | Azure Cosmos confidential |
| `pav2data.eastus.aipusageaudit` | Default | PAv2 billing |
| `hdmprod.hdmprod` | Default | HDM throttling |
| `azmsicl.azmsidb` | **JIT** | MSI RP telemetry. Request `CoreIdentity MSI-Telemetry` |
| `armprodgbl.eastus.ARMProd.General` → `PolicyServiceDebug` | **PG-only** | Azure Policy debug traces |
| `armprodgbl.eastus.ARMProd` → `JobTraces` | **PG-only** | RunCommand job traces |
| `azmc2.centralus.rsm_Prod` | Default | RSM rollout (ext auto-upgrade) |
| `rdfeprod.rdfeprodDB` | Default | Classic / RDFE |
| `azureallocator.westcentralus.AzureAllocator` | Default | Allocator events |
| `azcrpeus.casprod` | Default | CAS allocator |
| Jarvis MDM `KailaniSVC` namespace | Via Jarvis DGrep (not direct Kusto) | Azure File Sync |
| Jarvis MDM `Xstore` namespace | Via Jarvis DGrep | XStore metrics |

When you discover a new cluster during schema exploration, **add it to this table** before promoting the query.

---

## Query Guardrails

Every KQL the agent runs must satisfy:

1. **Time-bounded** — wrapping `where TimeStamp between (_t1 .. _t2)` (or equivalent column name). Default window ≤ 6h. Widen consciously (multiplicatively: 6h → 24h → 7d), one step at a time.
2. **Identity-bounded** — at least one of `subscriptionId =~`, `roleInstanceName has`, `containerId ==`, `nodeId ==`, `resourceId has`. Never query a chatty table without an identity filter.
3. **Bounded result** — `| take 1000` at the end. Acceptable larger caps:
   - 5,000 for aggregation outputs (`summarize ... | order by ... | take N`)
   - 50,000 only for one-off audit/report queries, and only after the user asks for a report
4. **Cluster.DB qualified** — `cluster('<host>').database('<db>').<Table>` form. No bare table references.
5. **No unnecessary joins** — prefer two sequential queries + in-Python merge over a Kusto `join` on two large fact tables.
6. **Case-insensitive equality** — `=~` for `string`. Subscription IDs are GUIDs but appear in mixed case in some tables.

### Default time-window helpers

```kusto
let _t1 = datetime({StartTime}) - 1h;   // 1h precursor lead-in
let _t2 = datetime({EndTime})   + 1h;   // 1h recovery tail
```

For "recurring issue in past N days" queries:
```kusto
let _t1 = ago(30d);   // upper bound for recurrence checks
let _t2 = now();
```

For host-side investigations where the impact window is unknown:
```kusto
let _t1 = datetime({IncidentTime}) - 4h;
let _t2 = datetime({IncidentTime}) + 1h;
```

---

## Investigation Budget

Per case, the agent self-limits to avoid runaway loops:

| Budget | Default | Hard cap | Action when hit |
|---|---|---|---|
| KQL queries run | 30 | 50 | Stop, summarize what's known and what was tried |
| Total result rows returned | 5,000 | 10,000 | Switch to aggregation-only queries |
| Distinct clusters touched | 4 | 6 | Stop and report — usually means routing was wrong |
| Wall time on autonomous loop | 10 min | 20 min | Stop, surface progress to user |
| Schema exploration tables sampled (Tier 2) | 5 | 8 | Stop, ask user / escalate to SME |

These are **stop-and-report** triggers, not abort-with-error. The agent must always produce a partial RCA + evidence trail.

---

## Error Classification

When a KQL fails, classify before retrying. **Do not retry the same query unmodified more than once**.

| Error pattern | Class | Recovery |
|---|---|---|
| `Sem0001: 'X' is not recognized` (table/function) | Schema | **First check "Known Schema Pitfalls" section below** — is it a phantom table? If not: try `_DSV` suffix; verify cluster.db; check follower vs primary; `.show database <db> tables \| where TableName has '<keyword>'`; if still missing → schema-exploration Step 1 |
| `Sem0011: column 'X' does not exist` | Schema | **First check "Known Schema Pitfalls" section below** — is it a phantom column? If not: re-sample (`\| getschema \| where ColumnName has '<keyword>'`); the column may be nested in `properties`, renamed across versions, or case-mismatched |
| `Sem0036: Failed to resolve table or column expression` | Syntax | Check `cluster('...').database('...').T` qualifier and parens |
| `KustoBadRequestException ... query syntax error` | Syntax | Fix the KQL; do not retry |
| `401 Unauthorized` | Auth | `az login --tenant 72f988bf-86f1-41af-91ab-2d7cd011db47`; if still fails → user must re-auth |
| `403 Forbidden` | Permission | Look up cluster in Permission Matrix above; JIT or PG-only branch |
| `429 Too Many Requests` / `Request is throttled` | Throttle | Wait 30 s, retry once; if persists, switch from MCP to `scripts/kusto_runner.py` (different throttle pool) or vice versa. For batches, lower `--max-workers` to 2–3 |
| `Query exceeds memory limit` | Cost | Tighten time window; add filters; `summarize` earlier; avoid wide `join` |
| `Query consumed too much CPU` | Cost | Same as memory; consider materialized view |
| Timeout (no specific error, request hangs) | Cluster | Reduce scope; try a follower cluster (e.g., `azcsupfollower2` instead of `azurecm`); in Python batch mode this is enforced automatically by `--server-timeout` / `--wall-timeout` |
| `404 Not Found` on cluster URL | Routing | Cluster URL typo; verify FQDN against Permission Matrix |
| `Failed to resolve hostname` | Network | Corpnet VPN / proxy issue, not Kusto |

After two consecutive errors of the same class, **stop and report** — don't iterate on broken queries.

---

## Known Schema Pitfalls — the SEM0100 blacklist (single source of truth)

> **This section is the ONE home for all "what's wrong" schema data.** SKILL.md § Step 2.5 holds the *behavioral gate* (the 3-tier verification flow); this section holds the *lookup data* (phantom tables + high-hallucination column reference + cluster-switch procedure). The agent lands here from the `Sem0001` / `Sem0011` rows in **Error Classification** above. Do NOT duplicate this content into other reference files — link here instead.
>
> **Why a blacklist and not an exhaustive schema dump**: column names are unbounded — you cannot record them all. The fix is *methodological* (verify-before-run, in SKILL.md Step 2.5), not encyclopedic. This section only captures the **bounded, high-value** cases: tables that don't exist (so `getschema` can't even help) and the handful of tables where the LLM hallucinates most.

### A. Phantom tables — these do NOT exist (getschema won't save you; use the alternative)

| Guessed name | Reality | Correct alternative |
|---|---|---|
| `ContainerOperationQoSEvent` | Never existed | `CRPContainerOperationsEtwTable` on `crp.CrpService` (MCP-unreachable) — or filter `ApiQosEvent_nonGet` on `azcrp/crp_allprod` by `resourceName` |
| `LiveMigrationTriggerLog` | Never existed | `LiveMigrationSessionCompleteLog` has `triggerType` |
| `LiveMigrationPerformanceLog` | Never existed | `LiveMigrationSessionCompleteLog` has `blackoutTimeInMs`, `durationInMs` |
| `NodeSnapshot` / `FabricNodeSnapshot` | Don't exist | `LogNodeSnapshot` is the ONLY node inventory table |

To discover a real table name: `.show database <db> tables | where TableName has '<keyword>'`.

### B. High-hallucination tables — use ONLY these columns (else `| getschema` first)

> For any **ad-hoc** query against these tables, use the correct columns below verbatim. Need a column not listed? Run `cluster('<host>').database('<db>').<Table> | getschema | where ColumnName has '<keyword>'` first. This is bounded on purpose — it is NOT a full schema; it is the 6 tables the LLM most often gets wrong.

| Table | Cluster.Database | Correct columns (most used) | Common WRONG names (DO NOT USE) |
|-------|-----------------|----------------------------|--------------------------------|
| `LogContainerSnapshot` | AzureCM.AzureCM | `containerId`, `nodeId`, `Tenant`, `roleInstanceName`, `tenantName`, `virtualMachineUniqueId`, `subscriptionId`, `creationTime`, `containerType`, `updateDomain`, `availabilitySetName`, `PreciseTimeStamp` | ~~containerIdString~~, ~~ClusterName~~, ~~cluster~~, ~~vmName~~, ~~containerName~~ |
| `LogNodeSnapshot` | AzureCM.AzureCM | `nodeId`, `Tenant`, `machinePoolName`, `nodeAvailabilityState`, `nodeState`, `faultDomain`, `updateDomain`, `PreciseTimeStamp` | ~~nodePropertyBag.MachinePool~~, ~~availabilityState~~, ~~cluster~~, ~~ClusterName~~ |
| `DiskManagerApiQoSEvent` | Disks.Disks | `e2EDurationInMilliseconds`, `subscriptionId`, `resourceGroupName`, `diskName`, `operationName`, `resultCode`, `PreciseTimeStamp` | ~~durationMs~~, ~~DurationMs~~, ~~duration~~, ~~durationInMilliseconds~~, ~~diskId~~ |
| `DiskManagerContextActivityEvent` | Disks.Disks | `activityId` (= ApiQoS `operationId`), `message`, `PreciseTimeStamp` | ~~resourceName~~, ~~operationId~~ (use `activityId`); for disk filter use `message has '<diskname>'` |
| `ApiQosEvent` / `ApiQosEvent_nonGet` | azcrp.crp_allprod | `subscriptionId`, `resourceName`, `operationName`, `httpStatusCode`, `resultCode`, `resultType`, `errorDetails`, `e2EDurationInMilliseconds`, `correlationId`, `operationId`, `PreciseTimeStamp` | ~~durationMs~~, ~~vmName~~, ~~containerId~~ (use `resourceName`), ~~correlationRequestId~~ (use `correlationId`) |
| `LiveMigrationSessionCompleteLog` | AzureCM.AzureCM | `triggerType`, `blackoutTimeInMs`, `durationInMs`, `containerId`, `nodeId`, `Tenant`, `PreciseTimeStamp` | (see Phantom tables — `LiveMigrationTriggerLog` / `LiveMigrationPerformanceLog` don't exist) |
| `CRPContainerOperationsEtwTable` | crp.CrpService (MCP-unreachable) | `containerId`, `nodeId`, `operationType`, `operationStatus`, `errorCode`, `errorMessage`, `durationMs`, `PreciseTimeStamp` | ~~containerIdString~~, ~~operationName~~ |

> Case-sensitivity note: several tables key on **lowercase** `containerId` / `nodeId` (e.g., `KronoxVmOperationEvent`). Match the exact casing from `getschema` — `ContainerId` ≠ `containerId`.

### C. Cluster switch — re-verify schema, never assume it carries over

When a primary cluster is unreachable (e.g., `crp.kusto.windows.net` is **not reachable via MCP**) and you switch to a follower/alternative, table AND column names may differ:

| Primary cluster.db | Use instead | Table/column differences |
|---|---|---|
| `crp.CrpService` (MCP-unreachable) | `azcrp.crp_allprod` / `azcsupfollower2.crp_allprod` | `CrpOperationQoSEtwTable` → `ApiQosEvent`; `CRPContainerOperationsEtwTable` has no `crp_allprod` equivalent; `correlationRequestId` → `correlationId` |

Procedure: run `<Table> | take 1` on the new cluster → confirm columns → update the query. Do not assume names carry over.

---

## MCP vs Python — which executor

The skill ships two executors. Pick by the table below; both auth via `AzureCliCredential` against tenant `72f988bf-86f1-41af-91ab-2d7cd011db47`.

| Situation | Prefer | Why |
|---|---|---|
| Default — any query in a curated catalog | **Azure MCP `kusto` tool** | Inline result rendering; tighter integration; faster turn-around |
| **≥3 independent queries in one investigation step** | **Python `kusto_runner.py --batch`** | One process, one auth pool, true concurrency, per-query timeout, isolated failures. See *Parallel Execution* below |
| Result > 1,000 rows expected | **Python `kusto_runner.py`** | MCP truncates / formats badly; Python can stream + serialize to `_work/<case>/data/*.json` |
| Need management commands (`.show`, `.set-or-replace`) | **Python** | MCP `kusto` tool sometimes refuses non-query KQL |
| Need automatic batch over multiple queries | **Python** (`kusto_vm_investigate.py` or custom) | One-shot 9-step VM walk; deterministic output |
| Cross-tenant query (e.g., a tenant other than Microsoft Corp) | **Python** | Re-credential via `AzureCliCredential(tenant_id=...)`; MCP defaults to current `az` context |
| Quick exploration / "show me 10 rows of X" | **MCP** | Lower friction |
| Output will feed another tool (Excel append, Python merge) | **Python** | Direct dict access; no parse of formatted text |

### Standard executor invocation

```python
# Python — single query
python scripts/kusto_runner.py \
  --cluster Azcsupfollower.kusto.windows.net \
  --database AzureCM \
  --query "LogContainerSnapshot | where ..."

# Python — automated VM 9-step
$env:PYTHONIOENCODING='utf-8'; python scripts/kusto_vm_investigate.py \
  --subscription-id <guid> \
  --vm-name <name> \
  --start-date 2026-06-10 --end-date 2026-06-11
```

For MCP, use the `kusto` tool directly with `--cluster-uri`, `--database`, `--query` parameters.

---

## Parallel Execution — eliminate the "10 minutes, no results" problem

> **Scope of this section: HOW to fan out, not WHETHER to run.** The decision to execute (auto-run / warn / confirm / hold) is governed by the **Execution Tiers** table in [SKILL.md → Step 3 — Execute](../../SKILL.md#step-3--execute), which has a dedicated *Parallel Behavior* column per tier. Always evaluate the tier first; if approved, use this section to pick the fan-out mechanism, worker count, and timeouts. The 🚫 opt-out (`先看 query` / `show me first`) overrides parallelism — never bypass it by claiming "it's just a batch".

The slowest part of any S2 FIND-AND-RUN step is rarely a single query — it's running 5–10 short queries one after another. Each MCP `kusto` call adds 1–3 s of RPC + render overhead even when the query returns in <500 ms; ten such calls in series feels like the agent has hung. Run them in parallel whenever the queries are **independent** (one query's body does NOT need another query's result).

### When to parallelize vs serialize

| Pattern | Decision | Example |
|---|---|---|
| Same time-range + identity, different tables/clusters | **Parallelize** | VMA + LogContainerHealthSnapshot + KronoxVmOperationEvent + CrpOperationQoSEtwTable for the same VM+window |
| Different symptom-bucket probes at the start of triage | **Parallelize** | `IsRestart`, `IsSlow`, `IsCantStart`, `IsMaintenance` shape-probes in parallel; pick winner |
| Multi-cluster cross-check (azurecm + crp + disks + nrp) | **Parallelize** | Confirming "did the SH event line up with CRP restart op + disk attach event?" |
| Subscription audit across regions / tenants | **Parallelize** | One query per region cluster, fan out |
| Step N's KQL uses Step N-1's identity output | **Serialize** | `LogContainerSnapshot` → extract `containerId` → use it in `FaultHandlingContainerFaultEventEtwTable`. This is why `kusto_vm_investigate.py` is sequential |
| Need to apply human / agent interpretation before deciding next query | **Serialize** | Tier-2 schema exploration (`take 1` → inspect → guess → validate) |

**Rule of thumb**: if the agent's mental model is "run these N queries, then look at all the results together," parallelize. If it is "run query A, decide based on the answer, then run B or C," serialize.

### Two ways to parallelize

#### Option 1 — MCP path (agent-driven fan-out)

Place multiple `mcp_azure_mcp_ser_kusto` calls in the **same** `function_calls` block. The agent runtime executes them concurrently. Use this for 2–4 independent queries when results are small (<1000 rows each) and the agent wants inline rendering.

```text
# Pseudo-call inside one assistant turn:
<function_calls>
  mcp_azure_mcp_ser_kusto(cluster=azurecm, database=AzureCM, query="VMA RCA ...")
  mcp_azure_mcp_ser_kusto(cluster=azurecm, database=AzureCM, query="LogContainerHealthSnapshot ...")
  mcp_azure_mcp_ser_kusto(cluster=azcrp,   database=crp_allprod, query="CrpOperationQoSEtwTable ...")
</function_calls>
```

Limit: ~4 parallel MCP calls per turn. Beyond that, switch to Option 2.

#### Option 2 — Python batch (`kusto_runner.py --batch`)

For ≥3 queries, or when results are large, or when you want a single JSON dump feeding a follow-up Python step:

```powershell
# 1. Write a JSON spec to _work/<case>/queries/batch.json
$env:PYTHONIOENCODING='utf-8'
python scripts/kusto_runner.py `
  --batch _work/<case-id>/queries/batch.json `
  --max-workers 5 `
  --server-timeout 60 `
  --wall-timeout 180 `
  --format json `
  > _work/<case-id>/data/batch-results.json
```

Spec file format (`_work/<case-id>/queries/batch.json`):
```json
[
  {"label": "vma_rca",       "cluster": "azurecm.kusto.windows.net",     "database": "AzureCM",     "query": "..."},
  {"label": "lch_snapshot",  "cluster": "azurecm.kusto.windows.net",     "database": "AzureCM",     "query": "..."},
  {"label": "crp_op",        "cluster": "azcrp.kusto.windows.net",       "database": "crp_allprod", "query": "..."},
  {"label": "disk_existence","cluster": "disks.kusto.windows.net",       "database": "Disks",       "query": "..."},
  {"label": "vm_kronox",     "cluster": "azurecm.kusto.windows.net",     "database": "AzureCM",     "query": "..."}
]
```

Output (`--format table` to chat, or `--format json` to file): one block per query labeled `[OK] / [ERROR] / [TIMEOUT]` with cluster, database, elapsed_ms, row count, then results; plus a final summary row.

What the batch runner guarantees:
- **One auth pool** — `KustoClient` per (cluster, tenant) cached process-wide; AAD token acquired once per cluster, not once per query.
- **True concurrency** — `ThreadPoolExecutor(max_workers=5)`; Kusto SDK is thread-safe.
- **Per-query server timeout** — `--server-timeout 60` (seconds) set as Kusto `servertimeout` ClientRequestProperty. A hung query gets aborted server-side, doesn't bleed budget.
- **Per-query wall-clock cap** — `--wall-timeout 180` (seconds) at the future level; if a thread refuses to return, it is marked `timeout` and the batch moves on.
- **Isolated failures** — one bad query never blocks the others; exit code is 0 if any query succeeded.
- **Order preserved** — output array index matches input spec index, so post-processing can match by position.

### Parallel-execution budget

The per-case budget in the table above applies to *queries*, not turns. Parallelism does NOT increase the budget — running 10 queries in parallel still counts as 10/30 queries used. The goal of parallelism is wall-clock latency, not query-volume amplification.

| Constraint | Limit |
|---|---|
| Max parallel MCP `kusto` calls per agent turn | 4 |
| Max `--max-workers` for Python batch (single cluster) | 5 |
| Max `--max-workers` for Python batch (≥3 clusters fanned out) | 8 |
| Server-side timeout per query | 60 s default, raise to 120 s only for known-expensive aggregations |
| Client wall-clock cap per query | 180 s default; if you hit this, the query is too broad — narrow it |

If a batch returns mostly `[TIMEOUT]` rows, the problem is query shape (missing identity filter, too-wide time window), not concurrency. Apply the **Query Guardrails** rules above before retrying.

---

## Stop-and-Report contract

When any guardrail / budget / permission / consecutive-error trigger fires, the agent must emit a chat message with:

```
[STOP] <one-line reason>

What we know:
- ... bullet
- ... bullet

What we tried (queries run: N / budget M):
1. <cluster.db.table>: <one-line result summary>
2. ...

Blockers:
- ... (JIT needed / PG-only data / 0-row pivot / etc.)

Suggested next:
- ... concrete action (request JIT / open collab / hand off to vm-log-analyzer)
```

Do not silently continue. Do not delete intermediate results. The user decides whether to push through.

---

## Cross-references

- The loop that calls these rules: [`investigation-loop.md`](investigation-loop.md)
- Pivot query interpretation: [`result-interpretation.md`](result-interpretation.md)
- Tier-2 fallback (when no curated KQL exists): [`schema-exploration-workflow.md`](schema-exploration-workflow.md)
- Variable convention: [`conventions.md`](conventions.md#variable-convention)
- KQL syntax / patterns: [`kql-language.md`](kql-language.md)
