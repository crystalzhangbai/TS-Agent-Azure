# CRP OperationId Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **CRP OperationId Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Allocation Activity](02-allocation-activity.md) — 1 queries
- [ApiQosEvent](03-apiqosevent.md) — 1 queries
- [ComponentQosEvent](04-componentqosevent.md) — 3 queries
- [ContextActivity](05-contextactivity.md) — 2 queries
- [Execution Graph](06-execution-graph.md) — 1 queries
- [Extract SVD](07-extract-svd.md) — 1 queries
- [GatewayApiQoSEvent](08-gatewayapiqosevent.md) — 1 queries
- [Preemption State](09-preemption-state.md) — 1 queries
- [Target Resource - VM](10-target-resource-vm.md) — 2 queries
- [Target Resource - VMSS](11-target-resource-vmss.md) — 1 queries
- [VMApiQosEvent](12-vmapiqosevent.md) — 1 queries
- [VmssVMApiQosEvent](13-vmssvmapiqosevent.md) — 1 queries
- [VmssVMGoalSeekingActivity](14-vmssvmgoalseekingactivity.md) — 2 queries

**Total queries: 21**

## Query index (by file)

### (top-level)

- Retrieve Resource "Operation Id" — see [01-top-level.md](01-top-level.md)
- CSS Insight for NetworkingInternalOperation — see [01-top-level.md](01-top-level.md)
- CSS Insight for WaitForOngoingAllocation — see [01-top-level.md](01-top-level.md)

### Allocation Activity

- Compute Allocation Activity - ActivityId — see [02-allocation-activity.md](02-allocation-activity.md)

### ApiQosEvent

- ExecutionGraph — see [03-apiqosevent.md](03-apiqosevent.md)

### ComponentQosEvent

- API QoS — see [04-componentqosevent.md](04-componentqosevent.md)
- FilterGets — see [04-componentqosevent.md](04-componentqosevent.md)
- Query ComponentQoSEvent — see [04-componentqosevent.md](04-componentqosevent.md)

### ContextActivity

- OperationId ContextActivity — see [05-contextactivity.md](05-contextactivity.md)
- Filter - All or Errors — see [05-contextactivity.md](05-contextactivity.md)

### Execution Graph

- Lookup up EG — see [06-execution-graph.md](06-execution-graph.md)

### Extract SVD

- Extract SVD — see [07-extract-svd.md](07-extract-svd.md)

### GatewayApiQoSEvent

- OperationId GatewayApiQoSEvent GET — see [08-gatewayapiqosevent.md](08-gatewayapiqosevent.md)

### Preemption State

- Preemption — see [09-preemption-state.md](09-preemption-state.md)

### Target Resource - VM

- Get VM from VMApiQosEvent — see [10-target-resource-vm.md](10-target-resource-vm.md)
- OperationId GatewayApiQoSEvent GET — see [10-target-resource-vm.md](10-target-resource-vm.md)

### Target Resource - VMSS

- Get VMSS from GatewayApiQoSEvent — see [11-target-resource-vmss.md](11-target-resource-vmss.md)

### VMApiQosEvent

- OperationId VMApiQosEvent GET — see [12-vmapiqosevent.md](12-vmapiqosevent.md)

### VmssVMApiQosEvent

- OperationId VmssVMApiQosEvent GET — see [13-vmssvmapiqosevent.md](13-vmssvmapiqosevent.md)

### VmssVMGoalSeekingActivity

- OperationId VmssVMGoalSeekingActivity — see [14-vmssvmgoalseekingactivity.md](14-vmssvmgoalseekingactivity.md)
- Filter - All or Errors — see [14-vmssvmgoalseekingactivity.md](14-vmssvmgoalseekingactivity.md)
