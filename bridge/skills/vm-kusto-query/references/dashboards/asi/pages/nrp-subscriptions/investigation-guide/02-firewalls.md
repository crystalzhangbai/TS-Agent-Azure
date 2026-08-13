# Firewalls

> Source: **NRP - Subscriptions** dashboard, chapter **Firewalls** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Subscription Firewalls

### Subscription Firewalls

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Firewalls > Subscription Firewalls`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where type == "microsoft.network/azurefirewalls" and subscriptionId =~ querySubscriptionId
| where isempty(queryOptionalResourceGroupName) or resourceGroup =~ queryOptionalResourceGroupName
| where not(deleted) and isnotempty(properties)
| summarize arg_max(timestamp, properties, tags, name, location) by id
| extend Name = name
| parse id with "/subscriptions/" fwSub "/resourceGroups/" fwRg "/providers/Microsoft.Network/azureFirewalls/" fwName
| extend provisioningState = tostring(properties.provisioningState)
| extend skuName = tostring(properties.sku.name)
| extend skuTier = tostring(properties.sku.tier)
| extend privateIPAddress = tostring(properties.ipConfigurations[0].properties.privateIPAddress)
| extend privateIPAllocationMethod = tostring(properties.ipConfigurations[0].properties.privateIPAllocationMethod)
| extend publicIPAddress = tostring(properties.ipConfigurations[0].properties.publicIPAddress.id)
| extend firewallPolicy = tostring(properties.firewallPolicy.id)
| project-away properties, name
| order by fwRg asc, fwName asc
```

**Params:** `{querySubscriptionId}`, `{queryOptionalResourceGroupName}`, `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `type == "microsoft.network/azurefirewalls"`

---
