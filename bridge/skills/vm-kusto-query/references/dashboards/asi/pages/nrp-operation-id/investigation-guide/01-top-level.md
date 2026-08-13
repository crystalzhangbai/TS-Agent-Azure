# (top-level)

> Source: **NRP - Operation Id** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Operation Id"

Cluster: `nrp` · Database: `mdsnrp` · Type: `ResourceGet` · Widget: `Container`

```kusto
QosEtwEvent 
| where PreciseTimeStamp between(globalFrom .. globalTo)
| where OperationId == local_OperationId
| summarize arg_max(Sequence, *)
| project StartTime, PreciseTimeStamp, CorrelationRequestId, OperationId, HttpMethod, ErrorCode, UserError, Success, ErrorDetails, TeamName, ResourceType, ResourceName, OperationName, Region, TraceSource, SubscriptionId, ResourceGroup, DurationInMilliseconds
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_OperationId}`

---

### Query FrontendOperationEtwEvent

_Widget purpose:_ FrontendOperationEtwEvent Table

Cluster: `nrp` · Database: `mdsnrp` · Type: `Table`

```kusto
FrontendOperationEtwEvent 
| where PreciseTimeStamp between (queryGlobalFrom .. queryGlobalTo)
| where OperationId == queryOperationId
| project PreciseTimeStamp, Level, EventCode, Message 
| order by PreciseTimeStamp asc
```

**Params:** `{queryGlobalFrom}`, `{queryGlobalTo}`, `{queryOperationId}`

---
