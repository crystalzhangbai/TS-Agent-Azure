# Container

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Container** (25 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Container / Tenant

### Anvil Event

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`
Source panel: `Container > Container / Tenant > Anvil Recovery Action > Anvil Recovery Action > Anvil Event`

```kusto
cluster("aplat.westcentralus.kusto.windows.net").database("APlat").AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (starttime .. endtime)
| where ResourceId == nodeid
| project PreciseTimeStamp, Cluster, Role, MessageTrigger, TreeName, TreeNodeKey, TreeActionName, TreeActionInput, Properties, TaskStatus, Message, ResourceId, ResourceType, ResourceDependencies
| order by PreciseTimeStamp asc
| extend level = case(TaskStatus in ("Failure", "Faulted"), "error", 
    TaskStatus contains "Failed", "error", 
    "info")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Anvil Operation

_Widget purpose:_ Anvil Event Timeline

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Container > Container / Tenant > Anvil Recovery Action > Anvil Recovery Action > Anvil Event Timeline`

```kusto
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (starttime .. endtime)
| where ResourceId == nodeid
| where MessageTrigger contains "OnBeforeVisitNode"
| extend tail_MessageTrigger = case (MessageTrigger contains "VisitNode", "VisitNode", "")
| project PreciseTimeStamp, Cluster, Role, SessionId, MessageTrigger, TreeNodeKey, Properties, TaskStatus, Message, ResourceId, ResourceType, ResourceDependencies, tail_MessageTrigger
| extend StartTime = PreciseTimeStamp
| order by StartTime asc
| join kind=leftouter (
    cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceForgeEvents
    | where PreciseTimeStamp between (starttime .. endtime)
    | where ResourceId == nodeid
    | where MessageTrigger contains "OnAfterVisitNode" 
    | extend tail_MessageTrigger = case (MessageTrigger contains "VisitNode", "VisitNode", "")
    | project EndTime = PreciseTimeStamp, SessionId,  tail_MessageTrigger, TreeNodeKey
) on $left.tail_MessageTrigger ==$right.tail_MessageTrigger and $left.TreeNodeKey == $right.TreeNodeKey and $left.SessionId == $right.SessionId
| extend Content = ""
| extend Health = case (isnotempty(EndTime), "Healthy", "Unhealthy")
| extend GroupBy = TreeNodeKey
| extend EndTime = case (isnotempty(EndTime), EndTime, datetime_add("minute", 5, StartTime))
| order by StartTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `MessageTrigger contains "OnBeforeVisitNode"` · `MessageTrigger contains "OnAfterVisitNode"`

---

### Anvil Event Trigger

_Widget purpose:_ Anvil Event Timeline

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Container > Container / Tenant > Anvil Recovery Action > Anvil Recovery Action > Anvil Event Timeline`

```kusto
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (starttime .. endtime)
| where ResourceId == nodeid
| where MessageTrigger contains "WalkTree"
| project PreciseTimeStamp, Cluster, Role, MessageTrigger, TreeName, TreeNodeKey, TreeActionName, TreeActionInput, Properties, TaskStatus, Message, ResourceId, ResourceType, ResourceDependencies
| order by PreciseTimeStamp asc 
| extend StartTime = PreciseTimeStamp
| extend Content = case (MessageTrigger contains "OnBefore", "Start",
    MessageTrigger contains "OnAfter", "End", 
    MessageTrigger contains "OnCleanup", "Cleanup", 
    "")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `MessageTrigger contains "WalkTree"`

---

### Azure Host VM Blobs

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `Container > Container / Tenant > Attached Disks`

```kusto
let ClusterInfo = cluster('Azcsupfollower.kusto.windows.net').database('AzureCM').LogClusterSnapshot
    | where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 1h)) //and Tenant == cluster
    | distinct Tenant, AvailabilityZone;
cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and Cluster == cluster
| extend ContainerId = tostring(split(split(SurfaceName, "_")[0], "~")[0])
| where ContainerId == containerId or SurfaceName contains vmId
| union (cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsUltraSSDCounterTable | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and Cluster == cluster and ContainerId contains containerId)
| parse ArmId with * "/disks/" DiskName
//| parse BlobPath with NewBlobPath "?" *
| parse BlobPath with * "/" NewBlobPath "?" *
| extend BlobPath = case(isnotempty(NewBlobPath), NewBlobPath, BlobPath)
| extend StorageAccount = tostring(split(BlobPath, "/")[0])
| extend SurfaceName = case(isempty(SurfaceName), SurfaceGUID, SurfaceName)
| extend ThrottleIndices = replace_string(ThrottleCountersListString, ";", "")
| extend DiskSkuType = case(IsXIOdisk == 1, "Premium SSD", 
                            BlobPath contains "md-ssd-", "Standard SSD", 
                            IsXIOdisk == 0 and BlobPath !contains "md-ssd-" and Type == 0, "Standard HDD",
                            DiskSkuType == 0, "UltraSSD",
                            DiskSkuType == 1, "Premium SSD V2","")
| summarize arg_max(PreciseTimeStamp, CachePolicy, BlobPath, ContainerId, StorageAccount, EncryptionFlags, Type, StorageTenant, SDFTenant, Cluster, DiskType, SlotId, DiskName, DiskSkuType, ArmId, BSId, WSId, ThrottleIndices) by SurfaceName
| distinct CachePolicy, SurfaceName, BlobPath, ContainerId, StorageAccount, EncryptionFlags, Type, StorageTenant, SDFTenant, Cluster, DiskType, SlotId, DiskName, DiskSkuType, ArmId, BSId, WSId, ThrottleIndices
| extend StorageTenant = case(isempty(StorageTenant), tolower(tostring(split(SDFTenant, "-")[1])), StorageTenant)
| join kind = leftouter (
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsConfigTable
    | where PreciseTimeStamp between ((startTime - 6h)  .. (endTime + 6h))
            and NodeId == nodeId and Component == "blobprop" and Cluster == cluster
    | extend BlobProperties = parse_json(ConfigValue)
    | extend 
             DiskAccessTier = tostring(BlobProperties.blobproperties['x-ms-access-tier']),
             EnhancedConnectionVersion = BlobProperties.blobproperties["x-ms-enhancedconnectionversion"],
             StorageTenant = tostring(BlobProperties.storagecluster)
    | extend BlobProperties = BlobProperties.blobproperties
    | summarize arg_max(PreciseTimeStamp, *) by ConfigName
    | project BlobPath = ConfigName, DiskAccessTier, EnhancedConnectionVersion, BlobProperties, StorageTenant, NodeId
    | parse BlobPath with * "/" BlobPath
) on BlobPath
| extend StorageTenant = case(isnotempty(StorageTenant), StorageTenant, StorageTenant1)
| extend EnhancedConnectionVersion = case(isempty(BlobProperties), "Unknown", EnhancedConnectionVersion)
| project-away BlobPath1
// Stitch Compute Cluster Properties for Availability Zone
| join kind=leftouter (
    ClusterInfo
) on $left.Cluster == $right.Tenant
| extend StorageCluster = substring(tolower(StorageTenant), 0, strlen(StorageTenant) - 1)
| join kind=leftouter (
    ClusterInfo | project Tenant = tolower(Tenant), StorageClusterAvailabilityZone = AvailabilityZone
) on $left.StorageCluster == $right.Tenant
// join for blobproperties from vhddisk, osconfigtable may not have entries for newly created disks
| join kind=leftouter (
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').VhdDiskEtwEventTable
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
    | where EventId == 31
    | parse EventMessage with * "NewDiskName: /" BlobPath "." * "x-ms-access-tier: " DiskAccessTier "\r" *  "x-ms-enhancedconnectionversion: " EnhancedConnectionVersion "\r" *
    | summarize arg_max(PreciseTimeStamp, *) by BlobPath
    | project BlobPath, DiskAccessTier, EnhancedConnectionVersion
) on BlobPath
| join kind=leftouter(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').XdiskSvcEvent
    | where PreciseTimeStamp between (startTime .. endTime) and eventType == 411 and NodeId == nodeId
    | extend ArmId = tostring(parse_json(message)["x-ms-disk-resource-uri"]), DiskAccessTier = tostring(parse_json(message)["x-ms-access-tier"]), 
            EnhancedConnectionVersion = tostring(parse_json(message)["x-ms-enhancedconnectionversion"])
    | summarize arg_max(PreciseTimeStamp, *) by ArmId
) on ArmId
| extend DiskAccessTier = case(isnotempty(DiskAccessTier2), DiskAccessTier2, isnotempty(DiskAccessTier1), DiskAccessTier1, DiskAccessTier),
         EnhancedConnectionVersion = case(isempty(EnhancedConnectionVersion2), EnhancedConnectionVersion2, isempty(EnhancedConnectionVersion1), EnhancedConnectionVersion1, EnhancedConnectionVersion)
//
// Stitch T2 Colocation
//
| extend compute_cluster = tolower(Cluster)
// | join kind=leftouter (
//     cluster("azdhrdma.centralus.kusto.windows.net").database("azdhrdma").AppStpUnderSameT2Mapping()
//     | where compute_cluster contains cluster
//     | extend compute_cluster = tolower(compute_cluster)
// ) on compute_cluster
| extend DiskType = case(DiskType == 1, "OS Disk", DiskType == 2, "Temp Disk", DiskType == 3 or BlobPath contains "md-dd", "Data Disk", SurfaceName startswith "BASE_", "Ephemeral OS Disk Base", "")
| extend DiskType = case(Type == 4, strcat(DiskType, " (WriteAccelerator)"), DiskType)
| extend AZColocation = case(CachePolicy == 5, "", AvailabilityZone  == StorageClusterAvailabilityZone, "Yes", isnotempty(AvailabilityZone) or isnotempty(StorageClusterAvailabilityZone), "No", "Unknown")
//| extend T2Colocation = case(CachePolicy == 5, "", xio_clusters contains StorageCluster, "Yes", "No")
| extend LUN = case(DiskType == "OS Disk" or DiskType == "Temp Disk", "NA", tostring(SlotId))
//| project CachePolicy, EncryptionFlags, DiskType, DiskSkuType, DiskName, SurfaceName, BlobPath, StorageTenant, DiskAccessTier, FastPathEnabled = case(DiskType == "Temp Disk", "", EnhancedConnectionVersion == "Unknown", "Unknown", tostring(isnotempty(EnhancedConnectionVersion))), LUN, BSId, WSId, ThrottleIndices, BlobProperties, StorageAccount, AZColocation, T2Colocation, ArmId //, xio_clusters, AvailabilityZone, StorageCluster, StorageClusterAvailabilityZone
| project CachePolicy, EncryptionFlags, DiskType, DiskSkuType, DiskName, SurfaceName, BlobPath, StorageTenant, DiskAccessTier, FastPathEnabled = case(DiskType == "Temp Disk", "", EnhancedConnectionVersion == "Unknown", "Unknown", tostring(isnotempty(EnhancedConnectionVersion))), LUN, BSId, WSId, ThrottleIndices, BlobProperties, StorageAccount, AZColocation, ArmId, NodeId //T2Colocation, xio_clusters, AvailabilityZone, StorageCluster, StorageClusterAvailabilityZone
| extend CachePolicy = case(CachePolicy == 0, "None", CachePolicy == 1, "ReadOnly", CachePolicy == 2, "ReadWrite", CachePolicy == 5, "LocalDisk", BlobPath contains "md-dd", "None", tostring(CachePolicy))
| extend DiskJson = strcat('{', '"DiskName": "', DiskName, '", "ArmId": "', ArmId, '","Cache": "', CachePolicy, '", "Type": "', DiskType, '", "SKU": "', DiskSkuType, '", "Tier": "', DiskAccessTier, 
    '", "Blob": "', BlobPath, '", "Surface": "', SurfaceName, '", "StorageTenant": "', StorageTenant, '", "FastPathEnabled": "', FastPathEnabled, '", "LUN": "', LUN,'"}')
//
// |join kind=leftouter (
//     cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwEventTable
//     //AsapPfEtwTraceLogEventView
//     | where PreciseTimeStamp between (startTime-2h..endTime)
//     | where NodeId == nodeId and EventMessage has containerId
//     | where EventId in (4243, 4244)
//     | parse EventMessage with * "AsapPF attached an XIO namespace. VfId: " VfId ", NSID: " NSID ", NsIndex: " NsIndex ", " *
//     // | extend json = parse_json(Message)
//     // | extend VfId = json.VfId
//     // | extend NSID = json.NSID
//     //| project PreciseTimeStamp, EventId, Level, EventName, VfId, NSID, NsIndex, NsName, Message //, json
//     | summarize arg_max(PreciseTimeStamp, *) by NSID
//     | project NodeId, VfId, NSID, NsIndex
// ) on NodeId
// | project-away NodeId1, NsIndex
//| where CachePolicy != "None"
//
| sort by DiskType desc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{cluster}`, `{nodeId}`, `{vmId}`

**Signal filters seen in KQL:** `CachePolicy != "None"`

---

### Query PaaS Container in  LogContainerSnapshot

_Widget purpose:_ Container Change History

Cluster: `Azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Change History`

```kusto
let instanceName  = toscalar(cluster('azcsupfollower').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where containerId == queryContainerId
| where isnotempty(roleInstanceName)
| distinct roleInstanceName
| take 1);
cluster('Azcsupfollower').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| where roleInstanceName == instanceName
| extend creationTime = todatetime(creationTime)
| distinct creationTime, roleInstanceName, Tenant, tenantName, containerId, nodeId, tenantOwners, containerType, Region, AvailabilityZone
| order by creationTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryTenantName}`

---

### Container Event

_Widget purpose:_ Container Health for Container Id

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Health for Container Id`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
| where containerId == containerid
//| where virtualMachineUniqueId == vmid
| where containerLifecycleState in ("ToBeDestroyedOnNode", "Destroyed")
| project StartTime = PreciseTimeStamp, Tenant, roleInstanceName,  tenantName, containerId, nodeId, 
  containerState, actualOperationalState, containerLifecycleState, containerOsState, faultInfo , virtualMachineUniqueId
| order by StartTime asc
| extend flag = case (containerState <> prev(containerState) or actualOperationalState <> prev(actualOperationalState) or containerLifecycleState <> prev(containerLifecycleState) or containerOsState <> prev(containerOsState) or faultInfo <> prev(faultInfo), "changed", "")
| where flag <> ""
// | extend level = case (containerOsState in ("ContainerOsStateUnknown", "ContainerOsStateUnresponsive", "ContainerOsStateUnhealthy"), "critical", 
//    containerOsState in ("ContainerOsStateHealthy", "ContainerOsStateProvisioningCompleted"), "info", 
//    containerOsState in ("ContainerOsStateInternalShutdown", "ContainerOsStateProvisioningTimedOut", "ContainerOsStateProvisioningRecovery", "ContainerOsStateProvisioningFailed"), "error", 
//    "warning")
| extend Content = containerLifecycleState
```

**Params:** `{starttime}`, `{endtime}`, `{containerid}`

---

### Query PaaS Container in LogContainerHealthSnapshot

_Widget purpose:_ Container Health State

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Health State`

```kusto
let instanceName  = toscalar(cluster('azcsupfollower').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where containerId == queryContainerId
| where isnotempty(roleInstanceName)
| distinct roleInstanceName
| take 1);
LogContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| where roleInstanceName == instanceName
| project PreciseTimeStamp, Tenant, roleInstanceName,  tenantName, containerId, nodeId, 
  containerState, actualOperationalState, containerLifecycleState, containerOsState, faultInfo , virtualMachineUniqueId, FabricRoleInstance = RoleInstance, containerIsolationState
| order by PreciseTimeStamp asc
| extend flag = case (
  containerState <> prev(containerState) 
  or actualOperationalState <> prev(actualOperationalState) 
  or containerLifecycleState <> prev(containerLifecycleState) 
  or containerOsState <> prev(containerOsState) 
  or faultInfo <> prev(faultInfo),
  "changed", "")
| where queryFilter == "All" or (queryFilter != "All" and flag <> "")
// | extend level = case (containerOsState in ("ContainerOsStateUnknown", "ContainerOsStateUnresponsive", "ContainerOsStateUnhealthy"), "critical", 
//    containerOsState in ("ContainerOsStateHealthy", "ContainerOsStateProvisioningCompleted"), "info", 
//    containerOsState in ("ContainerOsStateInternalShutdown", "ContainerOsStateProvisioningTimedOut", "ContainerOsStateProvisioningRecovery", "ContainerOsStateProvisioningFailed"), "error", 
//    "warning")
| extend level = case (containerState in ("ContainerStateUnresponsive", "ContainerStateUnhealthy"), "critical",
  isnotempty(faultInfo), "critical", 
  "info")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryFilter}`, `{queryTenantName}`

**Signal filters seen in KQL:** `queryFilter == "All"`

---

### FilterStates

_Widget purpose:_ Container Health State

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Filter` · Widget: `Table`
Source panel: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Health State`

```kusto
datatable (Value:string, Description:string)
[
    "StateTransition", "State Transition Only (default)",
    "All", "All"
]
```

---

### Container Performance for Container Id

_Widget purpose:_ Container Performance

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Performance`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (starttime .. endtime)
| where VmId == containerid
| project PreciseTimeStamp, Cluster, TenantId, NodeId, VmId, RoleId, RoleInstanceId, CounterName, SampleCount, AverageCounterValue, MinCounterValue, MaxCounterValue
| summarize sum(AverageCounterValue) by PreciseTimeStamp, CounterName
```

**Params:** `{starttime}`, `{endtime}`, `{containerid}`

---

### FilterStates

_Widget purpose:_ Container Performance

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Performance`

