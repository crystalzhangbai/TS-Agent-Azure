# Aztec Nodes Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Aztec Nodes Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 8 queries
- [Containers](02-containers.md) — 3 queries
- [Disk Health](03-disk-health.md) — 1 queries
- [High CPU](04-high-cpu.md) — 1 queries

**Total queries: 13**

## Query index (by file)

### (top-level)

- Retrieve Resource "Nodes" — see [01-top-level.md](01-top-level.md)
- Node Flags — see [01-top-level.md](01-top-level.md)
- Node Hosting Environment — see [01-top-level.md](01-top-level.md)
- Node State — see [01-top-level.md](01-top-level.md)
- Node Availability State — see [01-top-level.md](01-top-level.md)
- Node OS Image — see [01-top-level.md](01-top-level.md)
- Node Disk Configuration — see [01-top-level.md](01-top-level.md)
- Node VMA — see [01-top-level.md](01-top-level.md)

### Containers

- Node container counts — see [02-containers.md](02-containers.md)
- Host Node Container Timeline — see [02-containers.md](02-containers.md)
- Node Containers — see [02-containers.md](02-containers.md)

### Disk Health

- Node Disk Health — see [03-disk-health.md](03-disk-health.md)

### High CPU

- Node High CPU — see [04-high-cpu.md](04-high-cpu.md)
