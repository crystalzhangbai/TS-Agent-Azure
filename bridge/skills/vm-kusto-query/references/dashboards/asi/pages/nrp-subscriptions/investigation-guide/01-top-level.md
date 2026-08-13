# (top-level)

> Source: **NRP - Subscriptions** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Subscriptions"

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `ResourceGet` · Widget: `Container`

```kusto
range index from 1 to 1 step 1
| project subscriptionId = local_subscriptionId
```

**Params:** `{local_subscriptionId}`

---

### Sub or RG Route Tables

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where subscriptionId =~ querySubscriptionId and type == "microsoft.network/routetables"
| where isempty(queryOptionalResourceGroupName) or resourceGroup =~ queryOptionalResourceGroupName
| where not(deleted) and isnotempty(properties)
| summarize arg_max(timestamp, properties, tags, name, location) by id
| extend Name = name
| parse id with "/subscriptions/" rtSub "/resourceGroups/" rtRg "/providers/Microsoft.Network/routeTables/" rtName
| extend provisioningState = tostring(properties.provisioningState)
| extend subnets = array_length(properties.subnets)
| extend routes = array_length(properties.routes)
| extend disableBgpRoutePropagation = tobool(properties.disableBgpRoutePropagation)
| project-away properties, name
| order by rtRg asc, rtName asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscriptionId}`, `{queryOptionalResourceGroupName}`

---
