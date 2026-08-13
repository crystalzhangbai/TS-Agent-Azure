# Host Details

> Source: **Azure Host — Azure Host Node** dashboard, chapter **Host Details** (22 queries across 5 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Azure Host Node VMA Query

Cluster: `Vmakpi.kusto.windows.net` · Database: `vmadb` · Type: `Timeline`
Source panel: `Host Details`

```kusto
VMA
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project StartTime, Content = strcat(RoleInstanceName, " - ", RCA), Health = "Unhealthy", EscalateTo, EscalateToBucket
| distinct *
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Azure Host Node State (Fabric)

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Host Details`

```kusto
TMMgmtNodeStateChangedEtwTable
| where PreciseTimeStamp between ((startTime - 1d) .. (endTime + 1d)) and BladeID == nodeId
| project StartTime = PreciseTimeStamp, Content = OldState, T = 1
 | union (
     TMMgmtNodeStateChangedEtwTable
     | where PreciseTimeStamp between ((startTime - 1d) .. (endTime + 1d)) and BladeID == nodeId
     | project StartTime = PreciseTimeStamp, Content = NewState, T = 2
 )
| sort by StartTime, T asc
| extend Health = case(Content == "Ready", "Healthy", Content == "Unhealthy", "Degraded", Content in ("HumanInvestigate", "PoweringOn"), "Unhealthy",  "Neutral")
| serialize
| extend EndTime = StartTime // case(isnotempty(next(StartTime)), next(StartTime), now())
| sort by StartTime asc, T asc 
| extend StartTime = case(isnotempty(prev(StartTime)), prev(EndTime), startTime - 1h),
         FilterOut = Content == next(Content) and Content == prev(Content)
| where FilterOut != 1
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), now())
| extend StartTime = case(isnotempty(prev(StartTime)), prev(EndTime), startTime - 1h)
| sort by StartTime asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Azure Host TOR Pingmesh

Cluster: `azphynet.kusto.windows.net` · Database: `azdhmds` · Type: `Timeline`
Source panel: `Host Details`

```kusto
cluster('aznwsdn.kusto.windows.net').database('aznwmds').TorPingSendAggreEvent
    | where TIMESTAMP between ((startTime - 1d) .. (endTime + 1d)) and NodeId == nodeId
    | summarize SendCount = max(SendCount) by TIMESTAMP, NodeId
    | join kind = leftouter
    (
        cluster('aznwsdn.kusto.windows.net').database('aznwmds').TorPingRecvAggreEvent
    | where TIMESTAMP between ((startTime - 1d) .. (endTime + 1d)) and NodeId == nodeId
    | summarize RecvCount = max(RecvCount) by TIMESTAMP, NodeId
    )on TIMESTAMP, NodeId
    | extend RecvCount = iff(isnull(RecvCount), 0, RecvCount)
    | project TIMESTAMP, NodeId, Availability = todouble(RecvCount) / todouble(SendCount) * 100, SendCount = toint(SendCount), RecvCount = toint(RecvCount), TimeWindowInMinutes = int(5)
    | order by TIMESTAMP asc 
    | extend flag = case (isempty(prev(TIMESTAMP)) or prev(Availability) <> Availability, "changed", "") 
    | where flag <> ""
    | project TIMESTAMP, flag, Availability
    | extend EndTime = case (isnotempty(next(TIMESTAMP)), next(TIMESTAMP) , endTime)
    | extend Health = case(Availability >= 100, "Healthy", "UnHealthy")
    | project StartTime = TIMESTAMP, EndTime, Health,  Content = tostring(Availability)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Node Power State Timeline

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`
Source panel: `Host Details`

```kusto
TMMgmtNodeStateChangedEtwTable
| where PreciseTimeStamp between (startTime .. endTime) and BladeID == nodeId
| where NewState in ("PoweringOn", "PoweredOff")
| project StartTime = PreciseTimeStamp, Content = NewState, HealthState = "Degraded"
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Vhddisk Events Query

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Host Details`

```kusto
OsVhddiskEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where EventId == 21 // Event17 will be covered in the Xstore Autotriage query
| summarize StartTime = min(PreciseTimeStamp), EndTime = max(PreciseTimeStamp), Blobs = make_set(ParamStr1) by EventId
| project StartTime, Content = strcat(Blobs, " - Event ", EventId), Health = "Unhealthy"
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Azure Host PF Service Updates

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Host Details`

```kusto
ServiceVersionSwitch 
| where NodeId == nodeId and PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h))
| project StartTime = PreciseTimeStamp, Health = "Degraded", Content = strcat(ServiceName," <i>updated</i> "), Tooltip = strcat("<b>", ServiceName, "</b> updated from <i>", CurrentVersion, "</i> to <b>", NewVersion, "</b>")
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Fabric Node Fault

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`
Source panel: `Host Details`

```kusto
TMMgmtNodeFaultEtwTable
| where PreciseTimeStamp between (startTime .. endTime) and BladeID == nodeId
| project StartTime = Time, Health = "Unhealthy", Content = strcat("Node Fault: ", FaultCode), 
          Tooltip = strcat(Reason," | ", Details)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Azure Host XStore E17 AutoTriage

