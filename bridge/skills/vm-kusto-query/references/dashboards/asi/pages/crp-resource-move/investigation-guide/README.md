# CRP Resource Move Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **CRP Resource Move Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [ARM Event](02-arm-event.md) — 2 queries
- [ARM HTTP Incoming](03-arm-http-incoming.md) — 1 queries
- [ARM HTTP Outgoing](04-arm-http-outgoing.md) — 1 queries
- [ARM Traces](05-arm-traces.md) — 1 queries

**Total queries: 7**

## Query index (by file)

### (top-level)

- Retrieve Resource "Resource Move" — see [01-top-level.md](01-top-level.md)
- Move ARM Event — see [01-top-level.md](01-top-level.md)

### ARM Event

- ARM Event — see [02-arm-event.md](02-arm-event.md)
- Error Details — see [02-arm-event.md](02-arm-event.md)

### ARM HTTP Incoming

- ARM HTTP Incoming — see [03-arm-http-incoming.md](03-arm-http-incoming.md)

### ARM HTTP Outgoing

- ARM HTTP Outgoing — see [04-arm-http-outgoing.md](04-arm-http-outgoing.md)

### ARM Traces

- ARM Trace — see [05-arm-traces.md](05-arm-traces.md)
