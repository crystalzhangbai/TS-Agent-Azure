# Hyper-V Tables

> Source: **Azure Host — Azure Host Node** dashboard, chapter **Hyper-V Tables** (9 queries across 6 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Analytic

### Azure Host HyperV Analytic

_Widget purpose:_ HyperVAnalyticEvents

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V Tables > Analytic > Analytic > HyperVAnalyticEvents`

```kusto
HyperVAnalyticEvents
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and Level < 4
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, NodeId, Level, ProviderName, TaskName, EventMessage, Message, level
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## HyperVEvents

### HyperVEventsV2 Host Query

_Widget purpose:_ HyperVEventsV2

Cluster: `azcore.centralus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `Hyper-V Tables > HyperVEvents > HyperVEventsV2`

```kusto
let _containerId = '';
HyperVEventsV2(fn_nodeId=['_nodeId'], fn_containerId=['_containerId'], fn_startTime = ['_startTime'], fn_endTime=['_endTime'])
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

---

## IO Latencies

### Azure Host VM HyperV Latency Query

_Widget purpose:_ Hyper-V IO Latencies seen (10+ second IOs)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V Tables > IO Latencies > Hyper-V IO Latencies seen (10+ second IOs)`

```kusto
HyperVStorageStackTable 
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where Message has_any (containerId) and EventId == 9
| parse EventMessage with * " took " TimeInMs " milliseconds" *
| project PreciseTimeStamp, Level, EventId, TaskName, EventMessage, TimeInMs, Message
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

## Storage Stack

### Azure Host HyperV Storage

_Widget purpose:_ HyperVStorageStackTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V Tables > Storage Stack > Storage Stack > HyperVStorageStackTable > HyperVStorageStackTable > HyperVStorageStackTable`

```kusto
let nodeStorageEvents = materialize(cluster('azcore.centralus').database('Fa').HyperVStorageStackTable 
                        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId);
let failedActivities = nodeStorageEvents | where Level == 2 and TaskName == "ActivityFailure";
let failedActivityIds = failedActivities | distinct ActivityId;
// Filter out known noisy errors that are activity based (search for activity Id here so that the start, failure, and stop events are all
// excluded from the resulting query).
// TSG: https://eng.ms/docs/cloud-ai-platform/azure/aep-platform/core-os/hyper-v-azure/hyper-v-svx/tsg/tsg-benign-errors-azure
// The failure code is on the "ActivityFailure" message but the type of activity is in the TaskName that aren't failed. So do a dance
// to find all of the activities with failures of a certain type and then filter on the code.
// This dance is because the status code isn't in the stop code (Opcode 2). This changes in AH 2021 ...
let flushActivities = nodeStorageEvents | where TaskName == "FileWrapperFlushBuffers" | distinct ActivityId;
let cancelledFlushActivityIds = failedActivities | where ActivityId in (flushActivities) and Message contains "3221225760" | distinct ActivityId;
let storVspSetBehaviorActivities = nodeStorageEvents | where TaskName == "StorVspDeviceSetBehavior" | distinct ActivityId;
let ignoredStorVspSetBehaviorActivityIds = failedActivities | where ActivityId in (storVspSetBehaviorActivities) and (Message contains "3221225488") | distinct ActivityId;
let fileWrapperSetBehaviorActivities = nodeStorageEvents | where TaskName == "FileWrapperSetBehavior" | distinct ActivityId;
let ignoredFileWrapperSetBehaviorActivityIds = failedActivities | where ActivityId in (fileWrapperSetBehaviorActivities) and (Message contains "3221225659" or Message contains "3221225488") | distinct ActivityId;
// Other failure events, these don't go down the above path. These are the events that we care about in AH 2021.
let failureActivityIdsToIgnore = nodeStorageEvents
                        | where  ActivityId in (failedActivityIds)
                        // RCT and MRT files don't exist unless RCT is enabled. It's not enabled on Azure.
                        | where (TaskName == "VhdmpFileWrapperOpenDownlevel" and Opcode == 2 and Message contains "3221225524"
                                 and (Message contains "rct" or Message contains "mrt"))
                        | distinct ActivityId
                        | union cancelledFlushActivityIds
                        | union ignoredStorVspSetBehaviorActivityIds
                        | union ignoredFileWrapperSetBehaviorActivityIds;
nodeStorageEvents
| where ActivityId in (failedActivityIds) or Level < 4
// Filter out known noisy errors:
// TSG: https://eng.ms/docs/cloud-ai-platform/azure/aep-platform/core-os/hyper-v-azure/hyper-v-svx/tsg/tsg-benign-errors-azure
| where not (ActivityId in (failureActivityIdsToIgnore))
| where not(TaskName == "VhdmpTrace"
                 // Calling code issued an IOCTL with too small of a buffer. Expected way to see how big the buffer should be
            and ((((Message contains "VhdmpiQueryDependentDisk") or (Message contains "VhdmpiQueryVirtualDiskName"))
                   and (Message contains "0x80000005"))
                 or (Message contains "VhdmpiVhdControlObjectDeviceControlHandler"
                     and (Message contains "query virtual disk name request failed (0x80000005)"))
                 or (Message contains "VhdmpiDiskDeviceControlHandler" 
                     and (Message contains "query VHD file name request failed (0xc0000023)"))
                 or (Message contains "VhdmpiQueryVhdFileName" and Message contains "0xC0000023")
                 or (Message contains "VhdmpiQueryProperty" and Message contains "0xC0000023")
                 // VHDMP logs truncation as a warning, but it's part of the expected VHD flow
                 or (Message contains "VhdmpiVhd1TryTruncateVhdFile")
                 or (Message contains "VhdmpiLockAndTryTruncateBackingStoreFile"))
                 // MODE SELECT fails by design. This is how guests determine if SCSI device has some capabilities
                 or (Message contains "CDB 26 failed (0x6)")
                 // This is an error, but VHDMP just lets it go. This is expected in Azure when new VHDs have a cleared out
                 // LinkedTimeStamp (of 0x0).
                 or (Message contains "VhdmpiVerifyParentDiskIdentify: Differencing disk violation. Parent time stamp is")
                 // RCT and MRT files don't exist unless RCT is enabled. It's not enabled on Azure.
                 or (Message contains "0xc0000034"
                     and (Message contains "rct" or Message contains "mrt")))
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, Level, ProviderName, TaskName, EventMessage, Message, ActivityId, level
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `TaskName == "FileWrapperFlushBuffers"` · `TaskName == "StorVspDeviceSetBehavior"` · `TaskName == "FileWrapperSetBehavior"`

---

### Azure Host HyperVStorageStack Incomplete IO Operations

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V Tables > Storage Stack > Storage Stack > Incomplete IO Operations > Incomplete IO Operations`

```kusto
cluster('azcore.centralus').database('Fa').HyperVStorageStackTable
| where NodeId == nodeId
| where PreciseTimeStamp between (startTime .. endTime)
| where ActivityId != "00000000-0000-0000-0000-000000000000" 
| where TaskName != "FileWrapper" and TaskName !contains "Vhdmp" and TaskName != "ActivityFailure"
| project PreciseTimeStamp, NodeId, Cluster, ProviderName, EventId, OpcodeName, Opcode, TaskName, Task, ActivityId, RelatedActivityId, Message
| extend OpcodeTranslation = case(Opcode == 1, "OPCODE_START", Opcode == 2, "OPCODE_STOP", "OPCODE_UNKNOWN")
| summarize OpcodeCount=count(), make_set(OpcodeTranslation), make_list(Message), min(PreciseTimeStamp) by NodeId, TaskName, ActivityId
| where OpcodeCount != 2
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `ActivityId != "00000000-0000-0000-0000-000000000000"` · `TaskName != "FileWrapper"`

---

### Azure Host HyperVStorageStack IO Operations Summary

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V Tables > Storage Stack > Storage Stack > IO Operations Summary > IO Operations Summary`

```kusto
HyperVStorageStackTable
| where PreciseTimeStamp between(startTime .. endTime) and NodeId == nodeId
| where ProviderName contains "StorageActivity" and TaskName != "FileWrapper" and TaskName !contains "Vhdmp"
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp), max(Level), max(EventId), max(OpcodeName), max(TaskName), min(Message) by ActivityId,NodeId
| extend duration=(max_PreciseTimeStamp-min_PreciseTimeStamp)
| project-away NodeId, max_Level, max_EventId, max_OpcodeName
| order by duration desc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `ProviderName contains "StorageActivity"`

