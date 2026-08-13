# DiskRPResourceLifecycleEvent

> Source: **Managed Disk - Correlation Id** dashboard, chapter **DiskRPResourceLifecycleEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### DiskRPResourceLifecycleEvent

Cluster: `Disks` · Database: `Disks` · Type: `Table`
Source panel: `DiskRPResourceLifecycleEvent`

```kusto
let ext_start = queryTime-timespan(30m);
let ext_end = queryTime+timespan(30m);
  let actids = DiskManagerApiQoSEvent
  | where PreciseTimeStamp between(ext_start .. ext_end)
  | where case(isnotempty(queryCorrelationId), correlationId =~ queryCorrelationId, false)
  | summarize by operationId;
  DiskRPResourceLifecycleEvent
  | where PreciseTimeStamp between(ext_start .. ext_end)
  | where isnotempty(activityId) and activityId in (actids)
  | project PreciseTimeStamp, subscriptionId, activityId, traceCode, message, callerName, resourceGroupName, resourceName, diskType, diskEvent, stage, state, hasActiveSASToken, storageAccountType, diskSizeBytes, blobUrl, storageAccountName, diskOwner, crpDiskId, importBlobUri, creationOption
```

**Params:** `{queryTime}`, `{queryCorrelationId}`

---
