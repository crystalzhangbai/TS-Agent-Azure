# Latest Data

> Source: **AIB KPIs** dashboard, chapter **Latest Data** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Latest Refresh DateTime

_Widget purpose:_ Latest Data

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Single` · Widget: `Card`
Source panel: `Latest Data`

```kusto
AsyncQoSEvents
| project PreciseTimeStamp
| summarize latestRefresh = max(PreciseTimeStamp)
| top 1 by latestRefresh desc
```

---
