# Update Investigation

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Update Investigation** (13 queries across 13 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## AirHostNetworkingUpdateEvents

### AirHostNetworkingUpdateEvents DS

_Widget purpose:_ AirHostNetworkingUpdateEvents

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `Update Investigation > AirHostNetworkingUpdateEvents > AirHostNetworkingUpdateEvents`

```kusto
AirHostNetworkingUpdateEvents
| where EventTime >= query_BeginTime and EventTime <= query_EndTime
| where NodeId == query_NodeId
| distinct EventTime,NodeId, EventCategoryLevel3, EventSource, RCALevel1, OutageType
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## AirManagedEvents

### AirManagedEvents DS

_Widget purpose:_ AirManagedEvents

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `Update Investigation > AirManagedEvents > AirManagedEvents`

```kusto
AirManagedEvents
| where EventTime between (query_BeginTime .. query_EndTime) and NodeId == query_NodeId 
| project EventTime, EventType, EventSource, ObjectType, ObjectId, Duration, EventCategoryLevel1, EventCategoryLevel2, EventCategoryLevel3, RCALevel1
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## AirManagedEventsBrownouts

### AirManagedEventsBrownouts DS

_Widget purpose:_ AirManagedEventsBrownouts

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `Update Investigation > AirManagedEventsBrownouts > AirManagedEventsBrownouts`

```kusto
AirManagedEventsBrownouts
| where EventTime between (query_BeginTime .. query_EndTime) and NodeId == query_NodeId 
| project EventTime, NodeId, EventType, EventSource, ObjectType, ObjectId, Duration, EventCategoryLevel1, EventCategoryLevel2, EventCategoryLevel3, RCALevel1, RCALevel2, RCALevel3
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## Combined Query

### CombinedQuery DS

_Widget purpose:_ Combined Query for Host Updates

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `AutopilotDeployment` · Type: `Table`
Source panel: `Update Investigation > Combined Query > Combined Query for Host Updates`

```kusto
let ServiceManger=(cluster('storageclient.eastus.kusto.windows.net').database('AutopilotDeployment').ServiceManagerInstrumentation);
let RootHE= (cluster('Vmainsight.kusto.windows.net').database('vmadb').RootHENodeGoalVersionChange
| extend  RootHE_OldValue=OldValue, RootHE_NewValue=NewValue);
let RootHEGaldaf= (cluster('storageclient.eastus.kusto.windows.net').database('Fc').RootHEGandalfInformationalEventEtwTable
| extend  RootHEGandalf_OldValue=OldVersion, RootHE_NewValueGandalf=NewVersion);
let NMAgent= (cluster('vmainsight.kusto.windows.net').database('Air').AirMaintenanceEvents
| extend PreciseTimeStamp = EventTime
| extend Diagnostics=tostring(Diagnostics));
union ServiceManger, RootHE, RootHEGaldaf, NMAgent
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId
| summarize NodeUpdatedAtApprox=min(PreciseTimeStamp) by ServiceVersion, ServiceName,RootHE_OldValue, RootHE_NewValue,RootHEGandalf_OldValue,RootHE_NewValueGandalf, EventCategoryLevel2, EventCategoryLevel3, Component, OutageType, Diagnostics, NodeId
| project-reorder  NodeUpdatedAtApprox, NodeId
| order by NodeUpdatedAtApprox asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## HostPlugin Update - TMMgmtNodeEventsEtwTable

### HostPlugin Update - TMMgmtNodeEventsEtwTable DS

_Widget purpose:_ HostPlugin Updates

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Update Investigation > HostPlugin Update - TMMgmtNodeEventsEtwTable > HostPlugin Updates`

```kusto
TMMgmtNodeEventsEtwTable  
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime)
| where NodeId == query_NodeId  
| where (Message contains 'CreatePluginComplete' or Message contains 'UpdatePluginCompleted')
| parse kind = regex Message with * ' = HostPluginName:' Component:string ', HostPluginSetupFile:' * 'HostPluginPackage:' NewVersion:string ', Action:'* 
| project PreciseTimeStamp, Component, NewVersion
| order by PreciseTimeStamp asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## Node Update Event - Event Log

### Node Update Event - Event Log DS

_Widget purpose:_ Node Update Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Update Investigation > Node Update Event - Event Log > Node Update Events`

```kusto
WindowsEventTable
| where PreciseTimeStamp  between(query_BeginTime .. query_EndTime)
| where NodeId == query_NodeId
| where not (ProviderName contains "Kernel-Processor" and EventId == 37) // eliminating periodical processor report event every day.
| where not (ProviderName contains "PnP" and EventId == 1010) // eliminating PnP errors. 
| where ProviderName in ("OSHostPlugin", "UpdateNotification", "NMAgent", "Microsoft-Windows-UserModePowerService", "EventLog") or 
    ProviderName contains "Microsoft-Windows-Kernel" or
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "EventType: AfterInstall") or 
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "EventType: BeforeInstall") or 
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "FPGA driver install") or
    (ProviderName contains "vfpext" and EventId == 7036) 
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by TimeCreated asc
| extend level = case (Level == 1, "critical", 
    Level == 2, "error", 
    Level == 3, "warning",
    "info")
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## OSHP FastSave

