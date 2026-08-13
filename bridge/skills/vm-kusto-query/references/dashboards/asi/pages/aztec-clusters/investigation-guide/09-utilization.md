# Utilization %

> Source: **Aztec — Clusters** dashboard, chapter **Utilization %** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Utilization %

### Tenant Utilization Percent TimeSeries 

_Widget purpose:_ Utilization %

Cluster: `AzureCM` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Utilization % > Utilization %`

```kusto
LogClusterCapacity
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where Tenant == queryTenant
| summarize TotalCores = max(totalCores), UsedCores = max(usedCores) by bin(PreciseTimeStamp, 15m)
| extend Utilization = round(todouble(UsedCores) / todouble(TotalCores) * 100, 2)
| extend Available = round(100.00 - Utilization, 2)
| project PreciseTimeStamp, Utilization, Available
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenant}`

---
