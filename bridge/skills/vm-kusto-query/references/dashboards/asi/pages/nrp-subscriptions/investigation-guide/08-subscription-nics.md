# Subscription NICs

> Source: **NRP - Subscriptions** dashboard, chapter **Subscription NICs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Subscription NICs

_Widget purpose:_ Subscription NICs

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Subscription NICs`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where subscriptionId =~ querySubscriptionId
| where isempty(queryOptionalResourceGroupName) or resourceGroup =~ queryOptionalResourceGroupName
| where type in ('microsoft.compute/virtualmachinescalesets/virtualmachines/networkinterfaces', 'microsoft.network/networkinterfaces')
| where not(deleted) and isnotempty(properties)
| summarize arg_max(timestamp, *) by id
| extend Region = location
| extend provisioningState = tostring(properties.provisioningState)
| extend vmId = tostring(properties.virtualMachine.id)
| extend vmName = tostring(split(properties.virtualMachine.id, "/")[-1])
| extend vmResourceGroup = tostring(split(properties.virtualMachine.id, "/")[4])
| extend nsgId = tostring(properties.networkSecurityGroup.id)
| extend nsgName = tostring(split(nsgId, "/")[-1])
| extend nsgResourceGroup = tostring(split(nsgId, "/")[4])
| extend mac = tostring(properties.macAddress)
| order by name asc
```

**Params:** `{querySubscriptionId}`, `{queryOptionalResourceGroupName}`

---
