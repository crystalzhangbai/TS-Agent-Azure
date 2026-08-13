# Container & Tenant State

> Source: EEE RDOS Start Hub dashboard (15 queries).

Use when investigating: **container state machine transitions, container OS state, container faults, CreateContainer/DestroyContainer failures, tenant-level events**. These queries answer *"what state was the container in and how did it change"*.

---

### Container State

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`

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

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus` · Database: `azurecp` · Type: `Timeline`

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

### Container Lifecycle

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`

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

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`

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

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

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

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

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

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Timeline`

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

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

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

### Anvil Event - Container

_Purpose:_ Container / Tenant Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Timeline`

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

### Holmes Events

_Purpose:_ Container / Tenant Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

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

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

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

### ContainerStateTransition

_Purpose:_ Container Transition

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`

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

_Purpose:_ Container Transition

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`

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

_Purpose:_ Extended Error Details (If Any)

Cluster: `azurecm` · Database: `azurecm` · Type: `Table`

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

_Purpose:_ CRP Operation

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`

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
