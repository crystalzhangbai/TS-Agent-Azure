# (top-level)

> Source: **NRP - Route Tables** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Route Tables"

Cluster: `nrp` · Database: `binrp` · Type: `ResourceGet` · Widget: `Container`

```kusto
NRP_RouteTable
| where isempty(local_timestamp) or PreciseTimeStamp between(datetime_add("minute", -15, local_timestamp)..datetime_add("minute", 15, local_timestamp))
| where SubscriptionId == local_subscriptionId and GroupName =~ local_resourceGroupName and Name =~ local_name
| top 1 by PreciseTimeStamp desc
```

**Params:** `{local_name}`, `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_timestamp}`

---

### Route Table

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Single` · Widget: `Container`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where (isnotempty(queryRouteTableName) and isnotempty(queryResourceGroupName)) 
    and (name =~ queryRouteTableName and resourceGroup =~ queryResourceGroupName) 
| where subscriptionId =~ querySubscriptionId
| where type == "microsoft.network/routetables" and not(partial) and not(deleted)
| summarize 
    arg_max(timestamp, properties), 
    take_any(name, type, tenantId, location, resourceGroup, subscriptionId, apiVersion)
    by id
| extend subnets = array_length(properties.subnets)
| extend routes = array_length(properties.routes)
| extend provisioningState = tostring(properties.provisioningState)
| extend disableBgpRoutePropagation = tobool(properties.disableBgpRoutePropagation)
| project id, name, type, tenantId, location, resourceGroup, subscriptionId, apiVersion,
    subnets, routes, provisioningState, disableBgpRoutePropagation
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryRouteTableName}`, `{queryOptionalHintTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/routetables"`

---
