# Start Page

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Start Page** (83 queries).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## Start Page

### Fabricator Instance

_Widget purpose:_ Cluster Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Cluster Health`

```kusto
cluster('azcsupfollower').database('AzureCM').LogClusterSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
| where tenantName == cluster
| order by PreciseTimeStamp asc 
| project StartTime = PreciseTimeStamp, tenantName, roleInstanceName
| extend flag = case (prev(roleInstanceName) <> roleInstanceName, "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), endtime)
| extend Content = roleInstanceName
| extend Health = "Neutral"
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Fabricator Downtime

_Widget purpose:_ Cluster Health

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Cluster Health`

```kusto
let clusters = print Tenant = cluster;
FabricFailoverDowtimeRawDataPerCluster(clusters=clusters, startTime=starttime, endTime=endtime)
| project StartTime = DownTimeStart, EndTime = DownTimeEnd, Content = strcat(tostring(DurationInMs/1000), " secs"), Health = "Unhealthy"
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Allocatable State

_Widget purpose:_ Cluster Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Cluster Health`

```kusto
cluster('azcsupfollower').database('AzureCM').LogClusterCapacity
| where PreciseTimeStamp between (starttime .. endtime)
| where Tenant == cluster
| project PreciseTimeStamp, categoryByMachinePoolNameJson, isAcceptedNewDeployment = tostring(parse_json(newDeploymentStatusJson).isAcceptingNewDeployments), rejectReason = tostring(parse_json(newDeploymentStatusJson).rejectReason)
| order by PreciseTimeStamp asc
| extend flag = case (prev(isAcceptedNewDeployment) <> isAcceptedNewDeployment, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp, Content = ""
| extend EndTime = case (isnotempty(next(isAcceptedNewDeployment)), next(PreciseTimeStamp), endtime)
| extend Health = case (isAcceptedNewDeployment == "true", "healthy", 
    isAcceptedNewDeployment == "false", "unhealthy", 
    "degraded")
| project StartTime, EndTime, Content, Health
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Cluster Planned Maintenance

_Widget purpose:_ Cluster Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Cluster Health`

```kusto
cluster('azcsupfollower').database('AzureCM').MaintenancePhaseDetails
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where Tenant == queryClusterName
 | project PreciseTimeStamp, phaseId, todatetime(startTimeUTC), todatetime(endTimeUTC), maintenanceOperationType, scheduledMaintenanceId
 | order by PreciseTimeStamp asc
| extend flag = case (prev(scheduledMaintenanceId) <> scheduledMaintenanceId, "changed", 
    prev(phaseId) <> phaseId, "changed", 
    "") 
| where flag <> ""
| where queryFrom between(startTimeUTC .. endTimeUTC) or queryTo between(startTimeUTC .. endTimeUTC)
| extend StartTime = max_of(queryFrom, startTimeUTC)
| extend EndTime = min_of(queryTo, endTimeUTC)
| extend Health = "degraded" 
| extend Content = maintenanceOperationType
| join kind=leftouter cluster("Icmcluster.kusto.windows.net").database("ACM.Backend").PublishRequest on $left.scheduledMaintenanceId==$right.ExternalIncidentId
| extend AdditionalProperties = parse_json(AdditionalProperties)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryClusterName}`

---

### Cluster Service Healing

_Widget purpose:_ Cluster Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `Aplat` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Cluster Health`

```kusto
MycroftClusterSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where ClusterName == queryClusterName
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, IsClusterServiceHealingDisabled, Content = iif(IsClusterServiceHealingDisabled == true, "Disabled", "Enabled")
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = iif(IsClusterServiceHealingDisabled == false, "Healthy", "Unhealthy")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryClusterName}`

---

### Container State

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp  between (starttime .. endtime)
| where (isnotempty(_vmid) and VirtualMachineUniqueId == _vmid) or (isempty(_vmid) and ContainerId == _containerid)
| project PreciseTimeStamp, ClusterName, RoleInstanceName,  TenantName, ContainerId, NodeId, 
  ContainerState, ActualOperationalState, LifecycleState, OsState, FaultInfo , VirtualMachineUniqueId
| project StartTime = PreciseTimeStamp, Content = ContainerState, LifecycleState, ClusterName, TenantName, ContainerId, NodeId, VirtualMachineUniqueId
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> "" or LifecycleState == "Destroyed"
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), endtime)
| where LifecycleState <> "Destroyed"
| extend Health = case (Content in ("ContainerStateUnresponsive", "ContainerStateUnhealthy", "ContainerStateUnknown"), "Unhealthy", Content == "ContainerStateStarted", "Healthy", "Degraded")
//| extend GroupBy = strcat("Container (", substring(containerId, 0, 8), "~)")
| project StartTime, EndTime, Content, Health //, GroupBy
```

**Params:** `{starttime}`, `{endtime}`, `{_vmid}`, `{_containerid}`

**Signal filters seen in KQL:** `LifecycleState <> "Destroyed"`

---

### Container OS State

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus` · Database: `azurecp` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp  between (starttime .. endtime)
| where (isnotempty(_vmid) and VirtualMachineUniqueId == _vmid) or (isempty(_vmid) and ContainerId == _containerid)
| project PreciseTimeStamp, ClusterName, RoleInstanceName,  TenantName, ContainerId, NodeId, 
  ContainerState, ActualOperationalState, LifecycleState, OsState, FaultInfo , VirtualMachineUniqueId
| project StartTime = PreciseTimeStamp, Content = OsState, LifecycleState, ContainerId
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> "" or LifecycleState == "Destroyed"
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), endtime)
| where LifecycleState <> "Destroyed"
| extend Health = case (Content in ("ContainerOsStateUnknown", "ContainerOsStateUnresponsive", "ContainerOsStateUnhealthy"), "Unhealthy", 
    Content in ("ContainerOsStateHealthy", "ContainerOsStateProvisioningCompleted"), "Healthy", 
    Content in ("ContainerOsStateInternalShutdown", "ContainerOsStateProvisioningTimedOut", "ContainerOsStateProvisioningRecovery", "ContainerOsStateProvisioningFailed"), "Degraded", 
    "Neutral")
//| extend GroupBy = strcat("ContainerOs (", substring(containerId, 0, 8), "~)")
| project StartTime, EndTime, Content, Health //, GroupBy
```

**Params:** `{starttime}`, `{endtime}`, `{_vmid}`, `{_containerid}`

**Signal filters seen in KQL:** `LifecycleState <> "Destroyed"`

---

### Hyper-V Heartbeat State

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").VmHealthRawStateEtwTable
| where PreciseTimeStamp between (queryStart .. queryEnd)
| where VirtualMachineUniqueId == queryVmUniqueId or ContainerId == queryContainerId
| where VmContext <> 'NotImplemented'
| project  StartTime = PreciseTimeStamp, IsVscStateOperational, Content = VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted, Context, ContainerId
| order by StartTime asc
| extend flag = case (
    ContainerId <> next(ContainerId), 'ended', 
    Content != prev(Content) 
    or VmPowerState != prev(VmPowerState)
    or Context != prev(Context) 
    or HasHyperVHandshakeCompleted != prev(HasHyperVHandshakeCompleted)
    or Content != prev(Content), "changed", '')
| where flag <> ""
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), queryEnd)
| extend flag1 = case((next(Content) != Content and prev(Content) == Content) or flag == 'ended', 1 ,0)
| extend Health = case (Content in ("HeartBeatStateNoContact", "HeartBeatStateNonRecoverableError", "HeartBeatStateLostCommunication"), "Unhealthy", 
    (Content == "HeartBeatStateOk" and VmPowerState == "PowerStateEnabled" and HasHyperVHandshakeCompleted == "true"), "Healthy", 
    Content in ("NotMonitored", "HeartBeatStateDegraded"), "Degraded", 
    "Neutral")
| where flag1 <> 1
| project StartTime, EndTime, Content, Health, VmPowerState, HasHyperVHandshakeCompleted, Context, ContainerId
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryVmUniqueId}`, `{queryContainerId}`

**Signal filters seen in KQL:** `VmContext <> "NotImplemented"`

---

### Hyper-V Power State

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").VmHealthRawStateEtwTable
| where PreciseTimeStamp between (queryStart .. queryEnd)
| where ContainerId == queryContainerId or (isnotempty(VirtualMachineUniqueId) and VirtualMachineUniqueId == queryVmUniqueId)
| project  StartTime = PreciseTimeStamp, Content = VmPowerState, HasHyperVHandshakeCompleted, Context, ContainerId
| order by StartTime asc
| extend flag = case (ContainerId <> next(ContainerId), 'ended', 
    Content != prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), datetime(null))
| where flag <> "ended"
| extend Health = case (Content in ("EnabledStateStopping", "EnabledStatePaused", "EnabledStateDisabled","EnabledStateStarting"), "Unexpected VM restart", 
    (Content == "PowerStateEnabled"), "Healthy", 
    Content in ("NotMonitored", "PowerStateUnknown"), "Degraded", 
    "Neutral")
| project StartTime, EndTime, Health,  Content, HasHyperVHandshakeCompleted, Context
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryVmUniqueId}`, `{queryContainerId}`

**Signal filters seen in KQL:** `flag <> "ended"`

---

### VMAvailabilityMetric

_Widget purpose:_ Container / Tenant Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
let queryShoeboxAccount = toscalar(cluster('azurecm.kusto.windows.net').database('AzureCM').LogClusterSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Tenant == queryCluster
| project shoeboxMdmAccountName
| take 1);
let query = strcat(@"metricNamespace('Shoebox').metric('VMAvailabilityMetric').dimensions('resourceId').samplingTypes('Average', 'Count') | where resourceId == '", queryVmId, "'");
evaluate geneva_metrics_request(queryShoeboxAccount, query, queryFrom, queryTo)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = todatetime(column_ifexists("TimestampUtc", 0)), Availability = column_ifexists("Average", 0)
| order by TimestampUtc asc
// for debug
//| extend Availability = case (TimestampUtc between (datetime(2025-04-22 00:04:00.0000000) .. datetime(2025-04-22 00:10:00.0000000)), 0, 1)
//| where not (TimestampUtc between (datetime(2025-04-22 20:00:00.0000000) .. datetime(2025-04-22 23:00:00.0000000)))
| extend flag = case ((TimestampUtc - 1m) <> prev(TimestampUtc) or Availability <> prev(Availability), 'begin', '')
| extend flag = case (flag == '' and next(flag) == 'begin', 'end', 
                      isempty(next(TimestampUtc)), 'end', flag)
| where flag <> ''
| extend StartTime = iff(flag == 'begin', TimestampUtc, datetime(null))
| extend EndTime = iff(flag == 'begin', next(TimestampUtc), datetime(null))
| where flag <> 'end'
| extend Health = iff (Availability == 1, 'Healthy', 'Unhealthy')
| extend Content = Health
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCluster}`, `{queryVmId}`

