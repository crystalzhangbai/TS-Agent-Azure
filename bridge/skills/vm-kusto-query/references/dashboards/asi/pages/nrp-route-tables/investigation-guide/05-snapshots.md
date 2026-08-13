# Snapshots

> Source: **NRP - Route Tables** dashboard, chapter **Snapshots** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Route Table Snapshots (ARG)

### NRP Route Table Snapshots

_Widget purpose:_ Route Table Snapshots (ARG)

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Snapshots > Route Table Snapshots (ARG)`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isempty(queryHintTime) or timestamp between(datetime_add('day', -2, queryHintTime) .. datetime_add('hour', 6, queryHintTime))
| where name =~ queryName
| where resourceGroup =~ queryResourceGroupName and subscriptionId =~ querySubscriptionId
| where type == "microsoft.network/routetables" and not(partial)
| extend JSON = properties
| extend provisioningState = JSON.provisioningState
| extend resourceGuid = JSON.resourceGuid
| order by timestamp desc
// because we are descending, we need next instead
| extend PreviousJSON = next(properties)
| project-away properties
| project-reorder timestamp, deleted, source, provisioningState, type, rowId
| where strlen(tostring(JSON)) != strlen(tostring(PreviousJSON))
```

**Params:** `{queryName}`, `{queryResourceGroupName}`, `{querySubscriptionId}`, `{queryHintTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/routetables"`

---
