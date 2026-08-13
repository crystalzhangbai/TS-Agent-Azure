# GatewayServiceTraceEvent

> Source: **Aztec RelatedActivityId Investigation Guide** dashboard, chapter **GatewayServiceTraceEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## GatewayServiceTraceEvent

### RelatedActivityId GatewayServiceTraceEvent

_Widget purpose:_ GatewayServiceTraceEvent

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `GatewayServiceTraceEvent > GatewayServiceTraceEvent`

```kusto
let queryFrom = datetime_add("day", -1, queryOperationTime);
let queryTo = datetime_add("day", 1, queryOperationTime);
let ActivityIds=CommonWebOperationStart
| where PreciseTimeStamp between (queryFrom..queryTo)
| where RelatedActivityId =~ local_RelatedActivityId
| distinct ActivityId;
GatewayServiceTraceEvent
| where PreciseTimeStamp between (queryFrom..queryTo)
| where ActivityId in (ActivityIds)
| project PreciseTimeStamp,ActivityId,level,message
| order by PreciseTimeStamp desc
```

**Params:** `{local_RelatedActivityId}`, `{queryOperationTime}`

---
