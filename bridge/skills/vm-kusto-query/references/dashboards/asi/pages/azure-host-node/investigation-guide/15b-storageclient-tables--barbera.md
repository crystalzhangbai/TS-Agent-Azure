# StorageClient Tables (part 2/3)

> Source: **Azure Host — Azure Host Node** dashboard, chapter **StorageClient Tables** (31 queries, part 2 of 3).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## Barbera

### Azure Host Barbera Events Query

_Widget purpose:_ OsBarberaEventTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Barbera > Barbera > Barbera Events > Barbera Events > OsBarberaEventTable`

```kusto
OsBarberaEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, ProviderName, EventId, ParamStr1, ParamBinary1
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Barbera Ring Creation Failures Query

_Widget purpose:_ Barbera Ring Creation Failures (StorageClient)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Barbera > Barbera > Barbera Ring Creation Failures > Barbera Ring Creation Failures (StorageClient)`

```kusto
OsDriverLogTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where Component has "barbera" and Status != "S00000000" and Message contains "ring creation complete"
| parse Message with "OWB " Owb " ring creation complete"
| summarize FailureCount=count() by bin(PreciseTimeStamp, 1m), Owb, Status, Thread
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `Component has "barbera"`

---

### Azure Host Barbera Active Owb Index Filter

_Widget purpose:_ Ring Statistics

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `StorageClient Tables > Barbera > Barbera > Barbera Ring Usage Stats > Ring Statistics`

```kusto
OsBarberaLLDCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| distinct Value = tostring(OwbIndex)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Barbera Usage Ring Stats Query

_Widget purpose:_ Ring Statistics

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > Barbera > Barbera > Barbera Ring Usage Stats > Ring Statistics`

```kusto
OsBarberaLLDCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where isnull( owbIndexArray ) or array_length( owbIndexArray ) == 0 or tostring(OwbIndex) in ( owbIndexArray )
| summarize LldIOPS = round(sum(LldIOPS), 0), maxActiveSlotCount = max(ActiveSlotCount), maxOutstandingSlotCount = max(OutstandingSlotCount), RingIoPct = avg(DelRingIOPct), DirectIOCount = sum(DelDirectIOCount), DirectIOTimeInSec = sum(DelDirectTimeInSec), 
    RingIOTimeInSec = sum(DelRingTimeInSec), PausedIOTimeInSec = sum(DelPausedTimeInSec), CollidedReads = sum(DelCollidedReads), CollidedWrites = sum(DelCollidedWrites), CollidedWriteOverlapExactMatch = sum(DelCollidedWriteOverlapExactMatch), 
    CollidedWriteOverlapNoMatch = sum(DelCollidedWriteOverlapNoMatch), CollidedWriteOverlapOffsetMatch = sum(DelCollidedWriteOverlapOffsetMatch), ShadowWrites = sum(DelShadowWrites), ShadowWritesDeferred = sum(DelShadowWritesDeferred), 
    CollidedWritesStillPending = sum(DelCollidedWritesStillPending), SlotOverflows = sum(DelSlotOverflows) 
    by bin(PreciseTimeStamp, 5m)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{owbIndexArray}`

---

### BarberaConfigDetails

_Widget purpose:_ Barbera Config Details

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Barbera > Barbera > BarberaConfigData > BarberaConfigData > Barbera Config Details`

```kusto
OsBarberaLLDConfigTable 
| where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId and OwbType == 0 
| parse BlobPath with * "/" BlobPath "?" *
| summarize arg_max(PreciseTimeStamp, *) by BlobPath, CacheBuddy1LocalAddress, CacheBuddy1RemoteAddress, CacheBuddy2RemoteAddress, OwbType, LldState, BackingType, NvType, IsRingBroken, SlotCount, L1Lease, L2Lease
| project PreciseTimeStamp, BlobPath, CacheBuddy1LocalAddress, CacheBuddy1RemoteAddress, CacheBuddy2RemoteAddress,
    OwbType = case(OwbType == 0, "Primary", OwbType == 1, "Secondary", OwbType == 2, "Tertiary", "Unknown"),
    LldState = case(LldState == 0, "Paused", LldState == 1, "Direct", LldState ==2, "Ring", "Unknown"),
    BackingType = case(BackingType == 0, "None", BackingType == 1, "Blob", BackingType == 2, "File", "Unknown"),
    NvType = case(NvType == 0, "RAM", NvType ==1, "File", "Unknown"),
    IsRingBroken, SlotCount, L1Lease, L2Lease 
