# Snapshots

> Source: **NRP - Network Security Groups** dashboard, chapter **Snapshots** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Snapshots

### Graph NSG Snapshots

_Widget purpose:_ NSG Snapshots (ARG)

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Snapshots > Snapshots > NSG Snapshots (ARG)`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where (isempty(queryHintTime) and timestamp > (queryFrom - 5d)) 
    or timestamp between(datetime_add('day', 1, queryHintTime) .. datetime_add('hour', 6, queryHintTime))
| where name =~ queryName and resourceGroup =~ queryResourceGroupName
| where subscriptionId =~ querySubscriptionId and type == "microsoft.network/networksecuritygroups"
| where not(partial)
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

**Params:** `{queryName}`, `{queryResourceGroupName}`, `{querySubscriptionId}`, `{queryHintTime}`, `{queryFrom}`

---
