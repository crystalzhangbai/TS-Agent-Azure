# Resource Groups

> Source: **ARM — Subscriptions** dashboard, chapter **Resource Groups** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Resource Groups

### Subscription Resource Groups

_Widget purpose:_ Resource Groups

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Resource Groups > Resource Groups`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where timestamp between ((qFrom - 3d) .. qTo)
| where subscriptionId =~ querySubscriptionId
| summarize SnapshotDate = arg_max(timestamp, location) by subscriptionId, resourceGroup
| order by resourceGroup asc
```

**Params:** `{querySubscriptionId}`, `{qFrom}`, `{qTo}`

---