Cluster: `azcore.centralus.kusto.windows.net` · Database: `XHealth` · Type: `Timeline`
Source panel: `Host Details`

```kusto
DiskFailureXStoreTriage
| where TimeStamp between (startTime .. endTime) and NodeId == nodeId
| summarize arg_max(TriageTimestamp, *) by VhdAppCluster, NodeId, DiskPath, TimeStamp
//| where TriageReason !contains "Lease"
| project StartTime = TimeStamp, Content = strcat("E17 RCA: ", TriageCategory, ".", TriageReason), Health = "Unhealthy", Tooltip = DiskPath
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host OSHostPlugin Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Host Details`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (startTime .. endTime) and ProviderName in ('OSHostPlugin', 'NMAgent') and NodeId == nodeId
| project StartTime = todatetime(TimeCreated), Content = EventId, Tooltip = strcat(ProviderName, " - ", Description)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Impactful Events

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Timeline`
Source panel: `Host Details`

```kusto
AirManagedEvents
| where EventTime between ((startTime - 12h) .. (endTime + 12h))
| where NodeId == nodeId
| extend UpdateType = split(EventSource, '_')[-1], Reference = iff(EventSource contains "VmPhu", "https://www.osgwiki.com/wiki/VM-PHU_Compute_Blackout", "")
| summarize arg_max(EventTime, *) by bin(EventTime, 1m)
| project StartTime = EventTime, //EndTime = EventTime + Duration, 
    Content = strcat(tostring(UpdateType), " (", Duration, ") "), Health = 'Unhealthy', 
    Tooltip = strcat(EventSource, " duration ", Duration), Diagnostics, Reference 
//
//AirManagedEvents
//| where EventTime between ((startTime - 12h) .. (endTime + 12h))
//| where NodeId == nodeId
//| extend UpdateType = split(EventSource, '_')[-1]
//| summarize arg_max(EventTime, *) by bin(EventTime, 1m)
//| project StartTime = EventTime, EndTime = EventTime + Duration, UpdateType, Duration, 
//    Content = strcat(tostring(UpdateType), " (", Duration, ") "), Health = 'Unhealthy', 
//    Tooltip = strcat(EventSource, " duration ", Duration), Diagnostics, NodeId
//| join kind = leftouter (
//    cluster("baseplatform.westus").database("vmphu").OSHPExecutionInstances
//    | where StartTime between (startTime .. endTime)
//    | extend OSHPStartTime = StartTime
//    //| where UpdateType == 'ksr_to_self'
//    //| extend ExecutionDetail = strcat('https://klondike.azurewebsites.net/scenario/vmphu/instance?InstanceId=', ExecutionId, " | Klondike Overview: aka.ms/FUNKlondike (how to access klondike: https://coreidentity.microsoft.com/manage/Entitlement/entitlement/funklondike-hfni)")
//    | extend KlondikeExecutionDetail = strcat('https://klondike.azurewebsites.net/scenario/vmphu/instance?InstanceId=', ExecutionId)
//    | project OSHPStartTime, UpdateType, NodeId, ExecutionId, KlondikeExecutionDetail
//) on NodeId
//| where OSHPStartTime < StartTime
//| project StartTime, //, EndTime
//          UpdateType = iff(isnotempty(UpdateType1), UpdateType1, UpdateType), 
//          Content, Duration, Tooltip, Health, Diagnostics, 
//          ExecutionDetail = iff(Content contains "VmPhu", KlondikeExecutionDetail, ""), 
//          Reference = iff(Content contains "VmPhu", "https://www.osgwiki.com/wiki/VM-PHU_Compute_Blackout", "")
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `UpdateType == "ksr_to_self"`