```kusto
datatable (Value:string, Description:string)
[
    "StateTransition", "State Transition Only (default)",
    "All", "All"
]
```

---

### Query LogRoleInstanceSnapshot

_Widget purpose:_ LogRoleInstanceSnapshot

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > LogRoleInstanceSnapshot`

```kusto
LogRoleInstanceSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName  and roleInstanceName == queryRoleInstanceName
| project PreciseTimeStamp, tenantName, roleInstanceName, containerId, roleState, provisioningState, isNmProgrammingComplete, updateDomain
| order by PreciseTimeStamp asc
| extend flag = case (
  containerId <> prev(containerId) 
  or roleState <> prev(roleState) 
  or provisioningState <> prev(provisioningState) 
  or isNmProgrammingComplete <> prev(isNmProgrammingComplete) 
  or updateDomain <> prev(updateDomain),
  "changed", "")
| where flag <> ""
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRoleInstanceName}`, `{queryTenantName}`

---

### Query PaaS Container in VmHealthRawStateEtwTable

_Widget purpose:_ VmHealthRawStateEtwTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > VmHealthRawStateEtwTable`

```kusto
let instanceName  = toscalar(cluster('azcsupfollower').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where containerId == queryContainerId
| where isnotempty(roleInstanceName)
| distinct roleInstanceName
| take 1);
VmHealthRawStateEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where ContainerId == queryContainerId
| project  PreciseTimeStamp, Cluster, ContainerId, IsVscStateOperational, VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted, NodeId, Context
| order by PreciseTimeStamp asc
| extend flag = case (VmHyperVIcHeartbeat != prev(VmHyperVIcHeartbeat)
    or VmPowerState != prev(VmPowerState)
    or Context != prev(Context) 
    or HasHyperVHandshakeCompleted != prev(HasHyperVHandshakeCompleted)
    or IsVscStateOperational != prev(IsVscStateOperational),
    "changed", "")
| where queryFilter == "All" or (queryFilter != "All" and flag <> "")
| extend level = case (VmHyperVIcHeartbeat in ("HeartBeatStateNoContact"), "critical", 
    (VmHyperVIcHeartbeat == "HeartBeatStateOk" and VmPowerState == "PowerStateEnabled" and HasHyperVHandshakeCompleted == "true" and IsVscStateOperational == "true"), "info", 
    VmHyperVIcHeartbeat in ("HeartBeatStateNonRecoverableError", "HeartBeatStateLostCommunication ", "NotMonitored", "HeartBeatStateDegraded"), "error", 
    "warning")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryTenantName}`, `{queryFilter}`

