# HostStorage VM Charts

> Source: **Azure VM Compare Investigation Guide** dashboard, chapter **HostStorage VM Charts** (6 queries across 6 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ASAP IO Stats for {{containerId1}}

### Azure Host VM ASAP 2.0 IO Stats

_Widget purpose:_ ASAP IO Stats for {{containerId1}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `HostStorage VM Charts > ASAP IO Stats for {{containerId1}}`

```kusto
OsAsapCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and ContainerId == containerId
| where isempty(blobPath) or BlobPath contains blobPath
| summarize IOPS = sum(IOPS), MBPS = sum(MBPS), 
            ReadIOPS = sum(ReadIOPS), WriteIOPS = sum(WriteIOPS), MaxReadIOPS = max(MaxReadIOPS), MaxReadMBPS = max(MaxReadMBPS),
            MaxWriteIOPS = max(MaxWriteIOPS), MaxWriteMBPS = max(MaxWriteMBPS),
            QD = sum(QD),
            DeltaFoCompleted = sum(DeltaFoCompleted), DeltaPoCompleted = sum(DeltaPoCompleted), DeltaIOCompleted = sum(DeltaIOCompleted),
            FO_IOPS = sum(DeltaFoCompleted) / max(OsDiagDurationInSec),
            FO_MBPS = sum(DeltaFoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
            PO_IOPS = sum(DeltaPoCompleted) / max(OsDiagDurationInSec),
            PO_MBPS = sum(DeltaPoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
            AverageReadLatency = avg(AverageReadLatency), AverageWriteLatency = avg(AverageWriteLatency)
            by bin(todatetime(OsDiagHostTimeStamp), 5s)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`, `{blobPath}`

---

## ASAP IO Stats for {{containerId2}}

### Azure Host VM ASAP 2.0 IO Stats

_Widget purpose:_ ASAP IO Stats for {{containerId2}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `HostStorage VM Charts > ASAP IO Stats for {{containerId2}}`

```kusto
OsAsapCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and ContainerId == containerId
| where isempty(blobPath) or BlobPath contains blobPath
| summarize IOPS = sum(IOPS), MBPS = sum(MBPS), 
            ReadIOPS = sum(ReadIOPS), WriteIOPS = sum(WriteIOPS), MaxReadIOPS = max(MaxReadIOPS), MaxReadMBPS = max(MaxReadMBPS),
            MaxWriteIOPS = max(MaxWriteIOPS), MaxWriteMBPS = max(MaxWriteMBPS),
            QD = sum(QD),
            DeltaFoCompleted = sum(DeltaFoCompleted), DeltaPoCompleted = sum(DeltaPoCompleted), DeltaIOCompleted = sum(DeltaIOCompleted),
            FO_IOPS = sum(DeltaFoCompleted) / max(OsDiagDurationInSec),
            FO_MBPS = sum(DeltaFoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
            PO_IOPS = sum(DeltaPoCompleted) / max(OsDiagDurationInSec),
            PO_MBPS = sum(DeltaPoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
            AverageReadLatency = avg(AverageReadLatency), AverageWriteLatency = avg(AverageWriteLatency)
            by bin(todatetime(OsDiagHostTimeStamp), 5s)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`, `{blobPath}`

---

## Blobcache/vdc IO stats for {{containerId1}}

### Azure Host StorageClient Surface Counter Stats

_Widget purpose:_ Blobcache/vdc IO stats for {{containerId1}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `HostStorage VM Charts > Blobcache/vdc IO stats for {{containerId1}}`

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

## Blobcache/vdc IO stats for {{containerId2}}

### Azure Host StorageClient Surface Counter Stats

_Widget purpose:_ Blobcache/vdc IO stats for {{containerId2}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `HostStorage VM Charts > Blobcache/vdc IO stats for {{containerId2}}`

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

## VM Disk Cache Usage Size in GB for {{containerId1}}

### Azure Host VM CacheUsagePct

_Widget purpose:_ VM Disk Cache Usage Size in GB for {{containerId1}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `HostStorage VM Charts > VM Disk Cache Usage Size in GB for {{containerId1}}`

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

## VM Disk Cache Usage Size in GB for {{containerId2}}

### Azure Host VM CacheUsagePct

_Widget purpose:_ VM Disk Cache Usage Size in GB for {{containerId2}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `HostStorage VM Charts > VM Disk Cache Usage Size in GB for {{containerId2}}`

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
