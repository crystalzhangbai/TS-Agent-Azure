# Node (Software)

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Node (Software)** (49 queries).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## Node (Software)

### AzureWatsonQuery

_Widget purpose:_ Azure Watson Dump List

Cluster: `azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Azure Watson > Azure Watson > Azure Watson Dump List`

```kusto
let azurewatsonlink = strcat("https://azurewatson.microsoft.com/?NodeId=", nodeid);
cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp between (starttime .. endtime)
| where nodeIdentity == nodeid
| project PreciseTimeStamp, EventMessage, platform, crashMode, process, environment, dumpUid
| join kind= leftouter (
    cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
    | where PreciseTimeStamp between (starttime..endtime)
    | project AnalyzedTime=PreciseTimeStamp, DumpAnalalysisMessage=EventMessage, faultingModule, faultingProcess, bucketString, crashTime, dumpType, bugId, bugLink, dumpUid
) on $left.dumpUid == $right.dumpUid
| extend AzureWatsonLink=azurewatsonlink
| where crashTime <> ""
| project crashTime, AnalyzedTime, dumpType, crashMode, platform, DumpAnalalysisMessage, faultingModule, faultingProcess, bugId, bugLink, AzureWatsonLink
| order by crashTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Node Container Performance

_Widget purpose:_ Node Container CPU Perf

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Node (Software) > Node (Software) > Container List > Container List > Node Container CPU Perf`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId == nodeid
| where CounterName contains "CPU"
| project PreciseTimeStamp, Cluster, TenantId, NodeId, ContainerId = VmId, RoleId, RoleInstanceId, CounterName, SampleCount, AverageCounterValue, MinCounterValue, MaxCounterValue
| project PreciseTimeStamp, ContainerId, AverageCounterValue
| order by ContainerId asc, PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `CounterName contains "CPU"`

---

