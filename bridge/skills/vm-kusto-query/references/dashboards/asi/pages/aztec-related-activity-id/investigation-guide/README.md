# Aztec RelatedActivityId Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Aztec RelatedActivityId Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Allocation Activity](02-allocation-activity.md) — 1 queries
- [CommonWebOperationEnd](03-commonweboperationend.md) — 1 queries
- [CommonWebOperationStart](04-commonweboperationstart.md) — 1 queries
- [GatewayServiceTraceEvent](05-gatewayservicetraceevent.md) — 1 queries

**Total queries: 6**

## Query index (by file)

### (top-level)

- Retrieve Resource "RelatedActivityId" — see [01-top-level.md](01-top-level.md)
- RelatedActivityId CRP QoS Get — see [01-top-level.md](01-top-level.md)

### Allocation Activity

- Compute Allocation Activity - ActivityId — see [02-allocation-activity.md](02-allocation-activity.md)

### CommonWebOperationEnd

- RelatedActivityId CommonWebOperationEnd — see [03-commonweboperationend.md](03-commonweboperationend.md)

### CommonWebOperationStart

- RelatedActivityId CommonWebOperationStart — see [04-commonweboperationstart.md](04-commonweboperationstart.md)

### GatewayServiceTraceEvent

- RelatedActivityId GatewayServiceTraceEvent — see [05-gatewayservicetraceevent.md](05-gatewayservicetraceevent.md)
