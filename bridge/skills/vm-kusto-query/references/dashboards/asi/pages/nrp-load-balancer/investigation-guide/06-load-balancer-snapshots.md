# Load Balancer Snapshots

> Source: **NRP - Load Balancer** dashboard, chapter **Load Balancer Snapshots** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Load Balancer Snapshots

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Load Balancer Snapshots`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where timestamp between(datetime_add('day', -1, queryFrom) .. queryTo)
| where id =~ queryId and subscriptionId =~ querySubscriptionId
| where not(partial)
| extend JSON = properties
| extend provisioningState = JSON.provisioningState
| extend resourceGuid = JSON.resourceGuid
| order by timestamp desc
// because we are descending, we need next instead
| extend PreviousJSON = next(properties)
| project-away properties
| project timestamp, deleted, source, provisioningState, type, rowId, JSON, PreviousJSON, sku, tags
| where strlen(tostring(JSON)) != strlen(tostring(PreviousJSON))
```

**Params:** `{querySubscriptionId}`, `{queryId}`, `{queryFrom}`, `{queryTo}`

---