### Node Container List

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Container List > Container List > Node Container List`

```kusto
cluster('azcsupfollower.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
| where nodeId == nodeid
| distinct creationTime, roleInstanceName, subscriptionId, Tenant, tenantName, containerId, nodeId, virtualMachineUniqueId, tenantOwners, containerType, Region, AvailabilityZone
| order by creationTime
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### TImeline_ContainerOSState

_Widget purpose:_ Timeline - Container OS State

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Container List > Container List > Timeline - Container State > Timeline - Container OS State`

```kusto
cluster('azcsupfollower').database('AzureCM').LogContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeId == queryNodeId
| project PreciseTimeStamp, Tenant, roleInstanceName,  tenantName, containerId, nodeId, 
  containerState, actualOperationalState, containerLifecycleState, containerOsState, faultInfo , virtualMachineUniqueId
| project StartTime = PreciseTimeStamp, Content = containerOsState, containerLifecycleState, Tenant, tenantName, containerId, nodeId, virtualMachineUniqueId
| order by containerId asc, StartTime asc
| extend flag = case (Content <> prev(Content), "changed", containerId <> prev(containerId), "changed", "")
| where flag <> "" or containerLifecycleState == "Destroyed"
| extend EndTime = case(isnotempty(next(StartTime)) and next(containerId) == containerId, next(StartTime), queryTo)
| where containerLifecycleState <> "Destroyed"
| extend Health = case (Content in ("ContainerOsStateUnresponsive", "ContainerOsStateUnhealthy", "ContainerOsStateUnknown"), "Unhealthy", Content in ("ContainerOsStateHealthy", "ContainerOsStateProvisioningCompleted"), "Healthy", "Degraded")
| extend GroupBy = containerId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `containerLifecycleState <> "Destroyed"`

---

### Node Container Timeline

_Widget purpose:_ Timeline - Container State

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Container List > Container List > Timeline - Container State > Timeline - Container State`

```kusto
cluster('azcsupfollower').database('AzureCM').LogContainerHealthSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
| where nodeId == nodeid
| project PreciseTimeStamp, Tenant, roleInstanceName,  tenantName, containerId, nodeId, 
  containerState, actualOperationalState, containerLifecycleState, containerOsState, faultInfo , virtualMachineUniqueId
| project StartTime = PreciseTimeStamp, Content = containerState, containerLifecycleState, Tenant, tenantName, containerId, nodeId, virtualMachineUniqueId
| order by containerId asc, StartTime asc
| extend flag = case (Content <> prev(Content), "changed", containerId <> prev(containerId), "changed", "")
| where flag <> "" or containerLifecycleState == "Destroyed"
| extend EndTime = case(isnotempty(next(StartTime)) and next(containerId) == containerId, next(StartTime), endtime)
| where containerLifecycleState <> "Destroyed"
| extend Health = case (Content in ("ContainerStateUnresponsive", "ContainerStateUnhealthy", "ContainerStateUnknown"), "Unhealthy", Content == "ContainerStateStarted", "Healthy", "Degraded")
| extend GroupBy = containerId
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `containerLifecycleState <> "Destroyed"`

---

### HyperV Heartbeat for Containers

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Container List > Container List > Timeline - HyperV Heartbeat`

```kusto
let mview = materialize(cluster("azcore.centralus.kusto.windows.net").database("Fa").VmHealthRawStateEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project StartTime = PreciseTimeStamp, Cluster, ContainerId, IsVscStateOperational, VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted, NodeId, VirtualMachineUniqueId, Context
| order by ContainerId asc, StartTime asc
| extend flag = case (VmHyperVIcHeartbeat != prev(VmHyperVIcHeartbeat) and ContainerId == prev(ContainerId), "StateChanged",
    ContainerId != next(ContainerId), "ContainerChanged",
    ContainerId != prev(ContainerId), "ContainerChanged", "")
| where flag <> ""
| extend Health  = case (VmHyperVIcHeartbeat in ("HeartBeatStateNoContact"), "Degraded", 
    (VmHyperVIcHeartbeat == "HeartBeatStateOk"), "Healthy", 
    VmHyperVIcHeartbeat in ("HeartBeatStateNonRecoverableError", "HeartBeatStateLostCommunication ", "NotMonitored", "HeartBeatStateDegraded"), "Unhealthy", 
    "Neutral")
| extend EndTime = case(isnotempty(next(StartTime)) and next(ContainerId) == ContainerId, next(StartTime), StartTime+1m)
| where prev(ContainerId) != ContainerId or prev(VmHyperVIcHeartbeat) != VmHyperVIcHeartbeat
| extend Content = VmHyperVIcHeartbeat
| extend FilterCategory  = "VmHyperVIcHeartbeat"
| extend GroupBy = strcat(ContainerId, " - VmHyperVIcHeartbeat"));
let containerIds  = mview | summarize by  ContainerId;
mview | union  (cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where Description has_any (containerIds)
| extend EventId = tolong(EventId) 
| where EventId in (18500, 18502, 18504, 18508, 18512, 18514, 18550, 18560, 18570, 18572, 18590, 18190)    
| extend Content = case (
    // Compute
    EventId == 18500, "(18500) VM was Started", 
    EventId == 18502, "(18502) VM was turned off", 
    EventId == 18504, "(18504) VM was shutdown by Host", 
    EventId == 18508, "(18508) VM was shutdown by Guest",
    EventId == 18512, "(18512) VM was reset by Host", 
    EventId == 18514, "(18514) VM was reset by Guest", 
    EventId == 18550, "(18550) VM was reset because of a triple fault", 
    EventId == 18560, "(18560) VM was reset because of a triple fault", 
    EventId == 18570, "(18570) VM was faulted", 
    EventId == 18572, "(18572) VM was faulted", 
    EventId == 18590, "(18590) Bugcheck of Guest VM", 
    EventId == 18190, "(18190) Worker process health is critical for Guest VM", "")    
| extend Health = iif(EventId in (18500), "Neutral", "Error") 
| project StartTime = todatetime(TimeCreated), Content, Health, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by StartTime asc 
| extend containerId = extract("[a-z0-9-]{36}", 0, Description)
| extend FilterCategory  = "HyperV Worker Event"
| extend GroupBy = strcat(containerId, " - HyperV Worker Event"))
| order by GroupBy asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Storage

_Widget purpose:_ Event Timeline

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Event Log > Event Log > Event Timeline`

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
| where Description !contains "RDMA Session Init Failed."
| where not (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and EventId == 31)
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| extend StartTime = TimeCreated, EndTime = TimeCreated + 1m, Content = EventId, GroupBy = ProviderName
| order by TimeCreated asc 
| order by GroupBy asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ProviderName <> "CMClientLib"`

---

### NodeWindowsEvent

_Widget purpose:_ Windows Event Table

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Event Log > Event Log > Windows Event Table`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp  between(starttime .. endtime)
| where NodeId == nodeid
| where not (ProviderName == "NETLOGON" and  EventId == 3095)
| where not (ProviderName == 'IPMIDRV' and EventId == 1004)
| where not (ProviderName == "Microsoft-Windows-PerfNet" and EventId == "2000" )
| where ProviderName <> "CMClientLib"
| where EventId <> 7000
| where EventId <> 1023
| where EventId !in (505, 504, 146, 145, 142)
| where not (ProviderName == "Microsoft-Windows-Kernel-Processor-Power" and EventId == 37)
| where not (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and EventId == 31)
| where not (ProviderName == "Microsoft-Windows-Ntfs" and EventId == 170)
| where Description !contains "RDMA Session Init Failed."
| extend level = case(Level == 1, "fatal", Level == 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, level
| order by TimeCreated asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ProviderName <> "CMClientLib"`

---

### FilterNodeState

_Widget purpose:_ Aggregation State from LogNodeSnapshot

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Filter` · Widget: `Table`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Aggregation State from LogNodeSnapshot`

```kusto
datatable (Value:string, Description:string)
[
    "IgnoreContainerCount", "Ignore containerCount (default)",
    "All", "All Details"
]
```

---

### LogNodeSnapshot

_Widget purpose:_ Aggregation State from LogNodeSnapshot

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Aggregation State from LogNodeSnapshot`

```kusto
cluster('azcsupfollower.kusto.windows.net').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeId == nodeid
| project PreciseTimeStamp, RoleInstance, nodeState, nodeAvailabilityState, containerCount, faultInfo, healthSignals, diskConfiguration, cmNodeChannelAggregatedHealthStatus,  cmNodeWasChannelHealthStatus, cmNodeWillBeChannelHealthStatus
| order by PreciseTimeStamp asc
| extend flag = case ( nodeState <> prev(nodeState) 
   or nodeAvailabilityState <> prev(nodeAvailabilityState) 
   or (filterValue == "All" and containerCount <> prev(containerCount))
   or faultInfo <> prev(faultInfo) , "changed", "")
   // or (filterValue == "All" and healthSignals <> prev(healthSignals)), "changed", "")
| where flag <> ""
| extend level = case (
   nodeAvailabilityState in ("Faulted", "OutForRepair") or nodeState in ("Booting", "OutForRepair", "PoweringOn", "HumanInvestigate", "PoweredOff", "Dead", "Recovering"), "error", 
   nodeAvailabilityState == "Available" and nodeState == "Ready", "info", "warning")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`, `{filterValue}`

---

### ContainerConunt

_Widget purpose:_ Container Count on Node

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Container Count on Node`

```kusto
cluster('azcsupfollower.kusto.windows.net').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
| where nodeId == nodeid
| project PreciseTimeStamp, toint(containerCount)
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### NodeStateQuery

_Widget purpose:_ Node State

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Node State`

```kusto
cluster('azcsupfollower').database('AzureCM').TMMgmtNodeStateChangedEtwTable
| where PreciseTimeStamp between (starttime..endtime)
| where BladeID == nodeid
| project PreciseTimeStamp, Tenant, OldState, NewState, BladeID
| extend level = case(
    NewState in ("Booting", "OutForRepair", "PoweringOn", "HumanInvestigate", "PoweredOff", "Dead", "Recovering"), "error", 
    NewState in ("Unhealthy"), "warning", 
    NewState == "Ready", "info", 
    "info")
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Node WasChannel Health Status

_Widget purpose:_ Services on Node

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Services on Node`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where nodeId == queryNodeId
| project StartTime = PreciseTimeStamp, Content = cmNodeWasChannelHealthStatus
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = case(Content == "Unhealthy", "Unhealthy", Content in ("Unresponsive", "Unknown"), "Degraded", Content == "Healthy",  "Healthy", "Neutral")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Node WillBe Channel Health Status

_Widget purpose:_ Services on Node

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Services on Node`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where nodeId == queryNodeId
| project StartTime = PreciseTimeStamp, Content = cmNodeWillBeChannelHealthStatus
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = case(Content == "Unhealthy", "Unhealthy", Content in ("Unresponsive", "Unknown"), "Degraded", Content == "Healthy",  "Healthy", "Neutral")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### PfAgent Status

_Widget purpose:_ Services on Node

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Services on Node`

```kusto
PFClientBootstrapAvailability
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where Id == queryNodeId
| project StartTime = PreciseTimeStamp, Content = iif(PfAgentUp == "True", "Up", "Down")
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = iif(Content == "Up", "healthy", "Unhealthy")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### PilotFish State

_Widget purpose:_ Services on Node

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Services on Node`

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
| project StartTime, EndTime, Content, Health, PfState
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### ApSvcMgr Status

_Widget purpose:_ Services on Node

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Services on Node`

```kusto
PFClientBootstrapAvailability
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where Id == queryNodeId
| project StartTime = PreciseTimeStamp, Content = iif(ApSvcMgrUp == "True", "Up", "Down")
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = iif(Content == "Up", "healthy", "Unhealthy")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### ApLauncher Status

_Widget purpose:_ Services on Node

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Services on Node`

```kusto
PFClientBootstrapAvailability
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where Id == queryNodeId
| project StartTime = PreciseTimeStamp, Content = iif(ApLauncherUp == "True", "Up", "Down")
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = iif(Content == "Up", "healthy", "Unhealthy")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Node Service Status

_Widget purpose:_ Services on Node

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Services on Node`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project StartTime = PreciseTimeStamp, Content = strcat("PID: " , tostring(Pid)), Pid
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| extend flag = case (Content <> next(Content), "changed", flag)
| where flag <> ""
| extend EndTime = iif (isnotempty(next(StartTime)), iif (Content == next(Content), next(StartTime), StartTime), StartTime)
| extend StartTime = iif(Content == prev(Content), prev(StartTime), StartTime)
| distinct *
| project StartTime, EndTime, Content, Pid
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### WireService Status

_Widget purpose:_ Services on Node

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Node Health > Node Health > Services on Node`

```kusto
WireserverHeartbeatEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, Status, Pid
| sort by PreciseTimeStamp asc
| serialize 
| extend prevTime = case (isnotempty(prev(PreciseTimeStamp)), prev(PreciseTimeStamp), queryFrom)
| extend prevDiff = PreciseTimeStamp - prevTime
| extend Health = case ( (prevDiff >= 62s and prevDiff != 0s and isnotempty(prev(PreciseTimeStamp))), "Unhealthy", "Healthy")
| extend flag = case (Health <> prev(Health), "changed" , "")
| where flag <> ""
| extend Content = Health
| extend StartTime  = case (isnotempty(prevTime), prevTime, queryFrom)
| extend EndTime = case (isnotempty(next(StartTime )), next(StartTime), queryTo)
| project StartTime , EndTime, Content, prevDiff, Pid
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query NodeServiceEventEtwTable

_Widget purpose:_ NS Events for this Container from NodeServiceEventEtwTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Service > Node Service > General - Node Service > NS Events for this Container from NodeServiceEventEtwTable`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').NodeServiceEventEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| where false == queryCheckThisContainer or (ScopeIdentifier == queryContainerId or Message contains queryContainerId)
| extend  level = case (Message has_any("Container workflow blocked", "Schedule reboot repair action"), "Warn", 
    Message contains "Recording new fault", "Error",
   "Info")
| project PreciseTimeStamp, Message, ScopeIdentifier, level
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`, `{queryCheckThisContainer}`

---

### Detector for NodeServiceEventEtwTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Node (Software) > Node (Software) > Node Service > Node Service > General - Node Service > NS Events for this Container from NodeServiceEventEtwTable`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| where ScopeIdentifier == queryContainerId
| extend Description = iif(Message contains "Container workflow blocked", "Container workflow blocked", "")
| extend Description = iif(Message contains "Schedule reboot repair action", "Schedule a reboot to repair the Container", Description)
| where isnotempty(Description)
// | summarize by Message, Description, Severity = "Error"
| summarize by Description, Severity = "Error"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`

---

### NSTimeline

_Widget purpose:_ NS Operation Timeline

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Node (Software) > Node (Software) > Node Service > Node Service > General - Node Service > NS Operation Timeline`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").NodeServiceOperationEtwTable
| where PreciseTimeStamp between( starttime .. endtime )  
| where NodeId == nodeid
| where OperationName !contains "Query"
| extend Health = case(Result == 1, "Healthy", "Unhealthy")
| project PreciseTimeStamp, GroupBy = OperationName, Identifier, Health, Content = strcat("0x", tohex(ResultCode, 8)), StartTime = RequestTime, EndTime = CompleteTime
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### NSOperationQuery

_Widget purpose:_ NS Operations for this Container from NodeServiceOperationEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Service > Node Service > General - Node Service > NS Operations for this Container from NodeServiceOperationEtwTable`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').NodeServiceOperationEtwTable
| where PreciseTimeStamp between( starttime .. endtime )  
| where NodeId == nodeid
| where false == queryCheckThisContainer or Identifier contains containerid
| where OperationName !contains "Query"
| extend ResultStr = case(Result == 1, "Success", "Error")
| project PreciseTimeStamp, OperationName, Identifier, Result, ResultStr, ResultCode, RequestTime, CompleteTime
| order by PreciseTimeStamp asc
| extend level = case (Result <> 1, "error", "info")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`, `{containerid}`, `{queryCheckThisContainer}`

---

### Query AgentNfcHttpDownloadFileEtwTable

_Widget purpose:_ File Downloading Status from AgentNfcHttpDownloadFileEtwTable 

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > File Downloading Status from AgentNfcHttpDownloadFileEtwTable `

```kusto
AgentNfcHttpDownloadFileEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, Url, LocalPath, ImageName, StatusCode, FileSize, DurationMs
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### NodeServiceBootstrapEtwTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > NodeServiceBootstrapEtwTable`

```kusto
NodeServiceBootstrapEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, Pid, ServiceStartTime, HostLastBootUpTime, StartupDelay, PfMode, NodeServiceVersion
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query NodeServiceExitEtwTable

_Widget purpose:_ NodeServiceExitEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > NodeServiceExitEtwTable`

```kusto
NodeServiceExitEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, NodeId, Pid, ExitCode
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query NodeServiceWatchdogEtwTable

_Widget purpose:_ NodeServiceWatchdogEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > NodeServiceWatchdogEtwTable`

```kusto
NodeServiceWatchdogEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, Scope, ResultCode, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### HostPlugin Update from TMMgmtNodeEventsEtwTable

_Widget purpose:_ CM Node Update - TMMgmtNodeEventsEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Update > Node Update > General > CM Node Update - TMMgmtNodeEventsEtwTable`

```kusto
cluster('azcsupfollower').database('AzureCM').TMMgmtNodeEventsEtwTable  
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId == nodeid  
| where Message contains 'CreatePluginComplete' or Message contains 'UpdatePluginCompleted' or Message contains "[NSD.WorkflowActionDuration] UpdateAgent" or Message contains "[NSD.WorkflowActionDuration] StartAgent " or (Message contains "AgentPackage.PF.zip" and Message !contains "RemoveRoleInstance")
| project PreciseTimeStamp, Message
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `Message contains "CreatePluginComplete"`

---

### Node Update Event

_Widget purpose:_ Node Update Event - Event Log

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Update > Node Update > General > Node Update Event - Event Log`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable()
| where PreciseTimeStamp  between(starttime .. endtime)
| where NodeId == nodeid
| where not (ProviderName contains "Kernel-Processor" and EventId == 37) // eliminating periodical processor report event every day.
| where not (ProviderName == "Microsoft-Windows-Kernel-PnP") // eliminating PnP messages
// | where not (ProviderName contains "PnP" and EventId == 1010) // eliminating PnP errors. 
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

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### PF Updates on ServiceVersionSwitch

_Widget purpose:_ PF Service Update - ServiceVersionSwitch

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Update > Node Update > General > PF Service Update - ServiceVersionSwitch`

```kusto
ServiceVersionSwitch 
| where NodeId == nodeid and PreciseTimeStamp between ((starttime - 1h) .. (endtime + 1h))
| project PreciseTimeStamp, ServiceName, CurrentVersion, NewVersion, SourceOfService
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Scheduled Events from AzPEWorkflowEvent

_Widget purpose:_ Scheduled Event for HostUpdate - AzPEWorkflowEvent

Cluster: `azpe` · Database: `azpe` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Update > Node Update > General > Scheduled Event for HostUpdate - AzPEWorkflowEvent`

```kusto
AzPEWorkflowEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where WorkflowId contains nodeid
| where WorkflowType == "OM"
| where EntityId contains "AzPEHostUpdateMonitor"
| project PreciseTimeStamp, WorkflowInstanceGuid, WorkflowId, WorkflowType, WorkflowEventData
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `WorkflowType == "OM"` · `EntityId contains "AzPEHostUpdateMonitor"`

---

### Query OsUpdateManagerEvents

_Widget purpose:_ OsUpdateManagerEvents 

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Node Update > Node Update > OSHP Details > OsUpdateManagerEvents `

```kusto
OsUpdateManagerEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project StartTime = todatetime(StartTime), TimeTaken, MessageType, Description
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query HostAgentEventsEtwTable

_Widget purpose:_ HostAgentEventsEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > HostAgentEventsEtwTable > HostAgentEventsEtwTable`

```kusto
cluster('azcore.centralus').database('Fa').HostAgentEventsEtwTable()
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, ProviderName, OpcodeName, Pid, TaskName, Message, Context, AgentPackage
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### HostGAPluginContextActivityLogs

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > HostGAPlugin > HostGAPluginContextActivityLogs`

```kusto
HostGAPluginContextActivityLogs
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, RequestId, CorrelationId, HResult, Message, Operation, FunctionName, EventTime
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### HostGAPluginRestApiLogs

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > HostGAPlugin > HostGAPluginRestApiLogs`

```kusto
HostGAPluginRestApiLogs
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query IfxOperationV2v1EtwTable

_Widget purpose:_ IfxOperationV2v1EtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > Ifx Operation > IfxOperationV2v1EtwTable`

```kusto
IfxOperationV2v1EtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNode  
| extend DurationInSeconds = DurationIn100ns/10000000.0
| extend StartTime = TIMESTAMP-(DurationInSeconds*1s)
| project StartTime, EndTime = TIMESTAMP, OperationName, RoleClass, ResultType, DurationInSeconds, ResultSignature, ContextInCsv, ActivityId, ParentActivityId, RootOperationId
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNode}`

---

### Query Heartbeat in MetadataServerLogTable

_Widget purpose:_ IMDS HeartBeat - MetadataServerLogTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > IMDS > IMDS > IMDS HeartBeat - MetadataServerLogTable`

