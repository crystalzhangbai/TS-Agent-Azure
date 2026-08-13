# (top-level)

> Source: **Managed Disk - Correlation Id** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Correlation Id"

Cluster: `Disks` · Database: `Disks` · Type: `ResourceGet` · Widget: `Container`

```kusto
let disks = DiskManagerApiQoSEvent
  //| where PreciseTimeStamp between(globalFrom .. globalTo)
  | where case(isnotempty(local_correlationId), correlationId =~ local_correlationId, false)
  //| where case(isnotempty(local_operationId), operationId =~ local_operationId, true)
  //| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
  //| project startTime, endTime = PreciseTimeStamp, subscriptionId, operationId, correlationId, operationName, resourceName, e2EDurationInMilliseconds, httpStatusCode, resultCode, errorDetails, e2eInMin = e2EDurationInMilliseconds/1000/60
  | extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp), endTime = PreciseTimeStamp, e2eInMin = e2EDurationInMilliseconds/1000/60
  | extend OperationPriority = case(
    operationName has "PUT", 1,
    operationName has "DELETE", 2,
    operationName has "POST", 3,
    operationName has "GET", 4,
    5 // Default priority for others
  );
disks
  | summarize Priority = arg_min(OperationPriority, *) by operationId 
  | sort by Priority asc
  | take 1
```

**Params:** `{local_correlationId}`, `{globalFrom}`, `{globalTo}`

---

### CRP

Cluster: `Disks` · Database: `Disks` · Type: `Single` · Widget: `Card`

```kusto
let ext_start = queryTime-timespan(30m);
let ext_end = queryTime+timespan(30m);
let disks = DiskManagerApiQoSEvent
  | where PreciseTimeStamp between(ext_start .. ext_end)
  | where case(isnotempty(queryCorrelationId), correlationId =~ queryCorrelationId, false)
  | where case(isnotempty(queryOperationId), operationId =~ queryOperationId, true)
  //| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
  //| project startTime, endTime = PreciseTimeStamp, subscriptionId, operationId, correlationId, operationName, resourceName, e2EDurationInMilliseconds, httpStatusCode, resultCode, errorDetails, e2eInMin = e2EDurationInMilliseconds/1000/60
  | extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp), endTime = PreciseTimeStamp, e2eInMin = e2EDurationInMilliseconds/1000/60;
disks
```

**Params:** `{queryTime}`, `{queryCorrelationId}`, `{queryOperationId}`

---

### Fabric & Aztec

Cluster: `Disks` · Database: `Disks` · Type: `Single` · Widget: `Card`

```kusto
let ext_start = queryTime-timespan(30m);
let ext_end = queryTime+timespan(30m);
let disks = DiskManagerApiQoSEvent
  | where PreciseTimeStamp between(ext_start .. ext_end)
  | where case(isnotempty(queryCorrelationId), correlationId =~ queryCorrelationId, false)
  //| where case(isnotempty(queryOperationId), operationId =~ queryOperationId, true)
  //| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
  //| project startTime, endTime = PreciseTimeStamp, subscriptionId, operationId, correlationId, operationName, resourceName, e2EDurationInMilliseconds, httpStatusCode, resultCode, errorDetails, e2eInMin = e2EDurationInMilliseconds/1000/60
  | extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp), endTime = PreciseTimeStamp, e2eInMin = e2EDurationInMilliseconds/1000/60;
let regionFriendlyName = disks | project region | take 1;
let regionName = cluster("AzureCM").database("AzureCM").LogClusterSnapshot | where RegionFriendlyName =~ toscalar(regionFriendlyName) | project Region | take 1;
disks
| extend RegionName = toscalar(regionName)
```

**Params:** `{queryTime}`, `{queryCorrelationId}`

---
