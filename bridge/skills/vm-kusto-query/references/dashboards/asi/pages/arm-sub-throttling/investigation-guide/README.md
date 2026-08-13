# ARM — Sub Throttling — Investigation Guide

Chapter-keyed reference derived from the **ARM — Sub Throttling** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

**Total queries: 8**

## Query index (by file)

### (top-level)

- Retrieve Resource "Sub Throttling" — see [01-top-level.md](01-top-level.md)
- Retrieve Resource "Subscriptions" — see [01-top-level.md](01-top-level.md)
- Get Throttling — see [01-top-level.md](01-top-level.md)
- Get RP Throttling — see [01-top-level.md](01-top-level.md)
- Subscription Requests — see [01-top-level.md](01-top-level.md)
- Get Sub Requests — see [01-top-level.md](01-top-level.md)
- ARM - throttles by provider — see [01-top-level.md](01-top-level.md)
- Get RP Throttling — see [01-top-level.md](01-top-level.md)
