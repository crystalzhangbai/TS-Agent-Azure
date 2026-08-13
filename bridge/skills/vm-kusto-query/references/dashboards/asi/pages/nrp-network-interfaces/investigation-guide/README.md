# NRP - Network Interfaces — Investigation Guide

Chapter-keyed reference derived from the **NRP - Network Interfaces** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Current Rules](02-current-rules.md) — 1 queries
- [NSG Updates](03-nsg-updates.md) — 1 queries
- [Snapshots](04-snapshots.md) — 1 queries

**Total queries: 6**

## Query index (by file)

### (top-level)

- Retrieve Resource "Network Interfaces" — see [01-top-level.md](01-top-level.md)
- NIC IP Configurations — see [01-top-level.md](01-top-level.md)
- Get Network Security Group — see [01-top-level.md](01-top-level.md)

### Current Rules

- NSG Security Rules — see [02-current-rules.md](02-current-rules.md)

### NSG Updates

- NSG Updates — see [03-nsg-updates.md](03-nsg-updates.md)

### Snapshots

- Graph NSG Snapshots — see [04-snapshots.md](04-snapshots.md)