---

### Azure Host Node Updates

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`
Source panel: `Host Details`

```kusto
TMMgmtNodeEventsEtwTable  
| where TIMESTAMP between (startTime .. endTime) and NodeId =~ nodeId  and (Message contains 'CreatePluginComplete' or Message contains 'UpdatePluginCompleted')
| parse kind = regex Message with * ' = HostPluginName:' Component:string ', HostPluginSetupFile:' * 'HostPluginPackage:'package:string ', Action:'* 
| project StartTime = TIMESTAMP, Health = "Degraded", Content = Component, Tooltip = strcat(Component, " <i> updated </i> to ", package)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Node TIP sessions

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Host Details`

```kusto
// Check LogNodeSnapshot for current TIP session ID
let logNodeTipSessionId = toscalar(
    LogNodeSnapshot
    | where PreciseTimeStamp between ((queryFrom - 1d) .. (queryTo + 1d)) and nodeId == _nodeId
    | summarize arg_max(PreciseTimeStamp,*)
    | project tipNodeSessionId
);
let logTipNodeSessionId = toscalar(
    LogTipNodeSessionSnapShot
    | where PreciseTimeStamp between ((queryFrom - 1d) .. (queryTo + 1d)) and nodeList has _nodeId
    | project tipNodeSessionId
);
let tipSessionId = coalesce(logTipNodeSessionId, logNodeTipSessionId);
let stuck = iff(isnotempty(logTipNodeSessionId), false, true);
LogTipNodeSessionSnapShot
| where tipNodeSessionId == tipSessionId
| project PreciseTimeStamp, startTime, expirationTime, tipNodeSessionId, createdBy, reason, nodeList
| summarize StartTime = arg_min(PreciseTimeStamp, *), EndTime = arg_max(PreciseTimeStamp, *) by tipNodeSessionId
| extend Health = iff(stuck, "Unhealthy", "Neutral")
| project StartTime, Content = strcat("TIP Id: ", tipNodeSessionId, ", CreatedBy: ", createdBy), Health, EndTime = iff(isnotempty(logTipNodeSessionId),EndTime, now())
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_nodeId}`

---

### Azure Host Node Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Host Details`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| where Level == 1 or EventId in (1001) or (EventId == (1014) and ProviderName == "Microsoft-Windows-DNS-Client")
| project StartTime = todatetime(TimeCreated), Content = strcat(ProviderName, "-", EventId), Health = case(Level == 1, "Unhealthy", "Degraded")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Fault Recovery Events

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Host Details`

```kusto
FaultHandlingRecoveryEventEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == nodeId
| parse Details with one ":" two ":" State
| extend Health = case(State == "Ready", "Healthy", State in ("Dead", "OutForRepair", "Unhealthy"), "Unhealthy",  "Neutral")
| extend Content = Details
| distinct StartTime = PreciseTimeStamp, Health, Content, RecoveryResult, RecoveryAction, FaultSignature, FaultRecoveryDurationInMinutes
| sort by StartTime asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Node HealthSignal (Fabric)

Cluster: `azurecm.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Host Details`

```kusto
let healthSignalDefaultString = "{\"Revision\":0,\"HealthSignals\":[]}";
cluster('azurecm.centralus.kusto.windows.net').database('AzureCM').LogNodeSnapshot  
| where PreciseTimeStamp between ((startTime - 1d) .. (endTime + 1d)) and nodeId == NodeID
| order by PreciseTimeStamp asc 
| extend flag = case (isempty(prev(PreciseTimeStamp)) or prev(healthSignals) <> healthSignals, "changed", "") 
| where flag <> ""
| project PreciseTimeStamp, flag, healthSignals
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp) , endTime)
| extend Content = case(healthSignals == "", "No Logs", healthSignals == healthSignalDefaultString, "No Logs", "Review Logs")
| extend Health = "Neutral"
| project StartTime = PreciseTimeStamp, EndTime, Health,  Content, healthSignals
```

