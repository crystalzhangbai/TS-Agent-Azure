# Routes

> Source: **NRP - Route Tables** dashboard, chapter **Routes** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Routes

### Route Table Routes

_Widget purpose:_ Routes

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Routes > Routes > Routes`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isempty(queryOptionalHintTime) or timestamp between(datetime_add('day', -2, queryOptionalHintTime) .. datetime_add('hour', 6, queryOptionalHintTime))
| where (isnotempty(queryRouteTableName) and isnotempty(queryResourceGroupName))
    and (name =~ queryRouteTableName and resourceGroup =~ queryResourceGroupName)
| where subscriptionId =~ querySubscriptionId
| where type == "microsoft.network/routetables" and not(partial) and not(deleted)
| top 1 by timestamp desc 
| mv-expand route = properties.routes
| project route
| project name = tostring(route.name),
    id = tostring(route.name),
    provisioningState = tostring(route.properties.provisioningState),
    addressPrefix = tostring(route.properties.addressPrefix),
    nextHopType = tostring(route.properties.nextHopType),
    nextHopIpAddress = tostring(route.properties.nextHopIpAddress),
    hasBgpOverride = tobool(route.properties.hasBgpOverride)
| order by name desc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryRouteTableName}`, `{queryOptionalHintTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/routetables"`

---
