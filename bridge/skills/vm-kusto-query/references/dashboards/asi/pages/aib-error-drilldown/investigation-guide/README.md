# Error Drilldown — Investigation Guide

Chapter-keyed reference derived from the **Error Drilldown** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [ARM](01-arm.md) — 2 queries
- [AsyncContextActivity](02-asynccontextactivity.md) — 1 queries
- [AsyncQoSEvents](03-asyncqosevents.md) — 1 queries

**Total queries: 4**

## Query index (by file)

### ARM

- Incoming Requests — see [01-arm.md](01-arm.md)
- All or Errors — see [01-arm.md](01-arm.md)

### AsyncContextActivity

- AsyncContextActivity — see [02-asynccontextactivity.md](02-asynccontextactivity.md)

### AsyncQoSEvents

- AsyncQoSEvents by correlationID — see [03-asyncqosevents.md](03-asyncqosevents.md)
