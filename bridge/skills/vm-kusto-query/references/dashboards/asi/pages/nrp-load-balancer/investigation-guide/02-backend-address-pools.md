# Backend Address Pools

> Source: **NRP - Load Balancer** dashboard, chapter **Backend Address Pools** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Backend Address Pools

### SLB - Backend Address Pools

_Widget purpose:_ Backend Address Pools

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Backend Address Pools > Backend Address Pools`

```kusto
let idMatch = strcat("/subscriptions/", querySub, "/resourceGroups/", queryGroup, "/providers/Microsoft.Network/loadBalancers/", queryName);
cluster('argwus2nrpone.westus2.kusto.windows.net').database('AzureResourceGraph').Resources
| where isempty(queryTime) or timestamp between(datetime_add('hour', -1, queryTime) .. datetime_add('hour', 1, queryTime))
| where resourceGroup =~ queryGroup and subscriptionId =~ querySub
| where type == "microsoft.network/loadbalancers" and not(partial)
| where id =~ idMatch and not(deleted)
| top 1 by timestamp desc
| mv-expand pool = properties.backendAddressPools
| extend id = tostring(pool.id)
| extend name = tostring(pool.name)
| extend etag = tostring(pool.etag)
| extend type = tostring(pool.type)
| extend pool_props = pool.properties
| extend provisioningState = tostring(pool_props.provisioningState)
| extend loadBalancerBackendAddresses = pool_props.loadBalancerBackendAddresses
| extend backendIPConfigurations = pool_props.backendIPConfigurations
| extend loadBalancingRules = pool_props.loadBalancingRules
| project-away pool, properties, pool_props
```

**Params:** `{querySub}`, `{queryGroup}`, `{queryName}`, `{queryTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/loadbalancers"`

---
