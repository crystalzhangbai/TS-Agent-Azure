# Region Hit Count

> Source: **AIB KPIs** dashboard, chapter **Region Hit Count** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Region AsyncQoSEvent Count

_Widget purpose:_ Region Hit Count

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `CategoryChart`
Source panel: `Region Hit Count`

```kusto
AsyncQoSEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| summarize regionCount = count() by RPSector
| extend Name = RPSector
| project Name, regionCount
| order by regionCount desc
```

**Params:** `{queryFrom}`, `{queryTo}`

---
