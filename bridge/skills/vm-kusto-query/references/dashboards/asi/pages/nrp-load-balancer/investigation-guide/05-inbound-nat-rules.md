# Inbound Nat Rules

> Source: **NRP - Load Balancer** dashboard, chapter **Inbound Nat Rules** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Inbound NAT Rules

### SLB - Inbound Nat Rules

_Widget purpose:_ Inbound NAT Rules

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Inbound Nat Rules > Inbound NAT Rules`

```kusto
let idMatch = strcat("/subscriptions/", querySub, "/resourceGroups/", queryGroup, "/providers/Microsoft.Network/loadBalancers/", queryName);
cluster('argwus2nrpone.westus2.kusto.windows.net').database('AzureResourceGraph').Resources
| where isempty(queryTime) or timestamp between(datetime_add('hour', -1, queryTime) .. datetime_add('hour', 1, queryTime))
| where resourceGroup =~ queryGroup and subscriptionId =~ querySub
| where type == "microsoft.network/loadbalancers" and not(partial)
| where id =~ idMatch and not(deleted)
| top 1 by timestamp desc
| project JSON = parse_json(properties)
| mv-expand rule = JSON.inboundNatRules
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
| extend frontendPort = toint(properties.frontendPort)
| extend backendPort = toint(properties.backendPort)
| extend enableFloatingIP = tobool(properties.enableFloatingIP)
| extend enableDestinationServiceEndpoint = tobool(properties.enableDestinationServiceEndpoint)
| extend enableTcpReset = tobool(properties.enableTcpReset)
| extend allowBackendPortConflict = tobool(properties.allowBackendPortConflict)
| project-away rule, JSON, properties
```

**Params:** `{querySub}`, `{queryGroup}`, `{queryName}`, `{queryTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/loadbalancers"`

---
