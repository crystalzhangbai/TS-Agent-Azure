# Hardware Investigation

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Hardware Investigation** (16 queries across 12 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Cluster Investigation

### FaultDescriptions

_Widget purpose:_ Fault Descriptions

Cluster: `Azuredcm` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Hardware Investigation > Cluster Investigation > Fault Descriptions`

```kusto
ResourceSnapshotHistoryV1
| where Tenant == queryCluster and LifecycleState != "Production" and FaultDescription != "<null>" 
| summarize max(FaultDescription) by ResourceId
```

**Params:** `{queryCluster}`

---

### NumbHostsCluster

_Widget purpose:_ Number of Hosts in Cluster

Cluster: `Azuredcm` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Hardware Investigation > Cluster Investigation > Number of Hosts in Cluster`

```kusto
ResourceSnapshotV1
| where Tenant == queryCluster
| distinct ResourceId
| summarize dcount(ResourceId)
| project-rename NumberOfHostInCluster=dcount_ResourceId
```

**Params:** `{queryCluster}`

---

### NumbHostsClusterNotProd

_Widget purpose:_ Number of Hosts in Cluster not in Production

Cluster: `Azuredcm` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Hardware Investigation > Cluster Investigation > Number of Hosts in Cluster not in Production`

```kusto
ResourceSnapshotHistoryV1
| where Tenant == queryCluster and LifecycleState != "Production" and FaultDescription != "<null>"
| distinct ResourceId, Tenant
| summarize dcount(ResourceId)
| project-rename NumberOfHostInClusterNotInProduction=dcount_ResourceId
```

**Params:** `{queryCluster}`

---

## DCM HW Events

### DCM HW Events DS

_Widget purpose:_ DCM HW Events

Cluster: `azuredcm.kusto.windows.net` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Hardware Investigation > DCM HW Events > DCM HW Events`

```kusto
ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(query_BeginTime .. query_EndTime)
| where ResourceId == query_NodeId
| project PreciseTimeStamp, ResourceId, OSType, LifecycleState, PfState, PfRepairState, HealthGrade, HealthSummary, FaultCode, FaultDescription
| order by PreciseTimeStamp asc
| where LifecycleState != prev(LifecycleState) 
    or PfState != prev(PfState) 
    or PfRepairState != prev(PfRepairState)
    or OSType != prev(OSType) 
    or FaultCode != prev(FaultCode)
    or FaultDescription != prev(FaultDescription)
    or HealthGrade != prev(HealthGrade)
    or HealthSummary != prev(HealthSummary)
| extend level = case(PfState in ("D", "C", "F"), "error", 
    PfRepairState <> "None" or FaultCode <> 0 or isnull(FaultDescription) or PfState <> "H", "warning",
    "info")
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## DCM Repair Events 1

### HW Repair Events DS

_Widget purpose:_ DCM Repair Events 1

Cluster: `azuredcm.kusto.windows.net` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Hardware Investigation > DCM Repair Events 1 > DCM Repair Events 1`

```kusto
ResourceSnapshotHistoryV2
| where ResourceId == query_NodeId and RepairCode != "<null>" and PreciseTimeStamp >= query_StartTime
| project PreciseTimeStamp, PowerCycleTime , UnexpectedRebootTime , RepairCode , RepairResolutionDetails , RepairRequireHardwareDiscovery
```

**Params:** `{query_NodeId}`, `{query_StartTime}`

---

## DCM Repair Events 2

### ResourceSnapshotHistoryV1_Unfiltered DS

_Widget purpose:_ DCM Repair Events 2

Cluster: `Azuredcm` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Hardware Investigation > DCM Repair Events 2 > DCM Repair Events 2`

```kusto
ResourceSnapshotHistoryV1
| where ResourceId == query_NodeId 
| where PreciseTimeStamp >= query_StartTime
| project  PreciseTimeStamp, LifecycleState, NeedFlags, FaultCode, FaultDescription, Tenant, ResourceId
```

**Params:** `{query_StartTime}`, `{query_NodeId}`

---

## HW Memory Errors

### BladeMemoryCorrectedFull

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `Table`
Source panel: `Hardware Investigation > HW Memory Errors`

```kusto
BladeMemoryCorrectedFull()
| where ObjectId == query_NodeId
| where TimeWindowStart >= query_BeginTime and TimeWindowEnd <= query_EndTime
| project EventTime, ObjectId, FailureOccurrence, FailureReason
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## NVME HW Troubleshooting

### NVMEHWissues

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Hardware Investigation > NVME HW Troubleshooting > NVME controller failures due HW issues`

```kusto
let fn_startTime = queryFrom - 2d;
let fn_endTime = queryTo + 2d;
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp >= fn_startTime and PreciseTimeStamp <= fn_endTime
| where NodeId =~ queryNodeId
| where EventId in (6002,6003)
| join kind=inner 
(cluster('sparkle.eastus.kusto.windows.net').database('defaultdb').Partner_NVMeHealthLog
| where PreciseTimeStamp between (fn_startTime .. fn_endTime)
| where MediaErrors > 0 ) on $left.NodeId == $right.NodeId
| distinct TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description, PreciseTimeStamp, Serial, MediaErrors
| take 10
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### NVMEDevRCA

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `Table`
Source panel: `Hardware Investigation > NVME HW Troubleshooting > NVME DevRCA`

```kusto
let fn_startTime = queryFrom - 2d;
let fn_endTime = queryTo + 2d;
Partner_E523_DevRCA
| where EventTime  between (fn_startTime .. fn_endTime)
| where NodeId == queryNodeId
| project EventTime,NodeId,SCTDescription, SCDescription, DriveSerialNumber, ErrorType, EventDefinition, EventData
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### NVMeHealthLog

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `Table`
Source panel: `Hardware Investigation > NVME HW Troubleshooting > NVMeHealthLog`

```kusto
let fn_startTime = queryFrom - 2d;
let fn_endTime = queryTo + 2d;
Partner_NVMeHealthLog
| where PreciseTimeStamp between (fn_startTime .. fn_endTime)
| where NodeId == querynodeId  
| project PreciseTimeStamp, NodeId, Serial, MediaErrors
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querynodeId}`

---

## RhwChassisSelItemEtwTable

### RhwChassisSelItemEtwTable DS

_Widget purpose:_ RhwChassisSelItemEtwTable

Cluster: `azuredcm.kusto.windows.net` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Hardware Investigation > RhwChassisSelItemEtwTable > RhwChassisSelItemEtwTable`

