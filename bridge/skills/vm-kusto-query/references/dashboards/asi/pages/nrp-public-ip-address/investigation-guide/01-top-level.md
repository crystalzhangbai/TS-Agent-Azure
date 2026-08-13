# (top-level)

> Source: **NRP - Public IP Address** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Public IP Address"

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `ResourceGet` · Widget: `Container`

```kusto
let idMatch = strcat("/subscriptions/", local_subscriptionId, "/resourceGroups/", local_resourceGroup, "/providers/Microsoft.Network/publicIPAddresses/", local_name);
cluster('argwus2nrpone.westus2.kusto.windows.net').database('AzureResourceGraph').Resources
| where (isempty(local_timestamp) or timestamp between(datetime_add('hour', -1, local_timestamp) .. datetime_add('hour', 1, local_timestamp)))
    and type == "microsoft.network/publicipaddresses" and not(partial) and not(deleted)
    and subscriptionId == local_subscriptionId
| where resourceGroup =~ local_resourceGroup and name =~ local_name
| top 1 by timestamp desc
| extend JSON = parse_json(properties)
| extend provisioningState = tostring(JSON.provisioningState)
| extend resourceGuid = tostring(JSON.resourceGuid)
| extend ipAddress = tostring(JSON.ipAddress)
| extend publicIPAddressVersion = tostring(JSON.publicIPAddressVersion)
| extend publicIPAllocationMethod = tostring(JSON.publicIPAllocationMethod)
| extend idleTimeoutInMinutes = toint(JSON.idleTimeoutInMinutes)
| extend ipTags = JSON.ipTags
| extend ipConfiguration = JSON.ipConfiguration
| extend ipConfigId= tostring(JSON.ipConfiguration.id)
| project-away properties
| project timestamp, name, resourceGroup, subscriptionId, id, type, sku, tags, provisioningState, resourceGuid, ipAddress, 
    publicIPAddressVersion, publicIPAllocationMethod, idleTimeoutInMinutes, ipTags, ipConfiguration, ipConfigId,
    JSON
| extend natGateway = tostring(JSON.natGateway.id)
```

**Params:** `{local_name}`, `{local_resourceGroup}`, `{local_subscriptionId}`, `{local_timestamp}`, `{globalFrom}`, `{globalTo}`

---
