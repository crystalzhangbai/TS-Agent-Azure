# Target Resource - VM

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **Target Resource - VM** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get VM from VMApiQosEvent

_Widget purpose:_ Target Resource - VM

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`
Source panel: `Target Resource - VM`

```kusto
VMApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where operationId =~ queryOperationId
| project subscriptionId = tolower(subscriptionId), resourceGroupName = tolower(resourceGroupName), resourceName=tolower(resourceName), VMId = tolower(vMId)
| extend targetARMResourceId = strcat("/subscriptions/", subscriptionId, "/resourceGroups/", resourceGroupName, "/providers/Microsoft.Compute/virtualMachines/", resourceName)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOperationId}`

---

### OperationId GatewayApiQoSEvent GET

_Widget purpose:_ Target Resource - VM

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`
Source panel: `Target Resource - VM`

```kusto
let adjustedStart = datetime_add('hour', -6, local_startDate);
let adjustedEnd = datetime_add('hour', 6, local_endDate);
GatewayApiQoSEvent
| where PreciseTimeStamp between (adjustedStart..adjustedEnd)
| where operationId =~ local_operationId
| extend startIndex = indexof(targetEndpoint, "/subscriptions")
| extend resourceId = substring(targetEndpoint, startIndex, indexof(targetEndpoint,"?") - startIndex)
| project PreciseTimeStamp,httpStatusCode,resultCode,lastPhase,targetEndpoint,targetRPNode,serviceName,serviceBuild,userName, resourceId
```

**Params:** `{local_operationId}`, `{local_endDate}`, `{local_startDate}`

---
