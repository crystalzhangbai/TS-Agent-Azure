# NRP - ReadOperationService — Investigation Guide

Chapter-keyed reference derived from the **NRP - ReadOperationService** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

**How to use:**

1. Identify which dashboard chapter matches what you're investigating.
2. Open the matching section file from the list below.
3. Pick the query whose name / source panel / filter tips match your symptom.
4. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.
5. Execute via the **vm-kusto-query** skill (`kusto_runner.py`) or via the `replay.py` next to this folder (handles param aliases).

**Companion files (in parent folder):**

- `library.json` — canonical machine-readable source of all queries (panel-organized).
- `library.md`   — same content as flat human-readable index.
- `meta.json`    — pageId, totals, ASI URL.

## Files

- [(top-level)](01-top-level.md) — 3 queries
- [5xx Error Frequencies](02-5xx-error-frequencies.md) — 1 queries
- [5xx Error Rates](03-5xx-error-rates.md) — 1 queries
- [Enablement Status](04-enablement-status.md) — 1 queries
- [GetVirtualNetworkOperation Concurrency Cirrus Runs](05-getvirtualnetworkoperation-concurrency-cirrus-runs.md) — 1 queries
- [ReadOperationService Load](06-readoperationservice-load.md) — 1 queries
- [RemoteDataAccess RPC Latencies](07-remotedataaccess-rpc-latencies.md) — 1 queries

**Total queries: 9**

## Query index (by file)

### (top-level)

- ReadOperationService OperationCount — see [01-top-level.md](01-top-level.md)
- ReadOperationService OperationReliability — see [01-top-level.md](01-top-level.md)
- ReadOperationService GatewayReliability — see [01-top-level.md](01-top-level.md)

### 5xx Error Frequencies

- ReadOperationService Errors — see [02-5xx-error-frequencies.md](02-5xx-error-frequencies.md)

### 5xx Error Rates

- ReadOperationService ErrorRates — see [03-5xx-error-rates.md](03-5xx-error-rates.md)

### Enablement Status

- ReadOperationService OperationEnablement — see [04-enablement-status.md](04-enablement-status.md)

### GetVirtualNetworkOperation Concurrency Cirrus Runs

- ReadOperationService GetVnet Cirrus — see [05-getvirtualnetworkoperation-concurrency-cirrus-runs.md](05-getvirtualnetworkoperation-concurrency-cirrus-runs.md)

### ReadOperationService Load

- ReadOperationService OperationTimeseries — see [06-readoperationservice-load.md](06-readoperationservice-load.md)

### RemoteDataAccess RPC Latencies

- ReadOperationService RPC Latency — see [07-remotedataaccess-rpc-latencies.md](07-remotedataaccess-rpc-latencies.md)