---

## Virtualization

### Azure Host Node UnderhillEventTable

_Widget purpose:_ UnderhillEventTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V Tables > Virtualization > UnderhillEventTable`

```kusto
UnderhillEventTable 
| where PreciseTimeStamp between(startTime..endTime) and NodeId == nodeId and Level < 4
| project PreciseTimeStamp, Level, Message
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Node Virtualization Configuration

_Widget purpose:_ Virtualization Configuration

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V Tables > Virtualization > Virtualization Configuration`

```kusto
HyperVVmConfigSnapshot 
| where PreciseTimeStamp between(startTime..endTime) and NodeId == nodeId and SummaryType == "Configuration" 
| summarize arg_max(PreciseTimeStamp, VmProcessorCount, VmVersion, VmMemoryInMB, VmGeneration, HclEnabled, IsUnderhill, IsolationSetting, SummaryJson) by ContainerId
| extend Hcl = case(HclEnabled =~ "true" and IsUnderhill =~ "true", "HCLv2 - OpenHCL/Underhill", HclEnabled =~ "true" and isempty(IsUnderhill), "HCLv1", "")
| project PreciseTimeStamp, ContainerId, VmProcessorCount, VmVersion, VmMemoryInMB, VmGeneration, Hcl, IsolationSetting //, SummaryJson
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Worker

### Azure Host Hyper-V Worker

_Widget purpose:_ HyperVWorkerTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V Tables > Worker > Worker > HyperVWorkerTable`

```kusto
cluster('azcore.centralus').database('Fa').HyperVWorkerTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, Level, ProviderName, TaskName, EventMessage, parse_json(Message), level
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---