**Signal filters seen in KQL:** `queryFilter == "All"`

---

### FilterStates

_Widget purpose:_ VmHealthRawStateEtwTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Filter` · Widget: `Table`
Source panel: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > VmHealthRawStateEtwTable`

```kusto
datatable (Value:string, Description:string)
[
    "StateTransition", "State Transition Only (default)",
    "All", "All"
]
```

---

### GuestAgentAndExtensionTimeline

_Widget purpose:_ Guest Agent & Extension Provisioning

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Container > Container / Tenant > Guest OS Logs > Guest OS Logs > Guest Agent & Extension Provisioning`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where PreciseTimeStamp between( queryFrom.. queryTo) 
| where ContainerId == queryContainerid
//| project PreciseTimeStamp, Level, RoleInstanceName, ContainerId, Name, TaskName, Operation, OperationSuccess, Message, OpcodeName
| where (TaskName == "Daemon") or (TaskName == "ExtHandler" and Operation == "GoalState") or OperationSuccess == "False" or (Name !contains "WALinuxAgent" and Name !contains "WindowsAzureGuestAgent")
| extend StartTime = todatetime(OpcodeName), Content = Operation
| extend GroupBy = case(Name contains "Agent", strcat(Name, "/", TaskName, "/", Operation), Name)
| extend Health = case (OperationSuccess <> "True", "Unhealthy", Message contains "transitioning" or Message contains "NotReady" or Message contains "error", "Degraded", "Healthy")
| project StartTime, GroupBy, PreciseTimeStamp, RoleInstanceName, ContainerId, Name, TaskName, Operation, OperationSuccess, Message, Content, Health
| order by GroupBy, StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerid}`

