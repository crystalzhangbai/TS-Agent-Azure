# Core Capacity

> Source: **Aztec — Clusters** dashboard, chapter **Core Capacity** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Cores

### Cluster Cores

_Widget purpose:_ Cores

Cluster: `azurecm` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Core Capacity > Cores`

```kusto
LogClusterCapacity
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where Tenant == queryTenant
| summarize TotalCores = max(totalCores), UsedCores = max(usedCores) by bin(PreciseTimeStamp, 15m)
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenant}`

---