```kusto
MetadataServerLogTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| where message startswith "Heartbeat"
| extend StartupId = extract("startup_id=([0-9a-zA-Z-]*)", 1, message)
| extend Build = extract("build=([0-9.]*)", 1, message)
| extend Package = extract("pkg=([0-9a-zA-z-_/\\.]*)", 1, message)
| extend PFRolloutPhase = extract("phase=([0-9a-zA-Z]*)", 1, message)
| extend ClusterClass = extract("class=([0-9a-zA-Z]*)", 1, message)
| extend ApiVersions = extract("schemas=([0-9a-z-_/]*)", 1, message)
| extend ClusterGeneration = extract("gen=([0-9a-zA-Z]*)", 1, message)
| extend ClusterType = extract("environ=([0-9a-zA-Z]*)", 1, message)
| extend NodeRole = extract("role=([0-9a-zA-Z]*)", 1, message)
| extend Sequence = extract("seq=([0-9]*)", 1, message, typeof(int))
| extend IsPf = Package startswith "MetadataServerPF"
| project PreciseTimeStamp, Sequence, Environment, Region, Cluster, DataCenter, NodeId, IsPf, NodeIdentity, StartupId, Build, Package, ApiVersions, PFRolloutPhase, ClusterClass, ClusterGeneration, ClusterType, NodeRole
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `message startswith "Heartbeat"`

---

### Query MetadataServerLogTable

_Widget purpose:_ IMDS Requests - MetadataServerLogTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > IMDS > IMDS > IMDS Requests - MetadataServerLogTable`

