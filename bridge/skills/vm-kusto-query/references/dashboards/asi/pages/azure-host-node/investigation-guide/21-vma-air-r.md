# VMA (AIR-R)

> Source: **Azure Host — Azure Host Node** dashboard, chapter **VMA (AIR-R)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VMA events for {{nodeId}}

### Azure Host VMA

_Widget purpose:_ VMA events for {{nodeId}}

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `VMA (AIR-R) > VMA events for {{nodeId}}`

```kusto
VMA
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| distinct StartTime, EndTime, RoleInstanceName, RCA, VmUniqueId, Subscription_CustomerName, Subscription, ContainerId, RCAEngineCategory, RCALevel1, RCALevel2
| invoke cluster("Vmainsight").database('Air').AddVmRestartSupportArticle()
| project-away EndTime, RCAEngineCategory, RCALevel1, RCALevel2
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---
