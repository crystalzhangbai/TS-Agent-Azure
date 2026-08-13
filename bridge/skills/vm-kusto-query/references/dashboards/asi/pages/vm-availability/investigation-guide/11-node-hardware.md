# Node (Hardware)

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Node (Hardware)** (11 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Node (Hardware)

### HardwareEvent

_Widget purpose:_ BMC/SEL Hardware Event - RhwChassisSelItemEtwTable

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > BMC/SEL Hardware Event - RhwChassisSelItemEtwTable`

```kusto
//cluster('sparkle.eastus.kusto.windows.net').database("defaultdb").RhwSelandSpklSelbyNodeId(
//    startTime=starttime, 
//    endTime=endtime, 
//    nodeId=nodeid)
//| where BmcSelTimeStamp between (starttime..endtime)
//| where RecordType !contains "OEM"
//| where BmcSelMessage <> ""
//| distinct  BmcSelTimeStamp, ClusterName, RecordId, RecordType, BmcSelMessage, SensorId, SensorType, EventData1, EventData2, EventData3, EventDataDetails1, EventDataDetails2, EventDataDetails3
//| order by BmcSelTimeStamp asc

cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').RhwChassisSelItemEtwTable
| where BmcSelItemTimeStamp between(starttime .. endtime)
| where ResourceId == nodeid
| where BmcSelItemSensorName <> "BMC Health"
| distinct BmcSelItemTimeStamp, Cluster, BmcSelItemId, BmcSelItemSeverity, BmcSelItemSource, BmcSelItemEventType, BmcSelItemSensorName, BmcSelItemDetails, BmcSelItemRawHex
| order by BmcSelItemTimeStamp asc
| extend level = case (BmcSelItemSeverity == "CRT", "critical", "info")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `BmcSelItemSensorName <> "BMC Health"`

---

### SparkleSELByNodeId

_Widget purpose:_ BMC/SEL Hardware Event - SparkleSELByNodeId

Cluster: `sparkle.eastus` · Database: `defaultdb` · Type: `Table`
Source panel: `Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > BMC/SEL Hardware Event - SparkleSELByNodeId`

```kusto
cluster("sparkle.eastus").database("defaultdb").SparkleSELByNodeId(nodeId=queryNodeId, queryFrom, queryTo)
| where BMCSelTimestamp between(queryFrom .. queryTo)
| where isnotempty( DataCenter )
| distinct BMCSelTimestamp, Cluster, RecordId, RecordType, BMCSelItemMessage, SensorId, SensorType, EventData1, EventData2, EventData3, EventDataDetails1, EventDataDetails2, EventDataDetails3
| order by BMCSelTimestamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Hardware Resource Event

_Widget purpose:_ DCM Hardware Resource Event - ResourceSnapshotHistoryV1

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > DCM Hardware Resource Event - ResourceSnapshotHistoryV1`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(starttime .. endtime)
| where ResourceId == nodeid
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

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### DCM Node State

_Widget purpose:_ DCM Health Timeline

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`
Source panel: `Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > DCM Health Timeline`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(starttime .. endtime)
| where ResourceId == nodeid
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, ResourceId, LifecycleState, PfState, PfRepairState, HealthSummary, FaultCode, FaultDescription
| extend flag = case(prev(LifecycleState) <> LifecycleState, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp), endtime)
| extend Content = LifecycleState
| extend Health = case (LifecycleState == "Production", "Healthy", 
    LifecycleState contains "OutForRepair", "Unhealthy", 
    "Degraded")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### PilotFish State

_Widget purpose:_ DCM Health Timeline

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`
Source panel: `Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > DCM Health Timeline`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(starttime .. endtime)
| where ResourceId == nodeid
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, Tenant, ResourceId, LifecycleState, PfState, PfRepairState, HealthSummary, FaultCode, FaultDescription
| extend flag = case (prev(PfState) <> PfState, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp), endtime)
| extend Content = strcat (PfState, " ", PfRepairState)
| extend Health = case (PfState == "H", "Healthy", 
    PfState in ("D", "C", "F"), "Unhealthy",
    "Degraded")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Windows Event Log for Hardware

