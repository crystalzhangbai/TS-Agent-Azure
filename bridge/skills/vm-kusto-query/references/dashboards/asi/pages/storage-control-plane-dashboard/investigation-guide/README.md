# Storage Control Plane Dashboard Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Storage Control Plane Dashboard Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [ARM Operations](02-arm-operations.md) — 1 queries
- [Pages - Storage Tools](03-pages-storage-tools.md) — 2 queries
- [SRP Operations](04-srp-operations.md) — 1 queries
- [SRP Throttling Detector](05-srp-throttling-detector.md) — 1 queries

**Total queries: 6**

## Query index (by file)

### (top-level)

- Get Tenant Info by Account — see [01-top-level.md](01-top-level.md)

### ARM Operations

- Get account ARM requests — see [02-arm-operations.md](02-arm-operations.md)

### Pages - Storage Tools

- Get Tenant Info by Account — see [03-pages-storage-tools.md](03-pages-storage-tools.md)
- TrimStorageName — see [03-pages-storage-tools.md](03-pages-storage-tools.md)

### SRP Operations

- List SRP Operations  — see [04-srp-operations.md](04-srp-operations.md)

### SRP Throttling Detector

- Detect SRP throttling Errors — see [05-srp-throttling-detector.md](05-srp-throttling-detector.md)