| join kind=leftouter (
    OsXIOSurfaceCounterTable
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
    | parse BlobPath with * "/" BlobPath "?" *
    | summarize arg_max(PreciseTimeStamp, *) by SurfaceName
    | extend DiskType = case(DiskType == 1, "OS Disk", DiskType == 2, "Temp Disk", DiskType == 3 or BlobPath contains "md-dd", "Data Disk", SurfaceName startswith "BASE_", "Ephemeral OS Disk Base", "")
    | project BlobPath, SurfaceName, BSId, DiskType
) on $left.BlobPath == $right.BlobPath
| sort by PreciseTimeStamp asc
| project-away BlobPath1
| project-reorder PreciseTimeStamp, BSId, BlobPath
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### BarberaConfigSummary

_Widget purpose:_ Latest Buddy Summary

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Card`
Source panel: `StorageClient Tables > Barbera > Barbera > BarberaConfigData > BarberaConfigData > Latest Buddy Summary`

```kusto
let _startTime = queryFrom;
let _endTime = queryTo;
let _nodeId = nodeId;
let barberaNodeConfig = OsBarberaLLDConfigTable 
| where PreciseTimeStamp between (_startTime.._endTime) and NodeId =~ _nodeId and OwbType == 0 
| summarize arg_max(PreciseTimeStamp, Cluster, NodeId, CacheBuddy1LocalAddress, CacheBuddy1RemoteAddress, CacheBuddy2RemoteAddress ) by NodeIdentity;
let barberaCluster = barberaNodeConfig | distinct Cluster;
let barberaBuddyIPs = barberaNodeConfig | project NodeIP = CacheBuddy1LocalAddress
| union (barberaNodeConfig | project NodeIP = CacheBuddy1RemoteAddress)
| union (barberaNodeConfig | project NodeIP = CacheBuddy2RemoteAddress);
OsBarberaLLDConfigTable
| where PreciseTimeStamp between (_startTime.._endTime) and Cluster in~ (barberaCluster) and NodeIdentity in~ ((barberaBuddyIPs))
| summarize arg_max(PreciseTimeStamp, * ) by NodeIdentity
| project PreciseTimeStamp, NodeId, NodeIdentity, CacheBuddy1LocalAddress, CacheBuddy1RemoteAddress, CacheBuddy2LocalAddress, CacheBuddy2RemoteAddress, OwbType,
    LldState = case(LldState == 0, "Paused", LldState == 1, "Direct", LldState == 2, "Ring", "Unknown"),
    BackingType = case(BackingType == 0, "None", BackingType == 1, "Blob", BackingType == 2, "File", "Unknown"),
    NvType = case(NvType == 0, "RAM", NvType == 1, "File", "Unknown")
| extend barberaNode = strcat(NodeId, " | ", NodeIdentity)
| summarize PrimaryNodeId = take_anyif(NodeId, OwbType == 0), PrimaryNodeIP = take_anyif(NodeIdentity, OwbType == 0), 
            SecondaryNodeId = take_anyif(NodeId, OwbType == 1), SecondaryNodeIP = take_anyif(NodeIdentity, OwbType == 1), 
            TertiaryNodeId = take_anyif(NodeId, OwbType == 2), TertiaryNodeIP = take_anyif(NodeIdentity, OwbType == 2) 
            by LldState, BackingType, NvType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host BarberaSvcEvent Query

