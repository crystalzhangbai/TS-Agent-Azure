# Component and Compute Allocations for {{operationId}}

> Source: **CRP VM Start Troubleshooter Investigation Guide** dashboard, chapter **Component and Compute Allocations for {{operationId}}** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### CRP Allocation and Component Events

_Widget purpose:_ Component and Compute Allocations for {{operationId}}

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Component and Compute Allocations for {{operationId}}`

```kusto
let components = ComponentQoSEvent
| where PreciseTimeStamp between(queryFrom..queryTo)
| where activityId == queryOperationId
| extend SourceTable = "ComponentQoSEvent";
let compute = ComputeAllocationActivity
| where PreciseTimeStamp between(queryFrom..queryTo)
| where activityId == queryOperationId
| extend SourceTable = "ComputeAllocationActivity";
union components, compute
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOperationId}`

---
