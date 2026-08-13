# ContextActivity

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **ContextActivity** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ContextActivity

### OperationId ContextActivity

_Widget purpose:_ ContextActivity - operationId {{operationId}}

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `ContextActivity > ContextActivity > ContextActivity - operationId {{operationId}}`

```kusto
ContextActivity
| where PreciseTimeStamp between ((queryOpStartTime - 1h) .. (queryOpEndTime + 2h))
| where activityId =~ local_operationId
| where not(queryFilter == 'errors') or traceLevel < 8
| project PreciseTimeStamp, traceLevel, callerName, message
| extend level = case(
    traceLevel == 4, 'warn', 
    traceLevel == 2, 'error', 
    'info'
)
| order by PreciseTimeStamp asc
```

**Params:** `{local_operationId}`, `{queryFilter}`, `{queryOpStartTime}`, `{queryOpEndTime}`

---

### Filter - All or Errors

_Widget purpose:_ ContextActivity - operationId {{operationId}}

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `Filter` · Widget: `Table`
Source panel: `ContextActivity > ContextActivity > ContextActivity - operationId {{operationId}}`

```kusto
datatable (Value:string, Description:string)
[
    "all", "All (default)",
    "errors", "Errors only"
]
```

---
