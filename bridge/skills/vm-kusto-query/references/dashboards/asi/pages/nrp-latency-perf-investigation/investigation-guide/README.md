# NRP - Latency and Performance Investigation Dashboard — Investigation Guide

Chapter-keyed reference derived from the **NRP - Latency and Performance Investigation Dashboard** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [Batch Sizes](01-batch-sizes.md) — 1 queries
- [Long Running Jobs](02-long-running-jobs.md) — 1 queries
- [Queue Processing Percentiles](03-queue-processing-percentiles.md) — 1 queries

**Total queries: 3**

## Query index (by file)

### Batch Sizes

- Batch Sizes — see [01-batch-sizes.md](01-batch-sizes.md)

### Long Running Jobs

- Long Running Jobs — see [02-long-running-jobs.md](02-long-running-jobs.md)

### Queue Processing Percentiles

- Queue Processing Percentiles — see [03-queue-processing-percentiles.md](03-queue-processing-percentiles.md)
