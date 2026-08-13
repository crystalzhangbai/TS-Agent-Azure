# Node Update & Maintenance

> Source: EEE RDOS Start Hub dashboard (5 queries).

Use when investigating: **planned maintenance / update events impacting the VM (PF, Host OS, CM, AzPE, FPGA updates)**. These help distinguish platform-initiated downtime from unexpected failure.

---

### PF Update

_Purpose:_ Node Update

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
cluster('azcsupfollower').database('AzureCM').ServiceVersionSwitch 
| where NodeId == queryNodeId and PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h))
| project PreciseTimeStamp, ServiceName, CurrentVersion, NewVersion, SourceOfService
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, Content = ServiceName, ServiceName, CurrentVersion, NewVersion, SourceOfService
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Host Update

_Purpose:_ Node Update

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
//cluster('azcsupfollower.kusto.windows.net').database('rdos').WindowsEventTable
| where PreciseTimeStamp  between(starttime .. endtime)
| where NodeId == nodeid
// | where ProviderName == "OSHostPlugin"
| where ProviderName == "UpdateNotification"
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by TimeCreated asc
//| extend EventType = parse_json(Description).EventType
//| extend StartTime = case( 
//    parse_json(Description).EventType == "Start", TimeCreated, 
//    parse_json(prev(Description)).EventType == "Start", prev(TimeCreated), 
//    starttime)
//| extend EndTime = case(
//    parse_json(Description).EventType == "End", TimeCreated, 
//    parse_json(next(Description)).EventType == "End", next(TimeCreated), 
//    endtime)
| extend StartTime = TimeCreated
| extend EventType = parse_json(Description).EventType
| extend UpdateResult = parse_json(Description).UpdateResult
| extend DiskImpact = parse_json(Description).ImpactDetails.Disk
| extend ComputeImpact = parse_json(Description).ImpactDetails.Compute
| extend NetworkImpact = parse_json(Description).ImpactDetails.Network
| extend OSImpact = parse_json(Description).ImpactDetails.OS
//| where EventType == "End"
//| extend Health = case (UpdateResult == "Success", "healthy", "unhealthy")
//| extend Content = tostring(UpdateResult)
| extend Content = strcat(parse_json(Description).EventType, "/", parse_json(Description).SourceServiceName, "/", parse_json(Description).ComponentName)
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ProviderName == "OSHostPlugin"` · `ProviderName == "UpdateNotification"` · `EventType == "End"`

---

### CM Node Update

_Purpose:_ Node Update

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
let nodeEvents = cluster('azcsupfollower').database('AzureCM').TMMgmtNodeEventsEtwTable  
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId  
| project PreciseTimeStamp, Message;
union (nodeEvents
| where Message contains "[NSD.WorkflowActionDuration] UpdateAgent"
| project StartTime = PreciseTimeStamp, Health = "Degraded", Content = "Agent Updated", Message), 
(nodeEvents
| where Message contains "Current Agent Package" and Message contains "Goal Agent Package"
| project StartTime = bin(PreciseTimeStamp, 1m),  Health = "Degraded", Content = "New Host Agent Detected", Message),
(nodeEvents
| where (Message contains 'CreatePluginComplete' or Message contains 'UpdatePluginCompleted')
| parse kind = regex Message with * ' = HostPluginName:' Component:string ', HostPluginSetupFile:' * 'HostPluginPackage:' NewVersion:string ', Action:'* 
| project StartTime = PreciseTimeStamp, Health = "Degraded", Content = "HostPlugin Update", Message)
| distinct StartTime, Health, Content, Message
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Message contains "[NSD.WorkflowActionDuration] UpdateAgent"` · `Message contains "Current Agent Package"`

---

### AzPE Update

_Purpose:_ Node Update

Cluster: `azpe` · Database: `azpe` · Type: `Timeline`

```kusto
AzPEWorkflowEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where WorkflowId contains queryNodeId
| where WorkflowType == "OM"
| where EntityId contains "AzPEHostUpdateMonitor"
| project StartTime = PreciseTimeStamp, WorkflowInstanceGuid, WorkflowId, WorkflowType, WorkflowEventType, WorkflowEventData, Content = strcat(WorkflowType, ':', WorkflowEventType), Health='Neutral'
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `WorkflowType == "OM"` · `EntityId contains "AzPEHostUpdateMonitor"`

---

### FPGA Update

_Purpose:_ Node Update

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp  between(starttime .. endtime)
| where NodeId == nodeid
| where (ProviderName contains "FPGA" and (Description contains "BeforeInstall" or Description contains "AfterInstall"))
| project PreciseTimeStamp, StartTime = todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| extend Content = "FPGA Driver Install"
| order by StartTime asc 
| extend EndTime = case (Description contains "BeforeInstall" and next(Description) contains "AfterInstall", next(StartTime), endtime)
| where Description !contains "AfterInstall"
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---
