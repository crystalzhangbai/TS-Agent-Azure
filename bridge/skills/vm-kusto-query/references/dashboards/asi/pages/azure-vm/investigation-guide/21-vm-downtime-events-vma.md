# VM Downtime Events (VMA)

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Downtime Events (VMA)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VM Availability Events

### Azure Host VM VMA Query v3

_Widget purpose:_ VM Availability Events

Cluster: `Vmainsight` · Database: `vmadb` · Type: `Table`
Source panel: `VM Downtime Events (VMA) > VM Availability Events`

**Tables:** `VmRestartRcaLevel1Level2ArticleMapping`, `VmRestartArticleCssWikiLinkMapping`, `VMA`
**Output columns:** `EndTime`, `RCAEngineCategory`, `RCALevel1`, `RCALevel2`, `ArticleId1`, `InternalArticleId`

```kusto
VMA
| where PreciseTimeStamp between (startTime .. endTime) 
| where (isnotempty(vmId) and VmUniqueId == vmId) or (isempty(vmId) and ContainerId == containerId) and RCALevel1 != "Unknown" 
| distinct StartTime, EndTime, RoleInstanceName, RCA, Subscription_CustomerName, Subscription, ContainerId, RCAEngineCategory, RCALevel1, RCALevel2
| join kind=leftouter ( cluster("https://vmainsight.kusto.windows.net").database("Air").VmRestartRcaLevel1Level2ArticleMapping ) on $left.RCALevel1 == $right.RCALevel1 and $left.RCALevel2 == $right.RCALevel2
| join kind=leftouter ( cluster("https://vmainsight.kusto.windows.net").database("Air").VmRestartArticleCssWikiLinkMapping ) on $left.ArticleId == $right.ArticleId
| project-away EndTime, RCAEngineCategory, RCALevel1, RCALevel2, ArticleId1, InternalArticleId
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`, `{vmId}`

---
