# DiskManagerContextActivityEvent 

> Source: **DRP — Operation Id** dashboard, chapter **DiskManagerContextActivityEvent ** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query DiskManagerContextActivityEvent

_Widget purpose:_ DiskManagerContextActivityEvent 

Cluster: `Disks` · Database: `Disks` · Type: `Table`
Source panel: `DiskManagerContextActivityEvent `

```kusto
DiskManagerContextActivityEvent
| where PreciseTimeStamp  between ((queryStartTime-1h) .. (queryEndTime+1h))
| where activityId == queryOperationId
| project PreciseTimeStamp, callerName, message
| order by PreciseTimeStamp asc
```

**Params:** `{queryStartTime}`, `{queryEndTime}`, `{queryOperationId}`

---

### Retrieve Resource "Operation Id"

_Widget purpose:_ DiskManagerContextActivityEvent 

Cluster: `disks` · Database: `Disks` · Type: `ResourceGet` · Widget: `Table`
Source panel: `DiskManagerContextActivityEvent `

```kusto
DiskManagerApiQoSEvent
| where PreciseTimeStamp between (globalFrom .. globalTo)
| where operationId =~ local_operationId
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| project startTime, endTime = PreciseTimeStamp, operationName, operationId, clientRequestId, correlationId, resourceName, resultCode, resultType, errorDetails, exceptionType, httpStatusCode,requestEntity, internalCorrelationId, e2eInMin = e2EDurationInMilliseconds/1000/60
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_operationId}`

---
