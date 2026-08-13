# DiskManagerContextActivityEvent

> Source: **Managed Disk - Operation Id** dashboard, chapter **DiskManagerContextActivityEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## DiskManagerContextActivityEvent 

### Query DiskManagerContextActivityEvent

_Widget purpose:_ DiskManagerContextActivityEvent 

Cluster: `Disks` · Database: `Disks` · Type: `Table`
Source panel: `DiskManagerContextActivityEvent > DiskManagerContextActivityEvent `

```kusto
DiskManagerContextActivityEvent
| where PreciseTimeStamp  between ((queryStartTime-1h) .. (queryEndTime+1h))
| where activityId == queryOperationId
| project PreciseTimeStamp, callerName, message, traceLevel
| extend level = case(
    traceLevel <= 2, 'error', 
    traceLevel <= 4, 'warn', 
    'info'
)
| order by PreciseTimeStamp asc
```

**Params:** `{queryStartTime}`, `{queryEndTime}`, `{queryOperationId}`

---
