# (top-level)

> Source: **Managed Disk - Operation Id** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Operation Id"

Cluster: `disks` · Database: `Disks` · Type: `ResourceGet` · Widget: `Container`

```kusto
DiskManagerApiQoSEvent
//| where PreciseTimeStamp between (globalFrom .. globalTo)
| where operationId =~ local_operationId
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| project startTime, endTime = PreciseTimeStamp, operationName, operationId, clientRequestId, correlationId, resourceName, resultCode, resultType, errorDetails, exceptionType, httpStatusCode,requestEntity, internalCorrelationId, e2eInMin = e2EDurationInMilliseconds/1000/60, clientApplicationId
```

**Params:** `{local_operationId}`, `{globalFrom}`, `{globalTo}`

---

### Target Disks from RequestEntity

_Widget purpose:_ Target Disks

Cluster: `Disks` · Database: `Disks` · Type: `Table`

```kusto
let crpDiskIds = toscalar(cluster("Disks").database("Disks").DiskManagerApiQoSEvent
| where PreciseTimeStamp between ((queryFrom-1h) .. (queryTo+1h))
| where operationId == queryOperationId
| extend disks = extract_all('"crpDiskId": "([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"', requestEntity)
| project disks);
cluster("Disksbi").database("DisksBi").Disk 
| where PreciseTimeStamp between ((queryFrom-1h) .. (queryTo+1h))
| where CrpDiskId in (crpDiskIds)
| summarize arg_max(PreciseTimeStamp, *) by CrpDiskId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOperationId}`

---