---

### Guest OS Logs

_Widget purpose:_ Guest OS Extension Log filter by ContainerId - GuestAgentExtensionEvents

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Container > Container / Tenant > Guest OS Logs > Guest OS Logs > Guest OS Extension Log filter by ContainerId - GuestAgentExtensionEvents`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where PreciseTimeStamp between( starttime .. endtime ) 
| where ContainerId == queryContainerId
| extend Message = iif (Name contains "AzureBatchComputeNode", base64_decode_tostring(Message) , Message)
| project PreciseTimeStamp, Level, RoleInstanceName, ContainerId, Name, TaskName, Operation, OperationSuccess, Message
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{queryContainerId}`

---

### GuestOSGenericLogs

_Widget purpose:_ Guest OS Log

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Container > Container / Tenant > Guest OS Logs > Guest OS Logs > Guest OS Log`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentGenericLogs
| where PreciseTimeStamp between( starttime .. endtime ) 
| where ContainerId == containerid
| extend Context1 = iif (EventName contains "AzureBatchComputeNode", base64_decode_tostring(Context1) , Context1)
| project PreciseTimeStamp, Cluster, Level, RoleInstanceName, GAVersion, EventName, CapabilityUsed, Context1, Context2, Context3, OSVersion, ExecutionMode, RAM
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{containerid}`