**Signal filters seen in KQL:** `resourceId == "", queryVmId, ""` · `flag <> "end"`

---

### Container Lifecycle

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
//| where containerId == containerid
// | where virtualMachineUniqueId == _vmid or containerId == _containerid
| where (isnotempty(_vmid) and VirtualMachineUniqueId == _vmid) or (isempty(_vmid) and ContainerId == _containerid)
| where LifecycleState <> "Alive"
| project StartTime = PreciseTimeStamp, ClusterName, RoleInstanceName,  TenantName, ContainerId, NodeId, 
  ContainerState, ActualOperationalState, LifecycleState, OsState, FaultInfo , VirtualMachineUniqueId
| order by StartTime asc
| extend flag = case (ContainerState <> prev(ContainerState) or ActualOperationalState <> prev(ActualOperationalState) or LifecycleState <> prev(LifecycleState) or OsState <> prev(OsState) or FaultInfo <> prev(FaultInfo), "changed", "")
| where flag <> ""
// | extend level = case (containerOsState in ("ContainerOsStateUnknown", "ContainerOsStateUnresponsive", "ContainerOsStateUnhealthy"), "critical", 
//    containerOsState in ("ContainerOsStateHealthy", "ContainerOsStateProvisioningCompleted"), "info", 
//    containerOsState in ("ContainerOsStateInternalShutdown", "ContainerOsStateProvisioningTimedOut", "ContainerOsStateProvisioningRecovery", "ContainerOsStateProvisioningFailed"), "error", 
//    "warning")
| extend Content = LifecycleState
```

**Params:** `{starttime}`, `{endtime}`, `{_vmid}`, `{_containerid}`

**Signal filters seen in KQL:** `LifecycleState <> "Alive"`

---

### Container Fault

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where (isnotempty(queryVMID) and VirtualMachineUniqueId == queryVMID) or (isempty(queryVMID) and ContainerId == queryContainerId)
| order by PreciseTimeStamp asc
| extend Health = iif(isnotempty(FaultInfo),  "Unhealthy", "Healthy")
| extend flag = case (FaultInfo <> prev(FaultInfo), "start", FaultInfo <> next(FaultInfo), "end", "")
| where flag <> ""
| extend EndTime = case (flag == "start" and isnotnull(next(flag)), next(PreciseTimeStamp), flag == "end", PreciseTimeStamp, queryTo)
| where flag <> "end"
| where isnotempty(FaultInfo)
| extend fault = parse_json(FaultInfo)
| project StartTime = PreciseTimeStamp, EndTime, Content = tostring(fault.FaultCode), ContainerId, Health, 
    faultReason = tostring(fault.Reason), FabricOperationString = tostring(fault.FabricOperationString), faultInfo = fault
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryVMID}`

**Signal filters seen in KQL:** `flag <> "end"`

---

### Node Service Error - Container

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').NodeServiceOperationEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where NodeId == queryNodeId
| where Identifier contains queryContainerId
| where OperationName !contains "Query"
| where Result <> 1
| extend ResultCode = tohex(toint(ResultCode), 8), Health = "Unhealthy"
| extend Content = strcat ("0x", ResultCode)
| project StartTime = RequestTime, EndTime = CompleteTime, OperationName, Identifier, Result, ResultCode, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

---

### VMAL Ops

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
VmServiceContainerOperations
| where PreciseTimeStamp between ( queryFrom .. queryTo)  
| where NodeId == queryNodeId
| where ContainerId == queryContainerId
// | where ResultCode !in ("0x0", "0x1")
| extend Content = ResultCode
| extend Health = iff (ResultCode !in ("0x0", "0x1"), "Unhealthy", "Healthy")
| project StartTime, EndTime, DurationMillis, Cluster, Level, Operation, Stage, ResultCode, ContainerId, NodeId, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`

---

### Hyper-V Events

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
let hypervvmid = toscalar(cluster('azcore.centralus.kusto.windows.net').database('Fa').OsHyperVWorkerAdminEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| where VmName == queryContainerId
| top 1 by PreciseTimeStamp
| project VmId);
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where Description contains queryContainerId or (isnotempty(hypervvmid) and Description contains hypervvmid)
| extend EventId = tolong(EventId) 
| where (ProviderName == "Microsoft-Windows-Hyper-V-Worker" and EventId in (18500, 18502, 18504, 18508, 18512, 18514, 18550, 18560, 18570, 18572, 18590, 18602, 18190, 33100, 33103, 33104, 33107, 33108)) or
    (ProviderName == "Microsoft-Windows-Hyper-V-SynthNic" and EventId in (12590, 12586, 12614, 12584, 12588)) or 
    (ProviderName == "Microsoft-Windows-Hyper-V-VID") or
    (ProviderName == 'Microsoft-Windows-Hyper-V-Chipset') and EventId in (1570, 18600) or
    (ProviderName == "Microsoft-Windows-Hyper-V-VMMS" and Level < 4)
| extend GroupBy = case (
    ProviderName == "Microsoft-Windows-Hyper-V-Worker", "Hyper-V Worker Events",
    ProviderName == "Microsoft-Windows-Hyper-V-SynthNic", "Hyper-V SynthNic Events",
    ProviderName == "Microsoft-Windows-Hyper-V-VID", "Hyper-V VID Events",
    ProviderName == "Microsoft-Windows-Hyper-V-VMMS", "Hyper-V VMMS Events",
    ProviderName == "Microsoft-Windows-Hyper-V-Chipset", "Hyper-V Chipset Events",
    ""
    )
| extend Content = case (
    // SynthNic
    EventId == 12590, "(12590) SynthNic - Unassgined a VF", 
    EventId == 12586, "(12586) SynthNic - Freed a VF", 
    EventId == 12614, "(12614) SynthNic - VF allocation delay", 
    EventId == 12584, "(12584) SynthNic - Allocated a VF", 
    EventId == 12588, "(12588) SynthNic - Assigned a VF", 
    // Worker
    EventId == 18190, "(18190) Worker process health is critical for Guest VM", 
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
    EventId == 18602, "(18602) Bugcheck of Guest VM",
    // VID
    EventId == 5043, "(5043) One or more corrected memory error. The page has been replaced",
    EventId == 5042, "(5042) One or more corrected memory error. The page could not be replaced",  
    // Chipset
    EventId == 1570, "(1570) VTL crash",
    EventId == 18600, "(18600) Watchdog Timeout",
    tostring(EventId))
| extend Health = case(EventId in (12584, 12588, 18500), "Neutral", EventId in (12590, 12586, 12614), "Degraded", 
    case(Level == 1, "Error", Level == 2, "Unhealthy", Level == 3, "Degraded", "Neutral")) 
| project StartTime = todatetime(TimeCreated), GroupBy, Content, Health, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`

---

### Hyper-V StorageStack

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVStorageStackTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventId == 9 
| where EventMessage contains queryContainerId
// | where Function in ('NvmdControllerStop', 'NvmdControllerStart')
// | where Message contains 'Stopping Physical Controller'
| where ProviderName == 'Microsoft-Windows-Hyper-V-StorageVSP'
| project PreciseTimeStamp, Level, ProviderName, EventId, Message
| extend Resource = tostring(parse_json(Message).DeviceName)
| summarize Count = count() by bin(PreciseTimeStamp, 1s), Level, ProviderName, EventId, Resource
| extend Health = 'Unhealthy'
| extend ExMessage = 'IO operation took over 10 secs'
| project StartTime = PreciseTimeStamp - 10s, EndTime = PreciseTimeStamp, Level, ProviderName, EventId, ExMessage, Resource, Count, Health, Content = strcat('IO Delay (', Count, ' counts)')
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Message contains "Stopping Physical Controller"` · `ProviderName == "Microsoft-Windows-Hyper-V-StorageVSP"`

---

### Tenant Scheduled Events

_Widget purpose:_ Container / Tenant Health

Cluster: `azpe` · Database: `azpe` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
cluster("azpe.kusto.windows.net").database("azpe").AzPEWorkflowEvent 
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where EntityId == queryTenantName    
| extend impactedInstances = tostring((parse_json(WorkflowEventData).Containers))
| project StartTime = PreciseTimeStamp,  impactedInstances, WorkflowInstanceGuid, WorkflowType, WorkflowEventType, WorkflowId, WorkflowEventData
//| project StartTime = PreciseTimeStamp, AzPEWorkflowId, WorkflowType, impactedInstances, WorkflowEventType, EventId, TenantManagementJobMessage, WorkflowEventData 
| extend Content = strcat (WorkflowType, " - ", WorkflowEventType), Health = iif (impactedInstances contains queryInstanceName, "Degraded", "Neutral")
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryInstanceName}`

---

### Anvil Event - Container

_Widget purpose:_ Container / Tenant Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (starttime .. endtime)
| where ResourceId == _nodeid or ResourceId == _containerid or ResourceId == _tenantname
| where MessageTrigger contains "OnBeforeWalkTree"
| project PreciseTimeStamp, Cluster, Role, MessageTrigger, TreeName, TreeNodeKey, TreeActionName, TreeActionInput, Properties, TaskStatus, Message, ResourceId, ResourceType, ResourceDependencies
| order by PreciseTimeStamp asc 
| extend StartTime = PreciseTimeStamp
| extend FaultCodeString = parse_json(Message).RepairContext.FaultCodeString
| extend Content = tostring(FaultCodeString)
```

**Params:** `{starttime}`, `{endtime}`, `{_nodeid}`, `{_containerid}`, `{_tenantname}`

**Signal filters seen in KQL:** `MessageTrigger contains "OnBeforeWalkTree"`

---

### Container Live Migration

_Widget purpose:_ Container / Tenant Health

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
let containers = cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogContainerSnapshot
    | where PreciseTimeStamp between(queryFrom ..queryTo)
    | where (isnotempty(vmid) and virtualMachineUniqueId == vmid) or (isempty(vmid) and containerId == queryContainerId)
    | distinct containerId;
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LiveMigrationSessionCompleteLog
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where sourceContainerId in (containers)
| extend elapsedSec = totimespan(elapsedTime) / 1s
| extend Health = case (status == "Completed", "Healthy", status == "Faulted" , "Unhealthy", "Degraded")
| extend Content = triggerType
| extend StartTime = PreciseTimeStamp - totimespan(elapsedTime)
| project StartTime, EndTime = PreciseTimeStamp, Health, Content, sessionId, status, elapsedTime, reason, message, sourceContainerId, sourceNodeId, destinationContainerId, destinationNodeId
| join kind=leftouter (cluster("azcsupfollower.kusto.windows.net").database("Air").LiveMigrationFailureEvents
| where EventTime between (queryFrom .. queryTo)
| where ObjectId in (containers)
| project RCALevel1, RCALevel2, Diagnostics = parse_json(Diagnostics), sessionId = tostring(parse_json(Diagnostics)["SessionId"])) on sessionId
| project-away sessionId1
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmid}`, `{queryContainerId}`