```kusto
RhwChassisSelItemEtwTable
| where BmcSelItemTimeStamp between(query_BeginTime .. query_EndTime)
| where ResourceId == query_NodeId
| where BmcSelItemSensorName <> "BMC Health"
| distinct BmcSelItemTimeStamp, Cluster, BmcSelItemId, BmcSelItemSeverity, BmcSelItemSource, BmcSelItemEventType, BmcSelItemSensorName, BmcSelItemDetails, BmcSelItemRawHex
| order by BmcSelItemTimeStamp asc
| extend level = case (BmcSelItemSeverity == "CRT", "critical", "info")
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

**Signal filters seen in KQL:** `BmcSelItemSensorName <> "BMC Health"`

---

## SEL

### SparkleSEL DS

_Widget purpose:_ SEL logs

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `Table`
Source panel: `Hardware Investigation > SEL > SEL logs`

```kusto
SparkleSELByNodeId(nodeId=query_NodeId)
| where BMCSelTimestamp >= query_BeginTime and BMCSelTimestamp <= query_EndTime
| project-reorder  BMCSelTimestamp, PreciseTimeStamp,EventDataDetails1
| summarize DuplicateCount=count(), tostring(make_set(SelSource)), tostring(make_set(EventDataDetails1)) by BMCSelTimestamp, RawHex
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## SEL filtered

### SEL filtered DS

_Widget purpose:_ SEL filtered

Cluster: `sparkle.eastus` · Database: `defaultdb` · Type: `Table`
Source panel: `Hardware Investigation > SEL filtered > SEL filtered`

