# (top-level)

> Source: **NRP - Virtual Networks** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Virtual Networks"

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `ResourceGet` · Widget: `Container`

```kusto
let vnetResourceId = strcat(
    "/subscriptions/", local_subscriptionId, 
    "/resourceGroups/", local_resourceGroupName, 
    "/providers/Microsoft.Network/virtualNetworks/", local_name);
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where type == "microsoft.network/virtualnetworks" and id =~ vnetResourceId and not(deleted) 
| top 1 by timestamp desc
| extend JSON = parse_json(properties)
| extend subnets = array_length(properties.subnets)
| extend virtualNetworkPeerings = properties.virtualNetworkPeerings
| extend addressPrefixes = properties.addressSpace.addressPrefixes
| extend resourceGuid = properties.resourceGuid
```

**Params:** `{local_name}`, `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_timestamp}`

**Signal filters seen in KQL:** `type == "microsoft.network/virtualnetworks"`

---
