# DiskManagerApiQoSEvent

> Source: **Managed Disk - Disks** dashboard, chapter **DiskManagerApiQoSEvent** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query DiskManagerApiQoSEvent

_Widget purpose:_ DiskManagerApiQoSEvent

Cluster: `Disks` · Database: `Disks` · Type: `Table`
Source panel: `DiskManagerApiQoSEvent`

```kusto
cluster("Disks").database("Disks").DiskManagerApiQoSEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionId == querySubId
| where resourceGroupName =~ queryResourceGroupName
| where resourceName =~ queryDiskName or requestEntity contains queryDiskName
| extend fitlerOperationType =  case (
  operationName contains "get", 0,
  operationName contains "Callback", 1, 
  operationName has_any("notify"), 2, 
  3)
| where fitlerOperationType >= case (queryOpsFilter == "All", 0, queryOpsFilter == "NonGet", 1, queryOpsFilter == "ExcludeCallbacks", 2, queryOpsFilter == "Critical", 3,  1)
| extend StartTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend requestEntity = parse_json(requestEntity)
| extend e2eMin = ceiling((e2EDurationInMilliseconds/1000/60.0))
| project StartTime, PreciseTimeStamp, operationName, operationId, clientRequestId, correlationId, resourceName,  e2eMin, resultCode, resultType, errorDetails, exceptionType, httpStatusCode,  requestEntity, clientApplicationId  
| extend level = iif(resultType == 0, iif(httpStatusCode < 300, "Info", "Error" ), "Error")
| extend resultType = case(resultType == 0, "Success", 
                       resultType == 1, "Client Failure", 
                       resultType == 2, "Server Failure",
                       "Unknown")
| order by StartTime  asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`, `{queryResourceGroupName}`, `{queryDiskName}`, `{queryOpsFilter}`

---

### FilterOperations

_Widget purpose:_ DiskManagerApiQoSEvent

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `Filter` · Widget: `Table`
Source panel: `DiskManagerApiQoSEvent`

```kusto
datatable (Value:string, Description:string)
[
    "Critical", "Critical NonGet Operations",
    "ExcludeCallbacks", "NonGet Operations without Callbacks",
    "NonGet", "NonGet Operations (default)",    
    "All", "All Operations"    
]
```

**Params:** `{queryFrom}`, `{queryTo}`

---
