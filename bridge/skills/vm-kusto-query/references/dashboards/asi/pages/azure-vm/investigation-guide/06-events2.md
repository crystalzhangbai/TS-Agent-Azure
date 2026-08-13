# Events2

> Source: **Azure Host - Azure VM** dashboard, chapter **Events2** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Events2 (all events from ASAP, Hyper-V, Blobcache, WinEvents)

### Azure VM ASAP TDPR Query

_Widget purpose:_ Events2 (all events from ASAP, Hyper-V, Blobcache, WinEvents)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Events2 > Events2 (all events from ASAP, Hyper-V, Blobcache, WinEvents)`

**Output columns:** `Level`

```kusto
AsapOverlake2BootEvents(nodeId, startTime, endTime, containerId)
| where EventId !in (1015, 1112, 1121, 9006)
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project-away Level
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---
