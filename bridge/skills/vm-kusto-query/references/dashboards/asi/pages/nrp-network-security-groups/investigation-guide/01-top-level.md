# (top-level)

> Source: **NRP - Network Security Groups** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Network Security Groups"

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `ResourceGet` · Widget: `Container`

```kusto
Resources
| where isempty(local_timestamp) or 
    timestamp between((local_timestamp-15m)..(local_timestamp+15m))
| where subscriptionId == local_subscriptionId and resourceGroup =~ local_resourceGroupName and name =~ local_name
| top 1 by timestamp desc
```

**Params:** `{local_name}`, `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_timestamp}`

---

### Get Network Security Group

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Single` · Widget: `Container`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isnotempty(queryNSGName) and (resourceGroup =~ queryResourceGroupName and subscriptionId =~ querySubscriptionId)
| where type == "microsoft.network/networksecuritygroups" and not(partial)
| where name =~ queryNSGName
| top 1 by timestamp desc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryNSGName}`

**Signal filters seen in KQL:** `type == "microsoft.network/networksecuritygroups"`

---
