# (top-level)

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Azure Subscription"

Cluster: `datastudiostreaming` · Database: `Shared` · Type: `ResourceGet` · Widget: `Container`

```kusto
let subscriptionSnapshotDataStudio = cluster('datastudiostreaming').database('Shared').DataStudio_AzureSubscription_Snapshot
| where SubscriptionId in~ (local_SubscriptionId)
| take 1;
let subscriptionSnapshotcustomerDomData = cluster('customerdomrptwus3prod.westus3.kusto.windows.net').database('CustomerDomData').CustomerModel
| where SubscriptionGuid_String in~ (local_SubscriptionId)
| take 1;
union subscriptionSnapshotcustomerDomData, subscriptionSnapshotDataStudio
| take 1
```

**Params:** `{local_SubscriptionId}`, `{globalFrom}`, `{globalTo}`

---
