# Charts

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **Charts** (4 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Cache Policy - Active Disks

### Azure Host Subscription Active Disks

_Widget purpose:_ Cache Policy - Active Disks

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CategoryChart`
Source panel: `Charts > Cache Policy - Active Disks`

```kusto
OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and ArmId contains subId
| extend CachePolicy = case(Type == 4, "WriteAccelerator", CachePolicy == 0, "None", CachePolicy == 1, "ReadOnly", CachePolicy == 2, "ReadWrite", "Others")
| summarize TotalDisks = dcount(BlobPath) by Name = CachePolicy
| sort by TotalDisks desc
```

**Params:** `{startTime}`, `{endTime}`, `{subId}`

---

## Disk IOPS - Active Regions

### Azure Host Subscriptions Surface Stats Region

_Widget purpose:_ Disk IOPS - Active Regions

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Charts > Disk IOPS - Active Regions`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and ArmId contains subId and IsNewDisk == 0
| union (
    OsUltraSSDCounterTable
    | where PreciseTimeStamp between (startTime .. endTime) and ArmId contains subId and IsNewDisk == 0
)
| summarize IOPS = sum(IOPS) by bin(PreciseTimeStamp, 5m), Region
```

**Params:** `{startTime}`, `{endTime}`, `{subId}`

---

## Stats by ResourceGroup

### Azure Host Analyzer Subscription Disk Stats by ResourceGroup

_Widget purpose:_ Stats by ResourceGroup

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Charts > Stats by ResourceGroup`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and ArmId contains subscriptionId
        and Type in (0, 4) and IsNewDisk == 0 and OsDiagDurationInSec == 300
| union (
    OsUltraSSDCounterTable
    | where PreciseTimeStamp between (queryFrom .. queryTo) and ArmId contains subscriptionId and IsNewDisk == 0
)
| parse ArmId with * "/resourceGroups/" ResourceGroup "/" * "/disks/" DiskName
| summarize avg(IOPS), percentiles(IOPS, 50, 95, 99, 100), ActiveDisks = dcount(ArmId) by ResourceGroup
| project ResourceGroup, AvgIOPS = round(avg_IOPS), P50_IOPS = round(percentile_IOPS_50), P95_IOPS = round(percentile_IOPS_95), P99_IOPS = round(percentile_IOPS_99), MaxIOPS = round(percentile_IOPS_100), ActiveDisks
| sort by ActiveDisks desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subscriptionId}`

---

## Total IOPS/MBPS

### Azure Host Subscription Surface IO Stats

_Widget purpose:_ Total IOPS/MBPS

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Charts > Total IOPS/MBPS`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and ArmId contains subId and IsNewDisk == 0
| parse SurfaceName with ContainerId "_" *
| union (
    OsUltraSSDCounterTable
    | where PreciseTimeStamp between (startTime .. endTime) and ArmId contains subId and IsNewDisk == 0
    | project PreciseTimeStamp, UDIOPS = IOPS, UDMBPS = MBPS, ContainerId, BlobPath
)
| extend CachedIOPS = (DeltaCacheReads + DeltaCacheWrites) / OsDiagDurationInSec
| summarize IOPS = sum(IOPS), UltraPv2IOPS = sum(UDIOPS), UltraPv2MBPS = sum(UDMBPS), CachedIOPS = sum(CachedIOPS), MBPS = sum(MBPS), ActiveDisks = dcount(BlobPath), ActiveVMs = dcount(ContainerId) by bin(PreciseTimeStamp, 5m)
```

**Params:** `{subId}`, `{startTime}`, `{endTime}`

---
