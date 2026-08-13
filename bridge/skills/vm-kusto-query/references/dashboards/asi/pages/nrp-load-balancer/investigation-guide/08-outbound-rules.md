# Outbound Rules

> Source: **NRP - Load Balancer** dashboard, chapter **Outbound Rules** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Outbound Rules

### SLB - Outbound Rules

_Widget purpose:_ Outbound Rules

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Outbound Rules > Outbound Rules`

```kusto
let idMatch = strcat("/subscriptions/", querySub, "/resourceGroups/", queryGroup, "/providers/Microsoft.Network/loadBalancers/", queryName);
cluster('argwus2nrpone.westus2.kusto.windows.net').database('AzureResourceGraph').Resources
| where isempty(queryTime) or timestamp between(datetime_add('hour', -1, queryTime) .. datetime_add('hour', 1, queryTime))
| where resourceGroup =~ queryGroup and subscriptionId =~ querySub
| where type == "microsoft.network/loadbalancers" and not(partial)
| where id =~ idMatch and not(deleted)
| top 1 by timestamp desc
| mv-expand rule = properties.outboundRules
| extend id = tostring(rule.id)
| extend name = tostring(rule.name)
| extend etag = tostring(rule.etag)
| extend type = tostring(rule.type)
| extend rule_props = rule.properties
| extend provisioningState = tostring(rule_props.provisioningState)
| extend idleTimeoutInMinutes = toint(rule_props.idleTimeoutInMinutes)
| extend protocol = tostring(rule_props.protocol)
| extend enableTcpReset = tobool(rule_props.enableTcpReset)
| extend allocatedOutboundPorts = toint(rule_props.allocatedOutboundPorts)
| extend backendAddressPool_id = tostring(rule_props.backendAddressPool.id)
| extend backendAddressPool_name= tostring(split(backendAddressPool_id, "/")[-1])
| extend frontendIPConfigurations = rule_props.frontendIPConfigurations
| project-away rule, rule_props, properties
```

**Params:** `{querySub}`, `{queryGroup}`, `{queryName}`, `{queryTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/loadbalancers"`

---
