# VM Counters (part 3/7)

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Counters** (10 queries, part 3 of 7).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## ASAP VM Events

### Azure Host VM ASAP VM AsapPfEtwTraceLogEventViewExtended2

_Widget purpose:_ Timeline events for the VM from AsapPfEtwTraceLogEventViewExtended

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > ASAP VM Events > Timeline events for the VM from AsapPfEtwTraceLogEventViewExtended`

**Output columns:** `PreciseTimeStamp`, `EventId`, `EventName`, `VfId`, `NsId`, `NsIndex`, `Message`

```kusto
database('Fa').AsapPfEtwTraceLogEventViewExtended
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
        and containerId == containerID
| project PreciseTimeStamp, EventId, EventName, VfId, NsId, NsIndex, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerID}`, `{nodeId}`

---

## Burst

### Azure Host VM Disk Burst Counters

_Widget purpose:_ Disk Burst Counters (XIO Disks)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Burst > Burst > Disk Burst Counters (XIO Disks)`

**Tables:** `OsXIOSurfaceCounterTable`, `OsBlobCacheConfigTableV2`, `OsXIOThrottleCounterTable`
**Aggregations:** `summarize arg_max(PreciseTimeStamp, *) by EntityId, EntityConfig, UserData` · `summarize DeltaBurstPausedCnt = sum(DeltaBurstPausedCnt), DeltaBurstResumedCnt = sum(Delta by bin(PreciseTimeStamp, 5s)`
**Output columns:** `ThrottleIndex`, `ThrottleType`

```kusto
let ThrottleType = (tag:string) {
    case(tag startswith "networkthrottle", "Remote Blob Limit",
        tag startswith "VmIoSettingsnetworkthrottle", "Remote VM Limit (VmIoSettingsnetworkthrottle)",
        tag startswith "XioSettingsnetworkthrottle", "Remote VM Limit (XioSettingsnetworkthrottle)",
        tag startswith "VmIoSettingsssdthrottle", "Local VM Limit (VmIoSettingsssdthrottle)",
        tag startswith "XioSettingsssdthrottle", "Local VM Limit (XioSettingsssdthrottle)",
        tag startswith "Hardware", "Hardware SSD",
        tag startswith "dedicated", "Local VM Limit (dedicated Cached Disk)", 
        tag startswith "LldIoSettingsNetworkThrottle", "Barbera Disk Limit",
        "Unknown")
};
let throttles = cluster("storageclient.eastus.kusto.windows.net").database("Fa").OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| parse BlobPath with BlobPath "?" *
| where isempty(blobPath) or BlobPath == blobPath or SurfaceName contains blobPath
| distinct ThrottleCountersListString, BlobPath
| project Throttles = split(replace(";", "", ThrottleCountersListString), ","), BlobPath
| mv-expand Throttles
| where isnotempty(Throttles)
| extend Throttles = tolong(Throttles)
| distinct Throttles;
let throttleConfigs = cluster("storageclient.eastus.kusto.windows.net").database("Fa").OsBlobCacheConfigTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId 
and EntityType == 3 and EntityId in (throttles) //and UserData contains containerId
| summarize arg_max(PreciseTimeStamp, *) by EntityId, EntityConfig, UserData
| extend UserData = case(UserData contains "Hardware" and UserData !endswith "}}", strcat(UserData, "}"), UserData)
| project PreciseTimeStamp, EntityId, parse_json(EntityConfig), parse_json(UserData)
| project ThrottleIndex = tolong(EntityId), ThrottleType = ThrottleType(UserData.user_data.Tag)
| where ThrottleType contains "Remote Blob Limit" or ThrottleType contains "Barbera Disk Limit"; //For Disk level burst
throttleConfigs | join kind=inner (
    cluster("storageclient.eastus.kusto.windows.net").database("Fa").OsXIOThrottleCounterTable
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ThrottleIndex in (throttles)
    | project DeltaBurstPausedCnt, DeltaBurstResumedCnt, DeltaBurstTokensUsedByte, DeltaBurstTokensUsedIO, PreciseTimeStamp, ThrottleIndex, CurrentBucketCountByte, CurrentBucketCountIO
) on ThrottleIndex
| summarize DeltaBurstPausedCnt = sum(DeltaBurstPausedCnt), DeltaBurstResumedCnt = sum(DeltaBurstResumedCnt), 
            DeltaBurstTokensUsedByte = sum(DeltaBurstTokensUsedByte), DeltaBurstTokensUsedIO = sum(DeltaBurstTokensUsedIO), 
            AvailableTokensForIOPS = sum(CurrentBucketCountIO), AvailableTokensForBytes = sum(CurrentBucketCountByte)
            by bin(PreciseTimeStamp, 5s)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{blobPath}`

