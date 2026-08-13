# Blob Inventory Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Blob Inventory Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 1 queries
- [Account Rules Status & SLO](02-account-rules-status-slo.md) — 1 queries
- [Pages - Storage Tools](03-pages-storage-tools.md) — 2 queries
- [Recent Run](04-recent-run.md) — 1 queries
- [Rule Definition](05-rule-definition.md) — 1 queries
- [Scheduler Logs](06-scheduler-logs.md) — 1 queries

**Total queries: 7**

## Query index (by file)

### (top-level)

- Get Tenant Info by Account — see [01-top-level.md](01-top-level.md)

### Account Rules Status & SLO

- Get Account Inventory Rules & SLO — see [02-account-rules-status-slo.md](02-account-rules-status-slo.md)

### Pages - Storage Tools

- Get Tenant Info by Account — see [03-pages-storage-tools.md](03-pages-storage-tools.md)
- TrimStorageName — see [03-pages-storage-tools.md](03-pages-storage-tools.md)

### Recent Run

- Get Blob Inventory Task Run — see [04-recent-run.md](04-recent-run.md)

### Rule Definition

- Get Blob Inventory Rule Definition — see [05-rule-definition.md](05-rule-definition.md)

### Scheduler Logs

- Get Blob Inventory Scheduler Logs — see [06-scheduler-logs.md](06-scheduler-logs.md)
