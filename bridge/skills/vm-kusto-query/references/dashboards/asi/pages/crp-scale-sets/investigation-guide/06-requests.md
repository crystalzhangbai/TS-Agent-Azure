# Requests

> Source: **CRP — Scale Sets** dashboard, chapter **Requests** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### VMSS Requests

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Requests`

```kusto
ApiQosEvent_nonGet
| where PreciseTimeStamp between(queryFrom..queryTo) and subscriptionId == querySubscriptionId
| where resourceGroupName =~ queryResourceGroupName
| where resourceName has queryScaleSetName
| extend requestEntity = parse_json(requestEntity)
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend e2eSec = round(e2EDurationInMilliseconds/1000, 2)
| extend e2eMin = round(e2eSec/60, 2)
| extend level = iif(resultType == 0, "info", "error")
| extend resultType = case(
    resultType == 0, "Success", 
    resultType == 1, "Client Failure", 
    resultType == 2, "Server Failure",
    "Unknown"
)
| project startTime = startTime, endTime = PreciseTimeStamp, resourceGroupName, resourceName, e2eSec, e2eMin
    , operationId, clientApplicationId, clientRequestId, correlationId, operationName, httpStatusCode, resultType
    , resultCode, exceptionType, goalSeekingActivityId, errorDetails, requestEntity, level, userAgent
| extend errorHead = iif(strlen(errorDetails)<500, errorDetails, strcat(substring(errorDetails, 0, 492), " ... ...")) 
| extend instanceIDs = array_strcat(requestEntity.instanceIds, ', ')
| sort by startTime asc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryScaleSetName}`, `{queryFrom}`, `{queryTo}`

---