```kusto
union (MetadataServerLogTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| where message startswith "Request "
| where message contains "Starting for requested url"
| where (queryTargetContainerOnly == false) or (message contains queryContainerId)
| extend action = "Start"
| extend ContainerId = extract("(cid|Container)=([0-9a-zA-Z-]*)", 2, message) 
| where ContainerId != "" and ContainerId != "42" // This is for filtering out local xping and warmer queries respectively
| extend Url = extract("url: ([^?]*)", 1, message)
| extend RequestId = extract("Request ([0-9]*):", 1, message, typeof(int))
| extend ApiVersion = extract("api-version=([0-9a-z-]*)", 1, message)
| extend Trace = extract("Trace: ([0-9a-z-]*)", 1, message)
| project PreciseTimeStamp, action, ContainerId, Url, RequestId, ApiVersion, Trace), (
MetadataServerLogTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| where (queryTargetContainerOnly == false) or (message contains queryContainerId)
| where message startswith '"Request'
| where message has "Complete"
| extend action = "Complete"
| extend ContainerId = extract("(cid|Container)=([0-9a-zA-Z-]*)", 2, message) 
| where ContainerId != "" and ContainerId != "42" // This is for filtering out local xping and warmer queries respectively
| extend Url = extract("Url=\"\"([^\"]*)\"\"", 1, message)
// | where Url !contains "health" // This is for filtering out health queries
| extend Build = extract("Build=([0-9.]*)", 1, message)
| extend RequestId = extract("Request ([0-9]*):", 1, message, typeof(int))
| extend ResponseTimeInMs = extract("Response Time=([0-9]*)ms", 1, message, typeof(int))
| extend ResponseSizeInBytes = extract("Response size=([0-9]*)", 1, message, typeof(int))
| extend ApiVersion = extract("ApiVersion=([0-9a-z-]*)", 1, message)
| extend LocalAddress = extract("LocalAddr=([0-9.]*)", 1, message)
| extend RemoteAddress = extract("RemoteAddr=([0-9.]*)", 1, message)
| extend StatusCode = extract("Status-code=([0-9]{3})", 1, message, typeof(int))
| extend UserAgent = extract("User-Agent=\"\"([^\"]*)\"\"", 1, message)
| extend level = case (
    StatusCode >= 500, "Critical", 
    StatusCode >= 400, "Error", 
    StatusCode >= 300, "Warning", 
    "Info")
| project PreciseTimeStamp, RequestId, action, ContainerId, Build, ApiVersion, Url, StatusCode, LocalAddress, RemoteAddress, ResponseTimeInMs, ResponseSizeInBytes, UserAgent, level
)
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`, `{queryTargetContainerOnly}`

