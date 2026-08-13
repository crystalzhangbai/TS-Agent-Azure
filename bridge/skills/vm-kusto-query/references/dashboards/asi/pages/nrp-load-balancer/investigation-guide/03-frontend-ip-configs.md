# Frontend IP Configs

> Source: **NRP - Load Balancer** dashboard, chapter **Frontend IP Configs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Front End IP Configurations

### SLB - Front End IP Configurations

_Widget purpose:_ Front End IP Configurations

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Frontend IP Configs > Front End IP Configurations`

```kusto
let idMatch = strcat("/subscriptions/", querySub, "/resourceGroups/", queryGroup, "/providers/Microsoft.Network/loadBalancers/", queryName);
cluster('argwus2nrpone.westus2.kusto.windows.net').database('AzureResourceGraph').Resources
| where isempty(queryTime) or timestamp between(datetime_add('hour', -1, queryTime) .. datetime_add('hour', 1, queryTime))
| where resourceGroup =~ queryGroup and subscriptionId =~ querySub
| where type == "microsoft.network/loadbalancers" and not(partial)
| where id =~ idMatch and not(deleted)
| top 1 by timestamp desc
| mv-expand fe_ip = properties.frontendIPConfigurations
| extend id = fe_ip.id
| extend name = fe_ip.name
| extend etag = fe_ip.etag
| extend type = fe_ip.type
| extend fe_props = fe_ip.properties
| extend provisioningState = fe_props.provisioningState
| extend privateIPAllocationMethod = fe_props.privateIPAllocationMethod
| extend publicIPAddress_id = fe_props.publicIPAddress.id
| parse publicIPAddress_id with "/subscriptions/" publicIPAddress_sub "/resourceGroups/" publicIPAddress_rg "/providers/Microsoft.Network/publicIPAddresses/" publicIPAddress_name
| extend loadBalancingRules = fe_props.loadBalancingRules
| extend outboundRules = fe_props.outboundRules
| project-away fe_ip, properties, fe_props
```

**Params:** `{querySub}`, `{queryGroup}`, `{queryName}`, `{queryTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/loadbalancers"`

---
