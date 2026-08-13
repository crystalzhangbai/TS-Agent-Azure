# Tenant QoS

> Source: **Aztec — Tenant** dashboard, chapter **Tenant QoS** (9 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Tenant QoS

### Query TMClusterFabricAuditEtwTable

_Widget purpose:_ Fabricator Calls from TMClusterFabricAuditEtwTable

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Tenant QoS > Tenant QoS > Fabric Calls > Fabricator Calls from TMClusterFabricAuditEtwTable`

```kusto
TMClusterFabricAuditEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where ParameterNamesAndValues contains queryTenantName
| where queryFilterValue == "All" or (InterfaceName !contains "get" and InterfaceNamespace != "GET")
| project PreciseTimeStamp, Tenant, ActivityId, CorrelationState, UserName, ClientAddress, InterfaceNamespace, InterfaceName, OperationName, ParameterNamesAndValues
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryFilterValue}`

**Signal filters seen in KQL:** `queryFilterValue == "All"`

---

### FilterGetOperations

_Widget purpose:_ Fabricator Calls from TMClusterFabricAuditEtwTable

Cluster: `azurecm` · Database: `Azurecm` · Type: `Filter` · Widget: `Table`
Source panel: `Tenant QoS > Tenant QoS > Fabric Calls > Fabricator Calls from TMClusterFabricAuditEtwTable`

```kusto
datatable (Value:string, Description:string)
[
    "ExcludeGet", "Exclude Get Operations (default)",
    "All", "All Operations"
]
```

---

### Query ComponentQoSEvent

_Widget purpose:_ Fabric Operations submit by CRP - ComponentQoSEvent 

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Tenant QoS > Tenant QoS > Requests by CRP > Fabric Operations submit by CRP - ComponentQoSEvent `

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ComponentQoSEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where fabricTenantName == queryTenantName
| where componentName == "Fabric"
| extend StartTime = datetime_add('millisecond', -toint(durationInMs), PreciseTimeStamp)
| extend level = case(
    operationResult == "UnexpectedFailure", "Error",
    operationResult != "Success", "Warning",
    "Info"
)
| where queryFilterValue == "All" or operationName !contains "get"
| project StartTime, PreciseTimeStamp, subscriptionId, activityId,  componentName, operationName, operationResult, resultDetails, durationInMs, fabricCluster, level
| order by StartTime asc, PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryFilterValue}`

**Signal filters seen in KQL:** `componentName == "Fabric"` · `queryFilterValue == "All"`

---

### FilterGetOperations

_Widget purpose:_ Fabric Operations submit by CRP - ComponentQoSEvent 

Cluster: `azurecm` · Database: `Azurecm` · Type: `Filter` · Widget: `Table`
Source panel: `Tenant QoS > Tenant QoS > Requests by CRP > Fabric Operations submit by CRP - ComponentQoSEvent `

```kusto
datatable (Value:string, Description:string)
[
    "ExcludeGet", "Exclude Get Operations (default)",
    "All", "All Operations"
]
```

---

### Query Operations in CommonWebOperationEnd

_Widget purpose:_ Operations from CommonWebOperationEnd

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > CommonWebOperationEnd > Operations from CommonWebOperationEnd`

```kusto
CommonWebOperationEnd
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where Url contains queryTenantName
| extend level = case(
    Result == "Success", "Info",
    Result == "Unknown", "Warning",
    "Error"
)
| where queryFilterValue == "All" or (Action !contains 'get' and Action != "Unknown" and HttpMethod != "GET")
| extend StartTime = datetime_add('millisecond', -TimeInMilliSeconds, PreciseTimeStamp)
| project StartTime, PreciseTimeStamp, Tenant, Action, HttpMethod, Url, HttpStatusCode, Result, Exception, RegionFriendlyName, TimeInMilliSeconds, ClientIP, ClientType, UserName, RequestSize, ResponseSize, Controller, ProcessName, ConfigurationType, ActivityId, RelatedActivityId, AvailabilityZone, level 
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryFilterValue}`

**Signal filters seen in KQL:** `queryFilterValue == "All"`

---

### FilterGetOperations

_Widget purpose:_ Operations from CommonWebOperationEnd

Cluster: `azurecm` · Database: `Azurecm` · Type: `Filter` · Widget: `Table`
Source panel: `Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > CommonWebOperationEnd > Operations from CommonWebOperationEnd`

```kusto
datatable (Value:string, Description:string)
[
    "ExcludeGet", "Exclude Get Operations (default)",
    "All", "All Operations"
]
```

---

### Query GatewayRequestCompleted

_Widget purpose:_ GatewayRequestCompleted

Cluster: `azcpplatform.westcentralus.kusto.windows.net` · Database: `azcpplatform` · Type: `Table`
Source panel: `Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > GatewayService > GatewayService > GatewayRequestCompleted`

```kusto
GatewayRequestCompleted
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where requestUri  contains queryTenantName
| project PreciseTimeStamp, requestUri, Tenant, ActivityId, userIdentity, clientType, clientIp, clientClaims, httpMethod,  requestSize, responseSize, result, httpStatusCode, SourceMoniker, SourceNamespace, timeInMilliseconds, upstreamTimeInMilliseconds, downstreamTimeInMilliseconds, externalTimeInMilliseconds, internalTimeInMilliseconds
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query GatewayServiceTraceEvent

_Widget purpose:_ GatewayServiceTraceEvent

Cluster: `azcpplatform.westcentralus.kusto.windows.net` · Database: `azcpplatform` · Type: `Table`
Source panel: `Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > GatewayService > GatewayService > GatewayServiceTraceEvent`

```kusto
GatewayServiceTraceEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where message contains queryTenantName
| where queryFilterValue == "All" or level in ("Warning", "Error")
| project PreciseTimeStamp, ActivityId, level, componentName, message, RoleInstance
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryFilterValue}`

**Signal filters seen in KQL:** `queryFilterValue == "All"`

---

### FilterMessages

_Widget purpose:_ GatewayServiceTraceEvent

Cluster: `azurecm` · Database: `AzureCM` · Type: `Filter` · Widget: `Table`
Source panel: `Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > GatewayService > GatewayService > GatewayServiceTraceEvent`

```kusto
datatable (Value:string, Description:string)
[
    "Critical", "Critical Messages/Errors/Warnings/Exceptions/Failures (default)",
    "All", "All Logs/Events"
]
```

---
