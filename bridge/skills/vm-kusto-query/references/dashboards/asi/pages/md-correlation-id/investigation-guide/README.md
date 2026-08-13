# Managed Disk - Correlation Id — Investigation Guide

Chapter-keyed reference derived from the **Managed Disk - Correlation Id** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [ApiQosEvent](02-apiqosevent.md) — 1 queries
- [DiskManagerApiQoSEvent](03-diskmanagerapiqosevent.md) — 1 queries
- [DiskManagerContextActivityEvent](04-diskmanagercontextactivityevent.md) — 1 queries
- [DiskRPResourceLifecycleEvent](05-diskrpresourcelifecycleevent.md) — 1 queries
- [HttpIncomingRequests](06-httpincomingrequests.md) — 1 queries
- [HttpOutgoingRequests](07-httpoutgoingrequests.md) — 1 queries

**Total queries: 9**

## Query index (by file)

### (top-level)

- Retrieve Resource "Correlation Id" — see [01-top-level.md](01-top-level.md)
- CRP — see [01-top-level.md](01-top-level.md)
- Fabric & Aztec — see [01-top-level.md](01-top-level.md)

### ApiQosEvent

- ApiQosEvent — see [02-apiqosevent.md](02-apiqosevent.md)

### DiskManagerApiQoSEvent

- DiskManagerApiQoSEvent — see [03-diskmanagerapiqosevent.md](03-diskmanagerapiqosevent.md)

### DiskManagerContextActivityEvent

- DiskManagerContextActivityEvent — see [04-diskmanagercontextactivityevent.md](04-diskmanagercontextactivityevent.md)

### DiskRPResourceLifecycleEvent

- DiskRPResourceLifecycleEvent — see [05-diskrpresourcelifecycleevent.md](05-diskrpresourcelifecycleevent.md)

### HttpIncomingRequests

- HttpIncomingRequests — see [06-httpincomingrequests.md](06-httpincomingrequests.md)

### HttpOutgoingRequests

- HttpOutgoingRequests — see [07-httpoutgoingrequests.md](07-httpoutgoingrequests.md)
