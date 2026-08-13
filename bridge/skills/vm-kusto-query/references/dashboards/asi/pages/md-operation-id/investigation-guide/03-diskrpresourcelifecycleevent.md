# DiskRPResourceLifecycleEvent

> Source: **Managed Disk - Operation Id** dashboard, chapter **DiskRPResourceLifecycleEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### DiskRPResourceLifecycleEvent

Cluster: `Disks` · Database: `Disks` · Type: `Table`
Source panel: `DiskRPResourceLifecycleEvent`

```kusto
let ext_start = queryFrom-timespan(30m);
let ext_end = queryTo+timespan(30m);
DiskRPResourceLifecycleEvent
| where PreciseTimeStamp between(ext_start .. ext_end)
| where activityId =~ operationId
| project PreciseTimeStamp, subscriptionId, activityId, traceCode, message, callerName, resourceGroupName, resourceName, diskType, diskEvent, stage, state, hasActiveSASToken, storageAccountType, diskSizeBytes, blobUrl, storageAccountName, diskOwner, crpDiskId, importBlobUri, creationOption
```

**Params:** `{queryFrom}`, `{queryTo}`, `{operationId}`

---