_Widget purpose:_ OsBarberaEventTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Barbera > Barbera > BarberaSvcEvent > BarberaSvcEvent > OsBarberaEventTable`

```kusto
BarberaSvcEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, eventType, error, description
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host BarberaSvcRingEvent Query

_Widget purpose:_ BarberaSvcRingEvent

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Barbera > Barbera > BarberaSvcRingEvent > BarberaSvcRingEvent > BarberaSvcRingEvent`

```kusto
BarberaSvcRingEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, EventId, eventType, owbIndex, error, description
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host BarberaSvcTopologyEvent Query

_Widget purpose:_ BarberaSvcTopologyEvent

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Barbera > Barbera > BarberaSvcTopologyEvent > BarberaSvcTopologyEvent > BarberaSvcTopologyEvent`

```kusto
BarberaSvcTopologyEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, EventId, eventType, hr, primaryNodeId, description
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## BlobCache

### Azure Host BlobCache Config Table

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > BlobCache > BlobCache > Blobcache Config`

```kusto
OsBlobCacheConfigTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId
| project PreciseTimeStamp, EntityType, EntityId, EntityConfig, UserData
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host BlobCache Event Table

_Widget purpose:_ OsBlobCacheEventTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > BlobCache > BlobCache > Blobcache Events > Blobcache Events > OsBlobCacheEventTable`

```kusto
OsBlobCacheEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, ProviderName, EventId, ParamStr1, ParamBinary1
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Blobcache InternalCounters Query

