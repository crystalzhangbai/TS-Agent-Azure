# NRP - Subnets — Investigation Guide

Chapter-keyed reference derived from the **NRP - Subnets** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [NSG](02-nsg.md) — 4 queries
- [Route Table](03-route-table.md) — 5 queries

**Total queries: 12**

## Query index (by file)

### (top-level)

- Retrieve Resource "Subnets" — see [01-top-level.md](01-top-level.md)
- Subnet Features — see [01-top-level.md](01-top-level.md)
- Subnet Private Endpoints — see [01-top-level.md](01-top-level.md)

### NSG

- Get Network Security Group — see [02-nsg.md](02-nsg.md)
- NSG Security Rules — see [02-nsg.md](02-nsg.md)
- NSG Updates — see [02-nsg.md](02-nsg.md)
- Graph NSG Snapshots — see [02-nsg.md](02-nsg.md)

### Route Table

- Route Table — see [03-route-table.md](03-route-table.md)
- Route Table Changes — see [03-route-table.md](03-route-table.md)
- Tim Query Created for Andy — see [03-route-table.md](03-route-table.md)
- Route Table Routes — see [03-route-table.md](03-route-table.md)
- NRP Route Table Snapshots — see [03-route-table.md](03-route-table.md)
