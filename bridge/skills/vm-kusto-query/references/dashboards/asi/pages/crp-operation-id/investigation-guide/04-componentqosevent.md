# ComponentQosEvent

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **ComponentQosEvent** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ComponentQosEvent

### API QoS

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `CoBeTimeline`
Source panel: `ComponentQosEvent > ComponentQosEvent`

```kusto
let startDatetime = datetime_add('hour', -12, timeStamp);
let endDatetime = datetime_add('hour', 12, timeStamp);
CRPAPIQoS(operationId, startDatetime, endDatetime)
// adding the following to try and make the timeline less noisy.
| where EventName !in (
    'Fabric:GetTenantInformation',
    'Fabric:GetRoleInstanceContainerProvisioningDetails'
)
```

**Params:** `{operationId}`, `{timeStamp}`

---

### FilterGets

_Widget purpose:_ ComponentQoSEvent

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `Filter` · Widget: `Table`
Source panel: `ComponentQosEvent > ComponentQosEvent > ComponentQoSEvent`

```kusto
datatable (Value:string, Description:string)
[
    "FilterGets", "Exclude Get Operations (default)",
    "All", "All (Including Get Operations)"
]
```

---

### Query ComponentQoSEvent

_Widget purpose:_ ComponentQoSEvent

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `ComponentQosEvent > ComponentQosEvent > ComponentQoSEvent`

```kusto
let adjustedStart = datetime_add('hour', -6, queryBegin);
let adjustedEnd = datetime_add('hour', 6, queryEnd);
ComponentQoSEvent
| where PreciseTimeStamp between (adjustedStart .. adjustedEnd)
| where activityId =~ queryOperationId
| invoke ComponentQosEventExecutionStack(filterOutGets=(queryFilter != "All"))
| extend level = iif(operationResult == "Success", "info", iif(operationResult == "UnexpectedFailure", "error", "warning"))
| extend requestLink = iif(((componentName == "DiskRP") and isnotempty(serverRequestId)), 
    strcat("azureserviceinsights.trafficmanager.net/view/services/Managed%20Disk/pages/Operation%20Id?", "globalFrom=", datetime_add('hour', -1, startTime), "&globalTo=", datetime_add('hour', +1, endTime), "&operationId=", serverRequestId), 
    "")
| extend requestLink = iif(((componentName == "NRP") and isnotempty(serverRequestId)), 
    strcat("azureserviceinsights.trafficmanager.net/view/services/NRP/pages/Operation%20Id?", "globalFrom=", datetime_add('hour', -1, startTime), "&globalTo=", datetime_add('hour', +1, endTime), "&operationId=", serverRequestId), 
    requestLink)
| extend hasLink = isnotempty(requestLink)
| order by startTime asc
```

**Params:** `{queryOperationId}`, `{queryBegin}`, `{queryEnd}`, `{queryFilter}`

---
