# Active Disks for the Subscription

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **Active Disks for the Subscription** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Azure Host Subscription Disks

_Widget purpose:_ Active Disks for the Subscription

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Active Disks for the Subscription`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 2h)) and ArmId contains subId and (Type == 0 or Type == 4)
| parse BlobPath with BlobPath "?" *
| parse BlobPath with * "/" StorageAccount "/" *
| where StorageAccount contains _storageAccountName
| parse SurfaceName with ContainerId "_" *
| distinct Region, StorageAccount, BlobPath, ContainerId, NodeId
| join kind=leftouter(
    OsConfigTable
    | where PreciseTimeStamp between ((startTime - 6h) .. endTime) and Component == "blobprop"
    | extend BlobProperties = parse_json(ConfigValue)
    | extend 
             DiskAccessTier = tostring(BlobProperties.blobproperties['x-ms-access-tier']),
             EnhancedConnectionVersion = BlobProperties.blobproperties["x-ms-enhancedconnectionversion"],
             StorageTenant = tostring(BlobProperties.storagecluster)
    | extend BlobProperties = BlobProperties.blobproperties
    | summarize hint.strategy=shuffle arg_max(PreciseTimeStamp, *) by ConfigName
    | project BlobPath = ConfigName, DiskAccessTier, StorageTenant
) on BlobPath
| project-away BlobPath1
```

**Params:** `{startTime}`, `{endTime}`, `{subId}`, `{_storageAccountName}`

---
