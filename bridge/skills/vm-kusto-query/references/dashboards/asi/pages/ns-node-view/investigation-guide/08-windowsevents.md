# WindowsEvents

> Source: **NodeService - NodeService_NodeView** dashboard, chapter **WindowsEvents** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### WindowsEventsTable

_Widget purpose:_ WindowsEvents

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `WindowsEvents`

```kusto
WindowsEventTable
| where PreciseTimeStamp between ((faultTime - 1h)..2h)
| where NodeId == queryNode
| project PreciseTimeStamp, Level, Description
```

**Params:** `{queryNode}`, `{faultTime}`

---