_Widget purpose:_ Hardware / Driver Event Log Timeline

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Node (Hardware) > Node (Hardware) > Hardware Event Log > Hardware Event Log > Hardware / Driver Event Log Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
| where ProviderName contains "Microsoft-Windows-WHEA-Logger" or 
        ProviderName contains "PnP" or 
        (ProviderName contains "Microsoft-Windows-Hyper-V" and Description contains "memory") or
        ProviderName contains "Wdf"
| project PreciseTimeStamp, TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| extend StartTime = PreciseTimeStamp, EndTime = PreciseTimeStamp + 1m, Content = EventId, GroupBy = strcat(ProviderName, " - ", EventId)
| order by TimeCreated asc , GroupBy asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ProviderName contains "Microsoft-Windows-WHEA-Logger"`

---

### Windows Event Log for Hardware

_Widget purpose:_ Hardware Events from WindowsEventTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Node (Hardware) > Node (Hardware) > Hardware Event Log > Hardware Event Log > Hardware Events from WindowsEventTable`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
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

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ProviderName <> "CMClientLib"` · `ProviderName contains "Microsoft-Windows-WHEA-Logger"`

---

### Query CPU from dcmInventoryComponentCPUV2Direct

_Widget purpose:_ CPU

Cluster: `AzureDCM` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Node (Hardware) > Node (Hardware) > Hardware Spec > CPU`

```kusto
dcmInventoryComponentCPUV2Direct
| where DataCollectedOn between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| summarize arg_max(DataCollectedOn, *) by ProcessorId, DeviceID
| order by DataCollectedOn asc, DeviceID asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query dcmInventoryComponentDiskHistory

_Widget purpose:_ HDD/SDD/NVME  from dcmInventoryComponentDiskHistory 

Cluster: `Azuredcm` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Node (Hardware) > Node (Hardware) > Hardware Spec > HDD/SDD/NVME  from dcmInventoryComponentDiskHistory `

```kusto
dcmInventoryComponentDiskHistory
| where DataCollectedOn  between(startofday(queryFrom) ..endofday(queryTo))
| where NodeId == queryNodeId
| extend SizeInGB = tolong(Size/1024/1024/1024)
| summarize arg_max(DataCollectedOn, *) by DriveSerialNumber, OSDiskNumber, FirmwareRevision
| order by DataCollectedOn asc, OSDiskNumber asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query dcmInventoryComponentDiskUtilDirect

_Widget purpose:_ HDD/SDD/Virtual Disk/NVME Direct Drives from dcmInventoryComponentDiskUtilDirect 

Cluster: `Azuredcm` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Node (Hardware) > Node (Hardware) > Hardware Spec > HDD/SDD/Virtual Disk/NVME Direct Drives from dcmInventoryComponentDiskUtilDirect `

```kusto
dcmInventoryComponentDiskUtilDirect
| where DataCollectedOn  between(startofday(queryFrom) ..endofday(queryTo))
| where NodeId == queryNodeId
| extend SizeInGB = tolong(Size/1024/1024/1024)
| summarize arg_max(DataCollectedOn, *) by AdapterSerial, FirmwareRevision, DeviceNumber, Location, Path
| order by DataCollectedOn asc, DeviceNumber asc, BusType asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query DIMM from dcmInventoryComponentDIMMDirect

_Widget purpose:_ Memory / DIMM

Cluster: `Azuredcm` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Node (Hardware) > Node (Hardware) > Hardware Spec > Memory / DIMM`

```kusto
dcmInventoryComponentDIMMDirect 
| where DataCollectedOn between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| extend Wmi_Tag = trim(" ", Wmi_Tag)
| extend Wmi_SerialNumber = trim(" ", Wmi_SerialNumber)
| summarize arg_max(DataCollectedOn, *) by Wmi_Tag, Wmi_SerialNumber, Wmi_DeviceLocator
| order by DataCollectedOn asc, Wmi_DeviceLocator asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---