---

### Service Healing(TM)

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fc').ServiceHealingTriggerEtwTable
| where PreciseTimeStamp between (starttime .. endtime)
| where TenantName == tenantName
| where RoleInstanceName contains roleInstanceName
| parse RoleInstanceName with "Name:" VMName ";RoleType" * 
| where VMName =~ roleInstanceName
// | where RoleInstanceName !contains "_IN_"
| project StartTime = PreciseTimeStamp, Tenant, VMName, TriggerId, TriggerObjectId, TriggerType, FaultInfoFabricOperation, TenantName, 
  RoleInstanceName, Region
| extend Content = TriggerType, Health = "Unhealthy"
```

**Params:** `{starttime}`, `{endtime}`, `{roleInstanceName}`, `{tenantName}`

---

### Service Healing(AzSM)

_Widget purpose:_ Container / Tenant Health

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between(starttime .. endtime)
| where tenantName =~ queryTenantName
| where triggerObjectId == queryContainerId
| order by PreciseTimeStamp asc
| summarize StartTime = min(PreciseTimeStamp), arg_max(PreciseTimeStamp, triggerType, faultCode, faultReason, faultCode) by triggerId
| join kind=leftouter (AzSMServiceHealingStepResultEvents
    | where PreciseTimeStamp between(starttime .. endtime)
    | where tenantName == queryTenantName
    | summarize EndTime = max(PreciseTimeStamp), arg_max(PreciseTimeStamp, result) by triggerId, failureReason, targetContainerId 
) on triggerId
| project StartTime, EndTime, triggerType, triggerId, faultReason, targetContainerId, result
| extend Health = iif (result != "Succeeded", "Error", "Degraded")
| extend Content = triggerType
```

**Params:** `{starttime}`, `{endtime}`, `{queryTenantName}`, `{queryContainerId}`

---

### Planned Maintenance

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
let maintenanceInformation = cluster('azcore.centralus.kusto.windows.net').database('Fc').ScheduledMaintenanceInformational
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where Tenant == queryClusterName
| where traceCode == "ScheduledMaintenance_BuildMaintenanceInformation_Succeeded"
| where message contains queryRoleInstanceName and message contains queryTenantName
| where message contains "MaintenanceInformation"
| parse message with * "for scheduled maintenance id: '" maintenanceId:string  "'. Elapsed time" * 
    "IsCustomerInitiatedMaintenanceAllowed: '" IsCustomerInitiatedMaintenanceAllowed:bool "'\r\n "
    "ControlledMaintenanceResultCode: '" ControlledMaintenanceResultCode:string "'\r\n "
    "ControlledMaintenanceResultCodeDetails: '" ControlledMaintenanceResultCodeDetails:string "'\r\n "
    "ControlledMaintenancePhaseStartTimeInUTC: '" ControlledMaintenancePhaseStartTimeInUTC:datetime "'\r\n "
    "ControlledMaintenancePhaseEndTimeInUTC: '" ControlledMaintenancePhaseEndTimeInUTC:datetime "'\r\n "
    "FabricMaintenanceOperationStartTimeInUTC: '" FabricMaintenanceOperationStartTimeInUTC:datetime "'\r\n "
    "FabricMaintenanceOperationEndTimeInUTC: '" FabricMaintenanceOperationEndTimeInUTC:datetime "'\r\n "
    "MaintenanceType: '" MaintenanceType:string "'\r\n "
    "ResourceMaintenanceType: '" ResourceMaintenanceType:string "'\r\n " *
| project PreciseTimeStamp, message, maintenanceId, IsCustomerInitiatedMaintenanceAllowed, ControlledMaintenanceResultCode, ControlledMaintenanceResultCodeDetails, 
    ControlledMaintenancePhaseStartTimeInUTC, ControlledMaintenancePhaseEndTimeInUTC,
    FabricMaintenanceOperationStartTimeInUTC, FabricMaintenanceOperationEndTimeInUTC,
    MaintenanceType, ResourceMaintenanceType
| distinct message, maintenanceId, IsCustomerInitiatedMaintenanceAllowed, ControlledMaintenanceResultCode, ControlledMaintenanceResultCodeDetails, 
    ControlledMaintenancePhaseStartTimeInUTC, ControlledMaintenancePhaseEndTimeInUTC,
    FabricMaintenanceOperationStartTimeInUTC, FabricMaintenanceOperationEndTimeInUTC,
    MaintenanceType, ResourceMaintenanceType;
union
(maintenanceInformation
| extend StartTime = todatetime(ControlledMaintenancePhaseStartTimeInUTC), EndTime = todatetime(ControlledMaintenancePhaseEndTimeInUTC), Phase = "Customer Controlled Maintenance Phase"),
(maintenanceInformation
| extend StartTime = todatetime(FabricMaintenanceOperationStartTimeInUTC), EndTime = todatetime(FabricMaintenanceOperationEndTimeInUTC), Phase = "Fabric Maintenance Phase")
| extend Health = case(Phase contains 'Controlled', "Healthy", Phase contains 'Fabric', "Degraded", "Neutral"), Content = strcat(Phase, " - ", MaintenanceType)
| project StartTime, EndTime, Phase, MaintenanceType, ResourceMaintenanceType, maintenanceId, message, Content, Health
| join kind=leftouter cluster("Icmcluster.kusto.windows.net").database("ACM.Backend").PublishRequest on $left.maintenanceId==$right.ExternalIncidentId
| summarize arg_max(CommunicationDateTime, *) by Content, message, ExternalIncidentId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRoleInstanceName}`, `{queryClusterName}`

**Signal filters seen in KQL:** `traceCode == "ScheduledMaintenance_BuildMaintenanceInformation_Succeeded"` · `message contains "MaintenanceInformation"`

---

### Holmes Events

_Widget purpose:_ Container / Tenant Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
cluster('azcsupfollower.kusto.windows.net').database('azureCM').HolmesGoalStateManagerEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where containerId == queryContainerId
| where message startswith "Triggering Holmes action"
| parse message with * "TriggerType:" triggerType:string ";" * "Deadline:" deadline:datetime "called from serviceName" serviceName:string " evaluatorName" evaluatorName:string
| project PreciseTimeStamp, containerId, nodeId, actionType,triggerType, deadline,serviceName, evaluatorName, message
| extend Content = actionType
| extend Health = "Degraded"
| extend StartTime = PreciseTimeStamp
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

**Signal filters seen in KQL:** `message startswith "Triggering Holmes action"`

---

### RH Annotation Report

_Widget purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
RhcAnnotationReportsEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where (isnotempty(queryVMId) and VmId == queryVMId) or (isempty(queryVMId) and ContainerId == queryContainerId)
| project PreciseTimeStamp, VmId, ContainerId, Annotation
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, Content = Annotation, VmId, ContainerId, Annotation
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVMId}`, `{queryContainerId}`

---

### VMA Event

_Widget purpose:_ Container / Tenant Health

Cluster: `vmainsight` · Database: `vmadb` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
cluster("vmainsight.kusto.windows.net").database("vmadb").VMA()
| where PreciseTimeStamp between(queryFrom .. queryTo)
//| where NodeId == nodeid
| where (isnotempty(vmid) and VmUniqueId == vmid) or (isempty(vmid) and ContainerId == queryContainerId)
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1,
  RCALevel2, RCALevel3, E17_StorageAccount, E17_StorageTenant, Network_TOR2 
| order by StartTime asc
| extend durationSec = datetime_diff("Second", EndTime, StartTime)
| extend Content = RCALevel2
| extend Health = iff (RCAEngineCategory == "CustomerInitiated", "Healthy", "Unhealthy")
| join kind=leftouter (
  cluster('vmainsight.kusto.windows.net').database('Air').VmRestartRcaLevel1Level2ArticleMapping
) on $left.RCALevel1 == $right.RCALevel1 and $left.RCALevel2 == $right.RCALevel2
| join kind=leftouter (
  cluster('vmainsight.kusto.windows.net').database('Air').VmRestartArticleCssWikiLinkMapping
) on $left.ArticleId == $right.ArticleId
| project Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, 
  RCALevel2, RCALevel3, E17_StorageAccount, E17_StorageTenant, Network_TOR2, ArticleId, CssWikiLink, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmid}`, `{queryContainerId}`

---

### AIR Events

_Widget purpose:_ Container / Tenant Health

Cluster: `vmainsight` · Database: `Air` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
let _vmid = iff(isempty(queryVmId), "dummyId", queryVmId);
union
(cluster('vmainsight.kusto.windows.net').database('Air').GetVMAvailabilityImpactEvents(VmId = _vmid, startTime = queryFrom, endTime = queryTo)
| project Timestamp, Cluster, RoleInstanceName, EventType, EventSource, ImpactCategory, TenantName, ObjectIds, FailureSignature, FailureDetails, StartTime = ImpactBeginTimeStamp, EndTime = ImpactEndTimeStamp, ImpactDurationTimeSpan, ImpactAIRGroup, InternalArticleId, CssWikiLink 
| extend EventId = tostring(new_guid()), Health="Unhealthy", Content = EventType),
(cluster('vmainsight.kusto.windows.net').database('Air').GetVMDiskBlipEvents(VmId = _vmid, startTime = queryFrom, endTime = queryTo)
| project Timestamp, Cluster, RoleInstanceName, EventType, EventSource, ImpactCategory, TenantName, ObjectIds, FailureSignature, FailureDetails, StartTime = ImpactBeginTimeStamp, EndTime = ImpactEndTimeStamp, ImpactDurationTimeSpan, ImpactAIRGroup, InternalArticleId, CssWikiLink
| extend EventId = tostring(new_guid()), Health="Unhealthy", Content = EventType)
| project StartTime, EndTime, ImpactDurationTimeSpan, EventId, FailureSignature, FailureDetails, ImpactAIRGroup, InternalArticleId, CssWikiLink, Health, Content
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`

---

### ICM Report

_Widget purpose:_ Container / Tenant Health

