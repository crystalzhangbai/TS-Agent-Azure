# VM Insights for a given TIMESTAMP

> Source: **VM Scuba - VM Details** dashboard, chapter **VM Insights for a given TIMESTAMP** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-VMInsights

_Widget purpose:_ VM Insights for a given TIMESTAMP

Cluster: `rdosdata.kusto.windows.net` · Database: `rdosdatapath` · Type: `Table`
Source panel: `VM Insights for a given TIMESTAMP`

```kusto
cluster("rdosdata.kusto.windows.net").database("rdosdatapath").StorageClientInsightsForNode(nodeId,queryFrom,queryTo)
| project PreciseTimeStamp, Message, EventName, ContainerId, level = case(EventName contains "Update", "warning", "error")
| limit 5
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---
