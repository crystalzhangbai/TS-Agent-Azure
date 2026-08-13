# NRP - Nrp Performance Drilldown — Investigation Guide

Chapter-keyed reference derived from the **NRP - Nrp Performance Drilldown** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [Batch Manager Summary](01-batch-manager-summary.md) — 7 queries
- [EG Breakdown](02-eg-breakdown.md) — 1 queries
- [Exclusive Write Attribution](03-exclusive-write-attribution.md) — 1 queries
- [QOS Overview](04-qos-overview.md) — 1 queries
- [Resource Locking Summary](05-resource-locking-summary.md) — 2 queries
- [Subscription Lock Summary](06-subscription-lock-summary.md) — 1 queries
- [Top Possible Perf Issues](07-top-possible-perf-issues.md) — 4 queries
- [Transaction Stats](08-transaction-stats.md) — 2 queries

**Total queries: 19**

## Query index (by file)

### Batch Manager Summary

- Batch Job Durations — see [01-batch-manager-summary.md](01-batch-manager-summary.md)
- Batch Manager Queue Processing Percentiles — see [01-batch-manager-summary.md](01-batch-manager-summary.md)
- Batch Sizes — see [01-batch-manager-summary.md](01-batch-manager-summary.md)
- Commit Duration — see [01-batch-manager-summary.md](01-batch-manager-summary.md)
- Long Running Jobs — see [01-batch-manager-summary.md](01-batch-manager-summary.md)
- Worst Performing Non-Tenant Operations — see [01-batch-manager-summary.md](01-batch-manager-summary.md)
- Worst Performing Tenant Operations — see [01-batch-manager-summary.md](01-batch-manager-summary.md)

### EG Breakdown

- NRP EG Percentile Times — see [02-eg-breakdown.md](02-eg-breakdown.md)

### Exclusive Write Attribution

- ExclusiveWriteTimes — see [03-exclusive-write-attribution.md](03-exclusive-write-attribution.md)

### QOS Overview

- QOS Overview — see [04-qos-overview.md](04-qos-overview.md)

### Resource Locking Summary

- Resource Locks Acquired — see [05-resource-locking-summary.md](05-resource-locking-summary.md)
- Resource Lock Acquisition Failures — see [05-resource-locking-summary.md](05-resource-locking-summary.md)

### Subscription Lock Summary

- Subscription Lock Durations — see [06-subscription-lock-summary.md](06-subscription-lock-summary.md)

### Top Possible Perf Issues

- Highest Read Size Operations — see [07-top-possible-perf-issues.md](07-top-possible-perf-issues.md)
- Longest EG Frames — see [07-top-possible-perf-issues.md](07-top-possible-perf-issues.md)
- Longest Sub Locks — see [07-top-possible-perf-issues.md](07-top-possible-perf-issues.md)
- Slowest Batch Jobs — see [07-top-possible-perf-issues.md](07-top-possible-perf-issues.md)

### Transaction Stats

- Resource Type Read Count — see [08-transaction-stats.md](08-transaction-stats.md)
- Transaction Stats — see [08-transaction-stats.md](08-transaction-stats.md)