Cluster: `icmcluster` · Database: `IcMDataWarehouse` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`

```kusto
let devicename = toscalar(cluster('azphynet').database('azdhmds').Servers
| where NodeId =~ queryNodeId
| project DeviceName );
let _torName = toscalar(cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice == devicename
| project NodeName=StartDevice, NodePort=StartPort, NodeSonicPort=StartSonicPort, TorDevice=EndDevice, TorSonicPort=EndSonicPort, BandwidthInGbps, DataCenter
| take 1
| project TorDevice);
let queryTorName = iff(isempty(_torName), "tor00-0000-0000-00t0-dummy", _torName);
cluster('icmcluster.kusto.windows.net').database('IcMDataWarehouse').Incidents
| where CreateDate between (queryFrom .. queryTo)
| where * has queryNodeId or * has queryContainerId or * has queryTenantName or Title contains queryTorName or (Title contains "Too many Unhealthy nodes" and Title contains queryCluster)
| order by ModifiedDate asc
| extend flag = case(IncidentId <> prev(IncidentId), "changed", "")
| where flag <> ""
| extend Content = strcat(iff(IncidentType == "CustomerReported", "CRI", "LSI"), " - ", IncidentId)
| project IncidentId, StartTime = CreateDate, Title, InitialOwningTeam = OwningTeamName, IncidentType, SupportTicketId, SubscriptionId, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`, `{queryTenantName}`, `{queryCluster}`

---

### ContainerStateTransition

_Widget purpose:_ Container Transition

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container Transition`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where (isnotempty(queryVmId) and VirtualMachineUniqueId =~ queryVmId) or (isempty(queryVmId) and ContainerId =~ queryContainerId)
| project StartTime = PreciseTimeStamp, ClusterName, RoleInstanceName,  TenantName, ContainerId, NodeId, 
  Content = ContainerState, ActualOperationalState, LifecycleState, OsState, FaultInfo , VirtualMachineUniqueId
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> "" or LifecycleState == "Destroyed"
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), queryTo)
| where LifecycleState <> "Destroyed"
| extend Health = case (Content in ("ContainerStateUnresponsive", "ContainerStateUnhealthy", "ContainerStateUnknown"), "Unhealthy", Content == "ContainerStateStarted", "Healthy", "Degraded")
| extend GroupBy = strcat("Container (", substring(ContainerId, 0, 8), "~)")
| project StartTime, EndTime, Content, Health, GroupBy, ClusterName, TenantName, ContainerId, NodeId, VirtualMachineUniqueId, RoleInstanceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`, `{queryContainerId}`

**Signal filters seen in KQL:** `LifecycleState <> "Destroyed"`

---

### ContainerOSStateTransition

_Widget purpose:_ Container Transition

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container Transition`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where (isnotempty(queryVmId) and VirtualMachineUniqueId =~ queryVmId) or (isempty(queryVmId) and ContainerId =~ queryContainerId)
| project PreciseTimeStamp, ClusterName, RoleInstanceName,  TenantName, ContainerId, NodeId, 
  ContainerState, ActualOperationalState, LifecycleState, OsState, FaultInfo, VirtualMachineUniqueId
| project StartTime = PreciseTimeStamp, Content = OsState, LifecycleState, ClusterName, RoleInstanceName, TenantName, ContainerId, NodeId, VirtualMachineUniqueId
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> "" or LifecycleState == "Destroyed"
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), queryTo)
| where LifecycleState <> "Destroyed"
| extend Health = case (Content in ("ContainerOsStateUnknown", "ContainerOsStateUnresponsive", "ContainerOsStateUnhealthy"), "Unhealthy", 
    Content in ("ContainerOsStateHealthy", "ContainerOsStateProvisioningCompleted"), "Healthy", 
    Content in ("ContainerOsStateInternalShutdown", "ContainerOsStateProvisioningTimedOut", "ContainerOsStateProvisioningRecovery", "ContainerOsStateProvisioningFailed"), "Degraded", 
    "Neutral")
| extend GroupBy = strcat("ContainerOs (", substring(ContainerId, 0, 8), "~)")
| project StartTime, EndTime, Content, Health, GroupBy, ClusterName, TenantName, RoleInstanceName, ContainerId, NodeId, VirtualMachineUniqueId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`, `{queryContainerId}`

**Signal filters seen in KQL:** `LifecycleState <> "Destroyed"`

---

### Get Extended Container Error Details

_Widget purpose:_ Extended Error Details (If Any)

Cluster: `azurecm` · Database: `azurecm` · Type: `Table`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container Transition > Extended Error Details (If Any)`

```kusto
cluster("azurecm").database("azurecm").LogContainerHealthSnapshot
| where PreciseTimeStamp between(qFrom .. qTo) and containerId == qContainer
| where isnotempty(faultInfo)
| extend faultJson = parse_json(faultInfo)
| extend 
    reason = tostring(faultJson.Reason), 
    correlationId = tostring(faultJson.CorrelationGuid),
    faultTime = tostring(faultJson.Time),
    ExtendedDetails = faultJson.ExtendedDetails
| project PreciseTimeStamp, containerId, nodeId, virtualMachineUniqueId, roleInstanceName, 
    tenantName, reason, correlationId, faultTime, faultJson, ExtendedDetails = faultJson.ExtendedDetails
| summarize arg_max(PreciseTimeStamp, ExtendedDetails) by containerId
| mv-expand row = ExtendedDetails 
| extend Name = tostring(row.Name), Value = tostring(row.Value)
| project Name, Value
| order by Name asc
```

**Params:** `{qFrom}`, `{qTo}`, `{qContainer}`

---

### CRP Operation Timeline

_Widget purpose:_ CRP Operation

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > CRP Operation`

```kusto
let vmname = trim_start("_", queryInstanceName);
let vmssname = trim_end("_[0-9]+", vmname);
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(starttime .. endtime)
| where subscriptionId =~ querySubId
| where resourceName contains vmname or 
        (vmssname <> "" and resourceName contains vmssname)
| where operationName !contains "GET"
| where operationName !contains "NrpCallback"
| where operationName !contains "AllocateDisks"
| where operationName !contains "ExtensionOperation"
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
| project StartTime, EndTime = PreciseTimeStamp, operationId, correlationId, operationName, resourceGroupName, resourceName, 
  httpStatusCode, e2EDurationInMilliseconds, resultCode, errorDetails, requestEntity, subscriptionId, userAgent, 
  apiVersion, labels, region, RPTenant, clientPrincipalName, clientRequestId, durationInMin
| extend Health = case (isnotempty(resultCode), "Unhealthy", "Healthy")
| extend GroupBy = operationName
| extend Content = case (isnotempty(resultCode), resultCode, tostring(httpStatusCode))
| order by operationName asc
```

**Params:** `{starttime}`, `{endtime}`, `{vmid}`, `{queryInstanceName}`, `{querySubId}`

---

### ToR-Hosts PingMesh

_Widget purpose:_ Network Health

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
let devicename = toscalar(cluster('azphynet').database('azdhmds').Servers
| where NodeId =~ nodeid
| project DeviceName );
let tor = toscalar(cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice == devicename
| project EndDevice);
let nodeIdlist = (cluster('azphynet').database('azdhmds').DeviceInterfaceLinks
| where EndDevice =~ tor and LinkType =~ 'DeviceInterfaceLink'
| summarize by DeviceName = StartDevice
| join kind = inner (
    cluster('azphynet').database('azdhmds').Servers
) on DeviceName
| summarize by NodeId);
let numOfNodes = tolong(toscalar(nodeIdlist|count));
cluster('aznwsdn').database('aznwmds').TorPingSendAggreEvent
| where TIMESTAMP between(queryFrom .. queryTo )
| where NodeId in~ (nodeIdlist)
| summarize SendCount = max(SendCount) by TIMESTAMP, NodeId
| join kind = leftouter (
    cluster('aznwsdn').database('aznwmds').TorPingRecvAggreEvent
    | where TIMESTAMP between(queryFrom .. queryTo )
    | where NodeId in~ (nodeIdlist)
    | summarize RecvCount = max(RecvCount) by TIMESTAMP, NodeId
) on TIMESTAMP, NodeId
| extend RecvCount = iff(isnull(RecvCount), 0, RecvCount)
| project StartTime = TIMESTAMP, rate = todouble(RecvCount)/todouble(SendCount) * 100, NodeId, RecvCount, SendCount
| summarize rate = min(rate), SendCount = toint(sum(SendCount)), RecvCount = toint(sum(RecvCount)), dcount(NodeId) by StartTime
| order by StartTime asc
| extend Health = case (
    dcount_NodeId < numOfNodes-1, "Unhealthy",
    rate < 90, "Unhealthy",    
    rate >= 100, "Healthy", 
    "Degraded")    
| extend flag = case (Health <> prev(Health), "changed", 
    isempty(next(StartTime)), "ended", 
    datetime_diff("Minute", next(StartTime), StartTime) > 5, "ended",
    "")
| where flag != ""
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), queryTo)
| where flag != "ended"    
| project StartTime, EndTime, rate, Health, Content = Health, ["Number of Responded Nodes"] =dcount_NodeId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

**Signal filters seen in KQL:** `flag != "ended"`

---

### Host-ToR PingMesh

_Widget purpose:_ Network Health

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
TorPingSendAggreEvent
| where TIMESTAMP >= starttime and TIMESTAMP < endtime
| where NodeId =~ nodeid
| summarize SendCount = max(SendCount) by TIMESTAMP, NodeId
| join kind = leftouter
(
TorPingRecvAggreEvent
| where TIMESTAMP >= starttime and TIMESTAMP < endtime 
| where NodeId =~ nodeid
| summarize RecvCount = max(RecvCount) by TIMESTAMP, NodeId
)on TIMESTAMP, NodeId
| extend RecvCount = iff(isnull(RecvCount), 0, RecvCount)
| project TIMESTAMP, NodeId, Availability = todouble(RecvCount) / todouble(SendCount) * 100, SendCount = toint(SendCount), RecvCount = toint(RecvCount), TimeWindowInMinutes = int(5)
| order by TIMESTAMP asc
| extend StartTime = TIMESTAMP
| extend Health = case (Availability == 100, "Healthy",
    Availability == 200, "Healthy", // Dual ToR Recv 2x Reply
    Availability < 90, "Unhealthy", 
    "Degraded")
| extend flag = case (Health <> prev(Health), "changed", 
    isempty(next(TIMESTAMP)), "ended", 
    datetime_diff("Minute", next(TIMESTAMP), TIMESTAMP) > 5, "ended",
    "")
| where flag != ""    
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), endtime)
| where flag != "ended"
| extend Content = Health
| project StartTime, EndTime, Content
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `flag != "ended"`

---

### ToR Health Event

_Widget purpose:_ Network Health

Cluster: `azphynet` · Database: `azdhmds` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
let devicename = toscalar(cluster('azphynet').database('azdhmds').Servers
| where NodeId =~ nodeid
| project DeviceName );
let tor = toscalar(cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice == devicename
| project EndDevice);
cluster('azphynet.kusto.windows.net').database('azdhmds').f_DeviceHealthLookupSimple(StartTime=queryFrom, EndTime=queryTo,SearchTerm=tor)
| project StartTime = TIMESTAMP, DeviceName, FailureReason, FailureSignal, HealthCategory, Health, Confidence, Persistence_1h, MetricValue, endDeviceIP, Content = FailureSignal
| extend Health = iif(FailureReason contains nodeid, "Error", "Neutral")
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### ToR Update

_Widget purpose:_ Network Health

Cluster: `azwan.kusto.windows.net` · Database: `FUSE` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
let devicename = toscalar(cluster("azphynet.kusto.windows.net").database("azdhmds").Servers
| where NodeId =~ queryNodeId
| project DeviceName );
let tor = toscalar(cluster("azphynet.kusto.windows.net").database("azdhmds").DeviceInterfaceLinks
| where StartDevice == devicename
| project EndDevice);
cluster("azwan.kusto.windows.net").database("FUSE").FUSE
| where Timestamp between ((queryFrom - 1h) .. (queryTo + 1h))
| where device contains tor
| where progress == "Finished"
| project Timestamp,  action, progress, targetState, jobId, StartTime = createTime, EndTime = endTime
| extend Content = strcat(action, " - ", targetState)
| extend Health  = "Degraded"
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `progress == "Finished"`

---

### ToR - Anvil Event

_Widget purpose:_ Network Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `aplat` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
let networkDeviceId = toscalar(cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(startofday(queryFrom) .. endofday(queryTo))
| where ResourceId == queryNodeId
| top 1 by PreciseTimeStamp desc
| project NetworkDeviceId);
cluster("aplat.westcentralus.kusto.windows.net").database("aplat").AnvilRepairServiceRequestSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ResourceId == networkDeviceId
| where SubStatus == "Received"
| extend Request = parse_json(Request)
| extend FaultCodeString = Request.RepairContext.FaultCodeString
| extend FaultReason = Request.RepairContext.FaultReason
| extend FaultTime = Request.RepairContext.Time
| project PreciseTimeStamp, RequestIdentifier, RequestAuthor, FaultCodeString, FaultReason, FaultTime, Request, Status, SubStatus, CorrelationIdentifier
| extend Content = tostring(FaultCodeString)
| extend StartTime = PreciseTimeStamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `SubStatus == "Received"`

---

### Wireserver Heartbeat

_Widget purpose:_ Network Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

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

### NMAgent Health

_Widget purpose:_ Network Health

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
AggVmHealthFailureVscStateEventTable
| where healthEventTime between (queryFrom .. queryTo)
| where NodeId  == queryNodeId
| where ContainerId  == queryContainerId
| where NMAgentHealth != 1
| summarize  arg_max(healthEventTime, NMAgentHealth), HealthReason = tostring(set_difference(array_sort_asc(make_set(split(HealthState, "___"))), pack_array("")))  by StartTimeStamp, EndTimeStamp
| order  by StartTimeStamp asc
| extend StartTime  = StartTimeStamp
| extend Health = case(NMAgentHealth == 1, "Healthy", NMAgentHealth == 0, "Unhealthy", "Degraded") 
| extend Tooltip = strcat("NMAgentHealth: ", NMAgentHealth, ", HealthState: ", tostring(HealthReason))
| extend Content = tostring(Health)
| extend EndTime = EndTimeStamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`

