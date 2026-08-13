# Host Tables

> Source: **Azure Host — Azure Host Node** dashboard, chapter **Host Tables** (29 queries across 13 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ASC HA Runs

### Azure Host ASC HA Runs

_Widget purpose:_ HostAnalyzer Runs from ASC for Host {{nodeId}}

Cluster: `Azds` · Database: `adsmds` · Type: `Table`
Source panel: `Host Tables > ASC HA Runs > ASC HA Runs > HostAnalyzer Runs from ASC for Host {{nodeId}}`

```kusto
TraceEvent
| where Output contains 'HostAnalyzer.ps1' and Output contains 'Start to run HA report for '
            and env_cloud_environment == 'Prod'
            and env_time between ((startTime - 6h) .. (endTime + 6h)) 
| parse Output with * '-cluster \'' Cluster '\' -nodeId \'' NodeId '\' -containerId \'' ContainerId '\' -startTime \'' StartTime '\' -endTime \'' EndTime '\' -ExecutedFromGetSub -resourceId \'' ResourceId '\'' *
| distinct StartTime, EndTime, Cluster, NodeId, ContainerId, ResourceId, RequestId
| where NodeId == '$($nodeId)'
| join kind=inner(
    TraceEvent
    | where env_time between ((startTime - 6h) .. (endTime + 6h)) and Output contains 'successfully upload'
    | parse Output with * ' to ' ReportUrl
    | extend ReportUrl = substring(ReportUrl, 0, strlen(ReportUrl)-1)
    | distinct RequestId, ReportUrl
) on RequestId
| project-away RequestId1
| sort by StartTime desc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `Output contains "HostAnalyzer.ps1"` · `NodeId == "$($nodeId)"`

---

## Azure Profiler

### Azure Profiler Traces with Hottest Callstacks

Cluster: `azureprofilerfollower.westus2.kusto.windows.net` · Database: `azureprofiler` · Type: `Table`
Source panel: `Host Tables > Azure Profiler > Azure Profiler > Hottest Callstacks`

```kusto
Identifiers
| where TraceStartTime between ((startTime) .. (endTime)) and NodeId == nodeId
| project Timestamp, TraceStartTime, NodeId, Cluster, PublishBlob, ViewerUrl, ActiveCPU, Fuse
| join kind = inner (
    TraceInsights
    | where Timestamp between ((startTime - 3h) .. (endTime + 3h)) and Name == "Top Processes by Active CPU"
    | extend TopProcess=tostring(SupportingData.TopActiveProcesses.Processes[0].Name), TopProcessCPU = todecimal(SupportingData.TopActiveProcesses.Processes[0].CPUPercentage)
) on PublishBlob
| join kind = inner (
    TraceInsights
    | where Timestamp between ((startTime - 3h) .. (endTime + 3h)) and Name == "Hot Function"
    | extend HotFunction=tostring(SupportingData.HotFunction.Function), HotFunctionExclusiveCPU = todecimal(SupportingData.HotFunction.ExclusiveCPUUsagePercentage), TopProcess=substring(Scope,8)
) on PublishBlob, TopProcess
    | join kind = inner (
    TraceInsights
    | where Timestamp between ((startTime - 3h) .. (endTime + 3h)) and Name == "Hot Callstack Path"
    | extend HotCallstack=tostring(SupportingData.HotCallstackPath.Callstack), HotCallstackExclusiveCPU = todecimal(SupportingData.HotCallstackPath.ExclusiveCPUUsagePercentage), TopProcess = substring(Scope,8)
) on PublishBlob, TopProcess
| project TraceStartTime, Fuse, ActiveCPU, TopProcess, TopProcessCPU, HotFunction, HotFunctionExclusiveCPU, HotCallstack, HotCallstackExclusiveCPU, ViewerUrl, PublishBlob
| sort by TraceStartTime asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Profiler

_Widget purpose:_ Azure Profiler Traces with Hot Functions

Cluster: `https://azureprofilerfollower.westus2.kusto.windows.net` · Database: `azureprofiler` · Type: `Table`
Source panel: `Host Tables > Azure Profiler > Azure Profiler > Hottest Functions > Azure Profiler Traces with Hot Functions`

```kusto
//Old Query
//HostProcessData
//| where TraceCollectionTimestamp between ((startTime - 1h) .. (endTime + 1h)) and StackRank == 1
//    and NodeId contains nodeId
//| project TraceStartTime, FuseName, HottestFunction, HottestCallstackProcessingTime, ViewerUrl
//| sort by TraceStartTime asc nulls last
//New Query
cluster('azureprofilerfollower').database('azureprofiler').Identifiers
| where TraceStartTime between ((startTime) .. (endTime)) and NodeId == nodeId
| project Timestamp, TraceStartTime, NodeId, Cluster, PublishBlob, ViewerUrl, ActiveCPU, Fuse
| join kind = inner (
    cluster('azureprofilerfollower').database('azureprofiler').TraceInsights
    | where Timestamp between ((startTime - 3h) .. (endTime + 3h)) and Name == "Top Processes by Active CPU"
    | extend TopProcess=tostring(SupportingData.TopActiveProcesses.Processes[0].Name), TopProcessCPU=todecimal(SupportingData.TopActiveProcesses.Processes[0].CPUPercentage)
) on PublishBlob
| join kind = inner (
    cluster('azureprofilerfollower').database('azureprofiler').TraceInsights
    | where Timestamp between ((startTime - 3h) .. (endTime + 3h)) and Name == "Hot Function"
    | extend HotFunction = tostring(SupportingData.HotFunction.Function), TopProcess = substring(Scope,8)
) on PublishBlob, TopProcess
| project TraceStartTime, Fuse, HotFunction, ViewerUrl
| sort by TraceStartTime asc nulls last
| sort by TraceStartTime asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Azure Watson

### Azure Host Watson Dumps

_Widget purpose:_ Azure Watson Dumps for {{nodeId}}

Cluster: `Azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `Table`
Source panel: `Host Tables > Azure Watson > Azure Watson > Azure Watson Dumps for {{nodeId}}`

```kusto
CustomerCrashOccurredV2
| where PreciseTimeStamp between ((startTime - 2d) .. (endTime + 2d))
| where nodeIdentity == nodeId
| project crashMode, crashProcessFullPath, process, dumpUid, nodeIdentity
| join kind=leftouter(
    CustomerDumpAnalysisResultV2 | where PreciseTimeStamp between ((startTime - 2d) .. (endTime + 2d))
) on dumpUid
| distinct crashTime, crashMode, bucketString, followup, faultingModule, faultingModuleVersion, bugLink,  dumpUid
| where todatetime(crashTime) between ((startTime - 2h) .. (endTime + 2h))
| sort by crashTime asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Hardware

### Azure Host SEL Logs

_Widget purpose:_ SEL Logs

Cluster: `sparkle.eastus` · Database: `defaultdb` · Type: `Table`
Source panel: `Host Tables > Hardware > Hardware > SEL Logs > SEL Logs > SEL Logs`

```kusto
cluster('sparkle.eastus').database('defaultdb').SparkleSELByNodeId(nodeId)
| where BMCSelTimestamp between (startTime .. endTime)
| summarize arg_min(RecordId, *) by RawHex
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
          RecordId,
          RecordType,
          RawHex,
          KnownError
| sort by Timestamp
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## HealthStore

### Azure Host Node HealthStore Regressed Signals

_Widget purpose:_ HealthStore Regressed Signals which stopped the deployment

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `sharedworkspace` · Type: `Table`
Source panel: `Host Tables > HealthStore > HealthStore Regressed Signals which stopped the deployment`

```kusto
RegressedHealthStoreDeployments(nodeId, queryFrom, queryTo)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Node HealthStore UnderThreshold Signals

_Widget purpose:_ HealthStore Underthreshold Signals

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `sharedworkspace` · Type: `Table`
Source panel: `Host Tables > HealthStore > HealthStore Underthreshold Signals`

```kusto
UnderThresholdHealthStoreDeployments(nodeId, queryFrom, queryTo)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

## Host Disk Storage

### HostStorage DCM Inventory

Cluster: `Azuredcm.kusto.windows.net` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Host Tables > Host Disk Storage > Disk Storage > Disk Inventory > Disk Inventory > HostStorage DCM Inventory`

```kusto
let Node = nodeId;
cluster("Azuredcm").database("AzureDCMDb").dcmInventoryComponentDisk
| where NodeId == Node
| where IsPhysical == 1 // Only Physical drives
| join kind = leftouter
cluster("Azuredcm").database("AzureDCMDb").dcmInventoryComponentDiskUtil
on $left.NodeId == $right.NodeId,
   $left.DriveSerialNumber == $right.Serial
| project DataCollectedOn,
          DriveProductId,
          DriveSerialNumber,
          AdapterSerial,
          DriveBusType,
          BusType,
          Location,
          DeviceGuid,
          Size,
          FirmwareRevision,
          OSDevicePath,
          OSDiskNumber,
          DriveMountPoints,
          Port = toint(SCSIPort),
          Path = toint(SCSIBus),
          Target = toint(SCSIAddress),
          Lun = toint(SCSILUN),
          BandCapabilities
```

**Params:** `{nodeId}`

---

### HostStorage Disk IO Errors - WindowsStorageEvents

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > Host Disk Storage > Disk Storage > Disk IO Errors > Disk IO Errors`

```kusto
let Node = nodeId;
let StartTime = startTime;
let EndTime = endTime;
WindowsStorageEvents
| where PreciseTimeStamp between (StartTime..EndTime)
| where NodeId == Node
| where ProviderName == "Microsoft-Windows-StorPort"
| where EventId == 549 and Version == 1
| where Lun == 0 and Target == 0 // Only Physical drives
| extend EventData = split(EventData, "!!")
| extend RequestDuration_ms = toint(EventData[13])
| extend WaitDuration_ms = toint(EventData[14])
| extend OpCode = toint(EventData[15])
| extend SrbStatus = toint(EventData[16])
| extend SenseKey = tohex(toint(EventData[18]))
| extend AddSense = tohex(toint(EventData[19]))
| extend AddSenseQ = tohex(toint(EventData[20]))
// Scope to Opcodes that are interesting
| where OpCode in ( 40, // SCSIOP_READ
                   136, // SCSIOP_READ16
                    42, // SCSIOP_WRITE
                   138, // SCSIOP_WRITE16
                   160, // SCSIOP_REPORT_LUNS
                    37, // SCSIOP_READ_CAPACITY
                   158, // SCSIOP_READ_CAPACITY16
                    18, // SCSIOP_INQUIRY
                    53) // SCSIOP_SYNCHRONIZE_CACHE
// Ignore SrbStatuses that are not interesting
| where SrbStatus !in (1, // SRB_STATUS_SUCCESS
                       5, // SRB_STATUS_BUSY
                       6) // SRB_STATUS_INVALID_REQUEST
| project PreciseTimeStamp, DeviceGuid, tohex(OpCode), SrbStatus, SenseKey, AddSense, AddSenseQ
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `ProviderName == "Microsoft-Windows-StorPort"`

---

### HostStorage Disk IO Timeouts - WindowsStorageEvents

_Widget purpose:_ Disk IO Timeouts - WindowsStorageEvents

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > Host Disk Storage > Disk Storage > Disk IO Timeouts > Disk IO Timeouts > Disk IO Timeouts - WindowsStorageEvents`

```kusto
let Node = nodeId;
let StartTime = startTime;
let EndTime = endTime;
let ExtractBlob = (Data: string, Offset: int, Bytes: int) {
    substring(Data, Offset * 2, Bytes * 2)
};
let GetValue1Byte = (Data: string, Offset: int) {
    let Blob = ExtractBlob(Data, Offset, 1);
    tolong(strcat("0x", Blob))
};
WindowsStorageEvents
| where PreciseTimeStamp between (StartTime..EndTime)
| where NodeId == Node
| where ProviderName == "Microsoft-Windows-StorPort"
| where EventId == 500 and Version == 3
| where Lun == 0 and Target == 0 // Only Physical drives
| extend EventData = split(EventData, "!!")
| extend Cdb = tostring(EventData[12])
| extend OpCode = tohex(GetValue1Byte(Cdb, 0))
| project PreciseTimeStamp, DeviceGuid, OpCode
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `ProviderName == "Microsoft-Windows-StorPort"`

---

## Host Networking

### NDIS DMA Allocation Summary

_Widget purpose:_ NDIS DMA Allocations

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > Host Networking > Host Networking > NDIS DMA Allocations > NDIS DMA Allocations > NDIS DMA Allocations`

```kusto
let ['_startTime']=startTime;
let ['_endTime']=endTime;
let ['_nodeId']=nodeId;
let callState = dynamic({"0" : "NotCalled", "1" : "Success", "2" : "Failure" });
let parse_call_state = (state: int, mask : int, shift : int)
{
    tostring(callState[tostring(binary_shift_right(binary_and(state, mask), shift))])
};
let parse_status_bit = (state : int, bit : int)
{
    iff(binary_and(state, bit) == bit, "Yes", "No");
};
let get_source = (state : int)
{
    iff (
        binary_shift_right(binary_and(state, 0xc), 2) == 0x1 and binary_shift_right(binary_and(state, 0x30), 4) == 0x1,
        "MM",
        "HAL")
};
cluster('azcore.centralus.kusto.windows.net').database('Fa').CloudNetworkingTriageTable
//cluster('azcore.centralus.kusto.windows.net').database('Fa').CloudNetworkingTriageTable
| where PreciseTimeStamp between ((['_startTime'] - 30minutes)..(_endTime + 30minutes)) // Time range filtering
| where NodeId == ['_nodeId']
| where TaskName == "NdisAllocateSharedMemory_Aggregate"
| parse Message with *
    "Count=\"" Count:int "\" " *
    "MinTimestamp=\"" MinTimestamp:datetime "\" " *
    "MaxTimestamp=\"" MaxTimestamp:datetime "\" " *
    "MaxAllocationTime_us=\"" MaxAllocationTime_us:int "\" " *
    "State=\"" State:int "\""
| where MinTimestamp between (_startTime .. _endTime) or MaxTimestamp between (_startTime .. _endTime)
| extend
    MaxAllocationTime = MaxAllocationTime_us * 1microsecond,
    Source = get_source(State),
    HybridDma = parse_status_bit(State, 0x800000),
    CompatMode = parse_status_bit(State, 0x400000),
    CallResult = parse_call_state(State, 3, 0)
| summarize FirstAllocationTimestamp = min(MinTimestamp), LastAllocationTimestamp = max(MaxTimestamp), MaxAllocationTime = max(MaxAllocationTime), Count = sum(Count) by Source, CallResult, HybridDma, CompatMode
| project HybridDma, CompatMode, CallResult, Source, FirstAllocationTimestamp, LastAllocationTimestamp, MaxAllocationTime, Count
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `TaskName == "NdisAllocateSharedMemory_Aggregate"`

---

### Azure Host Network Port Quota

_Widget purpose:_ Port Quota

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > Host Networking > Host Networking > Network Port Quota > Network Port Quota > Port Quota`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').CloudNetworkingTriageTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where TaskName in ('PortQuotaPolicyConfig', 'PortQuotaModeOfOperation')
| summarize arg_max(PreciseTimeStamp, *) by NodeId, TaskName
| parse Message with Key '="' Value '"'
| extend Value = iff(TaskName == 'PortQuotaPolicyConfig',
                     strcat(Value, ' %'),
                     Value)
| extend Value = iff(TaskName == 'PortQuotaModeOfOperation',
                     case(Value == '0', '0 (Enforcement)',
                          Value == '1', '1 (Monitoring)',
                          Value),
                     Value)
| extend Config = replace('_', ' ', Key)
| project PreciseTimeStamp, Config, Value
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## IcMs for Host

### Azure Host IcMs

_Widget purpose:_ IcMs for {{nodeId}}

Cluster: `icmcluster` · Database: `IcmDataWarehouse` · Type: `Table`
Source panel: `Host Tables > IcMs for Host > IcMs for Host > IcMs for {{nodeId}}`

```kusto
let incidentCustomFields = IncidentCustomFieldEntries | where ModifiedDate between ((startTime - 1d) .. (endTime + 1d)) | where Value contains nodeId | distinct IncidentId;
//Incidents
//| where (CreateDate between ((startTime - 1d) .. (endTime + 1d)) and * contains nodeId) or (IncidentId in (incidentCustomFields))
//| summarize arg_max(ModifiedDate, *) by IncidentId
//| distinct CreateDate, ModifiedDate, IncidentId, Status, Title, OwningTeamName
//| extend IncidentLink = strcat('https://portal.microsofticm.com/imp/v3/incidents/details/', IncidentId, '/home')
let incidents = IncidentDescriptions
| where * contains nodeId and Lens_IngestionTime between ((startTime - 3d) .. (endTime + 3d))
| distinct IncidentId;
Incidents
| where Lens_IngestionTime between ((startTime - 30d) .. (endTime + 7d)) and (IncidentId in (incidents) or IncidentId in (incidentCustomFields))
| summarize arg_max(Lens_IngestionTime, *) by IncidentId
| distinct CreateDate, IncidentId, Status, Title, OwningTeamName
| extend IncidentLink = strcat('https://portal.microsofticm.com/imp/v3/incidents/details/', IncidentId, '/home')
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## LiveMigration

### Azure Host Node LiveMigration Completions

_Widget purpose:_ LiveMigration Events

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Host Tables > LiveMigration > LiveMigration Events`

```kusto
cluster('AzureCM').database('AzureCM').LiveMigrationSessionCompleteLog
| where PreciseTimeStamp between (queryFrom .. queryTo) and (destinationNodeId == nodeIdStr or sourceNodeId == nodeIdStr)
| project PreciseTimeStamp, triggerType, status, elapsedTime, sourceNodeId, sourceContainerId, destinationNodeId, destinationContainerId, reason, message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeIdStr}`

---

## OSHP

### Azure Host Fast Restore Events

_Widget purpose:_ Fast Restore Events

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Host Tables > OSHP > OSHP > OSHP FastSave > OSHP FastSave > Fast Restore Events`

```kusto
OsUpdateManagerFastRestoreEvents
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
|  project PreciseTimeStamp = todatetime(StartTime), Operation, VmName, ExecutionId
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host FastSave Events

_Widget purpose:_ Fast Save Events

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Host Tables > OSHP > OSHP > OSHP FastSave > OSHP FastSave > Fast Save Events`

```kusto
OsUpdateManagerFastSaveEvents
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp = todatetime(StartTime), Operation, VmName, ExecutionId
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host OSHP Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > OSHP > OSHP > OSHP Timeline Events > OSHP Timeline Events`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (startTime .. endTime) and ProviderName in ('OSHostPlugin', 'NMAgent') and NodeId == nodeId
| project todatetime(TimeCreated), ProviderName, EventId, Description
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host OSHP Update Logs

_Widget purpose:_ OSHP Update Logs (PF)

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Host Tables > OSHP > OSHP > OSHP Update Logs > OSHP Update Logs > OSHP Update Logs (PF)`

```kusto
OsUpdateManagerEvents
| where PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h)) and NodeId == nodeId
| project StartTime = todatetime(StartTime), ExecutionId, MessageType, TimeTaken, Description
| sort by StartTime asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host OSHP Plugin Update

_Widget purpose:_ OSHP Update Logs (plugin)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > OSHP > OSHP > OSHP Update Logs > OSHP Update Logs > OSHP Update Logs (plugin)`

```kusto
OSUpdateManagerEvents
| where PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h)) and NodeId == nodeId
| project StartTime = todatetime(StartTime), ExecutionId, MessageType, TimeTaken, Description
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### VM-PHU Node Compute Blackout Query

Cluster: `baseplatform.westus` · Database: `vmphu` · Type: `Table`
Source panel: `Host Tables > OSHP > OSHP > VM-PHU Compute Blackout`

```kusto
cluster('baseplatform.westus').database('vmphu').VmphuComputeBlackoutFromTraceProfilerMeasure
| where ComputeBlackoutStartTime between ((startTime - 1d) .. (endTime + 1d)) and NodeId == nodeId
| summarize arg_max(ComputeBlackoutInSec, *) by ExecutionId, NodeId
| project StartTime = ComputeBlackoutStartTime, StopTime = ComputeBlackoutStopTime
    , Message = strcat('Node Compute Blackout is ', round(ComputeBlackoutInSec, 2), 's')
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## OsLoggerTable

### Azure Host OsLoggerTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > OsLoggerTable > OsLoggerTable`

```kusto
OsLoggerTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| extend level = case(LogErrorLevel == "Error", "error", LogErrorLevel == "Warning", "warning", LogErrorLevel == "Critical", "fatal", "info")
| project PreciseTimeStamp = tostring(PreciseTimeStamp), level, ComponentName, SubComponentName, FileName, FunctionName, LineNumber, ResultCode, ErrorDetails 
| sort by PreciseTimeStamp asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## System

### Azure Host Disk Space Table

_Widget purpose:_ Folders using large Disk Space (usage in MB)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > System > System > Disk Space > Disk Space > Folders using large Disk Space (usage in MB)`

```kusto
OsConfigTable
| where PreciseTimeStamp between ((startTime - 1d) .. endTime) and NodeId == nodeId
        and ConfigType == "du"
| project PreciseTimeStamp, ConfigType, Component, ConfigName, ConfigValue, ConfigPath
| summarize arg_max(PreciseTimeStamp, *) by Component, ConfigName, ConfigValue, ConfigPath
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host WindowsEventTable

_Widget purpose:_ WindowsEventTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > System > System > Events > Events > WindowsEventTable`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where EventId !in ('0','3095') 
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project TimeCreated = todatetime(TimeCreated), Id = EventId, ProviderName, Message = Description, level
| sort by TimeCreated asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Azure Host HighCPUTable Chart View

_Widget purpose:_ VPs running hot chart view (30 second averages per VP)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Tables > System > System > HighCPU Table > HighCPU Table > VPs running hot chart view (30 second averages per VP)`

```kusto
HighCpuCounterNodeTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| parse CounterName with "\\Hyper-V Hypervisor Root Virtual Processor(" CounterName ")\\% Total Run Time"
| project PreciseTimeStamp, CounterName, CounterValue
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host HighCPUTable

_Widget purpose:_ VPs running hot tabular view (30 second averages per VP)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > System > System > HighCPU Table > HighCPU Table > VPs running hot tabular view (30 second averages per VP)`

```kusto
HighCpuCounterNodeTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, CounterName, CounterValue
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Poolmon Data for Azure Host Node

_Widget purpose:_ OsPoolmonTable (pushed by OsAnalyzer from poolmon output)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > System > System > Poolmon > Poolmon > OsPoolmonTable (pushed by OsAnalyzer from poolmon output)`

```kusto
OsPoolMonTable
| where PreciseTimeStamp between ((startTime - 12h) .. (endTime + 12h)) and NodeId == nodeId
| summarize arg_max(PreciseTimeStamp, *) by NodeId, Tag, Type
| project PreciseTimeStamp = tostring(PreciseTimeStamp) , Tag, Rank = toint(Rank), Type, Allocs, Frees, Diff, Bytes, PerAlloc 
| sort by Type asc, Rank asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Azure Host OsConfigTable

_Widget purpose:_ OsConfigTable (pushed by OsAnalyzer)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > System > System > Settings > Settings > OsConfigTable (pushed by OsAnalyzer)`

```kusto
OsConfigTable
| where PreciseTimeStamp between ((startTime - 6h) .. endTime) and NodeId == nodeId
        and ConfigType in ("command", "registry")
| project PreciseTimeStamp, ConfigType, Component, ConfigName, ConfigValue, ConfigPath
| summarize arg_max(PreciseTimeStamp, *) by ConfigType, Component, ConfigName, ConfigValue, ConfigPath
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Updates

### Azure Host PF Updates Table

_Widget purpose:_ PF Service Updates

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Host Tables > Updates > Updates > PF Service Updates`

```kusto
ServiceVersionSwitch 
| where NodeId == nodeId and PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h))
| project PreciseTimeStamp, ServiceName, CurrentVersion, NewVersion, SourceOfService
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Azure Host RootHE Updates

_Widget purpose:_ Root HE Component Updates

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Host Tables > Updates > Updates > Root HE Component Updates`

```kusto
TMMgmtNodeEventsEtwTable  
| where TIMESTAMP between (startTime .. endTime) and NodeId =~ nodeId  and (Message contains 'CreatePluginComplete' or Message contains 'UpdatePluginCompleted')
| parse kind = regex Message with * ' = HostPluginName:' Component:string ', HostPluginSetupFile:' * 'HostPluginPackage:'package:string ', Action:'* 
| project PreciseTimeStamp=TIMESTAMP, Component, NewVersion=package, Message
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---