**Signal filters seen in KQL:** `ThrottleType contains "Remote Blob Limit"`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ Disk Burst Counters (XIO Disks)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Burst > Burst > Disk Burst Counters (XIO Disks)`

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

### VM Burst Counters

_Widget purpose:_ VM Burst Counters (Uncached)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Burst > Burst > VM Burst Counters (Uncached)`

**Tables:** `OsXIOSurfaceCounterTable`, `OsBlobCacheConfigTableV2`, `OsXIOThrottleCounterTable`
**Aggregations:** `summarize arg_max(PreciseTimeStamp, *) by EntityId, EntityConfig, UserData` · `summarize DeltaBurstPausedCnt = sum(DeltaBurstPausedCnt), DeltaBurstResumedCnt = sum(Delta by bin(PreciseTimeStamp, 5s)`
**Output columns:** `ThrottleIndex`, `ThrottleType`

```kusto
let blobPath = ""; //No blobpath for VM level burst visualization
let ThrottleType = (tag:string) {
    case(tag startswith "networkthrottle", "Remote Blob Limit",
        tag startswith "VmIoSettingsnetworkthrottle", "Remote VM Limit (VmIoSettingsnetworkthrottle)",
        tag startswith "XioSettingsnetworkthrottle", "Remote VM Limit (XioSettingsnetworkthrottle)",
        tag startswith "VmIoSettingsssdthrottle", "Local VM Limit (VmIoSettingsssdthrottle)",
        tag startswith "XioSettingsssdthrottle", "Local VM Limit (XioSettingsssdthrottle)",
        tag startswith "Hardware", "Hardware SSD",
        tag startswith "dedicated", "Local VM Limit (dedicated Cached Disk)", 
        tag startswith "LldIoSettingsNetworkThrottle", "Barbera Disk Limit",
        "Unknown")
};
let throttles = OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| parse BlobPath with BlobPath "?" *
| where isempty(blobPath) or BlobPath == blobPath or SurfaceName contains blobPath
| distinct ThrottleCountersListString, BlobPath
| project Throttles = split(replace(";", "", ThrottleCountersListString), ","), BlobPath
| mv-expand Throttles
| where isnotempty(Throttles)
| extend Throttles = tolong(Throttles)
| distinct Throttles;
let throttleConfigs = OsBlobCacheConfigTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId 
and EntityType == 3 and EntityId in (throttles) //and UserData contains containerId
| summarize arg_max(PreciseTimeStamp, *) by EntityId, EntityConfig, UserData
| extend UserData = case(UserData contains "Hardware" and UserData !endswith "}}", strcat(UserData, "}"), UserData)
| project PreciseTimeStamp, EntityId, parse_json(EntityConfig), parse_json(UserData)
| project ThrottleIndex = tolong(EntityId), ThrottleType = ThrottleType(UserData.user_data.Tag)
| where (ThrottleType contains "Remote VM Limit" or ThrottleType contains "Local VM Limit") and ThrottleType !contains "dedicated"; //For VM level burst
throttleConfigs | join kind=inner (
    OsXIOThrottleCounterTable
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ThrottleIndex in (throttles)
    //| project DeltaBurstPausedCnt, DeltaBurstResumedCnt, DeltaBurstTokensUsedByte, DeltaBurstTokensUsedIO, PreciseTimeStamp, ThrottleIndex
) on ThrottleIndex
| summarize DeltaBurstPausedCnt = sum(DeltaBurstPausedCnt), DeltaBurstResumedCnt = sum(DeltaBurstResumedCnt), 
            DeltaBurstTokensUsedByte = sum(DeltaBurstTokensUsedByte), DeltaBurstTokensUsedIO = sum(DeltaBurstTokensUsedIO),
            AvailableTokensForIOPS = sum(CurrentBucketCountIO), AvailableTokensForBytes = sum(CurrentBucketCountByte)
            by bin(PreciseTimeStamp, 5s)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

## Cache

### Azure Host VM Active Blobs Filter

_Widget purpose:_ VM Disk Cache Usage Size in GB (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Cache > Cache > VM Disk Cache Usage Size in GB (StorageClient)`

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