---

### NMAgent Event

_Widget purpose:_ Network Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp  between(starttime .. endtime)
| where NodeId == nodeid
| where ProviderName == "NMAgent"
| project PreciseTimeStamp, StartTime = todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| extend Content = Description //, EndTime = datetime_add("minute", 1, StartTime)
| order by StartTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ProviderName == "NMAgent"`

---

### NM Programming

_Widget purpose:_ Network Health

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
AggVmHealthFailureVscStateEventTable
| where healthEventTime  between (queryFrom .. queryTo)
| where NodeId  == queryNodeId
| where ContainerId  == queryContainerId
| where PortProgrammingStatus != 1
| summarize healthEventTime = arg_max(healthEventTime, PortProgrammingStatus)  by StartTimeStamp, EndTimeStamp
| extend StartTime  = StartTimeStamp
| extend Health = case( PortProgrammingStatus == 1, "Healthy", PortProgrammingStatus == 0, "Unhealthy", "Degraded")
| extend Content = Health
| extend Tooltip = tostring(PortProgrammingStatus)
| extend EndTime = EndTimeStamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

---

### SoC OS Update

_Widget purpose:_ Network Health

Cluster: `azurehn.kusto.windows.net` · Database: `Azurehn` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
let _ContainerId = '';
let _NodeId = queryNodeId;
let _endTime = queryTo;
let _startTime = queryFrom;
let NodeInformation = () {
    let impactedContainerId = tolower(["_ContainerId"]);
    let impactStartTime =["_startTime"];
    let impactEndTime = ["_endTime"];
    let output = materialize(cluster("azurehn.kusto.windows.net").database("Azurehn").fn_GetNodeInfo_v2(impactStartTime, impactEndTime,["_NodeId"], impactedContainerId));
    output
};
let impactedContainerId = tolower(["_ContainerId"]);
let impactStartTime =["_startTime"];
let impactEndTime = ["_endTime"];
let impactedNodeId = toscalar(NodeInformation | project NodeId);
let socID = toscalar(NodeInformation | project SocId);
let query=strcat(```cluster("```, toscalar(NodeInformation | project AzCoreCluster),```").database('OvlProd').LinuxOverlakeSystemd()
| where NodeId =~ impactedNodeId or NodeId =~ socID
| where PreciseTimeStamp between (impactStartTime .. impactEndTime)
| where _SYSTEMD_UNIT startswith "SocOsUpdate"
| project PreciseTimeStamp, Severity=case(PRIORITY == 2, "Crit", PRIORITY == 3, "Error", PRIORITY == 4, "Warn", PRIORITY == 5, "Notice", PRIORITY == 6, "Info", PRIORITY == 7, "Debug", "Undef"),
          MESSAGE, _PID, _SYSTEMD_UNIT```);
evaluate execute_query(".", query)
| where MESSAGE startswith "SocOsUpdate: SoC-OS version"
| extend StartTime = PreciseTimeStamp
| summarize arg_max(MESSAGE,StartTime) 
| project StartTime,Content = MESSAGE
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `_SYSTEMD_UNIT startswith "SocOsUpdate"` · `MESSAGE startswith "SocOsUpdate: SoC-OS version"`

---

### SoC Pilot Fish State

_Widget purpose:_ Network Health

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(queryFrom .. queryTo)
// | where ResourceId == queryNodeId
| where PairId == queryNodeId
| order by PreciseTimeStamp asc
| extend flag = case (prev(PfState) <> PfState, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp), queryTo)
| extend Content = strcat (PfState, " ", PfRepairState)
| extend Health = case (PfState == "H", "Healthy", 
    PfState in ("D", "C", "F"), "Unhealthy",
    "Degraded")
| project StartTime, EndTime, Tenant, ResourceId, PairId, LifecycleState, PfState, PfRepairState, HealthSummary, FaultCode, FaultDescription, IPAddress, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### SoC PF Update

_Widget purpose:_ Network Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').OverlakeServiceManagerStatus
| where  PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h))
| where NodeId =~ querySocNodeId 
| where EventType == "versionswitch"
| order by PreciseTimeStamp desc
| extend detailsParsed = parse_json(detail)
| extend CurrentVersion=tostring(detailsParsed.Version)
| extend NewVersion=tostring(detailsParsed.NewVersion)
| project PreciseTimeStamp, ServiceName, CurrentVersion, NewVersion, NodeId, MachineName, Cluster
| extend StartTime = PreciseTimeStamp
| extend Content = strcat(ServiceName, ": ", NewVersion)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySocNodeId}`

**Signal filters seen in KQL:** `EventType == "versionswitch"`

---

### SoC Signal Event

_Widget purpose:_ Network Health

Cluster: `overlakedata.southcentralus.kusto.windows.net` · Database: `overlake-syslog` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
let socHostName = toscalar(cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMap_Latest
| where NodeId == queryNodeId
| project hostMachineName
| take 1);
cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeSoCProcessedSignals
| where IngestionTime between (queryFrom..queryTo)
| where isnotempty(socHostName) and MESSAGEList contains strcat (socHostName, "SOC")
| where Scenario <> "SELinuxViolations"
| where Scenario in ("KernelDumps", "WatchDogReset", "KexecRepeatedBoots", "RebootTypes")
| extend Content = Scenario
| extend Health = "Unhealthy"
| project StartTime = StartTimeStamp, EndTime = EndTimeStamp, IngestionTime, Cluster, SoCNameList, Scenario, Component, MESSAGEList, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Scenario <> "SELinuxViolations"`

---

### SoC Azure Watson

_Widget purpose:_ Network Health

Cluster: `azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
let azurewatsonlink = strcat("https://azurewatson.microsoft.com/?NodeId=", querySocNodeId);
cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. queryTo)
// | where nodeIdentity == queryNodeId
| where nodeIdentity == querySocNodeId
| where isnotempty(nodeIdentity) 
| project PreciseTimeStamp, EventMessage, platform, crashMode, process, environment, dumpUid
| join kind= leftouter (
    cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
    | where PreciseTimeStamp between (queryFrom..queryTo)
    | project AnalyzedTime=PreciseTimeStamp, DumpAnalalysisMessage=EventMessage, faultingModule, faultingProcess, bucketString, crashTime, dumpType, bugId, bugLink, dumpUid
) on $left.dumpUid == $right.dumpUid
| extend AzureWatsonLink=azurewatsonlink
| where crashTime <> ""
| project StartTime = todatetime(crashTime), AnalyzedTime, dumpType, crashMode, platform, DumpAnalalysisMessage, faultingModule, faultingProcess, bugId, bugLink, AzureWatsonLink
| extend Content = strcat(crashMode, " ", faultingProcess,"!",faultingModule)
| extend Health = case (crashMode == "um", "Degraded", "Unhealthy")
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySocNodeId}`

---

### SoC - Anvil Event

_Widget purpose:_ Network Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `aplat` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
cluster("aplat.westcentralus.kusto.windows.net").database("aplat").AnvilRepairServiceRequestSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ResourceId == querySocNodeId
| where SubStatus == "Received"
| extend Request = parse_json(Request)
| extend FaultCodeString = Request.RepairContext.FaultCodeString
| extend FaultReason = Request.RepairContext.FaultReason
| extend FaultTime = Request.RepairContext.Time
| project PreciseTimeStamp, RequestIdentifier, RequestAuthor, FaultCodeString, FaultReason, FaultTime, Request, Status, SubStatus, CorrelationIdentifier
| extend Content = tostring(FaultCodeString)
| extend StartTime = PreciseTimeStamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySocNodeId}`

**Signal filters seen in KQL:** `SubStatus == "Received"`

---

### SoC VNetAgent Event

_Widget purpose:_ Network Health

