# Private Endpoints

> Source: **NRP - Resource Groups** dashboard, chapter **Private Endpoints** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### NRP Sub and RG Private Endpoints

_Widget purpose:_ Private Endpoints

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Private Endpoints`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where type == "microsoft.network/privateendpoints" and subscriptionId =~ querySubscriptionId
| where isempty(queryOptionalResourceGroupName) or resourceGroup =~ queryOptionalResourceGroupName
| where not(deleted) and isnotempty(properties)
| summarize arg_max(timestamp, properties, tags, name, location, type) by id
| parse id with "/subscriptions/" peSub "/resourceGroups/" peRg "/providers/Microsoft.Network/privateEndpoints/" peName
| extend provisioningState = tostring(properties.provisioningState)
| extend customNetworkInterfaceName = tostring(properties.customNetworkInterfaceName)
| extend subnet = tostring(properties.subnet.id)
| parse subnet with "/subscriptions/" subSub "/resourceGroups/" subRg "/providers/Microsoft.Network/virtualNetworks/" subVnet "/subnets/" subName
| extend ipConfigurations = array_length(properties.ipConfigurations)
| extend networkInterfaces = array_length(properties.networkInterfaces)
| extend privateLinkServiceConnections = array_length(properties.privateLinkServiceConnections)
| extend plsConnectionState = tostring(properties.privateLinkServiceConnections[0].properties.privateLinkServiceConnectionState.status)
| extend manualPrivateLinkServiceConnections = array_length(properties.manualPrivateLinkServiceConnections)
| extend customDnsConfigs = array_length(properties.customDnsConfigs)
| project-away properties
| order by peRg asc, peName asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOptionalResourceGroupName}`, `{querySubscriptionId}`

**Signal filters seen in KQL:** `type == "microsoft.network/privateendpoints"`

---
