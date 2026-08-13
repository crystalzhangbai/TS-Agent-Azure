# Resource Operations

> Source: **EEE CRP — VM Operation** dashboard, chapter **Resource Operations** (8 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Subscription Operations

### ARM Operation Timeline

_Widget purpose:_ ARM Operation Timeline for Subscription

Cluster: `armprod` · Database: `ARMProd` · Type: `Timeline`
Source panel: `Resource Operations > Subscription Operations > Subscription Operations > ARM > ARM > ARM Operation Timeline for Subscription`

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').HttpIncomingRequests
| where PreciseTimeStamp between (starttime..endtime)
// | where correlationId == correlationid
| where httpMethod <> "GET"
| where subscriptionId == "21128a5f-9486-40ab-bc5d-d398aadc0100"
// | where targetUri contains "xSellSrvPrd"
| where TaskName == "HttpIncomingRequestStart"
| project PreciseTimeStamp, RoleInstance, Level, ActivityId, TaskName, subscriptionId, correlationId, operationName, 
  httpMethod, hostName, targetUri, httpStatusCode, errorCode, errorMessage, durationInMilliseconds, 
  contentLength, referer, userAgent, clientIpAddress, SourceNamespace, failureCause, clientApplicationId
| project StartTime = PreciseTimeStamp, TaskName, correlationId, ActivityId
| join kind=leftouter (
    cluster('armprod.kusto.windows.net').database('ARMProd').HttpIncomingRequests
    | where PreciseTimeStamp between (starttime..endtime)
//     | where correlationId == correlationid
    | where subscriptionId == subscriptionid
    | where TaskName contains "HttpIncomingRequestEnd"
    | where httpMethod <> "GET"
    | project EndTime = PreciseTimeStamp, TaskName, operationName, correlationId, httpMethod, httpStatusCode, durationInMilliseconds, contentLength, errorCode, targetUri, clientIpAddress, authorizationAction, ActivityId
) on $left.correlationId == $right.correlationId and $left.ActivityId == $right.ActivityId
| order by StartTime asc
| extend GroupBy = authorizationAction, Content = tostring(httpStatusCode)
| extend Health = case (httpStatusCode >= 500, "Unhealthy", 
    httpStatusCode >= 400, "Degraded", 
    "Healthy")
```

**Params:** `{starttime}`, `{endtime}`, `{subscriptionid}`

**Signal filters seen in KQL:** `httpMethod <> "GET"` · `subscriptionId == "21128a5f-9486-40ab-bc5d-d398aadc0100"` · `targetUri contains "xSellSrvPrd"` · `TaskName == "HttpIncomingRequestStart"` · `TaskName contains "HttpIncomingRequestEnd"`

---

### CRP Operation Table

_Widget purpose:_ CRP Operations for Subscription

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Resource Operations > Subscription Operations > Subscription Operations > CRP > CRP > CRP Operations for Subscription`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(starttime .. endtime)
| where subscriptionId == subscriptionid
| where operationName !contains "GET"
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
| project StartTime, EndTime = PreciseTimeStamp, operationId, correlationId, operationName, resourceGroupName, resourceName, 
  httpStatusCode, e2EDurationInMilliseconds, durationInMin, resultCode, errorDetails, requestEntity, subscriptionId, userAgent, 
  apiVersion, labels, region, RPTenant, clientPrincipalName, clientRequestId
| extend level = case (isnotempty(resultCode), "error", "info")
| order by StartTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{subscriptionid}`

---

### CRP Operation Table

_Widget purpose:_ CRP Operations Timeline for Subscription

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`
Source panel: `Resource Operations > Subscription Operations > Subscription Operations > CRP > CRP > CRP Operations Timeline for Subscription`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(starttime .. endtime)
| where subscriptionId == subscriptionid
| where operationName !contains "GET"
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
| project StartTime, EndTime = PreciseTimeStamp, operationId, correlationId, operationName, resourceGroupName, resourceName, 
  httpStatusCode, e2EDurationInMilliseconds, durationInMin, resultCode, errorDetails, requestEntity, subscriptionId, userAgent, 
  apiVersion, labels, region, RPTenant, clientPrincipalName, clientRequestId
| extend Content = resultCode
| extend Health = case (isnotempty(resultCode), "Unhealthy", "Healthy")
| extend GroupBy = operationName
| order by operationName asc
```

**Params:** `{starttime}`, `{endtime}`, `{subscriptionid}`

---

## VM Operations

### ARM Operation for VM

_Widget purpose:_ ARM Operation

Cluster: `armprod` · Database: `ARMProd` · Type: `Table`
Source panel: `Resource Operations > VM Operations > VM Operations > ARM > ARM > ARM Operation`

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').HttpIncomingRequests
| where PreciseTimeStamp between (starttime..endtime)
// | where correlationId == correlationid
| where httpMethod <> "GET"
| where subscriptionId == subscriptionid
| where targetUri contains resourcename
| where TaskName == "HttpIncomingRequestStart"
| project StartTime = PreciseTimeStamp, TaskName, correlationId, ActivityId
| order by StartTime asc
| join kind=leftouter (
    cluster('armprod.kusto.windows.net').database('ARMProd').HttpIncomingRequests
    | where PreciseTimeStamp between (starttime..endtime)
    // | where correlationId == correlationid
    | where subscriptionId == subscriptionid
    | where targetUri contains resourcename
    | where TaskName contains "HttpIncomingRequestEnd"
    | where httpMethod <> "GET"
    | project EndTime = PreciseTimeStamp, TaskName, operationName, correlationId, httpMethod, httpStatusCode, durationInMilliseconds, contentLength, errorCode, errorMessage, targetUri, clientIpAddress, authorizationAction, ActivityId, failureCause
) on $left.correlationId == $right.correlationId and $left.ActivityId == $right.ActivityId
| project StartTime, EndTime, correlationId, operationName, httpMethod, httpStatusCode, errorCode, errorMessage, targetUri, failureCause
| order by StartTime asc
| extend level = case (httpStatusCode >= 500, "error", 
    httpStatusCode >= 400, "warning", 
    "info")
```

**Params:** `{starttime}`, `{endtime}`, `{subscriptionid}`, `{resourcename}`

**Signal filters seen in KQL:** `httpMethod <> "GET"` · `TaskName == "HttpIncomingRequestStart"` · `TaskName contains "HttpIncomingRequestEnd"`

---

### ARM Operation

_Widget purpose:_ ARM Operation Timeline

Cluster: `armprod` · Database: `ARMProd` · Type: `CoBeTimeline`
Source panel: `Resource Operations > VM Operations > VM Operations > ARM > ARM > ARM Operation Timeline`

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').HttpIncomingRequests
| where PreciseTimeStamp between (starttime..endtime)
// | where correlationId == correlationid
| where httpMethod <> "GET"
| where subscriptionId == subscriptionid
| where targetUri contains resourcename
| where TaskName == "HttpIncomingRequestStart"
| project PreciseTimeStamp, RoleInstance, Level, ActivityId, TaskName, subscriptionId, correlationId, operationName, 
  httpMethod, hostName, targetUri, httpStatusCode, errorCode, errorMessage, durationInMilliseconds, 
  contentLength, referer, userAgent, clientIpAddress, SourceNamespace, failureCause, clientApplicationId
| project StartTime = PreciseTimeStamp, TaskName, correlationId, ActivityId
| join kind=leftouter (
    cluster('armprod.kusto.windows.net').database('ARMProd').HttpIncomingRequests
    | where PreciseTimeStamp between (starttime..endtime)
    //| where correlationId == correlationid
    | where subscriptionId == subscriptionid
    | where targetUri contains resourcename
    | where TaskName contains "HttpIncomingRequestEnd"
    | where httpMethod <> "GET"
    | project EndTime = PreciseTimeStamp, TaskName, operationName, correlationId, httpMethod, httpStatusCode, durationInMilliseconds, contentLength, errorCode, targetUri, clientIpAddress, authorizationAction, ActivityId
) on $left.correlationId == $right.correlationId and $left.ActivityId == $right.ActivityId
| order by StartTime
| extend EventId = correlationId, EventName = strcat(httpMethod, " - ", authorizationAction)
| extend Health = case (httpStatusCode >= 500, "Unhealthy", 
  httpStatusCode >= 400, "Degraded", 
  "Healthy")
```

**Params:** `{starttime}`, `{endtime}`, `{subscriptionid}`, `{resourcename}`

**Signal filters seen in KQL:** `httpMethod <> "GET"` · `TaskName == "HttpIncomingRequestStart"` · `TaskName contains "HttpIncomingRequestEnd"`

---

### CRP Operations for VM

_Widget purpose:_ VM CRP Operations

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Resource Operations > VM Operations > VM Operations > CRP > CRP > VM CRP Operations`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(starttime .. endtime)
| where subscriptionId == subscriptionid
| where resourceName contains resourcename
| where resourceGroupName contains resourcegroupname
| where operationName !contains "GET"
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
| project StartTime, EndTime = PreciseTimeStamp, operationId, correlationId, operationName, resourceGroupName, resourceName, 
  httpStatusCode, e2EDurationInMilliseconds, durationInMin, resultCode, errorDetails, requestEntity, subscriptionId, userAgent, 
  apiVersion, labels, region, RPTenant, clientPrincipalName, clientRequestId
| order by StartTime asc
| extend level = case (resultCode <> "", "error", "info")
```

**Params:** `{starttime}`, `{endtime}`, `{subscriptionid}`, `{resourcename}`, `{resourcegroupname}`

---

### Retrieve Resource "VM Operation"

_Widget purpose:_ VM CRP Operations

Cluster: `azcrp` · Database: `crp_allprod` · Type: `ResourceGet` · Widget: `Table`
Source panel: `Resource Operations > VM Operations > VM Operations > CRP > CRP > VM CRP Operations`

```kusto
//print correlationId = local_correlationId, operationId = local_operationId
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(globalFrom .. globalTo)
| where operationId == local_operationId
| where operationName !contains ".GET"
| where operationName !contains "FabricCallback"
| where operationName !contains "NrpCallback"
| where operationName !contains "AllocateDisks"
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
| project StartTime, EndTime = PreciseTimeStamp, operationId, correlationId, operationName, resourceGroupName, resourceName, 
  httpStatusCode, e2EDurationInMilliseconds, durationInMin, resultCode, errorDetails, requestEntity, subscriptionId, userAgent, 
  apiVersion, labels, region, RPTenant, clientPrincipalName, clientRequestId
| project correlationId, operationId, subscriptionId, resourceGroupName, resourceName
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_correlationId}`, `{local_operationId}`

---

### VM Operation

_Widget purpose:_ VM Operation Timeline

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`
Source panel: `Resource Operations > VM Operations > VM Operations > CRP > CRP > VM Operation Timeline`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(starttime .. endtime)
| where subscriptionId == subscriptionid
| where resourceName contains resourcename
| where operationName !contains "GET"
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
| project StartTime, EndTime = PreciseTimeStamp, operationId, correlationId, operationName, resourceGroupName, resourceName, 
  httpStatusCode, e2EDurationInMilliseconds, durationInMin, resultCode, errorDetails, requestEntity, subscriptionId, userAgent, 
  apiVersion, labels, region, RPTenant, clientPrincipalName, clientRequestId
| extend Content = resultCode
| extend Health = case (isnotempty(resultCode), "Unhealthy", "Healthy")
| extend GroupBy = operationName
| order by operationName
```

**Params:** `{starttime}`, `{endtime}`, `{subscriptionid}`, `{resourcename}`

---