Cluster: `azcore.centralus` · Database: `OvlProd` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
let portIDs = materialize(cluster('aznwsdn').database('aznwmds').ContainerInformationEvent
| where ContainerId =~ queryContainerId
| where PreciseTimeStamp >= queryFrom - 96h and queryTo <= queryTo + 24h
| distinct PortId);
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').LinuxOverlakeSystemd
| where NodeId =~ queryNodeId or NodeId =~ querySocNodeId
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where PRIORITY in ("3", "4") // Error,  Warn
| where MESSAGE has_any (portIDs)
| where SYSLOG_IDENTIFIER == "vnetagent"
| extend MESSAGE1 = extract("VnetAgent::\\[.*\\](.*)", 1, MESSAGE)
| order by PreciseTimeStamp asc
| summarize PRIORITY = min(PRIORITY), message = make_set(MESSAGE1) by bin(PreciseTimeStamp, 1m)
| extend Health  = iif(PRIORITY == "3", "Error", "Degraded")
| project StartTime = PreciseTimeStamp, Content = iif(PRIORITY == "3", "Error", "Warning"), Message = tostring(message), Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`, `{querySocNodeId}`

**Signal filters seen in KQL:** `SYSLOG_IDENTIFIER == "vnetagent"`

---

### SoC Systemd Event

_Widget purpose:_ Network Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').LinuxOverlakeSystemd
| where PreciseTimeStamp between( queryFrom .. queryTo ) 
| where NodeId == querySocNodeId // SocNodeId
// need to add more filters once we get more known issues on SoC...
| where MESSAGE has "Too many open files" 
| project StartTime = PreciseTimeStamp, Cluster, MachineName, SocNodeId = NodeId, _TRANSPORT, _COMM, _SYSTEMD_UNIT, MESSAGE
| extend Content = 'TooManyOpenFiles', Health = 'Unhealthy'
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySocNodeId}`

**Signal filters seen in KQL:** `MESSAGE has "Too many open files"`

---

### DCM Node State

_Widget purpose:_ Node Health

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

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

### DCM Node Fault

_Widget purpose:_ Node Health

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ResourceId == queryNodeId
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, ResourceId, LifecycleState, PfState, PfRepairState, HealthSummary, FaultCode, FaultDescription
| extend flag = case(prev(FaultCode) <> FaultCode, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp), queryTo)
| extend Content = tostring(FaultCode)
| extend Health = "Unhealthy"
| where FaultCode <> 0
| project StartTime, EndTime, LifecycleState, HealthSummary, FaultCode, FaultDescription, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### DCM SEL (Sparkle)

_Widget purpose:_ Node Health

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
cluster("sparkle.eastus.kusto.windows.net").database("defaultdb").SparkleSELByNodeId(nodeId=queryNodeId, queryFrom, queryTo)
| where isnotempty( DataCenter )
| where SensorType <> "" and BMCSelItemMessage <> ""
| where BMCSelTimestamp > queryFrom
// | where SensorType == 'Management Subsystem Health'
| distinct BMCSelTimestamp, Cluster, RecordId, RecordType, BMCSelItemMessage, SensorId, SensorType, EventData1, 
  EventData2, EventData3, EventDataDetails1, EventDataDetails2, EventDataDetails3, RawHex
| project StartTime = BMCSelTimestamp, RecordId, BMCSelItemMessage, RawHex, Content = SensorType
| extend Health = case (BMCSelItemMessage contains ' CRT ' or BMCSelItemMessage contains ' MAJ ', 'Unhealthy', 
    BMCSelItemMessage contains ' MIN ', 'Degraded', 'Neutral')
| order by StartTime asc, RecordId asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `SensorType == "Management Subsystem Health"`

---

### DCM SEL

_Widget purpose:_ Node Health

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").RhwChassisSelItemEtwTable
| where BmcSelItemTimeStamp between(queryFrom .. queryTo)
| where ResourceId == queryNodeId
| where BmcSelItemSensorName <> "BMC Health"
| where BmcSelItemEventType in ( "Critical Interrupt", "Processor", "Temparature", "Memory", "Button", "OS Critical Stop") or 
    (BmcSelItemEventType == 'Battery' and BmcSelItemDetails contains 'Failed') or 
    (BmcSelItemEventType == 'Management Subsystem Health' and BmcSelItemDetails contains 'HAL error') or 
    (BmcSelItemEventType == 'Voltage' and BmcSelItemSensorName !contains 'CPU' and BmcSelItemSeverity == 'MAJ') or 
    (BmcSelItemEventType == 'Power Supply' and BmcSelItemDetails in ('AC Lost', 'Failure detected'))
| distinct BmcSelItemTimeStamp, Cluster, BmcSelItemId, BmcSelItemSeverity, BmcSelItemSource, BmcSelItemEventType, BmcSelItemSensorName, BmcSelItemDetails, BmcSelItemRawHex
| order by BmcSelItemTimeStamp asc
| extend level = case (BmcSelItemSeverity == "CRT", "critical", "info")
| extend Content = BmcSelItemDetails, Health = "Unhealthy"
| project StartTime = BmcSelItemTimeStamp, Cluster, BmcSelItemId, BmcSelItemSeverity, BmcSelItemSource, BmcSelItemEventType, BmcSelItemSensorName, BmcSelItemDetails, BmcSelItemRawHex, level, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `BmcSelItemSensorName <> "BMC Health"`

---

### Root Update Alloc Type

_Widget purpose:_ Node Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
cluster('azcsupfollower').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeId == nodeid
// | where nodeId == 'ee939a66-a270-48d4-a3bc-8687227fe2dc'
// | project PreciseTimeStamp, Tenant, nodeState, nodeAvailabilityState, containerCount, 
//   cmNodeChannelHealthStatus ,faultInfo, healthSignals
| project PreciseTimeStamp, rootUpdateAllocationType
| order by PreciseTimeStamp asc 
| extend flag = case (rootUpdateAllocationType <> prev(rootUpdateAllocationType), "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp, EndTime = case (isnotnull(next(PreciseTimeStamp)), next(PreciseTimeStamp), queryTo)
| extend Health = case ( rootUpdateAllocationType == 'MultipleUpdateSet', "Healthy", "Unknown")
| extend Content = rootUpdateAllocationType
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

**Signal filters seen in KQL:** `nodeId == "ee939a66-a270-48d4-a3bc-8687227fe2dc"`

---

### Node State

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
MycroftNodeHealthSnapshot
| where PreciseTimeStamp between (starttime..endtime)
| where NodeId == nodeid
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, Content = NsdState
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), endtime)
| extend Health = case(Content in ("Booting", "OutForRepair", "PoweringOn", "HumanInvestigate", "PoweredOff", "Dead", "Recovering"), "Unhealthy", Content in ("Unhealthy"), "Degraded", Content == "Ready", "Healthy", "Neutral")
| project StartTime, EndTime, Health, Content
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Node Availability

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
MycroftNodeHealthSnapshot
| where PreciseTimeStamp between (starttime..endtime)
| where NodeId == nodeid
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, Content = AvailabilityState
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), endtime)
| extend Health = case (Content in ("Faulted", "OutForRepair"), "Unhealthy", Content == "Available", "Healthy", "Degraded")
| project StartTime, EndTime, Health, Content
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Node Fault

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
MycroftNodeHealthSnapshot
| where PreciseTimeStamp between (starttime..endtime)
| where NodeId == nodeid
| order by PreciseTimeStamp asc
| extend flag = case (FaultInfo <> prev(FaultInfo), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp), endtime)
| extend Health = "Unhealthy"
| where FaultInfo <> ""
| project StartTime = PreciseTimeStamp, EndTime, Content = tostring(parse_json(FaultInfo)["FaultCode"]), tostring(parse_json(FaultInfo)["FabricOperationString"]), Health, parse_json(FaultInfo)
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Node WillBe Channel Health Status

_Widget purpose:_ Node Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

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

### Node WasChannel Health Status

_Widget purpose:_ Node Health

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

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

### Node Service Error

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').NodeServiceOperationEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
// | where Identifier contains "{containerid}"
| where OperationName !contains "Query"
| where Result <> 1
| extend ResultCode = tohex(toint(ResultCode), 8), Health = "Unhealthy"
| extend Content = strcat("0x", ResultCode)
| project StartTime = RequestTime, EndTime = CompleteTime, OperationName, Identifier, Result, ResultCode, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Identifier contains "{containerid}"`

---

### VMAL Error

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
VmServiceContainerOperations
| where PreciseTimeStamp between ( queryFrom .. queryTo )  
| where NodeId == queryNodeId
// | where Identifier contains "{containerid}"
| where ResultCode !in ("0x0", "0x1")
| extend Content = ResultCode, Health = "Unhealthy"
| project StartTime, EndTime, DurationMillis, Cluster, Level, Operation, Stage, ResultCode, ContainerId, NodeId, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Identifier contains "{containerid}"`

---

### Node Live Migration

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fc').LiveMigrationContainerDetailsEventLog
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where sourceNodeId == nodeid
| project StartTime = PreciseTimeStamp, sessionId, triggerType, migrationConstraint, Tenant, sourceContainerId, sourceNodeId, sourceDip, sourceVlan, 
          destinationContainerId, destinationNodeId, destinationDip, destinationVlan
| join kind=inner(
    cluster('azcore.centralus.kusto.windows.net').database('Fc').LiveMigrationSessionCompleteLog
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where sourceNodeId == nodeid
    | project EndTime = PreciseTimeStamp, sessionId, status, elapsedTime, message, resourceId
) on $left.sessionId == $right.sessionId
| extend elapsedSec = totimespan(elapsedTime) / 1s
| extend Health = case (status == 'Faulted', 'Unhealthy', status == 'Completed', 'Healthy', 'Degraded' )
| extend Content = triggerType
| project StartTime, EndTime, sessionId, triggerType, migrationConstraint, status, elapsedTime, elapsedSec, message, Tenant, tenantName = resourceId, 
          sourceContainerId, sourceNodeId, sourceDip, sourceVlan, destinationContainerId, destinationNodeId, destinationDip, destinationVlan, Health, Content
| join kind=leftouter (cluster("azcsupfollower.kusto.windows.net").database("Air").LiveMigrationFailureEvents
| where EventTime between (queryFrom .. queryTo)
| project RCALevel1, RCALevel2, Diagnostics = parse_json(Diagnostics), sessionId = tostring(parse_json(Diagnostics)["SessionId"])) on sessionId
| project-away sessionId1
| order by StartTime asc             
| order by StartTime
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### Anvil Event - Node

_Widget purpose:_ Node Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
cluster("aplat.westcentralus.kusto.windows.net").database("APlat").AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where ResourceId == queryNodeId
| where MessageTrigger contains "OnBeforeWalkTree"
| project PreciseTimeStamp, Cluster, Role, MessageTrigger, TreeName, TreeNodeKey, TreeActionName, TreeActionInput, Properties, TaskStatus, Message, ResourceId, ResourceType, ResourceDependencies
| order by PreciseTimeStamp asc 
| extend StartTime = PreciseTimeStamp
| extend FaultCodeString = parse_json(Message).RepairContext.FaultCodeString
| extend Content = tostring(FaultCodeString)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `MessageTrigger contains "OnBeforeWalkTree"`

---

