# (top-level)

> Source: **NRP - NRP Operation details** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### nrp operation details

_Widget purpose:_ Operation logs

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`

```kusto
let readTable = (FrontendReadOperationEtwEvent
| where PreciseTimeStamp between (datetime_add('day', -1, timestamp) .. datetime_add('day', 1, timestamp))
| where OperationId == operationId
| where SubscriptionId == subscriptionId
| project PreciseTimeStamp, Level, EventCode, Message, RoleInstance, SourceAssemblyFileVersion, Pid
| order by PreciseTimeStamp asc);
let writeTable = (FrontendOperationEtwEvent
| where PreciseTimeStamp between (datetime_add('day', -1, timestamp) .. datetime_add('day', 1, timestamp))
| where OperationId == operationId
| where SubscriptionId == subscriptionId
| project PreciseTimeStamp, Level, EventCode, Message, RoleInstance, SourceAssemblyFileVersion, Pid
| order by PreciseTimeStamp asc);
readTable
| union writeTable
```

**Params:** `{operationId}`, `{subscriptionId}`, `{timestamp}`

---
