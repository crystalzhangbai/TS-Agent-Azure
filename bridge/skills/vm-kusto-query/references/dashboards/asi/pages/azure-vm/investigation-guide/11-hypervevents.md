# HyperVEvents

> Source: **Azure Host - Azure VM** dashboard, chapter **HyperVEvents** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## HyperVEventsV2

### HyperVEventsV2 Guest Query

_Widget purpose:_ HyperVEventsV2

Cluster: `azcore.centralus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `HyperVEvents > HyperVEventsV2`

```kusto
HyperVEventsV2(fn_nodeId=['_nodeId'], fn_containerId=['_containerId'], fn_startTime = ['_startTime'], fn_endTime=['_endTime'])
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`, `{_containerId}`

---
