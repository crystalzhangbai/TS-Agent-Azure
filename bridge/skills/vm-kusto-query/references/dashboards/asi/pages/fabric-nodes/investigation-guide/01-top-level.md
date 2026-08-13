# (top-level)

> Source: **Fabric - Nodes** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Node Containers

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where nodeId == queryNodeId
| summarize StartTime = min(PreciseTimeStamp), EndTime = arg_max(PreciseTimeStamp, *) by containerId
| project StartTime, EndTime, Content = containerId
| order by StartTime asc
```

**Params:** `{queryNodeId}`

---