### Azure Host VM CacheUsagePct

_Widget purpose:_ VM Disk Cache Usage Size in GB (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `VM Counters > Cache > Cache > VM Disk Cache Usage Size in GB (StorageClient)`

**Tables:** `OsXIOSurfaceCounterTable`
**Aggregations:** `summarize CacheSizeinGB = sum(CacheSizeinGB), CacheUsagePct = sum(CacheUsagePct), TotalCac by bin(todatetime(OsDiagHostTimeStamp), 5s)`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| parse BlobPath with BlobPath "?" *
| where isempty(blobPath) or BlobPath == blobPath
| where SurfaceName contains containerId and BlobPath != ""
| distinct *
| summarize CacheSizeinGB = sum(CacheSizeinGB), CacheUsagePct = sum(CacheUsagePct), TotalCacheSizeinGB = sum(CacheSizeinGB) / sum(CacheUsagePct) * 100.0 by bin(todatetime(OsDiagHostTimeStamp), 5s)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{blobPath}`

---

### Azure Host VM Active Working Sets Filter

_Widget purpose:_ Cache Tier Block Counts per WorkingSet (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Cache > Cache Tier Block Counts per WorkingSet (StorageClient)`

**Tables:** `OsXIOSurfaceCounterTable`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| where isnotempty(WSId) and WSId != -1
| distinct Value = tostring(WSId)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

### Azure Host VM Cache Tier Block Counts

_Widget purpose:_ Cache Tier Block Counts per WorkingSet (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `VM Counters > Cache > Cache Tier Block Counts per WorkingSet (StorageClient)`

**Tables:** `OsXIOSurfaceCounterTable`
**Aggregations:** `summarize T0Free = sum(Tier0Free), T0Present = sum(Tier0Present), Tier0Dirty = sum(Tier0Di by bin(todatetime(OsDiagHostTimeStamp), 5s)`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable 
| where PreciseTimeStamp between (startTime .. endTime) 
| where NodeId == nodeId and WSId != -1 and isnotempty(WSId)
| where isempty(wsId) or WSId == wsId
| distinct *
| summarize T0Free = sum(Tier0Free), T0Present = sum(Tier0Present), Tier0Dirty = sum(Tier0Dirty), T1Free = sum(Tier1Free), T1Present = sum(Tier1Present), Tier1Dirty = sum(Tier1Dirty) by bin(todatetime(OsDiagHostTimeStamp), 5s)
```

**Params:** `{startTime}`, `{endTime}`, `{wsId}`, `{nodeId}`

---

### Azure Host VM Active Working Sets Filter

_Widget purpose:_ VM Disk Cache Usage Size Per WorkingSet in GB (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Cache > VM Disk Cache Usage Size Per WorkingSet in GB (StorageClient)`

**Tables:** `OsXIOSurfaceCounterTable`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| where isnotempty(WSId) and WSId != -1
| distinct Value = tostring(WSId)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

### Azure Host VM CacheUsagePct Per WS

_Widget purpose:_ VM Disk Cache Usage Size Per WorkingSet in GB (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Cache > VM Disk Cache Usage Size Per WorkingSet in GB (StorageClient)`

**Tables:** `OsXIOSurfaceCounterTable`
**Aggregations:** `summarize CacheSizeinGB = sum(CacheSizeinGB), CacheUsagePct = sum(CacheUsagePct) by bin(todatetime(OsDiagHostTimeStamp), 5m)`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where NodeId == nodeId and WSId != -1 and isnotempty(WSId)
| where isempty(wsId) or WSId == wsId
| distinct *
| summarize CacheSizeinGB = sum(CacheSizeinGB), CacheUsagePct = sum(CacheUsagePct) by bin(todatetime(OsDiagHostTimeStamp), 5m)
```

**Params:** `{startTime}`, `{endTime}`, `{wsId}`, `{nodeId}`

---
