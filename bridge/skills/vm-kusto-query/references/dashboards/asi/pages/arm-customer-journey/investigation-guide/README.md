# ARM Customer Journey Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **ARM Customer Journey Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 10 queries

**Total queries: 10**

## Query index (by file)

### (top-level)

- Retrieve Resource "Customer Journey" — see [01-top-level.md](01-top-level.md)
- new subscriptions — see [01-top-level.md](01-top-level.md)
- Retention — see [01-top-level.md](01-top-level.md)
- Control Plane Request — see [01-top-level.md](01-top-level.md)
- Client Failures — see [01-top-level.md](01-top-level.md)
- Server Failures — see [01-top-level.md](01-top-level.md)
- Write Operations — see [01-top-level.md](01-top-level.md)
- ARM - Doc Views — see [01-top-level.md](01-top-level.md)
- Portal Traffic — see [01-top-level.md](01-top-level.md)
- Non-Portal Traffic — see [01-top-level.md](01-top-level.md)