**Signal filters seen in KQL:** `message startswith "Request "` · `message contains "Starting for requested url"` · `message startswith ""Request"` · `message has "Complete"`

---

### Query Error in MetadataServerLogTable

_Widget purpose:_ Query Error or Specific Request in MetadataServerLogTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > IMDS > IMDS > Query Error or Specific Request in MetadataServerLogTable`

```kusto
MetadataServerLogTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where (isempty(queryFilterKeyword) and tagId contains "LogError") or (isnotempty(queryFilterKeyword) and message contains queryFilterKeyword)
| project PreciseTimeStamp, tagId, message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryFilterKeyword}`

---

### Query OsLoggerTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > OS Logger > OS Logger`

```kusto
OsLoggerTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| extend level = LogErrorLevel
| project PreciseTimeStamp, ProcessId, ThreadId, ComponentName, SubComponentName, FileName, FunctionName, LineNumber, LogErrorLevel, ResultCode, ErrorDetails, level
| sort by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Pool Memory Details

_Widget purpose:_ Details of Pool Memory Usage

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > Pool Memory (Kernel) > Pool Memory (Kernel) > Details of Pool Memory Usage`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').OsPoolMonTable
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId == nodeid
| where Tag <> "TagsCount"
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, Rank, Tag, Type, Allocs, Frees, Diff, Bytes, PerAlloc
| join kind=leftouter(
    cluster('rdos.kusto.windows.net').database('rdos').OsPoolTagDescription
) on $left.Tag == $right.Tag
| order by PreciseTimeStamp asc, Rank asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `Tag <> "TagsCount"`