**Params:** `{startTime}`, `{endTime}`, `{NodeID}`

---

## {{nodeId}} Properties

### Host OS Version

_Widget purpose:_ {{nodeId}} Properties

Cluster: `wdgeventstore.kusto.windows.net` · Database: `HostOSDeploy` · Type: `Single` · Widget: `Card`
Source panel: `Host Details > {{nodeId}} Properties`

```kusto
cluster('wdgeventstore.kusto.windows.net').database('HostOSDeploy').nodes
| where nodeId == local_nodeId
| distinct nodeId, HostOS = OSVersion | take 1 | project HostOS
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_nodeId}`

---

### Retrieve Node Hardware Details

_Widget purpose:_ {{nodeId}} Properties

Cluster: `azuredcm.kusto.windows.net` · Database: `AzureDCMDb` · Type: `Single` · Widget: `Card`
Source panel: `Host Details > {{nodeId}} Properties`

```kusto
cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").RdmResourceSnapshot
| where ResourceId == local_nodeId and PreciseTimeStamp > ago(1d)
| summarize arg_max(PreciseTimeStamp, Sku, Manufacturer, Model, ResourceId) by ResourceId
| project Sku, Manufacturer, Model, ResourceId
| join kind=leftouter(
    cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").dcmInventoryComponentSystemDirect 
    | where NodeId == local_nodeId
    | extend Total_RootVP = case(HyperVCore_MinRoot == 0, HyperVCore_PhysicalCoreCount, HyperVCore_MinRoot) 
    | project NodeId, PhysicalCoreCount = HyperVCore_PhysicalCoreCount, Total_LP = HyperVCore_LogicalCoreCount, Total_RootVP, Hostname | take 1
) on $left.ResourceId == $right.NodeId
| project-away ResourceId, NodeId
//| extend globalFrom = globalFrom
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_nodeId}`

---

### Cluster Overlake Version (HostOS)

_Widget purpose:_ {{nodeId}} Properties

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Single` · Widget: `Card`
Source panel: `Host Details > {{nodeId}} Properties`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp > ago(7d)
| where nodeId == _nodeId
| summarize arg_max(PreciseTimeStamp, *) by nodeId
| project Tenant
| lookup kind=leftouter (
    cluster('hostosdata.centralus.kusto.windows.net').database('HostOsData').OverlakeClusterVersions
    | project Cluster, OverlakeVersion, RTET
    ) on $left.Tenant == $right.Cluster
| project OverlakeVersion
```

**Params:** `{_nodeId}`

---

### GetTimeinDeviceDrillFormat

_Widget purpose:_ {{nodeId}} Properties

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `fa` · Type: `Single` · Widget: `Card`
Source panel: `Host Details > {{nodeId}} Properties`

```kusto
print startTime = format_datetime(queryFrom, "MM-dd-yyyy HH:mm"), endTime = format_datetime(queryTo, "MM-dd-yyyy HH:mm")
```

**Params:** `{queryFrom}`, `{queryTo}`

---

## File Versions

### Azure Host FileVersions Query

_Widget purpose:_ File Versions

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `Host Details > File Versions`

```kusto
GetFileVersion(nodeId, startTime, endTime)
| sort by FileName asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Insights

### Azure Host Node StorageClient Insights

_Widget purpose:_ Insights

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `Host Details > Insights`

```kusto
let tempEndTime = iff(datetime_diff('day', startTime, endTime) > 1, startTime + 1d, endTime);
StorageClientInsightsForNodeV2(nodeId, startTime, tempEndTime)
//| where ContainerId != containerId or isempty(containerId) // this is already added above in the vm insights
| project PreciseTimeStamp, Message, EventName, ContainerId, level = case(EventName contains "Update" or EventName contains "CacheHint", "warning", "error")
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`, `{containerId}`

---

## PF Services

### Azure Host PF Services Versions

_Widget purpose:_ PF Services

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Host Details > PF Services`

```kusto
ServiceManagerInstrumentation
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 2h)) and NodeId == nodeId
| summarize arg_max(PreciseTimeStamp, ServiceName) by ServiceVersion
| project PreciseTimeStamp, ServiceName, ServiceVersion
| sort by ServiceName desc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---
