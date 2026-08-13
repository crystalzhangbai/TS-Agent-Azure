# Helpers & Resource Lookups

> Source: EEE RDOS Start Hub dashboard (21 queries).

Metadata and helper queries: resolve ARM resource IDs, find Shoebox accounts, look up node hardware properties, container policy, billing, attached disks, etc. Use these to gather context before/after running the diagnostic queries above.

---

### Retrieve Resource "Start Hub"

_Purpose:_ Start Hub - ContainerId: {{containerId}}, NodeId: {{nodeId}}

Cluster: `azcore.centralus` · Database: `azurecp` · Type: `ResourceGet`

```kusto
// print cluster = local_cluster, tenantName = local_tenantname, containerId = local_containerid, nodeId = local_nodeid, vmid = local_vmid, roleInstanceName = local_roleInstanceName
// | extend vmid = iff(isnotempty(vmid), vmid, "nodata")
MycroftContainerSnapshot
| where PreciseTimeStamp between ((globalFrom - 6h) .. (globalTo + 6h))
| where ContainerId == local_containerid and NodeId == local_nodeid 
| where isnotempty(RoleInstanceName) and RoleInstanceName endswith local_roleInstanceName
| top 1 by PreciseTimeStamp
| project azsmCluster = Cluster, cluster = Tenant, tenantName = TenantName, containerId = ContainerId, nodeId = NodeId, vmid=VirtualMachineUniqueId, roleInstanceName = RoleInstanceName, subscriptionId = SubscriptionId, creationTime = todatetime(CreationTime), additionalContainerProperties = AdditionalContainerProperties, containerType = PolicyName, billingType = BillingContext, priority = Priority, tenantOwners = ContainerLifeCycleOwner, Region, RegionFriendlyName
//| extend Dummy = "***"
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_cluster}`, `{local_containerid}`, `{local_nodeid}`, `{local_roleInstanceName}`, `{local_tenantname}`, `{local_vmid}`

---

### OverlakeNodeMap

_Purpose:_ Start Hub - ContainerId: {{containerId}}, NodeId: {{nodeId}}

Cluster: `overlakedata.southcentralus.kusto.windows.net` · Database: `overlake-syslog` · Type: `Single`

```kusto
let QueryFilterByNodeId = cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMap_Latest
| where NodeId =~ queryNodeId;
QueryFilterByNodeId
| summarize count()
| extend OverlakeState = iff(count_ == 0, "Not Enabled", "Enabled")
| project OverlakeState, NodeId = tolower(queryNodeId)
| join kind=leftouter (QueryFilterByNodeId) on NodeId
| project OverlakeState, Cluster, NodeId, SocNodeId, hostMachineName, AvailabilityZone, Region, SocOSVersion, FWVersion
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### GetShoeboxAccount

_Purpose:_ Start Hub - ContainerId: {{containerId}}, NodeId: {{nodeId}}

Cluster: `azurecm` · Database: `AzureCM` · Type: `Single`

```kusto
cluster('azurecm.kusto.windows.net').database('AzureCM').LogClusterSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Tenant =~ queryCluster
| project shoeboxMdmAccountName
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCluster}`

---

### AIPromptGenerator

_Purpose:_ AI Tool

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Single`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('AzureCP').MycroftContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where VirtualMachineUniqueId =~ queryVmId
| join kind=leftouter ( 
  cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').VM
  | where PreciseTimeStamp between (queryFrom .. queryTo)
  | where VMId == queryVmId
  | distinct armId = Key, VMId
  | take 1
  ) on $left.VirtualMachineUniqueId == $right.VMId
| parse armId with '/Subscriptions/' SubscriptionId '/ResourceGroup' *
| project PreciseTimeStamp, vmId = queryVmId, NodeId, ContainerId, TenantName, armId, SubscriptionId, RoleInstanceName, startTime = queryFrom, endTime = queryTo | order by ContainerId asc, PreciseTimeStamp asc
| extend _flag = case(prev(ContainerId) <> ContainerId, 'head', ContainerId <> next(ContainerId), 'tail', '') | where _flag <> ''
| extend From = iff (_flag == 'head', PreciseTimeStamp, datetime(null)), To = iff (_flag == 'tail', PreciseTimeStamp, datetime(null))
| extend To = iff (_flag == 'head', next (To), datetime(null))
| where _flag <> 'tail'
| project From, To, vmId, NodeId, ContainerId, TenantName, armId, SubscriptionId, RoleInstanceName, startTime, endTime | order by From asc
| distinct From, To, ContainerId, NodeId, AI_Prompt = strcat("Please run diagnostics for vmId:", vmId, " nodeId:", NodeId, " containerId: ", ContainerId, " tenantName:", TenantName, 
    " armResourceId:", armId, " subscriptionId:", SubscriptionId, " resourceName:", RoleInstanceName, " startTime:", startTime, 
    " endTime:", endTime)