```kusto
SparkleSELByNodeId(query_NodeId)
| where BMCSelTimestamp between (query_BeginTime .. query_EndTime)
| extend KnownError = case(
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. .. 04 28 fd 6f a3 06 ff$", "Possible BMC Reset",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. .. 04 07 .. 6f 00 ff ff$", "IERR – Intel",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. .. 04 07 .. 6f 00 .. ..$", "IERR – Intel/AMD",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. .. 04 dc 17 75 a0 0d ..$", "ME FW Health - PECI over DMI Error", 
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. .. 04 0c .. 6f .1 01 ..$", "Correctable ECC Error Limit Reached",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. 00 04 07 9d .. ab .. ..$", "QPI Uncorrectable Error",
    RawHex matches regex @"^.. .. 02 .. .. .. .. 01 00 04 13 a1 6f a7 .. ..$", "PCI correctable",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .1 00 04 13 a1 6f a8 .. ..$", "PCI uncorrectable",
    RawHex matches regex @"^.. .. 02 .. .. .. .. 01 00 04 13 a1 6f aa .. ..$", "PCI fatal",
    RawHex matches regex @"^.. .. 02 .. .. .. .. 01 00 04 13 a1 6f ac .. ..$", "PCI Logging Limit",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. 00 04 02 2a .. .. .. ..$", "Temperature / Voltage Issue",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. 00 04 0f 00 6f c2 .. ff$", "Normal Initialization Stage",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. 00 04 10 8a 6f 05 ff ..$", "SEL Almost Full",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. .. 04 23 .. .. .. .1 ff$", "BIOS FRB2",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. .. 04 23 .. .. .. .2 ff$", "BIOS/POST",
    RawHex matches regex @"^.. .. 02 .. .. .. .. .. .. 04 23 .. .. .. .4 ff$", "SMS/OS",
    RawHex matches regex @"^.. .. de .. .. .. .. 37 01 00 01 .. .. .. .. 01$", "Bugcheck",
    EventDetail contains "Correctable ECC", "Correctable ECC",
    EventDetail contains "ThermProtection", "ThermProtection",
    EventDetail contains "DCMI_Watchdog", "DCMI_Watchdog",
    EventDetail contains "CATERROR", "CATERROR",
    'Other')
| project Timestamp = BMCSelTimestamp,
          Source = GeneratorId,
          EventType,
          Sensor = SensorType,
          Details = EventDataDetails1,
          RawHex,
          KnownError
| sort by Timestamp
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## WHEA

### Whea DS

_Widget purpose:_ WHEA

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `Table`
Source panel: `Hardware Investigation > WHEA > WHEA`

```kusto
WheaXPFMCAFull
| where NodeId =~ query_NodeId
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| project TIMESTAMP, ProviderName,ErrorRecordSeverity,PhysicalAddress,Status,RetryReadData
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## WindowsEventsHW

### WindowsEventsFilteredHW DS

_Widget purpose:_ WindowsEventsHW

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Hardware Investigation > WindowsEventsHW > WindowsEventsHW`

```kusto
WindowsEventTable
| where PreciseTimeStamp between(query_BeginTime .. query_EndTime)
| where NodeId == query_NodeId
| where not (ProviderName == "NETLOGON" and  EventId == 3095)
| where not (ProviderName == 'IPMIDRV' and EventId == 1004)
| where ProviderName <> "CMClientLib"
| where EventId <> 7000
| where EventId <> 1023
| where EventId !in (505, 504, 146, 145, 142)
//| where Description !contains "RDMA Session Init Failed."
| where ProviderName contains "Microsoft-Windows-WHEA-Logger" or 
        ProviderName contains "PnP" or 
        (ProviderName contains "Microsoft-Windows-Hyper-V" and Description contains "memory") or
        ProviderName contains "Wdf"
| project PreciseTimeStamp, TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
// | extend StartTime = PreciseTimeStamp, EndTime = PreciseTimeStamp + 1m, Content = EventId, GroupBy = strcat(ProviderName, " - ", EventId)
| order by TimeCreated asc 
// | order by GroupBy asc
| extend level = case(Level == 1, "critical", Level == 2, "error", Level == 3, "warning", "info")
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

**Signal filters seen in KQL:** `ProviderName <> "CMClientLib"` · `ProviderName contains "Microsoft-Windows-WHEA-Logger"`

---

## WindowsStorageEvents

### WindowsStorageEvents

Cluster: `sparkle.eastus` · Database: `defaultdb` · Type: `Table`
Source panel: `Hardware Investigation > WindowsStorageEvents`

```kusto
WindowsStorageEventsByNodeId(queryNodeId, queryFrom, queryTo)
| extend Level = case(EventId in (7,11,129,500),1, ProviderName == "Microsoft-Windows-StorPort" and EventId == 505 and Description !has "The IO failed counts are 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0", 2, 5)
| project PreciseTimeStamp, ProviderName, EventId, Description, EventData, Level, NodeId, Cluster
| where Level in (1,2)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---
