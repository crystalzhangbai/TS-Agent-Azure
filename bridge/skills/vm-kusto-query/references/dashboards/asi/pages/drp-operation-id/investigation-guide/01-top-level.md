# (top-level)

> Source: **DRP — Operation Id** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Operation Id"

Cluster: `disks` · Database: `Disks` · Type: `ResourceGet` · Widget: `Container`

```kusto
DiskManagerApiQoSEvent
| where PreciseTimeStamp between (globalFrom .. globalTo)
| where operationId =~ local_operationId
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| project startTime, endTime = PreciseTimeStamp, operationName, operationId, clientRequestId, correlationId, resourceName, resultCode, resultType, errorDetails, exceptionType, httpStatusCode,requestEntity, internalCorrelationId, e2eInMin = e2EDurationInMilliseconds/1000/60
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_operationId}`

---
