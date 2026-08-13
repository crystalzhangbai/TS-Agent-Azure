# NRP - Route Tables — Investigation Guide

Chapter-keyed reference derived from the **NRP - Route Tables** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 2 queries
- [Route Table Updates](02-route-table-updates.md) — 1 queries
- [Route Updates](03-route-updates.md) — 1 queries
- [Routes](04-routes.md) — 1 queries
- [Snapshots](05-snapshots.md) — 1 queries

**Total queries: 6**

## Query index (by file)

### (top-level)

- Retrieve Resource "Route Tables" — see [01-top-level.md](01-top-level.md)
- Route Table — see [01-top-level.md](01-top-level.md)

### Route Table Updates

- Route Table Changes — see [02-route-table-updates.md](02-route-table-updates.md)

### Route Updates

- Tim Query Created for Andy — see [03-route-updates.md](03-route-updates.md)

### Routes

- Route Table Routes — see [04-routes.md](04-routes.md)

### Snapshots

- NRP Route Table Snapshots — see [05-snapshots.md](05-snapshots.md)
