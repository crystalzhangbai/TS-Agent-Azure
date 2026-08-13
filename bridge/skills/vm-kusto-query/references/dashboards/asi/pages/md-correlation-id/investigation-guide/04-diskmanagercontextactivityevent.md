# DiskManagerContextActivityEvent

> Source: **Managed Disk - Correlation Id** dashboard, chapter **DiskManagerContextActivityEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### DiskManagerContextActivityEvent

Cluster: `Disks` · Database: `Disks` · Type: `Table`
Source panel: `DiskManagerContextActivityEvent`

```kusto
let ext_start = queryTime-timespan(30m);
let ext_end = queryTime+timespan(30m);
let actids = DiskManagerApiQoSEvent
  | where PreciseTimeStamp between(ext_start .. ext_end)
  | where case(isnotempty(queryCorrelationId), correlationId =~ queryCorrelationId, false)
  | summarize by operationId;
DiskManagerContextActivityEvent
  | where PreciseTimeStamp between(ext_start .. ext_end)
  | where isnotempty(activityId) and activityId in (actids)
  | project PreciseTimeStamp, subscriptionId, correlationId, activityId, traceCode, message
```

**Params:** `{queryTime}`, `{queryCorrelationId}`

---
