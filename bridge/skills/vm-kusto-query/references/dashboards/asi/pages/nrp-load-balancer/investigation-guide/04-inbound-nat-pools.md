# Inbound Nat Pools

> Source: **NRP - Load Balancer** dashboard, chapter **Inbound Nat Pools** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Inbound NAT Pools

### SLB - Inbound NAT Pools

_Widget purpose:_ Inbound NAT Pools

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Inbound Nat Pools > Inbound NAT Pools`

```kusto
let idMatch = strcat("/subscriptions/", querySub, "/resourceGroups/", queryGroup, "/providers/Microsoft.Network/loadBalancers/", queryName);
cluster('argwus2nrpone.westus2.kusto.windows.net').database('AzureResourceGraph').Resources
| where isempty(queryTime) or timestamp between(datetime_add('hour', -1, queryTime) .. datetime_add('hour', 1, queryTime))
| where resourceGroup =~ queryGroup and subscriptionId =~ querySub
| where type == "microsoft.network/loadbalancers" and not(partial)
| where id =~ idMatch and not(deleted)
| top 1 by timestamp desc
| project JSON = parse_json(properties)
| mv-expand rule = JSON.inboundNatPools
| extend id = tostring(rule.id)
| extend name = tostring(rule.name)
| extend etag = tostring(rule.etag)
| extend type = tostring(rule.type)
| extend properties = rule.properties
| extend provisioningState = tostring(properties.provisioningState)
| extend idleTimeoutInMinutes = toint(properties.idleTimeoutInMinutes)
| extend protocol = tostring(properties.protocol)
| extend frontendIPConfiguration_id = tostring(properties.frontendIPConfiguration.id)
| extend frontendIPConfiguration_name= tostring(split(frontendIPConfiguration_id, "/")[-1])
| extend backendPort = toint(properties.backendPort)
| extend enableFloatingIP = tobool(properties.enableFloatingIP)
| extend enableDestinationServiceEndpoint = tobool(properties.enableDestinationServiceEndpoint)
| extend enableTcpReset = tobool(properties.enableTcpReset)
| extend allowBackendPortConflict = tobool(properties.allowBackendPortConflict)
| extend frontendPortRangeStart = toint(properties.frontendPortRangeStart)
| extend frontendPortRangeEnd = toint(properties.frontendPortRangeEnd)
| project-away rule, JSON, properties
```

**Params:** `{querySub}`, `{queryGroup}`, `{queryName}`, `{queryTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/loadbalancers"`

---
