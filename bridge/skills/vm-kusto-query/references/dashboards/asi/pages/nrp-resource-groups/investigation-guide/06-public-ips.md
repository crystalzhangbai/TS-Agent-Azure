# Public IPs

> Source: **NRP - Resource Groups** dashboard, chapter **Public IPs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### NRP Public IPs by Sub and RG

_Widget purpose:_ Public IPs

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Public IPs`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where type == "microsoft.network/publicipaddresses" and subscriptionId =~ querySubscriptionId
| where isempty(queryOptionalResourceGroup) or resourceGroup =~ queryOptionalResourceGroup
| where isnotempty(properties) and not(deleted)
| summarize arg_max(timestamp, name, properties, tags, resourceGroup) by id
| extend ipAddress = tostring(properties.ipAddress)
| extend provisioningState = tostring(properties.provisioningState)
| extend publicIPAddressVersion = tostring(properties.publicIPAddressVersion)
| extend publicIPAllocationMethod = tostring(properties.publicIPAllocationMethod)
| extend idleTimeoutInMinutes = tostring(properties.idleTimeoutInMinutes)
| order by name asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscriptionId}`, `{queryOptionalResourceGroup}`

**Signal filters seen in KQL:** `type == "microsoft.network/publicipaddresses"`

---
