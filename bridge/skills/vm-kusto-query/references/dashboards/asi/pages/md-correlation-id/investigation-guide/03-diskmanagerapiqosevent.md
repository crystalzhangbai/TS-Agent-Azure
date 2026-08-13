# DiskManagerApiQoSEvent

> Source: **Managed Disk - Correlation Id** dashboard, chapter **DiskManagerApiQoSEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### DiskManagerApiQoSEvent

Cluster: `Disks` · Database: `Disks` · Type: `Table`
Source panel: `DiskManagerApiQoSEvent`

```kusto
let ext_start = queryTime-timespan(30m);
let ext_end = queryTime+timespan(30m);
DiskManagerApiQoSEvent
  | where PreciseTimeStamp between(ext_start .. ext_end)
  | where case(isnotempty(queryCorrelationId), correlationId =~ queryCorrelationId, false)
  | project PreciseTimeStamp, subscriptionId, operationId, correlationId, operationName, resourceName, e2EDurationInMilliseconds, httpStatusCode, resultCode, errorDetails
```

**Params:** `{queryTime}`, `{queryCorrelationId}`

---
