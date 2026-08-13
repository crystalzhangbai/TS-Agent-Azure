# Disk Manager Events

> Source: **Confidential Virtual Machines - Confidential Virtual Machine** dashboard, chapter **Disk Manager Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Disk Manager Events

Cluster: `disks` · Database: `Disks` · Type: `Table`
Source panel: `Disk Manager Events`

```kusto
DiskManagerApiQoSEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where correlationId == queryCorrelationId
| project 
    PreciseTimeStamp, 
    CorrelationId = correlationId, 
    OperationName = operationName, 
    OperationId = operationId, 
    ResourceGroupName = tolower(resourceGroupName), 
    ResourceName = tolower(resourceName),
    E2EDurationInMilliseconds = e2EDurationInMilliseconds,
    HttpStatusCode = httpStatusCode,
    ResultCode = resultCode,
    ExceptionType = exceptionType,
    ErrorDetails = errorDetails,
    RequestBody = requestEntity
| sort by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCorrelationId}`

---
