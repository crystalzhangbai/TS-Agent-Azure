# VMA

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **VMA** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### VMA1 DS

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `VMA`

```kusto
let myTable = cluster("Vmainsight").database("vmadb").VMA 
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime 
| where Subscription =~ query_SubscriptionId and RoleInstanceName has query_VMName 
| distinct  PreciseTimeStamp,NodeId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2, RCA_CSS, Cluster, ContainerId, CSS_SrID;
myTable
| extend StartTime = now(), EndTime = now(), RCAEngineCategory = ""
| invoke cluster("Vmainsight").database('Air').AddVmRestartSupportArticle()
| project-away StartTime, EndTime, RCAEngineCategory, InternalArticleId
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_SubscriptionId}`, `{query_VMName}`

---