| project AI_Prompt
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`

**Signal filters seen in KQL:** `_flag <> "tail"`

---

### JarvisDashTimeHelper

_Purpose:_ General Tool Links

Cluster: `azurecm` · Database: `azurecm` · Type: `Single`

```kusto
print startTimeInMs = datetime_diff('Millisecond',queryFrom, startofyear(datetime("1970"))), endTimeInMs = datetime_diff('Millisecond',queryTo, startofyear(datetime("1970")))
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### VmssIdHelper

_Purpose:_ General Tool Links

Cluster: `azurecm` · Database: `azurecm` · Type: `Single`

```kusto
print vmssid = parse_json(queryContainerProperties).VmssUniqueId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerProperties}`

---

### Unix Time Helper

_Purpose:_ General Tool Links

Cluster: `azurecm` · Database: `AzureCM` · Type: `Single`

```kusto
let toUnixTime = (dt:datetime) 
{ 
    (dt - datetime(1970-01-01)) / 1s 
};
print unixTimeFrom = toUnixTime(queryFrom)*1000, unixTimeTo = toUnixTime(queryTo)*1000, queryFrom = queryFrom, queryTo = queryTo
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### TorDeviceInfo

_Purpose:_ Network / TOR

Cluster: `azphynet` · Database: `azdhmds` · Type: `Single`

```kusto
let devicename = toscalar(cluster('azphynet').database('azdhmds').Servers
| where NodeId =~ nodeid
| project DeviceName );
cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice == devicename
| project NodeName=StartDevice, NodePort=StartPort, NodeSonicPort=StartSonicPort, TorDevice=EndDevice, EndPort, TorSonicPort=EndSonicPort, BandwidthInGbps, DataCenter
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### Unix Time Helper

_Purpose:_ Network / TOR

Cluster: `azurecm` · Database: `AzureCM` · Type: `Single`

```kusto
let toUnixTime = (dt:datetime) 
{ 
    (dt - datetime(1970-01-01)) / 1s 
};
print unixTimeFrom = toUnixTime(queryFrom)*1000, unixTimeTo = toUnixTime(queryTo)*1000, queryFrom = queryFrom, queryTo = queryTo
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### vfpMDM

_Purpose:_ Network / TOR

Cluster: `azurehn` · Database: `azurehn` · Type: `Single`

```kusto
MdmVfpVnetAccountMaps
| where Cluster == queryCluster
| project VfpAccount
```

**Params:** `{queryCluster}`

---

### Node Hardware Properties

_Purpose:_ Node (Physical)

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Single`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(startofday(starttime) .. endofday(endtime))
| where ResourceId =~ nodeid
| top 1 by PreciseTimeStamp desc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### OverlakeNodeMap

_Purpose:_ Overlake / SoC

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `Single`

```kusto
let socId = toscalar(cluster('azcore.centralus.kusto.windows.net').database('SharedWorkspace').htos(queryNodeId) | take 1);
let overlakeEnabled = iff(isempty(socId), "Not Enabled", "Enabled");
print overlakeEnabled, NodeId = queryNodeId, SocNodeId = socId
| join kind=leftouter(cluster('azcore.centralus.kusto.windows.net').database('OvlProd').LinuxOverlakeVersion
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId =~ socId
) on $left.SocNodeId == $right.NodeId
| project OverlakeState = overlakeEnabled, NodeId = queryNodeId, SocNodeId = socId, MachineName, MachineFunction, Version = PRETTY_NAME, Region
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Container Features

_Purpose:_ Tenant / Container / Node

Cluster: `azurecm.kusto.windows.net` · Database: `azurecm` · Type: `FeatureList`

```kusto
let spotVM = (cluster('azurecm.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where containerId == queryContainer
| top 1 by PreciseTimeStamp desc
| project priority
| project features = pack("Spot VM", iif((priority == "200000"), "Enabled", "Disabled")));
union spotVM, (cluster('vmainsight.kusto.windows.net').database('Air').LmApplicableVms
| where SnapshotTime between (queryFrom .. queryTo)
| where ContainerId == queryContainer
| summarize arg_max(SnapshotTime, *) 
| project ContainerId, IsLmEligible, IsSwiftVm, IsLmDisabledTenantVm
| project features = pack(
    "Swift VM", iif(tobool(IsSwiftVm), "Enabled", "Disabled"),
    "LM Eligible", iif(tobool(IsLmEligible), "Enabled", "Disabled"), 
    "LM on Tenant", iif(tobool(IsLmDisabledTenantVm), "Disabled", "Enabled")))   
| mv-expand bagexpansion=array features
| project FeatureName = tostring(features[0]), State = tostring(features[1])
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainer}`

---

### PageInputHelper

_Purpose:_ VM

Cluster: `azurecm` · Database: `AzureCM` · Type: `Single`

```kusto
let vmssid = parse_json(queryContainerProperties).VmssUniqueId;
print Input = strcat ("{\"Cluster\":\"", queryCluster, "\",\"ContainerId\":\"", queryContainerId, "\",\"NodeId\":\"", queryNodeId, "\",\"RoleInstanceName\":\"", 
queryRoleInstanceName, "\",\"VMSize\":\"", queryContainerType, "\",\"TenantName\":\"", queryTenantName, "\",\"VmId\":\"", queryVmId, "\",\"VmssId\":\"", vmssid, "\",\"Region\":\"", queryRegion, "\"}")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCluster}`, `{queryContainerId}`, `{queryNodeId}`, `{queryRoleInstanceName}`, `{queryTenantName}`, `{queryVmId}`, `{queryRegion}`, `{queryContainerType}`, `{queryContainerProperties}`

---

### GetARMResourceId

_Purpose:_ VM

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Single`

