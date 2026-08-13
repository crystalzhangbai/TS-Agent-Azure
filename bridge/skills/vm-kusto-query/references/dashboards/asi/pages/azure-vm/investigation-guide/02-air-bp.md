# AIR-BP

> Source: **Azure Host - Azure VM** dashboard, chapter **AIR-BP** (5 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

##  Brownouts

### Azure VM AirManagedEventsBrownouts

_Widget purpose:_ AIR-BP Brownouts

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `AIR-BP >  Brownouts > AIR-BP Brownouts`

**Tables:** `AirManagedEventsBrownouts`
**Output columns:** `EventTime`, `NodeId`, `EventType`, `EventSource`, `ObjectType`, `ObjectId`, `Duration`, `EventCategoryLevel1`, `EventCategoryLevel2`, `EventCategoryLevel3`

```kusto
AirManagedEventsBrownouts
| where EventTime between (startTime .. endTime) and NodeId == queryNodeId and ObjectType == "Container" and ObjectId == queryContainerId
| project EventTime, NodeId, EventType, EventSource, ObjectType, ObjectId, Duration, EventCategoryLevel1, EventCategoryLevel2, EventCategoryLevel3, RCALevel1, RCALevel2, RCALevel3
```

**Params:** `{startTime}`, `{endTime}`, `{queryNodeId}`, `{queryContainerId}`

---

## Disk

### Azure Host VM AIRBP Disk

_Widget purpose:_ AIR-BP for Disks attached to the VM

Cluster: `Vmainsight` · Database: `Air` · Type: `Table`
Source panel: `AIR-BP > Disk > Disk > AIR-BP for Disks attached to the VM`

**Tables:** `AirDiskIOBlipEvents`
**Output columns:** `EventTime`, `RoleInstanceName`, `RCAType`, `RCALevel1`, `RCALevel2`, `RCALevel3`, `BlobPath`

```kusto
AirDiskIOBlipEvents
| where EventTime  between (startTime .. endTime) and ContainerId == containerId
| where TotalIOsGt1s > 0
// ignoring overflows
| where TotalIOsGt1s <= 10000000 and TotalIOsGt5s <= 10000000 and TotalIOsGt10s <= 10000000 and TotalIOsGt15s <= 10000000 and TotalIOsGt30s <= 10000000
| project EventTime, RoleInstanceName, RCAType, RCALevel1, RCALevel2, RCALevel3, BlobPath
| sort by EventTime asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Disk AIRBP Timeline

_Widget purpose:_ Timeline of AIR-BP for Disks attached to the VM 

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `TimeSeries`
Source panel: `AIR-BP > Disk > Disk > Timeline of AIR-BP for Disks attached to the VM `

**Tables:** `AirDiskIOBlipEvents`
**Aggregations:** `summarize TotalIOsGt1s = sum(TotalIOsGt1s), TotalIOsGt5s = sum(TotalIOsGt5s), TotalIOsGt10 by bin(EventTime, 5m)`

```kusto
AirDiskIOBlipEvents
| where EventTime  between (startTime .. endTime) and ContainerId == containerId
| where TotalIOsGt1s > 0
// ignoring overflows
| where TotalIOsGt1s <= 10000000 and TotalIOsGt5s <= 10000000 and TotalIOsGt10s <= 10000000 and TotalIOsGt15s <= 10000000 and TotalIOsGt30s <= 10000000
| summarize TotalIOsGt1s = sum(TotalIOsGt1s), TotalIOsGt5s = sum(TotalIOsGt5s), 
            TotalIOsGt10s = sum(TotalIOsGt10s), TotalIOsGt15s = sum(TotalIOsGt15s), TotalIOsGt30s = sum(TotalIOsGt30s),
            DelXBlockoutCnt = sum(DelXBlockoutCnt),
            TotalIOsGt60s = sum(TotalIOsGt60s), TotalIOsGt120s = sum(TotalIOsGt120s)
            by bin(EventTime, 5m)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

## DiskBlackoutXStoreTriage

### VM_XHealth_DiskBlackoutXStoreTriage

_Widget purpose:_ DiskBlackoutXStoreTriage

Cluster: `xlivesite.kusto.windows.net` · Database: `XHealthDiskTriage` · Type: `Table`
Source panel: `AIR-BP > DiskBlackoutXStoreTriage > DiskBlackoutXStoreTriage`

**Tables:** `LogClusterSnapshot`, `OsXIOSurfaceCounterTable`, `OsUltraSSDCounterTable`, `XHealth_DiskBlackoutXStoreTriage`
**Aggregations:** `summarize arg_max(TriageTimestamp, *) by BlobPath) on $left.BlobPath==$right.BlobPath`
**Output columns:** `EventTime`, `TriageCategory`, `TriageReason`, `StorageRegion`, `StorageTenant`, `BlobPath`, `ClusterFailureReportUrl`

```kusto
let ClusterInfo = cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogClusterSnapshot
    | where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 1h)) 
    | distinct Tenant, AvailabilityZone;
cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and Cluster == cluster
| extend ContainerId = tostring(split(split(SurfaceName, "_")[0], "~")[0])
| where ContainerId == containerId or SurfaceName has vmId
| union (cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsUltraSSDCounterTable | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and Cluster == cluster and ContainerId contains containerId)
| parse ArmId with * "/disks/" DiskName
| parse BlobPath with * "/" NewBlobPath "?" *
| extend FullPath = case(isnotempty(NewBlobPath), NewBlobPath, BlobPath)
| extend StorageAccount = tostring(split(FullPath, "/")[0])
| extend halfpath = tostring(split(FullPath, "/" )[1])
| extend BlobPath = strcat(halfpath, "/abcd")
| where BlobPath != "/abcd"
| distinct  BlobPath
| join kind=inner
(cluster("xlivesite.kusto.windows.net").database("XHealthDiskTriage").XHealth_DiskBlackoutXStoreTriage
| where EventTime between (startTime..endTime)
| where NodeId == nodeId
| summarize arg_max(TriageTimestamp, *) by BlobPath) on $left.BlobPath==$right.BlobPath
| project EventTime, TriageCategory, TriageReason, StorageRegion, StorageTenant, BlobPath, ClusterFailureReportUrl
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{cluster}`, `{vmId}`, `{containerId}`

**Signal filters seen in KQL:** `BlobPath != "/abcd"`

---

## Managed Events

### Azure VM AIRBP Managed Events

_Widget purpose:_ AIR-BP Managed Events

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `AIR-BP > Managed Events > AIR-BP Managed Events`

**Tables:** `AirManagedEvents`
**Output columns:** `EventTime`, `EventType`, `EventSource`, `ObjectType`, `ObjectId`, `Duration`, `EventCategoryLevel1`, `EventCategoryLevel2`, `EventCategoryLevel3`, `RCALevel1`

```kusto
AirManagedEvents
| where EventTime between (startTime .. endTime) and NodeId == queryNodeId and ObjectType == "Container" and ObjectId == queryContainerId
| project EventTime, EventType, EventSource, ObjectType, ObjectId, Duration, EventCategoryLevel1, EventCategoryLevel2, EventCategoryLevel3, RCALevel1, RoleInstanceName
```

**Params:** `{startTime}`, `{endTime}`, `{queryNodeId}`, `{queryContainerId}`

---