### Kernel/Driver Events

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp  between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where not (ProviderName contains "Kernel-Processor" and EventId == 37) // eliminating periodical processor report event every day.
| where not (ProviderName == "Microsoft-Windows-Kernel-PnP") // eliminating PnP messages
// | where not (ProviderName contains "PnP" and EventId == 1010) // eliminating PnP errors. 
| where ProviderName in ("OSHostPlugin", "UpdateNotification", "NMAgent", "Microsoft-Windows-UserModePowerService", "EventLog") or 
    ProviderName contains "Microsoft-Windows-Kernel" or
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "EventType: AfterInstall") or 
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "EventType: BeforeInstall") or 
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "FPGA driver install") or
    (ProviderName contains "vfpext" and EventId == 7036) or
    (ProviderName == "Microsoft-Windows-Kernel-General" and EventId == "12") or
    (ProviderName == "Microsoft-Windows-Kernel-General" and EventId == "18") or 
    (ProviderName contains "Microsoft-Windows-Kernel-Power" and EventId == "41")
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by TimeCreated asc
| extend level = case (Level == 1, "critical", 
    Level == 2, "error", 
    Level == 3, "warning",
    "info")
| project StartTime = TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, Content = strcat(ProviderName, " - ", EventId)
| extend Health = case (Level <= 2, "Unhealthy", Level == 3, "Degraded", "Healthy")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Remarkable Event - Disk

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
let referenceTable = datatable(ProviderName:string, EventId:string, ShortName:string, Category:string, Health:string) [
    // disk
    "disk", 7, "disk", "Disk", "Unhealthy",
    "LSI_SAS2i", 11, "LSI_SAS", "Disk", "Unhealthy",
    "LSI_SAS3i", 11, "LSI_SAS", "Disk", "Unhealthy",
    "VhdDiskPrt", 16, "VhdDiskPrt", "Disk", "Degraded",
    "VhdDiskPrt", 17, "VhdDiskPrt", "Disk", "Unhealthy",
    "disk", 52, "disk", "Disk", "Degraded",
    "Ntfs", 55, "Ntfs", "Disk", "Degraded",
    "VhdDiskPrt", 66, "VhdDiskPrt", "Disk", "Degraded",
    "VhdDiskPrt", 67, "VhdDiskPrt", "Disk", "Degraded",
    "Storahci", 129, "Storahci", "Disk", "Unhealthy",
    "vhdmp", 129, "vhdmp", "Disk", "Unhealthy",
    "elxstor", 129, "elxstor", "Disk", "Unhealthy",
    "HpCISSs3", 129, "HpCISSs3", "Disk", "Unhealthy",
    "stornvme", 129, "stornvme", "Disk", "Unhealthy",
    "LSI_SAS2i", 129, "LSI_SAS", "Disk", "Unhealthy",
    "LSI_SAS3i", 129, "LSI_SAS", "Disk", "Unhealthy",
    "VhdDiskPrt", 129, "VhdDiskPrt", "Disk", "Unhealthy",
    "Microsoft-Windows-Ntfs", 141, "NTFS", "Disk", "Unhealthy",
    "Microsoft-Windows-Ntfs", 147, "NTFS", "Disk", "Degraded",
    "Microsoft-Windows-Ntfs", 149, "NTFS", "Disk", "Degraded",
    "disk", 153, "disk", "Disk", "Degraded",
    "disk", 154, "disk", "Disk", "Degraded",
    "Microsoft-Windows-StorPort", 500, "StorPort", "Disk", "Unhealthy",
    "Microsoft-Windows-Hyper-V-NvmeDirectDriver", 5006, "HyperV NVME", "Disk", "Unhealthy",
    //"Microsoft-Windows-Hyper-V-NvmeDirectDriver", 6003, "HyperV NVME", "Disk", "Unhealthy", // in most cases, this event is ignorable
];
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| join kind=inner (referenceTable) on $left.ProviderName == $right.ProviderName and $left.EventId == $right.EventId
| extend Content = strcat (ShortName, ", ", EventId)
| project StartTime = TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, ShortName, Category, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Remarkable Event - WHEA

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
let referenceTable = datatable(ProviderName:string, EventId:string, ShortName:string, Category:string, Health:string) [
    // WHEA
    "Microsoft-Windows-WHEA-Logger", 16, "WHEA", "Hardware", "Unhalthy",
    //"Microsoft-Windows-WHEA-Logger", 17, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 22, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 23, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 26, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 40, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 41, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 46, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 47, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-Kernel-PnP", 902, "PnP",  "Driver/Hardware", "Degraded",
    "Microsoft-Windows-Kernel-PnP", 903, "PnP",  "Driver/Hardware", "Degraded",
];
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| join kind=inner (referenceTable) on $left.ProviderName == $right.ProviderName and $left.EventId == $right.EventId
| extend Content = strcat (ShortName, ", ", EventId)
| where Description !contains "Component: Memory"
| project StartTime = TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, ShortName, Category, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Remarkable Event - Memory

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
let referenceTable = datatable(ProviderName:string, EventId:string, ShortName:string, Category:string, Health:string) [
    // Memory events
    "Microsoft-Windows-WHEA-Logger", 16, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 17, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 22, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 23, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 26, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 40, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 41, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 46, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 47, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-Resource-Exhaustion-Detector", 2004, "ResourceExaust", "Memory", "Unhealthy",
    "Microsoft-Windows-Hyper-V-Worker", 3050, "Hyper-V", "Hardware", "Unhealthy",
    "Microsoft-Windows-Hyper-V-Worker", 3122, "Hyper-V", "Hardware", "Unhealthy",
    "Microsoft-Windows-Hyper-V-Worker", 3273, "Hyper-V", "Hardware", "Unhealthy",
    "Microsoft-Windows-Hyper-V-VID", 5043, "Hyper-V", "Hardware", "Unhealthy",
    "Microsoft-Windows-Hyper-V-VID", 5043, "Hyper-V", "Hardware", "Unhealthy",
];
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| where (ProviderName == "Microsoft-Windows-WHEA-Logger" and Description contains "Component: Memory") or 
        Description contains "0x8007000E" or
        ProviderName <> "Microsoft-Windows-WHEA-Logger"
| join kind=inner (referenceTable) on $left.ProviderName == $right.ProviderName and $left.EventId == $right.EventId
| extend ShortName = case (isempty(ShortName), ProviderName, ShortName) // in case of 0x8007000E
| extend Health = case (isempty(Health), "Unhealthy", Health) // in case of 0x8007000E
| extend Content = strcat (ShortName, ", ", EventId)
| project StartTime = TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, ShortName, Category, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Remarkable Event - HyperV

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
let referenceTable = datatable(ProviderName:string, EventId:string, SuspiciousCategory:string, Health:string) [
    // Guest OS 
    "Microsoft-Windows-Hyper-V-Worker", 18590, "GuestOS", "Degraded",
    "Microsoft-Windows-Hyper-V-Chipset", 18600, "GuestOS", "Degraded",
    "Microsoft-Windows-Hyper-V-Worker", 18602, "GuestOS", "Degraded",
    "Microsoft-Windows-Hyper-V-Worker", 18604, "GuestOS", "Degraded",
    "Microsoft-Windows-Hyper-V-Worker", 18540, "GuestOS", "Degraded", // triple fault by guest
    "Microsoft-Windows-Hyper-V-Worker", 18570, "GuestOS", "Degraded", // unsupported interception instruction
    "Microsoft-Windows-Hyper-V-Worker", 18610, "GuestOS", "Degraded", // guest virtual firmware - fatal error
    "Microsoft-Windows-Hyper-V-Chipset", 18610, "GuestOS", "Degraded", // guest virtual firmware - fatal error
    // Platform 
    "Microsoft-Windows-Hyper-V-VMMS", 14070, "Platform", "Degraded",
    "Microsoft-Windows-Hyper-V-VMMS", 14154, "Platform", "Degraded",
    "Microsoft-Windows-Hyper-V-VMMS", 15140, "Platform", "Degraded",
    "Microsoft-Windows-Hyper-V-VMMS", 16000, "Platform", "Degraded",
    "Microsoft-Windows-Hyper-V-Worker", 18550, "Platform/HyperV", "Degraded", // triple fault
    "Microsoft-Windows-Hyper-V-Worker", 18560, "Platform", "Degraded",  // triple fault
    "Microsoft-Windows-Hyper-V-Worker", 18572, "Platform", "Degraded",  // general protection
    "Microsoft-Windows-Hyper-V-Worker", 21102, "Platform/LM", "Degraded", // recover failure from migration under LM
    "Microsoft-Windows-Hyper-V-VMMS", 16010, "Platform/HyperV", "Degraded", // hyper-v operation error - ignorable if the count is not high. 
    // Platform - critical error
    "Microsoft-Windows-Hyper-V-VMMS", 18190, "Platform/HyperV", "Unhealthy", // hyper-v worker process issue
    "Microsoft-Windows-Hyper-V-Worker", 18524, "Platform", "Unhealthy", // network critical issue? 
    "Microsoft-Windows-Hyper-V-VMMS", 19050, "Platform/HyperV", "Unhealthy", // hyper-v operation failures. 
    "Microsoft-Windows-Hyper-V-VMMS", 19060, "Platform/HyperV", "Unhealthy", // hyper-v operation failures. 
    "Microsoft-Windows-Hyper-V-VMMS", 19062, "Platform/HyperV", "Unhealthy", // hyper-v operation timeout. 
    "Microsoft-Windows-Hyper-V-VMMS", 19064, "Platform/HyperV", "Unhealthy", // hyper-v operation being locked. 
    "Microsoft-Windows-Hyper-V-Worker", 21102, "Platform/LM", "Degraded", // recover failure from migration under LM
    "Microsoft-Windows-Hyper-V-Worker", 12004, "Platform/HyperV", "Unhealthy", // hyper-v bios error 
];
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between( queryFrom .. queryTo )
| where NodeId == queryNodeId
| where ProviderName in ("Microsoft-Windows-Hyper-V-Worker", "Microsoft-Windows-Hyper-V-Chipset", "Microsoft-Windows-Hyper-V-VMMS")
| project PreciseTimeStamp, todatetime(TimeCreated), Level, Cluster, Channel, ProviderName, EventId, Description
| extend ProviderNameAndEventId = strcat (ProviderName, "_", EventId)
| join kind=leftouter (referenceTable) on $left.ProviderName == $right.ProviderName, $left.EventId == $right.EventId
| where SuspiciousCategory <> ""
| extend Content = EventId, StartTime = TimeCreated
| project StartTime, Level, Cluster, ProviderName, EventId, Description, SuspiciousCategory, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Azure Watson

_Widget purpose:_ Node Health

