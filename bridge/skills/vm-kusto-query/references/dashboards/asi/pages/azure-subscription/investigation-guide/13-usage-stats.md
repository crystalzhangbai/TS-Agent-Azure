# Usage Stats

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **Usage Stats** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## IOPS Stats by DiskName

### Azure Host Analyzer Subscription Disk Stats

_Widget purpose:_ IOPS Stats by DiskName

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Usage Stats > IOPS Stats by DiskName`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and ArmId contains subscriptionId
        and Type in (0, 4) and IsNewDisk == 0 and OsDiagDurationInSec == 300
| union (
        OsUltraSSDCounterTable 
        | where PreciseTimeStamp between (queryFrom .. queryTo) and ArmId contains subscriptionId
                and IsNewDisk == 0
)
| extend DiskType = case(DiskSkuType == 0, "UltraDisk", DiskSkuType == 1, "PremiumV2", IsXIOdisk == 1, "Premium SSD", BlobPath contains "md-ssd-", "Standard SSD", "Standard HDD")
| parse ArmId with * "/resourceGroups/" ResourceGroup "/" * "/disks/" DiskName
| summarize avg(IOPS), percentiles(IOPS, 50, 95, 99, 100) by ResourceGroup, DiskName, DiskType
| sort by avg_IOPS desc
| project ResourceGroup, DiskType, DiskName, Avg = round(avg_IOPS), P50 = round(percentile_IOPS_50), P95 = round(percentile_IOPS_95), P99 = round(percentile_IOPS_99), Max = round(percentile_IOPS_100)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subscriptionId}`

---

## MBPS Stats by DiskName

### Azure Host Subscription Disk MBPS Stats

_Widget purpose:_ MBPS Stats by DiskName

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Usage Stats > MBPS Stats by DiskName`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and ArmId contains subId
        and Type in (0, 4) and IsNewDisk == 0 and OsDiagDurationInSec == 300
| union (
        OsUltraSSDCounterTable 
        | where PreciseTimeStamp between (startTime .. endTime) and ArmId contains subId
                and IsNewDisk == 0
)
| extend DiskType = case(DiskSkuType == 0, "UltraDisk", DiskSkuType == 1, "PremiumV2", IsXIOdisk == 1, "Premium SSD", BlobPath contains "md-ssd-", "Standard SSD", "Standard HDD")
| parse ArmId with * "/resourceGroups/" ResourceGroup "/" * "/disks/" DiskName
| summarize avg(MBPS), percentiles(MBPS, 50, 95, 99, 100) by ResourceGroup, DiskName
| sort by avg_MBPS desc
| project ResourceGroup, DiskName, Avg = round(avg_MBPS), P50 = round(percentile_MBPS_50), P95 = round(percentile_MBPS_95), P99 = round(percentile_MBPS_99), Max = round(percentile_MBPS_100)
```

**Params:** `{startTime}`, `{endTime}`, `{subId}`

---
