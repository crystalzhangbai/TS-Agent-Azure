# Unhealthy Node Analysis - Node Recovery Detail — Investigation Guide

Chapter-keyed reference derived from the **Unhealthy Node Analysis - Node Recovery Detail** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [Anvil Repair Events](01-anvil-repair-events.md) — 1 queries
- [Container Snapshot](02-container-snapshot.md) — 1 queries
- [LogNodeSnapshot](03-lognodesnapshot.md) — 1 queries
- [Node Diagnostic Details](04-node-diagnostic-details.md) — 1 queries
- [Node Events](05-node-events.md) — 1 queries

**Total queries: 5**

## Query index (by file)

### Anvil Repair Events

- Anvil Repair events — see [01-anvil-repair-events.md](01-anvil-repair-events.md)

### Container Snapshot

- Container Snapshot — see [02-container-snapshot.md](02-container-snapshot.md)

### LogNodeSnapshot

- LogNodeSnapshot Query — see [03-lognodesnapshot.md](03-lognodesnapshot.md)

### Node Diagnostic Details

- Node Diagnostic Detail — see [04-node-diagnostic-details.md](04-node-diagnostic-details.md)

### Node Events

- Node events — see [05-node-events.md](05-node-events.md)
