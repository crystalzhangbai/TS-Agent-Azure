# DiskRPResourceLifecycleEvent

> Source: **Managed Disk - Disks** dashboard, chapter **DiskRPResourceLifecycleEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query DiskRPResourceLifecycleEvent

_Widget purpose:_ DiskRPResourceLifecycleEvent

Cluster: `Disks` · Database: `Disks` · Type: `Table`
Source panel: `DiskRPResourceLifecycleEvent`

```kusto
cluster("Disks").database("Disks").DiskRPResourceLifecycleEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where subscriptionId == querySubId
| where resourceGroupName =~ queryResourceGroup
| where resourceName =~ queryDiskName
// | project PreciseTimeStamp, activityId, message,  diskEvent, stage, state,, crpDiskId, diskOwner, storageAccountName
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`, `{queryResourceGroup}`, `{queryDiskName}`

---
