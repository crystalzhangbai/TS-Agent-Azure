# VNets

> Source: **NRP - Subscriptions** dashboard, chapter **VNets** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Subscription VNets

### Subscription VNets

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `VNets > Subscription VNets`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
//| where timestamp between (queryFrom .. queryTo)
| where type == "microsoft.network/virtualnetworks" and subscriptionId =~ querySubscriptionId
| where isempty(queryOptionalResourceGroup) or resourceGroup =~ queryOptionalResourceGroup
| summarize arg_max(timestamp, name, properties, tags, resourceGroup, deleted) by id
| extend provisioningState = tostring(properties.provisioningState)
| extend addressPrefixes = array_strcat(properties.addressSpace.addressPrefixes, ", ")
| project-away properties
| order by name asc
```

**Params:** `{querySubscriptionId}`, `{queryOptionalResourceGroup}`, `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `type == "microsoft.network/virtualnetworks"`

---
