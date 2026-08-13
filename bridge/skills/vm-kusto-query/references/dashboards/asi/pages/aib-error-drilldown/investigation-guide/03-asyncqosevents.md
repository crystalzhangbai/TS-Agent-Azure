# AsyncQoSEvents

> Source: **Error Drilldown** dashboard, chapter **AsyncQoSEvents** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## AsyncQoSEvents

### AsyncQoSEvents by correlationID

_Widget purpose:_ AsyncQoSEvents

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`
Source panel: `AsyncQoSEvents > AsyncQoSEvents`

```kusto
AsyncQoSEvents
| where correlationID == local_correlationID
| order by PreciseTimeStamp desc
```

**Params:** `{local_correlationID}`

---
