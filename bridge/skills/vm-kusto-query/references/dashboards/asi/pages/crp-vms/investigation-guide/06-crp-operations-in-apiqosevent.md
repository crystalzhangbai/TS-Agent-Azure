# CRP Operations in ApiQosEvent

> Source: **CRP — VMs** dashboard, chapter **CRP Operations in ApiQosEvent** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### FilterOperations

_Widget purpose:_ CRP Operations in ApiQosEvent

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `Filter` · Widget: `Table`
Source panel: `CRP Operations in ApiQosEvent`

```kusto
datatable (Value:string, Description:string)
[
    "Critical", "Critical NonGet Operations",
    "ExcludeCallbacks", "NonGet Operations without Callbacks (default)",
    "NonGet", "NonGet Operations",    
    "All", "All Operations"    
]
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### Query VM Operations in ApiQosEvent

_Widget purpose:_ CRP Operations in ApiQosEvent

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `CRP Operations in ApiQosEvent`

```kusto
ApiQosEvent
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where subscriptionId  =~ querySubId
| where resourceGroupName  =~ queryResourceGroup
| where resourceName =~ queryResourceName or resourceName =~ strcat("_", queryResourceName) or resourceName startswith_cs strcat(queryResourceName, "/") or resourceName =~ strcat("virtualMachines/", queryResourceName)
| extend fitlerOperationType =  case (
  operationName contains "get", 0,
  operationName contains "Callback" or operationName contains "AsyncOperation", 1, 
  operationName has_any("AllocateDisks", "RetrieveBootDiagnosticsData", "RetrieveVMConsoleScreenshot", "PreflightRetrieveSasUri", "OnRoleInstanceStateChange",
  "Register", "Preflight", "ExtensionOperation", "RetrieveSasUris", "RetrieveVMConsoleSerialLogs"), 2, 
  3)
| where fitlerOperationType >= case (queryOpsFilter == "All", 0, queryOpsFilter == "NonGet", 1, queryOpsFilter == "ExcludeCallbacks", 2, queryOpsFilter == "Critical", 3,  2)
| extend level = iif(resultType == 0, iif(httpStatusCode < 300, "Info", "Error" ), "Error")
| extend resultType = case(resultType == 0, "Success", 
                       resultType == 1, "Client Failure", 
                       resultType == 2, "Server Failure",
                       "Unknown")
| extend StartTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| project StartTime, PreciseTimeStamp, operationId, operationName, resourceName,resultType, correlationId, clientApplicationId, e2eMin = (e2EDurationInMilliseconds/1000/60), httpStatusCode, resultCode, exceptionType, errorDetails, labels, requestEntity, goalSeekingActivityId, level
| extend errorDetails = iif(strlen(errorDetails)<500, errorDetails, strcat(substring(errorDetails, 0, 492), " ... ...")) 
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`, `{queryResourceGroup}`, `{queryResourceName}`, `{queryOpsFilter}`

---