---

### Container Change History

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Table`
Source panel: `Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > Container Change History`

```kusto
MycroftContainerSnapshot
| where PreciseTimeStamp between (starttime .. now())
| where (isnotempty(vmid) and VirtualMachineUniqueId == vmid) or (isempty(vmid) and ContainerId == queryContainerId)
| extend CreationTime = todatetime(CreationTime)
| summarize LastSeen = max(PreciseTimeStamp), FirstSeen = min(PreciseTimeStamp) by CreationTime, RoleInstanceName, Tenant, ClusterName, ContainerId, NodeId, VirtualMachineUniqueId, TenantName, ContainerType, Region, AvailabilityZone
| where FirstSeen < endtime or CreationTime < endtime
| order by CreationTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{vmid}`, `{queryContainerId}`

---

### FilterStates

_Widget purpose:_ Container Health State

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Filter` · Widget: `Table`
Source panel: `Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > Container Health State`

```kusto
datatable (Value:string, Description:string)
[
    "StateTransition", "State Transition Only (default)",
    "All", "All"
]
```

---

### LogContainerHealthSnapshot

_Widget purpose:_ Container Health State

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Table`
Source panel: `Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > Container Health State`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
// | where containerId == local_containerId
| where (isnotempty(vmid) and VirtualMachineUniqueId == vmid) or (isempty(vmid) and ContainerId == queryContainerId)
| project PreciseTimeStamp, RoleInstance, Tenant, RoleInstanceName,  TenantName, ContainerId, NodeId, 
  ContainerState, ActualOperationalState, LifecycleState, OsState, FaultInfo , VirtualMachineUniqueId, FabricRoleInstance = RoleInstance, IsolationState
| order by PreciseTimeStamp asc
| extend flag = case (
  ContainerState <> prev(ContainerState) 
  or ActualOperationalState <> prev(ActualOperationalState) 
  or LifecycleState <> prev(LifecycleState) 
  or OsState <> prev(OsState) 
  or FaultInfo <> prev(FaultInfo),
  "changed", "")
| where queryFilter == "All" or (queryFilter != "All" and flag <> "")
| extend level = case (OsState in ("ContainerOsStateUnknown", "ContainerOsStateUnresponsive", "ContainerOsStateUnhealthy"), "critical", 
    OsState in ("ContainerOsStateHealthy", "ContainerOsStateProvisioningCompleted"), "info", 
    OsState in ("ContainerOsStateInternalShutdown", "ContainerOsStateProvisioningTimedOut", "ContainerOsStateProvisioningRecovery", "ContainerOsStateProvisioningFailed"), "error", 
    "warning")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryFilter}`, `{queryContainerId}`, `{vmid}`

