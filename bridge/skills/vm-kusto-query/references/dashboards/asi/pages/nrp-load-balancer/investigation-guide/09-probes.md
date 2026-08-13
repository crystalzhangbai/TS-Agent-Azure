# Probes

> Source: **NRP - Load Balancer** dashboard, chapter **Probes** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Probes

### SLB - Probes

_Widget purpose:_ Probes

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Probes > Probes`

```kusto
let idMatch = strcat("/subscriptions/", querySub, "/resourceGroups/", queryGroup, "/providers/Microsoft.Network/loadBalancers/", queryName);
cluster('argwus2nrpone.westus2.kusto.windows.net').database('AzureResourceGraph').Resources
| where isempty(queryTime) or timestamp between(datetime_add('hour', -1, queryTime) .. datetime_add('hour', 1, queryTime))
| where resourceGroup =~ queryGroup and subscriptionId =~ querySub
| where type == "microsoft.network/loadbalancers" and not(partial)
| where id =~ idMatch and not(deleted)
| top 1 by timestamp desc
| mv-expand probe = properties.probes
| extend id = tostring(probe.id)
| extend name = tostring(probe.name)
| extend etag = tostring(probe.etag)
| extend type = tostring(probe.type)
| extend probe_props = probe.properties
| extend provisioningState = tostring(probe_props.provisioningState)
| extend protocol = tostring(probe_props.protocol)
| extend loadBalancingRules = probe_props.loadBalancingRules
| extend port = toint(probe_props.port)
| extend intervalInSeconds = toint(probe_props.intervalInSeconds)
| extend numberOfProbes = toint(probe_props.numberOfProbes)
| extend probeThreshold = toint(probe_props.probeThreshold)
| project-away probe, probe_props, properties
```

**Params:** `{querySub}`, `{queryGroup}`, `{queryName}`, `{queryTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/loadbalancers"`

---
