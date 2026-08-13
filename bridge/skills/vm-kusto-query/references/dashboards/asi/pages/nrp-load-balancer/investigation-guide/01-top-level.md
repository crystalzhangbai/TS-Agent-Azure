# (top-level)

> Source: **NRP - Load Balancer** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Load Balancer"

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `ResourceGet` · Widget: `Container`

```kusto
let idMatch = strcat("/subscriptions/", local_subscriptionId, "/resourceGroups/", local_resourceGroup, "/providers/Microsoft.Network/loadBalancers/", local_name);
cluster('argwus2nrpone.westus2.kusto.windows.net').database('AzureResourceGraph').Resources
| where isempty(local_timestamp) or timestamp between(datetime_add('hour', -1, local_timestamp) .. datetime_add('hour', 1, local_timestamp))
| where resourceGroup =~ local_resourceGroup and subscriptionId =~ local_subscriptionId
| where type == "microsoft.network/loadbalancers" and not(partial)
| where id =~ idMatch and not(deleted)
| top 1 by timestamp desc
| extend provisioningState = properties.provisioningState
| extend resourceGuid = properties.resourceGuid
| project-away properties
```

**Params:** `{local_name}`, `{local_resourceGroup}`, `{local_subscriptionId}`, `{local_timestamp}`

**Signal filters seen in KQL:** `type == "microsoft.network/loadbalancers"`

---

### Load Balancer Operation Timeline

_Widget purpose:_ Operation Timeline

Cluster: `nrp` · Database: `mdsnrp` · Type: `Timeline`

```kusto
cluster("nrp.kusto.windows.net").database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between(queryFrom..queryTo) 
| where ResourceName =~ queryResourceName and ResourceGroup =~ queryResourceGroupName and SubscriptionId == querySubscriptionId 
| where ResourceType == "loadBalancers" and HttpMethod != "GET"
| project todatetime(StartTime), Content = OperationName, OperationId, CorrelationRequestId, NRPGatewayRequestId, ClientOperationId, 
    DurationInMilliseconds, Success, ErrorCode, ErrorDetails, InternalErrorCode
| summarize take_any(*) by OperationId
| extend Health = iff(Success, "", "Unhealthy")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryResourceName}`

**Signal filters seen in KQL:** `ResourceType == "loadBalancers"`

---