**Signal filters seen in KQL:** `queryFilter == "All"`

---

### FilterStates

_Widget purpose:_ HyperV States - VmHealthRawStateEtwTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Filter` · Widget: `Table`
Source panel: `Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > HyperV States - VmHealthRawStateEtwTable`

```kusto
datatable (Value:string, Description:string)
[
    "StateTransition", "State Transition Only (default)",
    "All", "All"
]
```

---

### HyperV states from VmHealthRawStateEtwTable

_Widget purpose:_ HyperV States - VmHealthRawStateEtwTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > HyperV States - VmHealthRawStateEtwTable`

```kusto
VmHealthRawStateEtwTable
| where PreciseTimeStamp between (queryStart .. queryEnd)
| where VirtualMachineUniqueId == queryVmUniqueId
| project  PreciseTimeStamp, Cluster, ContainerId, IsVscStateOperational, VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted, NodeId, VirtualMachineUniqueId, Context
| order by PreciseTimeStamp asc
| extend flag = case (VmHyperVIcHeartbeat != prev(VmHyperVIcHeartbeat)
    or VmPowerState != prev(VmPowerState)
    or Context != prev(Context) 
    or HasHyperVHandshakeCompleted != prev(HasHyperVHandshakeCompleted)
    or IsVscStateOperational != prev(IsVscStateOperational),
    "changed", "")
| where queryFilter == "All" or (queryFilter != "All" and flag <> "")
| extend level = case (VmHyperVIcHeartbeat in ("HeartBeatStateNoContact"), "critical", 
    (VmHyperVIcHeartbeat == "HeartBeatStateOk" and VmPowerState == "PowerStateEnabled" and HasHyperVHandshakeCompleted == "true" and IsVscStateOperational == "true"), "info", 
    VmHyperVIcHeartbeat in ("HeartBeatStateNonRecoverableError", "HeartBeatStateLostCommunication ", "NotMonitored", "HeartBeatStateDegraded"), "error", 
    "warning")
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryVmUniqueId}`, `{queryFilter}`