Cluster: `azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
let azurewatsonlink = strcat("https://portal.watson.azure.com/?NodeId=", queryNodeId);
cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeIdentity == queryNodeId
| project PreciseTimeStamp, EventMessage, platform, crashMode, process, environment, dumpUid
| join kind= leftouter (
    cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
    | where PreciseTimeStamp between (queryFrom..queryTo)
    | project AnalyzedTime=PreciseTimeStamp, DumpAnalalysisMessage=EventMessage, faultingModule, faultingProcess, bucketString, crashTime, dumpType, bugId, bugLink, dumpUid
) on $left.dumpUid == $right.dumpUid
| extend AzureWatsonLink=azurewatsonlink
| where crashTime <> ""
| project StartTime = todatetime(crashTime), AnalyzedTime, dumpType, crashMode, platform, DumpAnalalysisMessage, faultingModule, faultingProcess, bugId, bugLink, AzureWatsonLink
| extend Content = strcat(crashMode, " ", faultingProcess,"!",faultingModule)
| extend Health = case (crashMode == "um", "Degraded", "Unhealthy")
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Hyper-V State

_Widget purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`

```kusto
HostAgentEventsEtwTable
| where PreciseTimeStamp between ( queryFrom .. queryTo )  
| where NodeId == queryNodeId and Message has "Hyper-V is unresponsive"
| extend Content = Message, Health = "Unhealthy"
| project StartTime = PreciseTimeStamp, Message, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### PF Update

_Widget purpose:_ Node Update

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Update`

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

_Widget purpose:_ Node Update

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Update`

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

_Widget purpose:_ Node Update

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Update`

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

_Widget purpose:_ Node Update

Cluster: `azpe` · Database: `azpe` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Update`

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

_Widget purpose:_ Node Update

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Update`

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

### ContainerPerformance

_Widget purpose:_ Container Performance Metrics (Node / Internal View)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Start Page > Start Page > At-A-Glance Performance  > Container Performance Metrics (Node / Internal View)`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (starttime .. endtime)
| where VmId == containerid
| project PreciseTimeStamp, Cluster, TenantId, NodeId, VmId, RoleId, RoleInstanceId, CounterName, SampleCount, AverageCounterValue, MinCounterValue, MaxCounterValue
| summarize sum(AverageCounterValue) by PreciseTimeStamp, CounterName
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{containerid}`

---

### Container Performance Shoebox

_Widget purpose:_ Container Performance Metrics (Shoebox Source / Customer View)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Start Page > Start Page > At-A-Glance Performance  > Container Performance Metrics (Shoebox Source / Customer View)`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmShoeboxCounterTable
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId  == nodeid
| where VmId == containerid
| project PreciseTimeStamp, Cluster, RoleInstanceId, VmResourceType, MDMCounterName, MDMAccountName, DurationInMinutes, AverageValue
| project PreciseTimeStamp, MDMCounterName, AverageValue
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`, `{containerid}`

---

### VMA filter by Subscription

Cluster: `vmainsight` · Database: `vmadb` · Type: `Table`
Source panel: `Start Page > Start Page > VMA > VM Availability > VMA for this Subscription`

```kusto
let subId = cluster("azcsupfollower.kusto.windows.net").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where containerId == queryContainerId
| top 1 by PreciseTimeStamp
| project subscriptionId;
cluster('vmainsight.kusto.windows.net').database('vmadb').VMA()
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where LastKnownSubscriptionId in (subId)
// | where RCAEngineCategory <> "CustomerInitiated"
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3, E17_StorageAccount, E17_StorageTenant, Network_TOR2 
| order by StartTime asc
| extend durationSec = datetime_diff("Second", EndTime, StartTime)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

**Signal filters seen in KQL:** `RCAEngineCategory <> "CustomerInitiated"`

---

### VMAQuery

_Widget purpose:_ VMA Event on Node

Cluster: `vmainsight` · Database: `vmadb` · Type: `Table`
Source panel: `Start Page > Start Page > VMA > VM Availability > VMA on Node > VMA on Node > VMA Event on Node`

```kusto
cluster('vmainsight.kusto.windows.net').database('vmadb').VMA()
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
// | where RCAEngineCategory <> "CustomerInitiated"
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, LastKnownSubscriptionId, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3, E17_StorageAccount, E17_StorageTenant, Network_TOR2 
| order by StartTime asc
| extend durationSec = datetime_diff("Second", EndTime, StartTime)
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `RCAEngineCategory <> "CustomerInitiated"`

---

### Impacted VM

_Widget purpose:_ VMA Timeline on Node

Cluster: `vmainsight` · Database: `vmadb` · Type: `Timeline`
Source panel: `Start Page > Start Page > VMA > VM Availability > VMA on Node > VMA on Node > VMA Timeline on Node`

```kusto
cluster('vmainsight.kusto.windows.net').database('vmadb').VMA()
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
| where RCAEngineCategory <> "CustomerInitiated"
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3, E17_StorageAccount, E17_StorageTenant, Network_TOR2 
| order by StartTime asc
| extend Content = RCALevel2
| extend GroupBy = RoleInstanceName
| extend Health = case (RCAEngineCategory in ( "Unplanned" ), "Unhealthy", RCAEngineCategory == "CustomerInitiated", "Healthy", "Neutral")
| extend durationSec = datetime_diff("Second", EndTime, StartTime)
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `RCAEngineCategory <> "CustomerInitiated"`

---

### AIR-R & AIR-BP

_Widget purpose:_ AIR Events

Cluster: `vmainsight` · Database: `Air` · Type: `Table`
Source panel: `Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > AIR Events`

```kusto
union
cluster('vmainsight.kusto.windows.net').database('Air').GetVMAvailabilityImpactEvents(VmId = vmid, startTime = starttime, endTime = endtime),
cluster('vmainsight.kusto.windows.net').database('Air').GetVMDiskBlipEvents(VmId = vmid, startTime = starttime, endTime = endtime),
cluster('vmainsight.kusto.windows.net').database('Air').GetVMPhuEvents(vmId = vmid, startTime = starttime, endTime = endtime)
| order by Timestamp asc
| project Timestamp, Cluster, RoleInstanceName, EventType, EventSource, ImpactCategory, TenantName, ObjectIds, FailureSignature, FailureDetails, ImpactBeginTimeStamp, ImpactEndTimeStamp, ImpactDurationTimeSpan
```

**Params:** `{starttime}`, `{endtime}`, `{vmid}`

---

### AIR & VMA Timeline

_Widget purpose:_ VMA / AIR Event Timeline

Cluster: `vmainsight` · Database: `Air` · Type: `CoBeTimeline`
Source panel: `Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > VMA / AIR Event Timeline`

```kusto
let parentAIR = print EventId = "AIR Event", ParentId = "", StartTime = starttime, EndTime = endtime, InferHealth = true, Content = "Expand child items if any errors";
let parentVMA = print EventId = "VMA", ParentId = "", StartTime = starttime, EndTime = endtime, InferHealth = true, Content = "Expand child items if any errors";
union
parentVMA,
(cluster('vmainsight.kusto.windows.net').database('vmadb').VMA()
| where PreciseTimeStamp between(starttime .. endtime)
| where VmUniqueId == vmid
| where RCAEngineCategory <> "CustomerInitiated"
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3, E17_StorageAccount, E17_StorageTenant, Network_TOR2 
| order by StartTime asc
| extend Content = RCALevel2
| extend EventId = strcat(RCALevel1, " - ", RCALevel2) //RoleInstanceName
| extend Health = case (RCAEngineCategory in ( "Unplanned" ), "Unhealthy", RCAEngineCategory == "CustomerInitiated", "Healthy", "Neutral")
| extend durationSec = datetime_diff("Second", EndTime, StartTime)
| extend ParentId = "VMA"
| project StartTime, EndTime, EventId, ParentId, Health, Content
),
parentAIR,
(
union
(cluster('vmainsight.kusto.windows.net').database('Air').GetVMAvailabilityImpactEvents(VmId = vmid, startTime = starttime, endTime = endtime)
| project Timestamp, Cluster, RoleInstanceName, EventType, EventSource, ImpactCategory, TenantName, ObjectIds, FailureDetails, StartTime = ImpactBeginTimeStamp, EndTime = ImpactEndTimeStamp, ImpactDurationTimeSpan
| extend EventId = tostring(new_guid()), ParentId = "AIR Event", EventName = EventType, Health="Unhealthy", Content = EventType),
(cluster('vmainsight.kusto.windows.net').database('Air').GetVMDiskBlipEvents(VmId = vmid, startTime = starttime, endTime = endtime)
| project Timestamp, Cluster, RoleInstanceName, EventType, EventSource, ImpactCategory, TenantName, ObjectIds, FailureDetails, StartTime = ImpactBeginTimeStamp, EndTime = ImpactEndTimeStamp, ImpactDurationTimeSpan
| extend EventId = tostring(new_guid()), ParentId = "AIR Event", EventName = EventType, Health="Unhealthy", Content = EventType)
| project StartTime, EndTime, EventId, ParentId, Health, Content, EventName
| order by StartTime asc)
```

**Params:** `{starttime}`, `{endtime}`, `{vmid}`

**Signal filters seen in KQL:** `RCAEngineCategory <> "CustomerInitiated"`

---

### VMA Event on VM ID

Cluster: `vmainsight` · Database: `vmadb` · Type: `Table`
Source panel: `Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > VMA Event on VM ID`

```kusto
cluster('vmainsight.kusto.windows.net').database('vmadb').VMA()
| where PreciseTimeStamp between(starttime .. endtime)
//| where NodeId == nodeid
| where (isnotempty(vmid) and VmUniqueId == vmid) or (isempty(vmid) and ContainerId == queryContainerId)
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3, E17_StorageAccount, E17_StorageTenant, Network_TOR2 
| order by StartTime asc
| extend durationSec = datetime_diff("Second", EndTime, StartTime)
```

**Params:** `{starttime}`, `{endtime}`, `{vmid}`, `{queryContainerId}`

---

### VMA on VM ID

_Widget purpose:_ VMA Timeline on VM ID

Cluster: `vmainsight` · Database: `vmadb` · Type: `Timeline`
Source panel: `Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > VMA Timeline on VM ID`

```kusto
cluster('vmainsight.kusto.windows.net').database('vmadb').VMA()
| where PreciseTimeStamp between(starttime .. endtime)
// | where NodeId == nodeid
| where VmUniqueId == vmid
| where RCAEngineCategory <> "CustomerInitiated"
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3, E17_StorageAccount, E17_StorageTenant, Network_TOR2 
| order by StartTime asc
| extend Content = RCALevel2
| extend GroupBy = strcat(RCALevel1, " - ", RCALevel2) //RoleInstanceName
| extend Health = case (RCAEngineCategory in ( "Unplanned" ), "Unhealthy", RCAEngineCategory == "CustomerInitiated", "Healthy", "Neutral")
| extend durationSec = datetime_diff("Second", EndTime, StartTime)
```

**Params:** `{starttime}`, `{endtime}`, `{vmid}`

**Signal filters seen in KQL:** `RCAEngineCategory <> "CustomerInitiated"`

---
