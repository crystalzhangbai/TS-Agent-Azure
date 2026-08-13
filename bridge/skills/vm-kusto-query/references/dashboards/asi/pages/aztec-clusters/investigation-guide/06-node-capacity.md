# Node Capacity

> Source: **Aztec — Clusters** dashboard, chapter **Node Capacity** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Nodes

### Cluster Nodes

_Widget purpose:_ Nodes

Cluster: `azurecm` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Node Capacity > Nodes`

```kusto
LogClusterCapacity
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where Tenant == queryTenant
| summarize TotalNodes = max(totalNodes), AllocatableNodes = max(allocatableNodes) by bin(PreciseTimeStamp, 30m)
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenant}`

---
