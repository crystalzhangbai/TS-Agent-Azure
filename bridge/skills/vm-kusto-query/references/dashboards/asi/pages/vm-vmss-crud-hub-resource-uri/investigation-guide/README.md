# Resource URI — Investigation Guide

Chapter-keyed reference derived from the **Resource URI** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 7 queries
- [CRP Operation Premption flow](02-crp-operation-premption-flow.md) — 3 queries
- [Fabric Failover](03-fabric-failover.md) — 1 queries
- [NetworkingInternalOperationError](04-networkinginternaloperationerror.md) — 3 queries
- [Slow Extensions](05-slow-extensions.md) — 1 queries
- [VMStartTimedOut](06-vmstarttimedout.md) — 1 queries

**Total queries: 16**

## Query index (by file)

### (top-level)

- Retrieve Resource "Resource URI" — see [01-top-level.md](01-top-level.md)
- Failover Issue Detector Query — see [01-top-level.md](01-top-level.md)
- NeworkingInternalOperationError Detector  — see [01-top-level.md](01-top-level.md)
- Slow Extensions — see [01-top-level.md](01-top-level.md)
- VMStartTimedOut Detector — see [01-top-level.md](01-top-level.md)
- Failures / Slow operations — see [01-top-level.md](01-top-level.md)
- Active Azsm/Fabric Tenants — see [01-top-level.md](01-top-level.md)

### CRP Operation Premption flow

- PreemptedOperations V2 — see [02-crp-operation-premption-flow.md](02-crp-operation-premption-flow.md)
- Operations - StartTime — see [02-crp-operation-premption-flow.md](02-crp-operation-premption-flow.md)
- Operations - Lifecycle until preemption — see [02-crp-operation-premption-flow.md](02-crp-operation-premption-flow.md)

### Fabric Failover

- Get Failovers — see [03-fabric-failover.md](03-fabric-failover.md)

### NetworkingInternalOperationError

- statemachinevents — see [04-networkinginternaloperationerror.md](04-networkinginternaloperationerror.md)
- NIOE — see [04-networkinginternaloperationerror.md](04-networkinginternaloperationerror.md)
- RnmOperationEvents — see [04-networkinginternaloperationerror.md](04-networkinginternaloperationerror.md)

### Slow Extensions

- Slow Extensions v2 — see [05-slow-extensions.md](05-slow-extensions.md)

### VMStartTimedOut

- Container Unknown Duration — see [06-vmstarttimedout.md](06-vmstarttimedout.md)
