# AIR-BP

> Source: **Azure Host — Azure Host Node** dashboard, chapter **AIR-BP** (4 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Brownouts

### Azure Host AirManagedEventsBrownouts

_Widget purpose:_ AIR-BP Brownouts

Cluster: `vmainsight` · Database: `Air` · Type: `Table`
Source panel: `AIR-BP > Brownouts > Brownouts > AIR-BP Brownouts`

```kusto
AirManagedEventsBrownouts
| where EventTime between (startTime .. endTime) and NodeId == nodeId
| project EventTime, NodeId, EventType, EventSource, ObjectType, ObjectId, Duration, EventCategoryLevel1, EventCategoryLevel2, EventCategoryLevel3, RCALevel1, RCALevel2, RCALevel3
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## DiskBlackoutXStoreTriage

### XHealth_DiskBlackoutXStoreTriage

_Widget purpose:_ DiskBlackoutXStoreTriage

Cluster: `Xlivesite` · Database: `XHealthDiskTriage` · Type: `Table`
Source panel: `AIR-BP > DiskBlackoutXStoreTriage > DiskBlackoutXStoreTriage`

```kusto
XHealth_DiskBlackoutXStoreTriage
| where EventTime between (query_StartTime..query_EndTime)
| where NodeId == query_NodeId
| summarize arg_max(TriageTimestamp, *) by BlobPath
| project EventTime, TriageCategory, TriageReason, StorageRegion, StorageTenant, BlobPath,ClusterFailureReportUrl
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## Disks

### Azure Host AIRBP

_Widget purpose:_ AIR-BP for Disks

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `AIR-BP > Disks > Disks > AIR-BP for Disks`

```kusto
AirDiskIOBlipEvents
| where EventTime  between (startTime .. endTime) and NodeId == nodeId
| where TotalIOsGt1s > 0
| project EventTime, RoleInstanceName, RCAType, RCALevel1, RCALevel2, RCALevel3, BlobPath, VirtualMachineUniqueId, Customer, SubscriptionId
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## Managed Events

### Azure Host AIRBP Managed Events

_Widget purpose:_ AIR-BP Managed Events

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `AIR-BP > Managed Events > Managed Events > AIR-BP Managed Events`

```kusto
AirManagedEvents
| where EventTime between (startTime .. endTime) and NodeId == nodeId
| project EventTime, EventType, EventSource, ObjectType, ObjectId, Duration, EventCategoryLevel1, EventCategoryLevel2, EventCategoryLevel3, RCALevel1
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---