---

### Kernel Pool Memory Usage

_Widget purpose:_ Non-Paged Pool Memory - Top 15

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > Pool Memory (Kernel) > Pool Memory (Kernel) > Non-Paged Pool Memory - Top 15`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').OsPoolMonTable
| where PreciseTimeStamp between (datetime_add("day", -5, starttime) .. endtime)
| where NodeId == nodeid
| where Tag <> "TagsCount"
| where Type == "Nonp"
| where Rank < 16
//| project PreciseTimeStamp, Rank, Tag, Type, Allocs, Frees, Diff, Bytes, PerAlloc
| order by PreciseTimeStamp asc
| summarize avg(Bytes) by bin (PreciseTimeStamp, 1d), Tag
```

**Params:** `{starttime}`, `{nodeid}`, `{endtime}`

**Signal filters seen in KQL:** `Tag <> "TagsCount"` · `Type == "Nonp"`

---

### Paged Pool Memory

_Widget purpose:_ Paged Pool Memory - Top 15

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > Pool Memory (Kernel) > Pool Memory (Kernel) > Paged Pool Memory - Top 15`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').OsPoolMonTable
| where PreciseTimeStamp between (datetime_add("day", -5, starttime) .. endtime)
| where NodeId == nodeid
| where Tag <> "TagsCount"
| where Type == "Paged"
| where Rank < 16
//| project PreciseTimeStamp, Rank, Tag, Type, Allocs, Frees, Diff, Bytes, PerAlloc
| order by PreciseTimeStamp asc
| summarize avg(Bytes) by bin (PreciseTimeStamp, 1d), Tag
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `Tag <> "TagsCount"` · `Type == "Paged"`

---

### VMServiceEvents

_Widget purpose:_ VM Service - Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > VM Service (VMAL) > VM Service (VMAL) > VM Service - Events`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmServiceEventsEtwTable()
| where (PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime)  
| where NodeId == nodeid
| project PreciseTimeStamp, Level, Cluster, Message, Context, ContainerId, NodeId, ActivityId, AgentPackage
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### VMServiceContainerOperations

