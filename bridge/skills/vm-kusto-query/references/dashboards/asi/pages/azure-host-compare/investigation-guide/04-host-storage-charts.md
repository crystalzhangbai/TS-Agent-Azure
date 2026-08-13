# Host Storage Charts

> Source: **Azure Host Compare Investigation Guide** dashboard, chapter **Host Storage Charts** (4 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ASAP IO Stats for {{nodeId1}}

### Azure Host Node ASAP 2.0 IO Stats

_Widget purpose:_ ASAP IO Stats for {{nodeId1}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Storage Charts > ASAP IO Stats for {{nodeId1}}`

```kusto
OsAsapCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| summarize IOPS = sum(IOPS), MBPS = sum(MBPS), 
            ReadIOPS = sum(ReadIOPS), WriteIOPS = sum(WriteIOPS), MaxReadIOPS = max(MaxReadIOPS), MaxReadMBPS = max(MaxReadMBPS),
            QD = sum(QD),
            DeltaFoCompleted = sum(DeltaFoCompleted), DeltaPoCompleted = sum(DeltaPoCompleted), DeltaIOCompleted = sum(DeltaIOCompleted),
            FO_IOPS = sum(DeltaFoCompleted) / max(OsDiagDurationInSec),
            FO_MBPS = sum(DeltaFoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
            PO_IOPS = sum(DeltaPoCompleted) / max(OsDiagDurationInSec),
            PO_MBPS = sum(DeltaPoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
            AverageReadLatency = avg(AverageReadLatency), AverageWriteLatency = avg(AverageWriteLatency)
            by bin(todatetime(OsDiagHostTimeStamp), 5s)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

## ASAP IO Stats for {{nodeId2}}

### Azure Host Node ASAP 2.0 IO Stats

_Widget purpose:_ ASAP IO Stats for {{nodeId2}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Storage Charts > ASAP IO Stats for {{nodeId2}}`

```kusto
OsAsapCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| summarize IOPS = sum(IOPS), MBPS = sum(MBPS), 
            ReadIOPS = sum(ReadIOPS), WriteIOPS = sum(WriteIOPS), MaxReadIOPS = max(MaxReadIOPS), MaxReadMBPS = max(MaxReadMBPS),
            QD = sum(QD),
            DeltaFoCompleted = sum(DeltaFoCompleted), DeltaPoCompleted = sum(DeltaPoCompleted), DeltaIOCompleted = sum(DeltaIOCompleted),
            FO_IOPS = sum(DeltaFoCompleted) / max(OsDiagDurationInSec),
            FO_MBPS = sum(DeltaFoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
            PO_IOPS = sum(DeltaPoCompleted) / max(OsDiagDurationInSec),
            PO_MBPS = sum(DeltaPoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
            AverageReadLatency = avg(AverageReadLatency), AverageWriteLatency = avg(AverageWriteLatency)
            by bin(todatetime(OsDiagHostTimeStamp), 5s)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

## BlobCache/Vdc IO Stats for {{nodeId1}}

### Azure Host Surface Stats for Node

_Widget purpose:_ BlobCache/Vdc IO Stats for {{nodeId1}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Storage Charts > BlobCache/Vdc IO Stats for {{nodeId1}}`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| extend OsDiagHostTimeStamp = todatetime(OsDiagHostTimeStamp)
| union (OsUltraSSDCounterTable | where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId | extend OsDiagHostTimeStamp = PreciseTimeStamp )
| distinct *
| where IsNewDisk == 0
| extend CachedIOPS = (DeltaCacheReads + DeltaCacheWrites) / OsDiagDurationInSec
| summarize IOPS = sum(IOPS), CachedIOPS = sum(CachedIOPS), MBPS = sum(MBPS), ReadIOPS = sum(ReadIOPS), WriteIOPS = sum(WriteIOPS), ReadMBPS = sum(ReadMBPS), WriteMBPS = sum(WriteMBPS), 
            AvgReadIOSizeInBytes = avg(AvgReadIOSizeInBytes), AvgWriteIOSizeInBytes = avg(AvgWriteIOSizeInBytes),
            QD = sum(QD), Trims = sum(DeltaTrims),
            MaxReadIOPS = avg(MaxReadIOPS), MaxWriteIOPS = avg(MaxWriteIOPS),
            MaxReadMBPS = avg(MaxReadMBPS), MaxWriteMBPS = avg(MaxWriteMBPS),
            DeltaMisalignedReads =  sum(DeltaMisalignedReads), DeltaMisalignedWrites = sum(DeltaMisalignedWrites), 
            DeltaReads = sum(DeltaReads), DeltaWrites = sum(DeltaWrites), 
            ActiveDisks = dcount(BlobPath), DeltaCacheReads = sum(DeltaCacheReads), VM_Cache_Available_Tier0Blocks_Pct = round(max(WsCacheAvailablePctTier0), 2),
            DeltaFlush = sum(DeltaFlush),
            AvgFlushLatencyInMs = avg(column_ifexists("AvgFlushLatencyInMs", 0.0)), AvgReadLatencyInMs = avg(column_ifexists("AvgReadLatencyInMs", 0.0)), AvgWriteLatencyInMs = avg(column_ifexists("AvgWriteLatencyInMs", 0.0))
            by bin(todatetime(OsDiagHostTimeStamp), 5m)
| extend ReadCacheHitPercentage = DeltaCacheReads * 100.0 / DeltaReads
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

## BlobCache/Vdc IO Stats for {{nodeId2}}

### Azure Host Surface Stats for Node

_Widget purpose:_ BlobCache/Vdc IO Stats for {{nodeId2}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Storage Charts > BlobCache/Vdc IO Stats for {{nodeId2}}`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| extend OsDiagHostTimeStamp = todatetime(OsDiagHostTimeStamp)
| union (OsUltraSSDCounterTable | where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId | extend OsDiagHostTimeStamp = PreciseTimeStamp )
| distinct *
| where IsNewDisk == 0
| extend CachedIOPS = (DeltaCacheReads + DeltaCacheWrites) / OsDiagDurationInSec
| summarize IOPS = sum(IOPS), CachedIOPS = sum(CachedIOPS), MBPS = sum(MBPS), ReadIOPS = sum(ReadIOPS), WriteIOPS = sum(WriteIOPS), ReadMBPS = sum(ReadMBPS), WriteMBPS = sum(WriteMBPS), 
            AvgReadIOSizeInBytes = avg(AvgReadIOSizeInBytes), AvgWriteIOSizeInBytes = avg(AvgWriteIOSizeInBytes),
            QD = sum(QD), Trims = sum(DeltaTrims),
            MaxReadIOPS = avg(MaxReadIOPS), MaxWriteIOPS = avg(MaxWriteIOPS),
            MaxReadMBPS = avg(MaxReadMBPS), MaxWriteMBPS = avg(MaxWriteMBPS),
            DeltaMisalignedReads =  sum(DeltaMisalignedReads), DeltaMisalignedWrites = sum(DeltaMisalignedWrites), 
            DeltaReads = sum(DeltaReads), DeltaWrites = sum(DeltaWrites), 
            ActiveDisks = dcount(BlobPath), DeltaCacheReads = sum(DeltaCacheReads), VM_Cache_Available_Tier0Blocks_Pct = round(max(WsCacheAvailablePctTier0), 2),
            DeltaFlush = sum(DeltaFlush),
            AvgFlushLatencyInMs = avg(column_ifexists("AvgFlushLatencyInMs", 0.0)), AvgReadLatencyInMs = avg(column_ifexists("AvgReadLatencyInMs", 0.0)), AvgWriteLatencyInMs = avg(column_ifexists("AvgWriteLatencyInMs", 0.0))
            by bin(todatetime(OsDiagHostTimeStamp), 5m)
| extend ReadCacheHitPercentage = DeltaCacheReads * 100.0 / DeltaReads
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---