**Signal filters seen in KQL:** `queryFilter == "All"`

---

### Query LogRoleInstanceSnapshot

_Widget purpose:_ LogRoleInstanceSnapshot

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > LogRoleInstanceSnapshot`

```kusto
LogRoleInstanceSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName  and roleInstanceName == queryRoleInstanceName
| project PreciseTimeStamp, tenantName, roleInstanceName, containerId, roleState, provisioningState, isNmProgrammingComplete, updateDomain
| order by PreciseTimeStamp asc
| extend flag = case (
  containerId <> prev(containerId) 
  or roleState <> prev(roleState) 
  or provisioningState <> prev(provisioningState) 
  or isNmProgrammingComplete <> prev(isNmProgrammingComplete) 
  or updateDomain <> prev(updateDomain),
  "changed", "")
| where flag <> ""
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRoleInstanceName}`, `{queryTenantName}`

---

### Query FaComputeHourUsageEventCentralBondTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Container > Container / Tenant > Others > Billing `

```kusto
FaComputeHourUsageEventCentralBondTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where (isnotempty(queryVMId) and BillingContext contains queryVMId) or (isempty(queryVMId) and ContainerId == queryContainerId)
| project PreciseTimeStamp, VMId, ContainerId, NodeId, VPCount, VMMemory, Quantity, HypervContextRank, UsageResourceKind, BillingContext
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryVMId}`

---

### Query LogHealthAnnotationEvent

_Widget purpose:_ Annotation from LogHealthAnnotationEvent

Cluster: `azcsupfollower.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `Container > Container / Tenant > Others > Resource Health Annotation > Annotation from LogHealthAnnotationEvent`

```kusto
LogHealthAnnotationEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where (isnotempty(queryVMId) and resourceIdentity contains queryVMId) or (isempty(queryVMId) and containerIdentifier == queryContainerId)
| project PreciseTimeStamp, resourceIdentity, containerIdentifier, annotation
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryVMId}`

---

### Query RhcAnnotationReportsEtwTable

_Widget purpose:_ Annotation from RhcAnnotationReportsEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Container > Container / Tenant > Others > Resource Health Annotation > Annotation from RhcAnnotationReportsEtwTable`

```kusto
RhcAnnotationReportsEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where (isnotempty(queryVMId) and VmId == queryVMId) or (isempty(queryVMId) and ContainerId == queryContainerId)
| project PreciseTimeStamp, VmId, ContainerId, Annotation
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVMId}`, `{queryContainerId}`

---
