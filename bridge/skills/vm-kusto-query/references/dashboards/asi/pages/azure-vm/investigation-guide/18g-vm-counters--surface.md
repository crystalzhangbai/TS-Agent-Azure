# VM Counters (part 7/7)

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Counters** (23 queries, part 7 of 7).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## Surface

### Azure Host StorageClient Surface Counter Stats

_Widget purpose:_ Surface Counter Stats (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Surface > Surface > Surface Counter Stats (StorageClient)`

**Tables:** `GetABCThrottleLimits`, `OsXIOSurfaceCounterTable`, `OsUltraSSDCounterTable`
**Aggregations:** `summarize arg_min(IOPS, BPS) by Join = startTime` · `summarize arg_min(IOPS, BPS) by Join = startTime`
**Output columns:** `Join1`, `Join2`

```kusto
//let throttles = cluster('rdosdata').database('rdosdatapath').GetABCThrottleLimits(containerId, nodeId, startTime, endTime);
//let localvmThrottle = throttles | where ThrottleType in ("Local VM Limit") | summarize arg_min(IOPS, BPS) by Join = startTime;
//let remotevmThrottle = throttles | where ThrottleType in ("Remote VM Limit") | summarize arg_min(IOPS, BPS) by Join = startTime;
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and SurfaceName has containerId //and IsNewDisk == 0
| union (OsUltraSSDCounterTable | where PreciseTimeStamp between (startTime .. endTime) and ContainerId has containerId) //and IsNewDisk == 0)
| distinct *
| extend BlobPath = case(isempty(BlobPath), SurfaceName, BlobPath)
| parse BlobPath with NewValue "?" *
| extend BlobPath = case(isempty(NewValue), BlobPath, NewValue)
| where BlobPath has blobPath
| extend CachedIOPS = (DeltaCacheReads + DeltaCacheWrites) / OsDiagDurationInSec
| summarize
            WriteAcceleratorWriteIOPS = sumif(WriteIOPS, Type == 4),
            IOPS = sum(IOPS), CachedIOPS = sum(CachedIOPS), MBPS = sum(MBPS), ReadIOPS = sum(ReadIOPS), WriteIOPS = sum(WriteIOPS), ReadMBPS = sum(ReadMBPS), WriteMBPS = sum(WriteMBPS), 
            AvgReadIOSizeInBytes = avg(AvgReadIOSizeInBytes), AvgWriteIOSizeInBytes = avg(AvgWriteIOSizeInBytes),
            QD = sum(QD), Trims = sum(DeltaTrims),
            MaxReadIOPS = max(MaxReadIOPS), MaxWriteIOPS = max(MaxWriteIOPS),
            MaxReadMBPS = max(MaxReadMBPS), MaxWriteMBPS = max(MaxWriteMBPS),
            DeltaMisalignedReads =  sum(DeltaMisalignedReads), DeltaMisalignedWrites = sum(DeltaMisalignedWrites), 
            DeltaReads = sum(DeltaReads), DeltaWrites = sum(DeltaWrites), 
            ActiveDisks = dcount(BlobPath), DeltaCacheReads = sum(DeltaCacheReads), VM_Cache_Available_Tier0Blocks_Pct = round(max(WsCacheAvailablePctTier0), 2),
            DeltaFlush = sum(DeltaFlush),
            CacheSizeinGB = sum(CacheSizeinGB), 
            CacheUsagePct = sum(CacheUsagePct),
            AvgFlushLatencyInMs = avg(AvgFlushLatencyInMs), AvgReadLatencyInMs = avg(AvgReadLatencyInMs), AvgWriteLatencyInMs = avg(AvgWriteLatencyInMs)
            by bin(todatetime(PreciseTimeStamp), 5s)
| extend ReadCacheHitPercentage = DeltaCacheReads * 100.0 / DeltaReads
            //, Join = startTime
//| join kind=leftouter(
//   localvmThrottle
//   | project Join, LocalIOPS_limit = IOPS, LocalMBPS_Limit = BPS / 1000 / 1000
//) on Join
//| join kind=leftouter(
//   remotevmThrottle
//   | project Join, RemoteIOPS_limit = IOPS, RemoteMBPS_Limit = BPS / 1000 / 1000
//) on Join
//| project-away Join, Join1, Join2
| where isnotempty(PreciseTimeStamp)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{blobPath}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ Surface Counter Stats (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Surface > Surface > Surface Counter Stats (StorageClient)`

**Tables:** `OsXIOHealthSignalEvent`, `OsRDSSDHealthSignalEvent`, `OsUltraSSDHealthSignalEvent`

```kusto
let xioDisks = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let rdssdDisks = OsRDSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let ddDisks = OsUltraSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId
| distinct BlobPath, SurfaceName = SurfaceGUID;
union xioDisks, rdssdDisks, ddDisks
| extend BlobPath = case(isempty(BlobPath), SurfaceName, BlobPath)
| parse BlobPath with NewValue "?" *
| extend Value = case(isempty(NewValue), BlobPath, NewValue)
| distinct Value
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

## Throttling

### VM Throttling Metrics Chart

_Widget purpose:_ VM Throttle metrics (5 min average)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Throttling > Throttling > Throttle Stats (StorageClient) > Throttle Stats (StorageClient) > VM Throttle metrics (5 min average)`

**Tables:** `OsXIOSurfaceCounterTable`
**Aggregations:** `summarize hint.strategy = shuffle OsDiagDurationInSec = max(OsDiagDurationInSec), TotalIOP by bin(PreciseTimeStamp, 5s)`

```kusto
let _starttime = queryFrom;
let _endtime = queryTo;
let _nodeId = nodeId;
let _containerid = containerId;
let _blobPath = blobPath;
OsXIOSurfaceCounterTable
| where TIMESTAMP >= _starttime and TIMESTAMP <= _endtime
and NodeId == _nodeId
and SurfaceName contains _containerid
//| extend Blob = substring(tostring(split(BlobPath,'?')[0]),indexof(BlobPath,'/'))
| extend BlobPath = case(isempty(BlobPath), SurfaceName, BlobPath)
| parse BlobPath with NewValue "?" *
| extend BlobPath = case(isempty(NewValue), BlobPath, NewValue)
| where BlobPath contains _blobPath
| summarize hint.strategy = shuffle 
            OsDiagDurationInSec = max(OsDiagDurationInSec), 
            TotalIOPS = sum(IOPS), TotalReadIOPS = sum(ReadIOPS), 
            TotalWriteIOPS = sum(WriteIOPS), 
            TotalMBPS = sum(MBPS),
            TotalReadMBPS = sum(ReadMBPS),
            TotalWriteMBPS = sum(WriteMBPS),
            TotalDeltaThrottled = sum(DeltaThrottled),
            TotalDeltaThrottleTimeInSec =sum(DeltaThrottleTimeInSec),
            TotalDeltaReadThrottled = sum(DeltaReadsThrottled), 
            TotalDeltaWriteThrottled = sum(DeltaWritesThrottled), 
            TotalDeltaReadThrottleTimeInSec = sum(DeltaReadThrottleTimeInSec),
            TotalDeltaWriteThrottleTimeInSec = sum(DeltaWriteThrottleTimeInSec) 
            by bin(PreciseTimeStamp, 5s)
| project PreciseTimeStamp,
        TotalThrottledIOPS = iff(OsDiagDurationInSec == 0, 0.0, toreal(TotalDeltaThrottled)/OsDiagDurationInSec),
        TotalThrottledReadIOPS = toreal(TotalDeltaReadThrottled)/OsDiagDurationInSec, 
        TotalThrottledWriteIOPS = toreal(TotalDeltaWriteThrottled)/OsDiagDurationInSec,
        AvgThrottleIOWaitInMs = iff(TotalDeltaThrottled == 0, 0.0, 1000*TotalDeltaThrottleTimeInSec/TotalDeltaThrottled), 
        AvgReadThrottleIOWaitInMs = iff(TotalDeltaReadThrottled == 0, 0.0, 1000*TotalDeltaReadThrottleTimeInSec/TotalDeltaReadThrottled), 
        AvgWriteThrottleIOWaitInMs = iff(TotalDeltaWriteThrottled == 0, 0.0, 1000*TotalDeltaWriteThrottleTimeInSec/TotalDeltaWriteThrottled),
        TotalIOPS, TotalReadIOPS, TotalWriteIOPS, TotalMBPS, TotalReadMBPS, TotalWriteMBPS
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`, `{blobPath}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ VM Throttle metrics (5 min average)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Throttling > Throttling > Throttle Stats (StorageClient) > Throttle Stats (StorageClient) > VM Throttle metrics (5 min average)`

**Tables:** `OsXIOHealthSignalEvent`, `OsRDSSDHealthSignalEvent`, `OsUltraSSDHealthSignalEvent`

```kusto
let xioDisks = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let rdssdDisks = OsRDSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let ddDisks = OsUltraSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId
| distinct BlobPath, SurfaceName = SurfaceGUID;
union xioDisks, rdssdDisks, ddDisks
| extend BlobPath = case(isempty(BlobPath), SurfaceName, BlobPath)
| parse BlobPath with NewValue "?" *
| extend Value = case(isempty(NewValue), BlobPath, NewValue)
| distinct Value
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

### Azure Host VM Throttle Stats

_Widget purpose:_ VM Throttle Stats

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `VM Counters > Throttling > Throttling > Throttle Stats (StorageClient) > Throttle Stats (StorageClient) > VM Throttle Stats`

```kusto
//GetThrottleStats(containerId, startTime, endTime)
//| where sum_DeltaThrottledByAllBuckets >= 2000
GetThrottleStatsForASCInsight(containerId, startTime, endTime)
| where isempty(BlobPath) or blobPath contains BlobPath
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{blobPath}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ VM Throttle Stats

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `Table`
Source panel: `VM Counters > Throttling > Throttling > Throttle Stats (StorageClient) > Throttle Stats (StorageClient) > VM Throttle Stats`

**Tables:** `OsXIOHealthSignalEvent`, `OsRDSSDHealthSignalEvent`, `OsUltraSSDHealthSignalEvent`

```kusto
let xioDisks = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let rdssdDisks = OsRDSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let ddDisks = OsUltraSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId
| distinct BlobPath, SurfaceName = SurfaceGUID;
union xioDisks, rdssdDisks, ddDisks
| extend BlobPath = case(isempty(BlobPath), SurfaceName, BlobPath)
| parse BlobPath with NewValue "?" *
| extend Value = case(isempty(NewValue), BlobPath, NewValue)
| distinct Value
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

## Vdc (UltraDisk Client)

### VdcAIRBPQueryRCA

_Widget purpose:_ RCA Categories

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Analytics` · Type: `CategoryChart`
Source panel: `VM Counters > Vdc (UltraDisk Client) > AIR-BP Triage > RCA Categories`

**Tables:** `UltradiskClientMasterIoAirBpAutoTriageV3Table`
**Aggregations:** `summarize TotalRows = count() by MasterIo_RCA`
**Output columns:** `PreciseTimeStamp`, `NodeId`, `ContainerId`, `MasterIo_OperationType`, `BlobPath`, `MasterIo_TotalDurationInUs`, `MasterIo_RCA`, `MasterIo_WorstSubIoRcaDetails`

```kusto
UltradiskClientMasterIoAirBpAutoTriageV3Table
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId
| project PreciseTimeStamp, NodeId, ContainerId, MasterIo_OperationType, BlobPath, MasterIo_TotalDurationInUs, MasterIo_RCA, MasterIo_WorstSubIoRcaDetails
| summarize TotalRows = count() by MasterIo_RCA
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

### VdcAIRBPQueryRCACount

_Widget purpose:_ RCA Categories

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Analytics` · Type: `Table`
Source panel: `VM Counters > Vdc (UltraDisk Client) > AIR-BP Triage > RCA Categories`

**Tables:** `UltradiskClientMasterIoAirBpAutoTriageV3Table`
**Aggregations:** `summarize RCACount = count() by MasterIo_RCA`
**Output columns:** `PreciseTimeStamp`, `NodeId`, `ContainerId`, `MasterIo_OperationType`, `BlobPath`, `MasterIo_TotalDurationInUs`, `MasterIo_RCA`, `MasterIo_WorstSubIoRcaDetails`

```kusto
UltradiskClientMasterIoAirBpAutoTriageV3Table
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId
| project PreciseTimeStamp, NodeId, ContainerId, MasterIo_OperationType, BlobPath, MasterIo_TotalDurationInUs, MasterIo_RCA, MasterIo_WorstSubIoRcaDetails
| summarize RCACount = count() by MasterIo_RCA
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

### VdcAIRBPQuery

_Widget purpose:_ VdcTriage Function output

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Analytics` · Type: `Table`
Source panel: `VM Counters > Vdc (UltraDisk Client) > AIR-BP Triage > VdcTriage Function output`

**Tables:** `UltradiskClientMasterIoAirBpAutoTriageV3Table`
**Output columns:** `PreciseTimeStamp`, `MasterIo_OperationType`, `BlobPath`, `MasterIo_TotalDurationInUs`, `MasterIo_IoSizes`, `SubIo_RcaDetails`, `MasterIo_RCA`, `MasterIo_WorstSubIoRcaDetails`

```kusto
UltradiskClientMasterIoAirBpAutoTriageV3Table
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId
| parse MasterIo_IoSizes with * "[" MasterIo_IoSizes "]" *
| project PreciseTimeStamp, MasterIo_OperationType, BlobPath, MasterIo_TotalDurationInUs, MasterIo_IoSizes, SubIo_RcaDetails, MasterIo_RCA, MasterIo_WorstSubIoRcaDetails
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### VdcBlobcacheThrottleStats

_Widget purpose:_ Blobcache Throttle Stats

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Vdc (UltraDisk Client) > Blobcache Throttle Stats > Blobcache Throttle Stats`

**Tables:** `OsBlobCacheConfigTableV2`, `VdcEtwEventTable`

```kusto
let throttleId = OsBlobCacheConfigTableV2
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and UserData contains "XioSettingsNetworkThrottle" and EntityType == 3 and UserData contains containerId
| distinct EntityId;
VdcEtwEventTable
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId 
| where ChannelName == "Microsoft-Azure-VDC/Operational" and EventId == 5000 and EventMessage has "Dynamic throttle stats"
| parse Message with * 'ThrottleId="' ThrottleId:long 
                       '" RequestsReceivedCount="' RequestsReceivedCount:long
                       '" BlobcacheGetTokensCallCount="' BlobcacheGetTokensCallCount:long
                       '" FailedGetTokensCallCount="' FailedGetTokensCallCount:long
                       '" AverageTimeInUsPerGetTokensCall="' AverageTimePerGetTokensCallInUs:long
                       '" MaxTimeInUsPerGetTokensCall="' MaxTimePerGetTokensCallInUs:long
                       '" IoBucketEmptyCount="' IoBucketEmptyCount:long
                       '" BytesBucketEmptyCount="' BytesBucketEmptyCount:long
                       '" IoLowWaterMarkTriggerCount="' IoLowWaterMarkTriggerCount:long
                       '" BytesLowWaterMarkTriggerCount="' BytesLowWaterMarkTriggerCount:long
                       '" ReceivedLessTokensThanRequestedCount="' ReceivedLessTokensThanRequestedCount:long
                       '" IgnoredGreedyRequestCount="' IgnoredGreedyRequestCount:long
                       '" TokenRequestSuspendedCount="' TokenRequestSuspendedCount:long
                       '" TokenRequestsInParallel="' TokenRequestsInParallel:long
                       '" PeakTokenRequestsInParallel="' PeakTokenRequestsInParallel:long
                       '" TimeElapsed="' TimeElapsed:long
                       '" IopsTokensRequested="' IopsTokensRequested:long
                       '" BytesTokensRequested="' BytesTokensRequested:long
                       '" IopsTokensGranted="' IopsTokensGranted:long
                       '" BytesTokensGranted="' BytesTokensGranted:long
                       '" IosCompleted="' IosCompleted:long
                       '" BytesCompleted="' BytesCompleted:long
                       '"' *
| where ThrottleId in (throttleId)
| parse Message with * ' IoScalingFactor="' IoScalingFactor:long
                       '" BpsScalingFactor="' BpsScalingFactor:long
                       '"' *
| extend IOPSGranted = tolong(IopsTokensGranted)/60
| extend IOPS = tolong(IosCompleted)/60
| extend BPS = tolong(BytesCompleted)/60
| extend BPSRequested = tolong(BytesTokensRequested)/60
| extend BPSGranted = tolong(BytesTokensGranted)/60
| project PreciseTimeStamp, 
    RequestsReceivedCount, IncomingIOPS = RequestsReceivedCount/60, BlobcacheGetTokensCallCount, FailedGetTokensCallCount,
AverageTimePerGetTokensCallInUs, MaxTimePerGetTokensCallInUs, ReceivedLessTokensThanRequestedCount,
IopsTokensRequested, IopsTokensGranted, IosCompleted, IOPSGranted, IOPS,
BytesTokensRequested, BytesTokensGranted, BytesCompleted, BPSRequested, BPSGranted, BPS,
IoScalingFactor, BpsScalingFactor
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

**Signal filters seen in KQL:** `ChannelName == "Microsoft-Azure-VDC/Operational"`

---

### Azure Host Analyzer VM Vdc Blob Properties

_Widget purpose:_ Vdc Blob Properties (Ultra/Premium V2)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > Vdc (UltraDisk Client) > Disk Info > Vdc Blob Properties (Ultra/Premium V2)`

**Tables:** `OsUltraSSDConfigTable`

```kusto
OsUltraSSDConfigTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId contains containerId
| distinct BlobPath, SDFTenant, DiskDifferencingType, tostring(PreferredNetworkType), DiskEncryptionType, DiskSkuType, LatencyFloorIn100ns, IOPSThrottleUnitsPerSec, TotalBytesThrottleUnitsPerSec, VmIOPSThrottleUnitsPerSec, VmTotalBytesThrottleUnitsPerSec
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ Vdc Counters (Storage Client)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Vdc (UltraDisk Client) > Vdc Counters > Vdc Counters (Storage Client)`

**Tables:** `OsXIOHealthSignalEvent`, `OsRDSSDHealthSignalEvent`, `OsUltraSSDHealthSignalEvent`

```kusto
let xioDisks = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let rdssdDisks = OsRDSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let ddDisks = OsUltraSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId
| distinct BlobPath, SurfaceName = SurfaceGUID;
union xioDisks, rdssdDisks, ddDisks
| extend BlobPath = case(isempty(BlobPath), SurfaceName, BlobPath)
| parse BlobPath with NewValue "?" *
| extend Value = case(isempty(NewValue), BlobPath, NewValue)
| distinct Value
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

### Azure Host Analyzer VM Vdc Counters

_Widget purpose:_ Vdc Counters (Storage Client)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Vdc (UltraDisk Client) > Vdc Counters > Vdc Counters (Storage Client)`

**Tables:** `OsUltraSSDCounterTable`
**Aggregations:** `summarize AvgReadIOSizeInBytes = avg(AvgReadIOSizeInBytes), AvgWriteIOSizeInBytes = avg(Av by bin(PreciseTimeStamp, 5s)`

```kusto
OsUltraSSDCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId 
    and ContainerId contains containerId
    and IsRFR != 1
| where BlobPath contains blobPath
| summarize AvgReadIOSizeInBytes = avg(AvgReadIOSizeInBytes), AvgWriteIOSizeInBytes = avg(AvgWriteIOSizeInBytes), QD = sum(QD), PendingIos = sum(PendingIos), DeltaReads = sum(DeltaReads), DeltaWrites = sum(DeltaWrites), IOPS = sum(IOPS), MBPS = sum(MBPS), DeltaWriteRetries = sum(DeltaWriteRetries), DeltaReadRetries = sum(DeltaReadRetries), DeltaCoordinatorUnreachableCount = sum(DeltaCoordinatorUnreachableCount), DeltaCoordinatorUnawareCount = sum(DeltaCoordinatorUnawareCount), DeltaCoordinatorReportedFailureCount = sum(DeltaCoordinatorReportedFailureCount), DeltaAllReplicaFailureCount = sum(DeltaAllReplicaFailureCount), DeltaCoordinatorNetworkErrorCount = sum(DeltaCoordinatorNetworkErrorCount), DeltaSubIoCount = sum(DeltaSubIoCount), DeltaSubIoCountOnRdma = sum(DeltaRdmaSubIoReads) + sum(DeltaRdmaSubIoWrites), DeltaSubIoCountOnTcp = sum(DeltaTcpSubIoReads) + sum(DeltaTcpSubIoWrites), DeltaIoFailureCountOnRdma = sum(DeltaIoFailureCountOnRdma), DeltaIoFailureCountOnTcp = sum(DeltaIoFailureCountOnTcp), DeltaIoTimeoutCountOnRdma = sum(DeltaIoTimeoutCountOnRdma), DeltaIoTimeoutCountOnTcp = sum(DeltaIoTimeoutCountOnTcp),
            MaxReadIOPS = max(MaxReadIOPS), MaxWriteIOPS = max(MaxWriteIOPS),
            MaxReadMBPS = max(MaxReadMBPS), MaxWriteMBPS = max(MaxWriteMBPS),
            MaxIOPS = max(MaxIOPS), MaxMBPS = max(MaxMBPS)
             by bin(PreciseTimeStamp, 5s)
| extend PercentRdma = (DeltaSubIoCountOnRdma * 100.0)/ DeltaSubIoCount, PercentTcp = (DeltaSubIoCountOnTcp * 100.0)/ DeltaSubIoCount
```

**Params:** `{startTime}`, `{endTime}`, `{blobPath}`, `{containerId}`, `{nodeId}`

---

## XDisk

### Azure Host VM AIR-RDMA

_Widget purpose:_ AIR-RDMA

Cluster: `moseisley` · Database: `Air` · Type: `Table`
Source panel: `VM Counters > XDisk > XDisk > Debug Report > AIR-RDMA`

**Tables:** `RdmaFailoverEvents_HighFrequency`
**Output columns:** `EventTime`, `RCALevel1`, `RCALevel2`, `Team`, `RdmaRatio`, `DelRdmaIOCnt`, `DelStcpIOCnt`, `DelXIOCnt`

```kusto
//RdmaFailoverEvents()
RdmaFailoverEvents_HighFrequency
| where EventTime between (queryFrom .. queryTo) and ContainerId == containerId and NodeId == nodeId 
| project EventTime, RCALevel1, RCALevel2, Team, RdmaRatio, DelRdmaIOCnt, DelStcpIOCnt, DelXIOCnt
| sort by EventTime
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Vhddisk Etw Evt1 Failures

_Widget purpose:_ ETW Event 1: Failures

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > XDisk > XDisk > Debug Report > ETW Event 1: Failures`

**Tables:** `OsXIOHealthSignalEvent`, `VhdDiskEtwEventTable`
**Output columns:** `PreciseTimeStamp`, `IoType`, `BlobPath`, `ClientRequestId`, `HttpResponseStatusCode`, `NTSTATUS`, `SubStatusErrorCode`, `RemoteIp`, `RemotePort`, `ResubmitCount`

```kusto
let blobs = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| parse BlobPath with * "/" BlobPath "?" *
| distinct BlobPath;
VhdDiskEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where EventId == 1
| parse EventMessage with * 
        'blobpath: /' BlobPath '.' * 
        'TransportType:' TransportType '.' * 
        'SessionType:' SessionType '.' * 
        'NTSTATUS: ' NTSTATUS '.' *
        'ClientRequestId:' ClientRequestId '.' *
        'HttpResponseStatusCode:' HttpResponseStatusCode '.' *
        'SubStatusErrorCode:' SubStatusErrorCode '.' *
        'RequestOpcode:' RequestOpcode '.' *
        'RemoteIp:' RemoteIp '\r\n' *
        'RemotePort:' RemotePort '.' *
        'ResubmitCount:' ResubmitCount '.' *
        'FastPathRetryCount:' FastPathRetryCount '.' *
        'CurrentRetryElapsedTimeMs:' CurrentRetryElapsedTimeMs '.' *
        'TotalRequestFailureElapsedTimeMs:' TotalRequestFailureElapsedTimeMs '.' *
| extend IoType = case(RequestOpcode == 6, "Read", "Write")
| extend Transport = case(TransportType == 1, "RDMA", TransportType == 2, "HTTP", "STCP")
| where BlobPath in (blobs)
| project PreciseTimeStamp, IoType = strcat(Transport, "-", IoType), BlobPath, ClientRequestId, HttpResponseStatusCode, NTSTATUS, SubStatusErrorCode, RemoteIp, RemotePort, ResubmitCount, FastPathRetryCount//, CurrentRetryElapsedTimeMs, TotalRequestFailureElapsedTimeMs
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Vhddisk MaxTime Summary

_Widget purpose:_ Max/Min Response time at Vhddisk Layer (including retries)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > XDisk > XDisk > Debug Report > Max/Min Response time at Vhddisk Layer (including retries)`

**Tables:** `OsXIOHealthSignalEvent`, `VhdDiskEtwEventTable`
**Aggregations:** `summarize count(), MaxRequestElapsedTimeMs = max(RequestElapsedTimeMs), AvgRequestElapsedT by bin(PreciseTimeStamp, 1m), IoType_Transport = strcat(IoType,'-',Transport), Blob`
**Output columns:** `PreciseTimeStamp`, `EventMessage`

```kusto
let blobs = OsXIOHealthSignalEvent | union OsXIOSurfaceCounterTable | union OsXIOXdiskCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and (SurfaceName contains containerId or SurfaceName contains vmId)
| parse BlobPath with * "/" BlobPath "?" *
| distinct BlobPath;
VhdDiskEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == nodeId
| where EventId == 13
| project PreciseTimeStamp, EventMessage
| parse EventMessage with * 'blobpath:/' BlobPath '.' * 'TransportType:' TransportType '.' * 'RequestOpCode:' RequestOpCode '.' * 'RequestElapsedTimeMs:' RequestElapsedTimeMs '.' * "ResubmitCount:" ResubmitCount "." *
| where BlobPath in (blobs)
| extend RequestElapsedTimeMs = tolong(RequestElapsedTimeMs)
| extend IoType = iff(RequestOpCode == 6, "Read", "Write")
| extend Transport = case(TransportType == 1, "RDMA", TransportType == 2, "HTTP", "STCP")
| summarize count(), MaxRequestElapsedTimeMs = max(RequestElapsedTimeMs), AvgRequestElapsedTimeMs = round(avg(RequestElapsedTimeMs), 2), 
            MinRequestElapsedTimeMs = min(RequestElapsedTimeMs),
            MaxResubmitCount = max(tolong(ResubmitCount)), AvgResubmitCount = round(avg(tolong(ResubmitCount)), 2)
            by bin(PreciseTimeStamp, 1m), IoType_Transport = strcat(IoType,'-',Transport), BlobPath
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{vmId}`

---

### Azure Host VM Xstore Role Crash

_Widget purpose:_ Xstore Role Crash data (hosting blobs of this VM)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > XDisk > XDisk > Debug Report > Xstore Role Crash data (hosting blobs of this VM)`

**Tables:** `WindowsEventTable`, `CustomerCrashOccurredV2`, `CustomerDumpAnalysisResultV2`, `OsXIOHealthSignalEvent`, `OsXIOSurfaceCounterTable`, `VhdDiskEtwEventTable`
**Aggregations:** `summarize count() by StorageTenant` · `summarize count() by RemoteIp`
**Output columns:** `crashTime`, `crashMode`, `bucketString`, `nodeIdentity`, `cluster`

```kusto
let blobs = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and (SurfaceName contains containerId)
| parse BlobPath with * "/" BlobPath "?" *
| distinct BlobPath;
let storageTenant = OsXIOSurfaceCounterTable
| where PreciseTimeStamp between ((startTime - 4h) .. 6h) and SurfaceName contains containerId
| summarize count() by StorageTenant
| project StorageTenant = substring(StorageTenant, 0, strlen(StorageTenant) - 1);
let RemoteIp = VhdDiskEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == nodeId and EventId == 1045
| parse EventMessage with * "RemoteIp:" RemoteIp ". " * "\n" * "ConnectionDropReason:" ConnectionDropReason "." *
| where ConnectionDropReason == 0
| summarize count() by RemoteIp
| distinct RemoteIp;
let storageNodeId = cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where NodeIdentity in (RemoteIp) and Cluster in~ (storageTenant) and PreciseTimeStamp between ((startTime - 2h).. (endTime + 2h))
| distinct NodeId;
cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp between ((startTime - 2h).. (endTime + 2h)) and nodeIdentity in (storageNodeId)
| join kind=inner(
    cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
    | where PreciseTimeStamp between ((startTime - 2h).. (endTime + 2h))
) on dumpUid
| project crashTime, crashMode, bucketString, nodeIdentity, cluster
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure VM Vhddisk Timeline Events

_Widget purpose:_ Timeline of Vhddisk Events

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Tab`
Source panel: `VM Counters > XDisk > XDisk > Timeline of Vhddisk Events`

**Tables:** `OsXIOHealthSignalEvent`, `VhdDiskEtwEventTable`
**Output columns:** `PreciseTimeStamp`, `ProviderName`, `EventId`, `EventMessage`

```kusto
let blobs = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and (SurfaceName contains containerId or SurfaceName contains vmId)
| parse BlobPath with * "/" BlobPath "?" *
| distinct BlobPath;
VhdDiskEtwEventTable | union (OsVhddiskEventTable)
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == nodeId
| parse EventMessage with * 'blobpath:/' BlobPath '.' * 
| parse ParamStr1 with "/" BlobPath2 "!" *
| parse ParamStr1 with "/" BlobPath3 "?" *
| where BlobPath in (blobs) or BlobPath2 in (blobs) or BlobPath3 in (blobs)
| extend EventMessage = case(isempty(EventMessage), ParamStr1, EventMessage)
| project PreciseTimeStamp, ProviderName, EventId, EventMessage
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{vmId}`

---

### Azure VM Vhddisk Timeline Events Full

_Widget purpose:_ Vhddisk Events for Disks attached to this VM

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > XDisk > XDisk > Timeline of Vhddisk Events > Vhddisk Events for Disks attached to this VM`

**Tables:** `OsXIOHealthSignalEvent`, `VhdDiskEtwEventTable`
**Output columns:** `PreciseTimeStamp`, `ProviderName`, `EventId`, `EventMessage`

```kusto
let blobs = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and (SurfaceName contains containerId or SurfaceName contains vmId)
| parse BlobPath with * "/" BlobPath "?" *
| distinct BlobPath;
VhdDiskEtwEventTable | union (OsVhddiskEventTable)
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == nodeId
| parse EventMessage with * 'blobpath:/' BlobPath '.' * 
| parse ParamStr1 with "/" BlobPath2 "!" *
| parse ParamStr1 with "/" BlobPath3 "?" *
| where BlobPath in (blobs) or BlobPath2 in (blobs) or BlobPath3 in (blobs)
| extend EventMessage = case(isempty(EventMessage), ParamStr1, EventMessage)
| project PreciseTimeStamp, ProviderName, EventId, EventMessage
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{vmId}`, `{nodeId}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ IOPS percentage by Transport

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > XDisk > XDisk > Transport Percentage > Transport Percentage > IOPS percentage by Transport`

**Tables:** `OsXIOHealthSignalEvent`, `OsRDSSDHealthSignalEvent`, `OsUltraSSDHealthSignalEvent`

```kusto
let xioDisks = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let rdssdDisks = OsRDSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let ddDisks = OsUltraSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId
| distinct BlobPath, SurfaceName = SurfaceGUID;
union xioDisks, rdssdDisks, ddDisks
| extend BlobPath = case(isempty(BlobPath), SurfaceName, BlobPath)
| parse BlobPath with NewValue "?" *
| extend Value = case(isempty(NewValue), BlobPath, NewValue)
| distinct Value
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

### Azure Host VM XDisk Transport Percentage

_Widget purpose:_ IOPS percentage by Transport

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > XDisk > XDisk > Transport Percentage > Transport Percentage > IOPS percentage by Transport`

**Tables:** `OsXIOXdiskCounterTable`
**Aggregations:** `summarize TotalHttpIoCount = sum(DelXIOCnt) - sum(DelXTrimCnt), TotalStcpIoCount = sum(Del by PreciseTimeStamp = bin(PreciseTimeStamp, 5s)`
**Output columns:** `PreciseTimeStamp`, `PercentRdmaIOPS`, `PercentStcpIOPS`, `PercentHTTPIOPS`

```kusto
OsXIOXdiskCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| parse BlobPath with BlobPath "?" *
| where isempty(blobPath) or BlobPath == blobPath
| distinct *
| summarize TotalHttpIoCount = sum(DelXIOCnt) - sum(DelXTrimCnt), TotalStcpIoCount = sum(DelStcpIOCnt), TotalRdmaIoCount = sum(DelRdmaIOCnt) by 
            PreciseTimeStamp = bin(PreciseTimeStamp, 5s)
| extend TotalIoCount = TotalHttpIoCount + TotalStcpIoCount + TotalRdmaIoCount
| project PreciseTimeStamp, PercentRdmaIOPS = tolong((TotalRdmaIoCount * 100.0) / TotalIoCount), PercentStcpIOPS = tolong((TotalStcpIoCount * 100.0) / TotalIoCount), PercentHTTPIOPS = tolong((TotalHttpIoCount * 100.0) / TotalIoCount)
```

**Params:** `{blobPath}`, `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM XDisk Counter Stats

_Widget purpose:_ XDisk Counter Stats (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > XDisk > XDisk > XDisk Counters > XDisk Counters > XDisk Counter Stats (StorageClient)`

**Tables:** `OsXIOXdiskCounterTable`
**Aggregations:** `summarize HTTPIOPS = sum(XIOPS), StcpIOPS = sum(StcpIOPS), RdmaIOPS = sum(RdmaIOPS), HTTPM by bin(todatetime(OsDiagHostTimeStamp), 5s)`

```kusto
OsXIOXdiskCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName has containerId
| parse BlobPath with BlobPath "?" *
| where isempty(blobPath) or BlobPath == blobPath
| distinct *
| summarize HTTPIOPS = sum(XIOPS), StcpIOPS = sum(StcpIOPS), RdmaIOPS = sum(RdmaIOPS),
            HTTPMBPS = sum(NWMBPS), StcpNWMBPS = sum(StcpNWMBPS), RdmaNWMBPS = sum(RdmaNWMBPS),
            Del503Cnt = sum(Del503Cnt), Del500Cnt = sum(Del500Cnt), 
            DelXDblBufferCnt = sum(DelXDblBufferCnt), DelXRetryCnt = sum(DelXRetryCnt), 
            DelXBlockoutCnt = sum(DelXBlockoutCnt), DelXConnCnt = sum(DelXConnCnt),
            DelStcpReqForcedHttp = sum(DelStcpReqForcedHttp), DelStcpReqTimedOut = sum(DelStcpReqTimedOut),
            DelRdmaToSTcpFailOverReq = sum(DelRdmaToSTcpFailOverReq), DelXTrimBytes = sum(DelXTrimBytes),
            DelRdmaReqForcedHttp = sum(DelRdmaReqForcedHttp), DelRdmaReqTO = sum(DelRdmaReqTO),
            CurAvgRxLatInms = avg(CurAvgRxLatInms), CurAvgTxLatInms = avg(CurAvgTxLatInms),
            CurAvgRdmaRxLatInms = avg(CurAvgRdmaRxLatInms), CurAvgRdmaTxLatInms = avg(CurAvgRdmaTxLatInms),
            CurAvgStcpRxLatInms = avg(CurAvgStcpRxLatInms), CurAvgStcpTxLatInms = avg(CurAvgStcpTxLatInms),
            XQD = sum(XQD), DelSendTimeoutCnt = sum(DelSendTimeoutCnt), DelRecvTimeoutCnt = sum(DelRecvTimeoutCnt), DelXTrimCnt = sum(DelXTrimCnt),
            AvgReadIOSizeInBytes = avg(NWAvgReadIOSizeInBytes), AvgWriteIOSizeInBytes = avg(NWAvgWriteIOSizeInBytes),
            DelRdmaReadReqRetries = sum(DelRdmaReadReqRetries), DelStcpReadReqRetries = sum(DelStcpReadReqRetries),
            DelRdmaWriteReqRetries = sum(DelRdmaWriteReqRetries), DelStcpWriteReqRetries = sum(DelStcpWriteReqRetries)
            by bin(todatetime(OsDiagHostTimeStamp), 5s)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{blobPath}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ XDisk Counter Stats (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > XDisk > XDisk > XDisk Counters > XDisk Counters > XDisk Counter Stats (StorageClient)`

**Tables:** `OsXIOHealthSignalEvent`, `OsRDSSDHealthSignalEvent`, `OsUltraSSDHealthSignalEvent`

```kusto
let xioDisks = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let rdssdDisks = OsRDSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let ddDisks = OsUltraSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId
| distinct BlobPath, SurfaceName = SurfaceGUID;
union xioDisks, rdssdDisks, ddDisks
| extend BlobPath = case(isempty(BlobPath), SurfaceName, BlobPath)
| parse BlobPath with NewValue "?" *
| extend Value = case(isempty(NewValue), BlobPath, NewValue)
| distinct Value
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---
