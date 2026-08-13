# RhcWatchdogReportsErrorEtwTable

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **RhcWatchdogReportsErrorEtwTable** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Represents errors emitting the watchdog report (calling IfxHealth API)

### RhcWatchdogReportsErrorEtwTable DS

_Widget purpose:_ Represents errors emitting the watchdog report (calling IfxHealth API)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `RhcWatchdogReportsErrorEtwTable > Represents errors emitting the watchdog report (calling IfxHealth API)`

```kusto
RhcWatchdogReportsErrorEtwTable
| where ContainerId == query_ContainerId
| where PreciseTimeStamp >= query_StartTime and PreciseTimeStamp <= query_EndTime
| project PreciseTimeStamp, TaskName, ChannelName, EventMessage, LevelName, NodeId
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_ContainerId}`

---