_Widget purpose:_ VM Service - Operations

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > VM Service (VMAL) > VM Service (VMAL) > VM Service - Operations`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmServiceContainerOperations
| where (PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime)  
| where NodeId == nodeid
// | where Operation !contains "Query"
// | where ContainerId == "{containerid}"
| project PreciseTimeStamp, Level, Cluster, Operation, Stage, ResultCode, DurationMillis, ContainerId, NodeId, StartTime, EndTime
| order by StartTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ContainerId == "{containerid}"`

---

### Query VmServiceVirtualDiskOperations

_Widget purpose:_ VmServiceVirtualDiskOperations

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > VM Service (VMAL) > VM Service (VMAL) > VmServiceVirtualDiskOperations`

```kusto
VmServiceVirtualDiskOperations
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### wireserverheartbeat

_Widget purpose:_ Wireserver Heartbeat

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > Wireserver > Wireserver > Wireserver Heartbeat`

```kusto
WireserverHeartbeatEtwTable
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId == nodeid
| project PreciseTimeStamp, Status, Pid
| sort by PreciseTimeStamp asc
| serialize 
| extend prevTime = case (isnotempty(prev(PreciseTimeStamp)), prev(PreciseTimeStamp), starttime)
| extend prevDiff = PreciseTimeStamp - prevTime
| extend Health = case ( (prevDiff >= 62s and prevDiff != 0s and isnotempty(prev(PreciseTimeStamp))), "Unhealthy", "Healthy")
| extend flag = case (Health <> prev(Health), "changed" , "")
| where flag <> ""
| extend Content = Health
| extend StartTime = case (isnotempty(prevTime), prevTime, starttime)
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), endtime)
| project StartTime, EndTime, Content, prevDiff, Pid
```

**Params:** `{nodeid}`, `{starttime}`, `{endtime}`

---

### Query WireserverHttpRequestLogEtwTable

_Widget purpose:_ Wireserver Request Log

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node (Software) > Node (Software) > Other Agents / Logs > Wireserver > Wireserver > Wireserver Request Log`

```kusto
WireserverHttpRequestLogEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| where queryQueryCheckContainerOnly == false or ContainerId =~ queryContainerd
| extend level = case (
    ResponseStatusCode >= 500, "Critical", 
    ResponseStatusCode >= 400, "Error", 
    ResponseStatusCode >= 300, "Warning", 
    "Info")
| project PreciseTimeStamp, ContainerId, ClientId, ClientRequestId, RequestUrl, RequestType, ResponseStatusCode, RequestStartTime, RequestProcessingTimeInMS, level
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerd}`, `{queryQueryCheckContainerOnly}`

---