_Widget purpose:_ Blobcache Global Internal Counters (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > BlobCache > BlobCache > BlobCache Internal Counters > Blobcache Global Internal Counters (StorageClient)`

```kusto
OsBlobCacheInternalCounterTable
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == nodeId
| project PreciseTimeStamp, BSPausedWrites = DeltaBSPausedWrites, BSWaitForFlush = DeltaBSWaitForFlush, OtherQuotaStalls = DeltaOtherQuotaStalls, BSWrite2Retries = DeltaBSWrite2Retries, 
        BSTier0EarlyWriteCount = DeltaBSTier0EarlyWriteCount, BSTier1EarlyWriteCount = DeltaBSTier1EarlyWriteCount, LazyDelayedEvictionTier0 = DeltaLazyDelayedEvictionTier0, 
        LazyDelayedEvictionTier1 = DeltaLazyDelayedEvictionTier1, WSPfnAllocationsL0 = DeltaWSPfnAllocationsL0, WSPfnAllocationsL1 = DeltaWSPfnAllocationsL1, 
        WSPfnAllocationWaitsL0 = DeltaWSPfnAllocationWaitsL0, WSPfnAllocationWaitsL1 = DeltaWSPfnAllocationWaitsL1, WSLockContentionCount = DeltaWSLockContentionCount,
        BSFileBackingLazyReadsInFlight = DeltaBSFileBackingLazyReadsInFlight, BSFileBackingLazyWritesInFlight = DeltaBSFileBackingLazyWritesInFlight, 
        PTblReadFromTier1 = DeltaPTblReadFromTier1, UtilWait = DeltaUtilWait, UtilWorkItemBypass = DeltaUtilWorkItemBypass, BSReadAheadHint = DeltaBSReadAheadHint, 
        LazySignalAttempt0 = DeltaLazySignalAttempt0, LazySignal0 = DeltaLazySignal0, LazySignalAttempt1 = DeltaLazySignalAttempt1, LazySignal1  = DeltaLazySignal1, DeltaOtherQuotaStalls
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{Cloud}`

---

### Azure Host CacheStore Configuration

_Widget purpose:_ CacheStore Config

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > BlobCache > BlobCache > CacheStore Stats > CacheStore Config`

```kusto
OsBlobCacheConfigTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId
| where EntityType == 4
| parse EntityConfig with * '"blocks":' cacheBlocksTotal:long ',"blocks_available":' cacheBlocksAvailable:long ',"type":' cacheTier ',"path_descriptor":"' pathDescriptor '"}'
| extend cacheBlockTotalMB = cacheBlocksTotal * 64 / 1024, cacheBlockAvailableMB = cacheBlocksAvailable * 64 / 1024
| project PreciseTimeStamp, EntityId, cacheBlockTotalMB, cacheBlockAvailableMB, cacheBlocksTotal, cacheBlocksAvailable, cacheTier, pathDescriptor
| project PreciseTimeStamp, cacheBlockTotalMB, cacheBlockAvailableMB, cacheBlocksTotal, cacheBlocksAvailable, cacheTier = strcat("Tier", cacheTier), pathDescriptor
| summarize arg_max(PreciseTimeStamp, *) by cacheTier, pathDescriptor
| project PreciseTimeStamp, cacheTier, cacheBlockTotalMB, cacheBlocksTotal, pathDescriptor
| sort by cacheTier asc, PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Node Blobcache CacheStore Stats TL

_Widget purpose:_ CacheStore Stats

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > BlobCache > BlobCache > CacheStore Stats > CacheStore Stats`

```kusto
cluster('Storageclient.eastus').database('Fa'). OsBlobcacheCacheStoreLatencyHistogramTable
    | where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
    // this has same values (IOPS/MBPS) for that cachestore, so take one single record for the 5 minute window
    | summarize hint.strategy=shuffle arg_max(PreciseTimeStamp, *)  by NodeId, bin(todatetime(OsDiagHostTimeStamp), 5m), CacheStoreIndex
    // take the sum for 5 mintues for all CacheStores to give total done in the node
    | summarize hint.strategy=shuffle
                        IOPS = sum(IOPS), ReadIOPS = sum(ReadIOPS), WriteIOPS = sum(WriteIOPS), 
                        MBPS = sum(MBPS), ReadMBPS = sum(ReadMBPS), WriteMBPS = sum(WriteMBPS) 
                        by bin(PreciseTimeStamp, 5m)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Node Blobcache Throttle missing 

_Widget purpose:_ Blobcache Throttle mismatch Surfaces

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > BlobCache > BlobCache > Throttle Config > Blobcache Throttle mismatch Surfaces`

```kusto
let CheckThrottles = (nodeId:string, startTime:datetime, endTime:datetime) {
        let surfaces = cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsBlobCacheConfigTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
        | where EntityType == 1
        | summarize arg_max(PreciseTimeStamp, *) by EntityId
        | extend EntityConfig = parse_json(EntityConfig)
        | extend BackingStoreIndex = tolong(EntityConfig.backing_store_index), SurfaceThrottleIndices = EntityConfig.throttle_indices
        | project Surface = EntityId, BackingStoreIndex, SurfaceThrottleIndices;
        let backingstores = cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsBlobCacheConfigTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
                and EntityId in (surfaces | distinct BackingStoreIndex)
        | where EntityType == 2
        | summarize arg_max(PreciseTimeStamp, *) by EntityId
        | extend EntityConfig = parse_json(EntityConfig)
        | extend BlobPath = EntityConfig.path_descriptor
        | project BackingStoreIndex = tolong(EntityId), BSThrottleIndices = EntityConfig.throttle_indices, CachePolicy = tolong(EntityConfig.cache_policy), Type = tolong(EntityConfig.type), BlobPath
        | parse BlobPath with BlobPath "?" *;
        backingstores
        | join kind=inner surfaces on BackingStoreIndex
        | extend Throttles = array_concat(BSThrottleIndices, SurfaceThrottleIndices)
        | project-away BackingStoreIndex1, BSThrottleIndices, SurfaceThrottleIndices
        | mv-expand Throttles
        | extend EntityId = tostring(Throttles)
        | join kind=inner(
            cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsBlobCacheConfigTableV2
            | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
            | where EntityType == 3
            | summarize arg_max(PreciseTimeStamp, *) by EntityId
            | extend UserData = case(UserData contains "Hardware" and UserData !endswith "}}", strcat(UserData, "}"), UserData)
            | extend Tag = tostring(parse_json(UserData).user_data.Tag)
            | distinct EntityId, Tag
        ) on EntityId
        | summarize Hardwaressd = take_anyif(Throttles, Tag contains "Hardwaressd"),
                    Hardwarenetwork = take_anyif(Throttles, Tag contains "Hardwarenetwork"),
                    XioSettingsNetworkThrottle = take_anyif(Throttles, Tag startswith "XioSettingsNetworkThrottle"),
                    VmIoSettingsNetworkThrottle = take_anyif(Throttles, Tag startswith "VmIoSettingsNetworkThrottle"),
                    VmIoSettingsSsdThrottle = take_anyif(Throttles, Tag startswith "VmIoSettingsSsdThrottle"),
                    XioSettingsSsdThrottle = take_anyif(Throttles, Tag startswith "XioSettingsSsdThrottle"),
                    NetworkThrottle = take_anyif(Throttles, Tag startswith "NetworkThrottle"),
                    LldIoSettingsNetworkThrottle = take_anyif(Throttles, Tag startswith "LldIoSettingsNetworkThrottle"),
                    dedicatedssd = take_anyif(Throttles, Tag startswith "dedicated")
        by Surface, CachePolicy, Type, BlobPath
        | extend Findings = case(Type in (0, 4) and isempty(NetworkThrottle), pack_array("No Blob Network throttle found"), pack_array("Blob Network Throttle Found"))
        | extend Findings = case(CachePolicy in (0, 1, 2) and isempty(VmIoSettingsNetworkThrottle) and isempty(XioSettingsNetworkThrottle), 
                                    array_concat(Findings, pack_array("No VM Level Network Throttle Found")), 
                                    array_concat(Findings, pack_array("VM Level Network Throttle Found")))
        | extend Findings = case(CachePolicy == 2 and (isempty(VmIoSettingsSsdThrottle) and isempty(XioSettingsSsdThrottle)), 
                                    array_concat(Findings, pack_array("No VM Level LocalSSD Throttle Found")),
                                    array_concat(Findings, pack_array("VM Level LocalSSD Throttle Found")))
        | extend Findings = case(CachePolicy == 2 and (isempty(dedicatedssd)), 
                                    array_concat(Findings, pack_array("No Dedicated SSD Throttle for the blob Found")),
                                    array_concat(Findings, pack_array("Dedicated SSD Throttle for the blob Found")))
//         | extend Findings = case(CachePolicy == 2 and (isempty(Hardwaressd)), 
//                                     array_concat(Findings, pack_array("No Node level Hardware SSD Throttle Found")),
//                                     array_concat(Findings, pack_array("Node level Hardware SSD Throttle Found")))
//         | extend Findings = case(Type in (0, 4) and (isempty(Hardwarenetwork)), 
//                                     array_concat(Findings, pack_array("No Node level Hardware Network Throttle Found")), 
//                                     array_concat(Findings, pack_array("Node level Hardware Network Throttle Found")))
        | extend Findings = case((Type == 4 and isempty(LldIoSettingsNetworkThrottle)), 
                                    array_concat(Findings, pack_array("No Barbera Throttle Found")),
                                    Type == 4, array_concat(Findings, pack_array("Barbera Throttle Found")),
                                    array_concat(Findings, pack_array("")))
        | project Surface, CachePolicy, Type, Findings, BlobPath
        | mv-expand Findings
        | where isnotempty(Findings)
        | where Findings startswith "No "
        | parse Surface with ContainerId "_" *
        | project PreciseTimeStamp = startTime, NodeId = nodeId, ContainerId, EventName = "Misconfigured Throttles", Message = strcat("Surface ", Surface, " CachePolicy: ", CachePolicy, " BlobPath: ", BlobPath ," ", Findings)
    };
CheckThrottles(nodeId, startTime, endTime)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `Findings startswith "No "`

---

## DAL

### Azure Host Node DAL Logs2

_Widget purpose:_ Storage Tracing Event Table

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > DAL > DAL Table > Storage Tracing Event Table`

```kusto
StorageTracingEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| extend Message = parse_json(Message)
| project PreciseTimeStamp, ThreadId = Tid, Result = Message.result, File = Message.file, Function = Message.function,
            Line = Message.line, Message = Message.message
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Node DirectAccessEvent

_Widget purpose:_ DirectAccessEvent

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table` · Widget: `Tab`
Source panel: `StorageClient Tables > DAL > DirectAccessEvent`

```kusto
DirectAccessEvent
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| project PreciseTimeStamp, ContainerId, Operation, Stage, ResultCode, DirectAccessType, DiskNumber, SerialNumber
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host DAL Logs

_Widget purpose:_ IFX Table with DAL/VMAL Logs

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > DAL > IFX Table > IFX Table with DAL/VMAL Logs`

```kusto
IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == nodeId
| extend Time = DurationIn100ns/10000000.0
| where OperationName contains "vmAbstractionLayer" or OperationName contains "DiskAbstractionLayer"
| extend StartTime = TIMESTAMP-(Time*1s)
| project StartTime, EndTime=TIMESTAMP, OperationName, Time, Tid, ResultType, ResultSignature, ContextInCsv
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `OperationName contains "vmAbstractionLayer"`

---

### Azure Host Node DAL OsLoggerTable

_Widget purpose:_ OsLoggerTable (filtered for DAL)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > DAL > OsLoggerTable (filtered for DAL) > OsLoggerTable (filtered for DAL)`

```kusto
OsLoggerTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
        and ComponentName == "DiskAbstractionLayer"
| extend level = case(LogErrorLevel == "Error", "error", LogErrorLevel == "Warning", "warning", LogErrorLevel == "Critical", "fatal", "info")
| project PreciseTimeStamp, level, FileName, FunctionName, LineNumber, ResultCode, ErrorDetails 
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Driver Logs

### Azure Host StorageClient Driver Logs

_Widget purpose:_ StorageClient Driver Logs (Barbera, BlobCache, HandleProxy)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Driver Logs > Driver Logs > StorageClient Driver Logs (Barbera, BlobCache, HandleProxy)`

```kusto
OsDriverLogTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp = tostring(todatetime(replace('/', '-', EventTime))), Component, Version, Status, Thread, Message 
| sort by PreciseTimeStamp asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## EDrive

### Azure Host Node EDrive Manager EvtTable

_Widget purpose:_ EDrvMgrEventTable

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > EDrive > EDrive Manager Event > EDrvMgrEventTable`

```kusto
EDrvMgrEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| project PreciseTimeStamp, EventId, ParamStr1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Node EDrive Operations

_Widget purpose:_ EdrvMgrOperationsTable

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > EDrive > EDrive Manager Operations > EdrvMgrOperationsTable`

```kusto
EdrvMgrOperationsTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| project todatetime(TimeCreated), UserID, NTStatus, EventType, InterfaceString, DevicePath, DiskNumber, BandStateb4Unlock, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Node EDrive Manager Table

_Widget purpose:_ EDrvMgrTable

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > EDrive > EDrive Manager Table > EDrvMgrTable`

```kusto
EDrvMgrTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| project PreciseTimeStamp, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Node EDrive Encryption Events

_Widget purpose:_ XdiskEncEvent

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > EDrive > Encryption Event > XdiskEncEvent`

```kusto
XdiskEncEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, edriveCount, driveCount, nodeSkuSupportBitMap, encSrvManagement, nodeType, encStateChange, errorCode, isHybridNode, message
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Event 17 Analysis

### Azure Host OsAnalyzerTable

_Widget purpose:_ OsAnalyzer Host Node Analysis

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `StorageClient Tables > Event 17 Analysis > Event 17 Analysis > OsAnalyzerTable > OsAnalyzerTable > OsAnalyzer Host Node Analysis`

```kusto
GetRDOSE17Triage(cluster, startTime, endTime)
| where NodeId == nodeId
| project PreciseTimeStamp, StorageClusterName, VhdPath, ErrorCode, ErrorDescription, EscalateTo, nextStep, AnalysisText = replace("VHD_NOTFOUND_IN_LMALL;", "", AnalysisText)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`, `{cluster}`

---

### Azure Host XStore AutoTriage

_Widget purpose:_ XStore AutoTriage Analysis

Cluster: `azcore.centralus.kusto.windows.net` · Database: `XHealth` · Type: `Table`
Source panel: `StorageClient Tables > Event 17 Analysis > Event 17 Analysis > XStore Analysis > XStore Analysis > XStore AutoTriage Analysis`

```kusto
DiskFailureXStoreTriage
| where TimeStamp between (startTime .. endTime) and NodeId == nodeId
| summarize arg_max(TriageTimestamp, *) by VhdAppCluster, NodeId, DiskPath, TimeStamp
| project TimeStamp, TriageTimestamp, TriageCategory, TriageReason, DiskPath
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## MFND

### PnP Events

_Widget purpose:_ WindowsEventTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > MFND > Driver Events > PnP Events > WindowsEventTable`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (['_startTime'] .. ['_endTime'])
| where ProviderName == "Microsoft-Windows-Kernel-PnP"
| where NodeId == ['_nodeId']
| project PreciseTimeStamp, TimeCreated, EventId, Level, Description
| sort by PreciseTimeStamp
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

**Signal filters seen in KQL:** `ProviderName == "Microsoft-Windows-Kernel-PnP"`

---

### StorPort Events

_Widget purpose:_ WindowsStorageEvents

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > MFND > Driver Events > StorPort Events > WindowsStorageEvents`

```kusto
WindowsStorageEvents
| where PreciseTimeStamp between (['_startTime']..['_endTime'])
| where ProviderName == "Microsoft-Windows-StorPort"
| where NodeId == ['_nodeId']
| project PreciseTimeStamp, EventId, Serial, Description, EventData
| sort by PreciseTimeStamp
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

**Signal filters seen in KQL:** `ProviderName == "Microsoft-Windows-StorPort"`

---

### DirectAccessEvent MFND Query

_Widget purpose:_ DirectAccessEvent

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > MFND > MFND Events > Direct Access MFND Event > DirectAccessEvent`

```kusto
DirectAccessEvent
| where TIMESTAMP between (['_startTime']..['_endTime'])
| where NodeId == ['_nodeId']
| where DirectAccessType =~ "Mfnd"
| project PreciseTimeStamp, ContainerId, DirectAccessType, Operation, Stage, ResultCode, LocationPath, SerialNumber, MfndControllerSettings
| sort by PreciseTimeStamp
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

**Signal filters seen in KQL:** `DirectAccessType =~ "Mfnd"`

---

### Storage Tracing MFND Event Query

_Widget purpose:_ StorageTracingEventTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > MFND > MFND Events > Storage Tracing MFND Event > StorageTracingEventTable`

```kusto
StorageTracingEventTable
| where PreciseTimeStamp between (['_startTime']..['_endTime'])
| where NodeId == ['_nodeId']
| where Message contains "MFND::"
| project PreciseTimeStamp, Level, Message
| sort by PreciseTimeStamp
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

**Signal filters seen in KQL:** `Message contains "MFND::"`

---

## StorSnap

### StorSnap Event Query

_Widget purpose:_ StorSnap Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > StorSnap > StorSnap > StorSnap Events`

```kusto
let _startTime = queryFrom;
let _endTime = queryTo;
let _nodeId = nodeId;
StorsnapEventTable 
| where PreciseTimeStamp between (_startTime.._endTime) and NodeId == _nodeId
| project PreciseTimeStamp, ProviderName, EventId, EventType, VMId, NTStatus, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---
