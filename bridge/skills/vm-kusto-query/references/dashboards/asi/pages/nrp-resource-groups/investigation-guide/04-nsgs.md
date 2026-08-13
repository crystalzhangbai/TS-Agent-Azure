# NSGs

> Source: **NRP - Resource Groups** dashboard, chapter **NSGs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Resource Group NSGs

### Subscription NSGs

_Widget purpose:_ Resource Group NSGs

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `NSGs > Resource Group NSGs`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where type == "microsoft.network/networksecuritygroups" and subscriptionId =~ querySubscriptionId
| where isempty(queryOptionalResourceGroupName) or resourceGroup =~ queryOptionalResourceGroupName
| where not(deleted) and isnotempty(properties)
| summarize arg_max(timestamp, properties, tags, name, location) by id
| extend Name = name
| extend ArmRegionName = location
| extend NumberOfSecurityRules = array_length(properties.securityRules) + array_length(properties.defaultSecurityRules)
| parse id with "/subscriptions/" nsgSubscriptionId "/resourceGroups/" nsgResourceGroupName "/providers/Microsoft.Network/networkSecurityGroups/" nsgName 
| extend provisioningState = tostring(properties.provisioningState)
| project-away properties, name
| order by nsgResourceGroupName asc, nsgName asc
```

**Params:** `{querySubscriptionId}`, `{queryOptionalResourceGroupName}`, `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `type == "microsoft.network/networksecuritygroups"`

---
