# VmssVMGoalSeekingActivity

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **VmssVMGoalSeekingActivity** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VmssVMGoalSeekingActivity

### OperationId VmssVMGoalSeekingActivity

_Widget purpose:_ VmssVMGoalSeekingActivity - operationId {{operationId}}

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `VmssVMGoalSeekingActivity > VmssVMGoalSeekingActivity > VmssVMGoalSeekingActivity - operationId {{operationId}}`

```kusto
let adjustedStart = datetime_add('hour', -6, local_startDate);
let adjustedEnd = datetime_add('hour', 6, local_endDate);
VmssVMGoalSeekingActivity
//| where PreciseTimeStamp between (adjustedStart..adjustedEnd)
| where activityId =~ local_operationId
| where not(queryFilter == 'errors') or traceLevel < 8
| where traceLevel <= qMaxLevel
| project PreciseTimeStamp, traceLevel, message, vMName, callerName
| extend level = case(
    traceLevel == 4, 'warn', 
    traceLevel == 2, 'error', 
    'info'
)
| order by PreciseTimeStamp desc
```

**Params:** `{local_operationId}`, `{local_endDate}`, `{local_startDate}`, `{queryFilter}`, `{qMaxLevel}`

---

### Filter - All or Errors

_Widget purpose:_ VmssVMGoalSeekingActivity - operationId {{operationId}}

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `Filter` · Widget: `Table`
Source panel: `VmssVMGoalSeekingActivity > VmssVMGoalSeekingActivity > VmssVMGoalSeekingActivity - operationId {{operationId}}`

```kusto
datatable (Value:string, Description:string)
[
    "all", "All (default)",
    "errors", "Errors only"
]
```

---
