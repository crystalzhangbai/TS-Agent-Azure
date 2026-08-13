# Load Balancers

> Source: **NRP - Resource Groups** dashboard, chapter **Load Balancers** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### NRP Sub and RG Load Balancers

_Widget purpose:_ Load Balancers

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Load Balancers`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where type == "microsoft.network/loadbalancers" and subscriptionId =~ querySubscriptionId
| where isempty(queryOptionalResourceGroupName) or resourceGroup =~ queryOptionalResourceGroupName
| where not(deleted) and isnotempty(properties)
| summarize arg_max(timestamp, properties, tags, name, location, type) by id
| parse id with "/subscriptions/" lbSub "/resourceGroups/" lbRg "/providers/Microsoft.Network/loadBalancers/" lbName
| extend provisioningState = tostring(properties.provisioningState)
| extend frontendIPConfigurations = array_length(properties.frontendIPConfigurations)
| extend inboundNatRules = array_length(properties.inboundNatRules)
| extend outboundRules = array_length(properties.outboundRules)
| extend inboundNatPools = array_length(properties.inboundNatPools)
| project-away properties
| order by lbRg asc, lbName asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOptionalResourceGroupName}`, `{querySubscriptionId}`

**Signal filters seen in KQL:** `type == "microsoft.network/loadbalancers"`

---