### Azure Host Fast Restore Events DS

_Widget purpose:_ OSHP FastSave

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Update Investigation > OSHP FastSave > OSHP FastSave`

```kusto
OsUpdateManagerFastRestoreEvents
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime) and NodeId == query_NodeId
|  project PreciseTimeStamp = todatetime(StartTime), Operation, VmName, ExecutionId
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## OSHP Timeline Events

### Azure Host OSHP Events DS

_Widget purpose:_ OSHP Timeline Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Update Investigation > OSHP Timeline Events > OSHP Timeline Events`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime) and ProviderName in ('OSHostPlugin', 'NMAgent') and NodeId == query_NodeId
| project todatetime(TimeCreated), ProviderName, EventId, Description
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## OSHP Update Logs

### OSHP Update DS

_Widget purpose:_ OSHP Update Logs

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `AutopilotDeployment` · Type: `Table`
Source panel: `Update Investigation > OSHP Update Logs > OSHP Update Logs`

```kusto
OsUpdateManagerEvents
| where PreciseTimeStamp between ((query_BeginTime - 1h) .. (query_EndTime + 1h)) and NodeId == query_NodeId
| project StartTime = todatetime(StartTime), ExecutionId, MessageType, TimeTaken, Description
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## PF Service Update - ServiceVersionSwitch

### ServiceVersionSwitch_UnexpectedRestart2 DS

_Widget purpose:_ PF Service Updates

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `AutopilotDeployment` · Type: `Table`
Source panel: `Update Investigation > PF Service Update - ServiceVersionSwitch > PF Service Updates`

```kusto
ServiceVersionSwitch 
| where NodeId == query_NodeId and PreciseTimeStamp between ((query_BeginTime - 1h) .. (query_EndTime + 1h))
| project PreciseTimeStamp, ServiceName, CurrentVersion, NewVersion, SourceOfService
| order by PreciseTimeStamp asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## Scheduled Event for HostUpdate - AzPEWorkflowEvent

### Scheduled Event for HostUpdate - AzPEWorkflowEvent DS

_Widget purpose:_ Scheduled Event for HostUpdate

Cluster: `azpe.kusto.windows.net` · Database: `azpe` · Type: `Table`
Source panel: `Update Investigation > Scheduled Event for HostUpdate - AzPEWorkflowEvent > Scheduled Event for HostUpdate`

```kusto
AzPEWorkflowEvent
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime)
| where WorkflowId contains query_NodeId
| where WorkflowType == "OM"
| where EntityId contains "AzPEHostUpdateMonitor"
| project PreciseTimeStamp, WorkflowInstanceGuid, WorkflowId, WorkflowType, WorkflowEventData
| order by PreciseTimeStamp asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

**Signal filters seen in KQL:** `WorkflowType == "OM"` · `EntityId contains "AzPEHostUpdateMonitor"`

---

## SoC PF Update

### SocUpdate

Cluster: `overlakedata.southcentralus.kusto.windows.net` · Database: `overlake-syslog` · Type: `Table`
Source panel: `Update Investigation > SoC PF Update`

```kusto
let QueryFilterByNodeId = cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMap_Latest
| where NodeId =~ queryNodeId;
QueryFilterByNodeId
| summarize count()
| extend OverlakeState = iff(count_ == 0, "Not Enabled", "Enabled")
| project OverlakeState, NodeId = tolower(queryNodeId)
| join kind=leftouter (QueryFilterByNodeId) on NodeId
| project SocNodeId
| join kind=inner
(cluster("azcore.centralus.kusto.windows.net").database("OvlProd").OverlakeServiceManagerStatus
| where  PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h))
| where EventType == "versionswitch"
| order by PreciseTimeStamp desc
| extend detailsParsed = parse_json(detail)
| extend CurrentVersion=tostring(detailsParsed.Version)
| extend NewVersion=tostring(detailsParsed.NewVersion)
| project PreciseTimeStamp, ServiceName, CurrentVersion, NewVersion, NodeId, MachineName, Cluster
| extend StartTime = PreciseTimeStamp
| extend Content = strcat(ServiceName, ": ", NewVersion)) on $left.SocNodeId == $right.NodeId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `EventType == "versionswitch"`

---

## VMPhuEvents

### VMPhuEvents DS

_Widget purpose:_ VMPhuEvents

Cluster: `https://moseisley.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `Update Investigation > VMPhuEvents > VMPhuEvents`

```kusto
GetVMPhuEvents(query_vmid,query_BeginTime,query_EndTime)
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_vmid}`

---
