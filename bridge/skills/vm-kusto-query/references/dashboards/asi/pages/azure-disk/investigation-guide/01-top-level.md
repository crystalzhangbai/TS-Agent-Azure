# (top-level)

> Source: **Azure Host — Azure Disk** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Azure Disk"

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `ResourceGet` · Widget: `Container`

```kusto
union 
OsXIOHealthSignalEvent,
OsUltraSSDHealthSignalEvent
| where PreciseTimeStamp between (globalFrom .. globalTo) and isnotempty(ArmId) and ArmId contains local_ArmId and (isempty(Type) or Type in (0, 4))
| extend ContainerId = case(isnotempty(ContainerId), ContainerId, tostring(split(SurfaceName, "_")[0]))
| join kind=leftouter (
    OsXIOSurfaceCounterTable
    | where PreciseTimeStamp between (globalFrom .. globalTo) and isnotempty(ArmId) and ArmId contains local_ArmId and (isempty(Type) or Type in (0, 4))
    | distinct ArmId, StorageTenant, SurfaceName
) on SurfaceName
| parse ArmId with "/subscriptions/" SubscriptionId "/" *
| join kind=leftouter (
     OsConfigTable
        | where PreciseTimeStamp between ((globalFrom - 6h).. (globalTo + 6h)) and ConfigValue contains local_ArmId
        | take 1
        | extend BlobProperties = parse_json(ConfigValue).blobproperties
        | extend ArmId = tostring(BlobProperties["x-ms-disk-resource-uri"]),
                 DiskTier = tostring(BlobProperties["x-ms-access-tier"]),
                 IOPSLimit = tostring(BlobProperties["x-ms-blob-iops-limit"]),
                 ThroughputLimit = tostring(BlobProperties["x-ms-blob-throughput-limit"]),
                 BurstIOPSLimit = tostring(BlobProperties["x-ms-blob-burst-iops-limit"]),
                 BurstThroughputLimit = tostring(BlobProperties["x-ms-blob-burst-throughput-limit"]),
                 DiskCreationTime = tostring(BlobProperties["x-ms-creation-time"])
) on ArmId
| summarize count() by Region, DataCenter, Cluster, NodeId, SubscriptionId, ContainerId, ArmId, StorageTenant, DiskTier, IOPSLimit, ThroughputLimit, BurstIOPSLimit, BurstThroughputLimit, DiskCreationTime
```

**Params:** `{local_ArmId}`, `{globalFrom}`, `{globalTo}`

---

### Azure Disks IO Stats

_Widget purpose:_ Disk IO Stats

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`

```kusto
union 
OsXIOSurfaceCounterTable,
OsUltraSSDCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and isnotempty(ArmId) and ArmId contains _armId and (isempty(Type) or Type in (0, 4)) and IsNewDisk == 0
| summarize IOPS = sum(IOPS), 
            MBPS = sum(MBPS),
            ReadIOPS = sum(ReadIOPS),
            WriteIOPS = sum(WriteIOPS),
            ReadMBPS = sum(ReadMBPS),
            WriteMBPS = sum(WriteMBPS),
            AvgReadIOSizeInBytes = avg(AvgReadIOSizeInBytes),
            AvgWriteIOSizeInBytes = avg(AvgWriteIOSizeInBytes),
            QD = sum(QD)
            by bin(PreciseTimeStamp, 5m)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_armId}`

---