```kusto
let _vmid = iff(isempty(queryVMId), "dummyId", queryVMId);
union
(cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').VMScaleSet
| where PreciseTimeStamp between (queryFrom .. queryTo)
// | where VMScaleSetVMInstanceId == queryVMId
| where SubscriptionId == querySubId
| extend _VMScaleSetId = parse_json(queryProperties).VmssUniqueId
| where VMScaleSetId == _VMScaleSetId
| top 1 by PreciseTimeStamp asc
| project SubscriptionId, ResourceGroupName, ResourceName = VMScaleSetName, VmssResourceId = strcat("/subscriptions/", SubscriptionId, "/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Compute/virtualMachineScaleSets/", VMScaleSetName) 
),(
cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').VM 
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where VMId == _vmid and toupper(VMName) == toupper(trim_start("_", queryRoleInstanceName))
| top 1 by PreciseTimeStamp asc 
| project SubscriptionId, ResourceGroupName, ResourceName = VMName, VMResourceId = strcat("/subscriptions/", SubscriptionId, "/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Compute/virtualMachines/", VMName) 
)
| extend ArmResourceId = case(isnotempty(VMResourceId), VMResourceId, isnotempty(VmssResourceId), VmssResourceId, "")
| extend ResourceType = case(isnotempty(VMResourceId), "CRP/VM", isnotempty(VmssResourceId), "CRP/VMSS", "Unknown")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`, `{queryVMId}`, `{queryRoleInstanceName}`, `{queryProperties}`

---

### GetShoeboxAccount

_Purpose:_ VM

Cluster: `azurecm` · Database: `AzureCM` · Type: `Single`

```kusto
cluster('azurecm.kusto.windows.net').database('AzureCM').LogClusterSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Tenant =~ queryCluster
| project shoeboxMdmAccountName
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCluster}`

---

### VmssIdHelper

_Purpose:_ VM

Cluster: `azurecm` · Database: `azurecm` · Type: `Single`

```kusto
print vmssid = parse_json(queryContainerProperties).VmssUniqueId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerProperties}`

---

### Azure Host VM Blobs

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`

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

### Compute Hour Usage Table

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`

```kusto
FaComputeHourUsageEventCentralBondTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where (isnotempty(queryVMId) and BillingContext contains queryVMId) or (isempty(queryVMId) and ContainerId == queryContainerId)
| project PreciseTimeStamp, VMId, ContainerId, NodeId, VPCount, VMMemory, Quantity, HypervContextRank, UsageResourceKind, BillingContext
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVMId}`, `{queryContainerId}`

---

### ContainerPolicyQuery

_Purpose:_ Container Definition

Cluster: `azurevmcentral.westus2.kusto.windows.net` · Database: `azurevmcentral` · Type: `Single`

```kusto
cluster('azurevmcentral.westus2.kusto.windows.net').database('azurevmcentral').latest_vm_definitions
| where fabricname contains queryPolicyName
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryPolicyName}`

---

### CRP VM Snapshot

_Purpose:_ VM Entry

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Single`

```kusto
union cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').VM ,  cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').VMScaleSetVMInstance
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where (VMId == vmid or VMScaleSetVMInstanceId ==vmid)and (toupper(VMName) == toupper(trim_start("_", queryRoleInstanceName)) or toupper(strcat(VMScaleSetName,"_",InstanceIdString)) == toupper(trim_start("_", queryRoleInstanceName)))
| top 1 by PreciseTimeStamp asc
| extend ArmResourceId = iff(isempty(VMId),strcat("/subscriptions/", SubscriptionId, "/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Compute/virtualMachineScaleSets/", VMScaleSetName) ,strcat("/subscriptions/", SubscriptionId, "/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Compute/virtualMachines/", VMName) )
| project PreciseTimeStamp, ResourceGroupName = tolower(ResourceGroupName), SubscriptionId = tolower(SubscriptionId),iff(isempty(VMId),VMId=VMScaleSetVMInstanceId,VMId), iif(isempty(VMName),VMName = tolower(VMName), VMName=toupper(strcat(VMScaleSetName,"_",InstanceIdString))), Region, Key, VMTags, VMResourcePurchasePlan, VMTimeCreated, VMToBeDeleted, VMSize, DesiredPowerState, NetworkProfile, 
   ComputerName, OSDiskOSType, OSDiskCreateOption, OSDiskCachingType, OSDiskId, OSDiskTimeCreated, OSDiskToBeDeleted, OSDiskManagedDiskStorageAccountType, 
   AvailabilitySetKey, HyperVGeneration, CommitSequenceNumber, ArmResourceId
| extend Dummy = "***"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmid}`, `{queryRoleInstanceName}`

---
