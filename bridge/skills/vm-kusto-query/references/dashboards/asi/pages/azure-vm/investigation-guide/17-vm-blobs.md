# VM Blobs

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Blobs** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ABC Throttles

### Azure Host VM ABCThrottles

_Widget purpose:_ ABC Throttles

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Blobs > ABC Throttles`

**Tables:** `OsBlobCacheConfigTableV2`, `OsXIOSurfaceCounterTable`
**Aggregations:** `summarize arg_max(PreciseTimeStamp, *) by EntityId, EntityConfig, UserData` · `summarize take_any(ThrottleConfig) by ThrottleIndex, IOPS, BPS, ThrottleType, BurstType, BurstState, BurstIOPS, BurstB`
**Output columns:** `userdata`

```kusto
let ThrottleType = (tag:string) {
    case(tag startswith "NetworkThrottle", "Remote Blob Limit (NetworkThrottle)",
        tag startswith "VmIoSettingsnetworkthrottle", "Remote VM Limit (VmIoSettingsnetworkthrottle)",
        tag startswith "XioSettingsnetworkthrottle", "Remote VM Limit (XioSettingsnetworkthrottle)",
        tag startswith "VmIoSettingsssdthrottle", "Local VM Limit (VmIoSettingsssdthrottle)",
        tag startswith "XioSettingsssdthrottle", "Local VM Limit (XioSettingsssdthrottle)",
        tag startswith "Hardwaressd", "Hardware SSD Limit",
        tag startswith "Hardwarenetwork", "Hardware Network Limit",
        tag startswith "dedicated", "Local VM Limit (dedicated Cached Disk)", 
        tag startswith "LldIoSettingsNetworkThrottle", "Barbera Disk Limit",
        "Unknown")
};
//
//Surfaces with respective backingStoreId and throttleIndices
//
let surfaces = OsBlobCacheConfigTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId and EntityType == 1 and EntityId contains containerId
| distinct EntityId, EntityType, EntityConfig, UserData
| extend backingStoreId = parse_json(EntityConfig).backing_store_index, throttleIndices = parse_json(EntityConfig).throttle_indices
| distinct surfaceName = EntityId, backingStoreId = tostring(backingStoreId), throttleIndices = tostring(throttleIndices);
//
//Surface level throttles
//
let surfacesThrottles = surfaces | mv-expand todynamic(throttleIndices) 
| distinct backingStoreId, throttleIndices = tostring(throttleIndices);
//
//BackingStore level throttles
//
let backingStores = OsBlobCacheConfigTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId and EntityType == 2 and EntityId in ((surfaces | distinct backingStoreId))
| distinct EntityId, EntityType, EntityConfig, UserData
| extend throttleIndices = parse_json(EntityConfig).throttle_indices
| mv-expand throttleIndices
| distinct backingStoreId = EntityId, throttleIndices = tostring(throttleIndices);
//
//Combined attached throttles
//
let throttlesAttached = union surfacesThrottles, backingStores | distinct throttleIndices;
//
//VM Remote Throttles
//
let vmRemoteThrottles = OsBlobCacheConfigTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId and EntityType == 3 and UserData contains containerId
| distinct EntityId, EntityType, EntityConfig, UserData
| extend UserData = parse_json(UserData).user_data
| extend throttleType = tostring(split(UserData.Tag, containerId)[0])
| where throttleType in~ ("VmIoSettingsNetworkThrottle", "XioSettingsNetworkThrottle")
| distinct throttleId = EntityId, throttleType;
//
//HW Throttles
//
let hwThrottles = OsBlobCacheConfigTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId and EntityType == 7
| extend UserData = case(UserData contains "Hardware" and UserData !endswith "}}", strcat(UserData, "}"), UserData)
| distinct EntityId, EntityType, EntityConfig, UserData
| extend UserData = parse_json(UserData).user_data
| extend throttleType = tostring(split(UserData.Tag, containerId)[0])
| where throttleType in~ ("Hardwarenetwork", "Hardwaressd")
| distinct throttleId = EntityId, throttleType;
//
//VM Remote and HW throttles to be shown always irrespective of disk type
//
let throttles2ShowAlways = union vmRemoteThrottles, hwThrottles | distinct throttleId;
//
//Summarized view of all throttles applicable to VM/disks
//
OsBlobCacheConfigTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId 
and ((EntityType == 3 and UserData contains containerId) or EntityType == 7)
| where EntityId in (throttles2ShowAlways) or EntityId in (throttlesAttached)
| summarize arg_max(PreciseTimeStamp, *) by EntityId, EntityConfig, UserData
| extend UserData = case(UserData contains "Hardware" and UserData !endswith "}}", strcat(UserData, "}"), UserData)
| extend EntityConfig = parse_json(EntityConfig), UserData = parse_json(UserData).user_data
| extend ThrottleIndex = tolong(EntityId), 
         ThrottleType = ThrottleType(UserData.Tag), //tostring(split(UserData.Tag, containerId)[0]), 
         ThrottleConfig = bag_pack("PreciseTimeStamp", PreciseTimeStamp, "EntityConfig", EntityConfig, "UserData", UserData),
         IOPS = tolong(EntityConfig.max_iops), 
         BPS = (tolong(EntityConfig.max_bps) * iff(isnotempty(EntityConfig.bps_multiplier), tolong(EntityConfig.bps_multiplier)/100.0, 1.0)), 
         QueueDepth = tolong(EntityConfig.queue_depth_limit), 
         QueueMBytes = tolong(EntityConfig.queue_mbytes_limit), 
         BurstType = case(EntityConfig.burst_type =~ "0", "NoBurst", EntityConfig.burst_type =~ "1", "MacroBurst", EntityConfig.burst_type =~ "2", "MicroBurst", EntityConfig.burst_type =~ "3", "InvalidBurst", ""), 
         BurstState = case(EntityConfig.burst_state =~ "0", "BurstStateOff", EntityConfig.burst_state =~ "1", "BurstStateOn", EntityConfig.burst_state =~ "2", "BurstStatePause", EntityConfig.burst_state =~ "3", "BurstStateInvalid", ""), 
         BurstIOPS = tolong(EntityConfig.burst_iops), 
         BurstBPS = tolong(EntityConfig.burst_bps), 
         BurstDuration = tolong(EntityConfig.burst_duration_seconds) 
| summarize take_any(ThrottleConfig) by ThrottleIndex, IOPS, BPS, ThrottleType, BurstType, BurstState, BurstIOPS, BurstBPS, BurstDuration, QueueDepth, QueueMBytes, userdata=tostring(UserData.Tag)
| sort by ThrottleType desc
| extend userdata = replace_strings(
        userdata,
        dynamic(['NetworkThrottle','dedicatedssdthrottle']), // Lookup strings
        dynamic(['','']) // Replacements
        )
| join kind=leftouter (OsXIOSurfaceCounterTable
| where NodeId == nodeId and SurfaceName contains containerId
| distinct SurfaceName, ArmId) on $left.userdata == $right.SurfaceName
| extend DDIopsMultiplier = todouble(parse_json(ThrottleConfig).UserData.IopsDirectDriveMultiplier)
| extend DDThroughputMultiplier = todouble(parse_json(ThrottleConfig).UserData.BpsDirectDriveMultiplier)
| extend DDIOPS = case(isnotempty(DDIopsMultiplier), IOPS * DDIopsMultiplier / 100.0, IOPS * 1.0)
| extend DDBPS = case(isnotempty(DDThroughputMultiplier), BPS * DDThroughputMultiplier / 100.0, BPS * 1.0)
| project-away userdata
```

**Params:** `{nodeId}`, `{containerId}`, `{startTime}`, `{endTime}`, `{vmId}`

---

## Disks Attached to the VM

### Azure Host VM Blobs

_Widget purpose:_ Disks Attached to the VM

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `VM Blobs > Disks Attached to the VM`

**Tables:** `MycroftContainerSnapshot`, `MycroftClusterSnapshot`, `OsXIOSurfaceCounterTable`, `OsUltraSSDCounterTable`, `OsConfigTable`, `VhdDiskEtwEventTable`
**Aggregations:** `summarize arg_max(PreciseTimeStamp, CachePolicy, BlobPath, ContainerId, StorageAccount, En by SurfaceName` · `summarize arg_max(PreciseTimeStamp, *) by ConfigName`
**Output columns:** `SurfaceName1`, `OvlVersion`, `IsVhd`, `CleanSurfaceName`, `DiskType1 // remove extra columns after join successfully done.`

```kusto
let VMCreationTime = todatetime(toscalar(cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
    | where PreciseTimeStamp between ((_startTime - 2h) .. (_endTime + 1h)) and ContainerId == _containerId
    | distinct CreationTime));
let ClusterInfo = cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftClusterSnapshot
    | where PreciseTimeStamp between ((_startTime - 2h) .. (_endTime + 1h)) //and Tenant == cluster
    | distinct Tenant = ClusterName, AvailabilityZone;
let VmDisksView= view()
    {
        cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
        | where PreciseTimeStamp between (_startTime .. _endTime) and NodeId == _nodeId and Cluster == _cluster
        | extend ContainerId = tostring(split(split(SurfaceName, "_")[0], "~")[0])
        | where ContainerId == _containerId or SurfaceName contains _vmId
        | union (cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsUltraSSDCounterTable | where PreciseTimeStamp between (_startTime .. _endTime) and NodeId == _nodeId and Cluster == _cluster and ContainerId contains _containerId)
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
            | where PreciseTimeStamp between ((_startTime - 6h)  .. (_endTime + 6h))
                    and NodeId == _nodeId and Component == "blobprop" and Cluster == _cluster
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
            | where PreciseTimeStamp between (_startTime .. _endTime) and NodeId == _nodeId
            | where EventId == 31
            | parse EventMessage with * "NewDiskName: /" BlobPath "." * "x-ms-access-tier: " DiskAccessTier "\r" *  "x-ms-enhancedconnectionversion: " EnhancedConnectionVersion "\r" *
            | summarize arg_max(PreciseTimeStamp, *) by BlobPath
            | project BlobPath, DiskAccessTier, EnhancedConnectionVersion
        ) on BlobPath
        | join kind=leftouter(
            cluster('storageclient.eastus.kusto.windows.net').database('Fa').XdiskSvcEvent
            | where PreciseTimeStamp between (_startTime .. _endTime) and eventType == 411 and NodeId == _nodeId
            | extend ArmId = tostring(parse_json(message)["x-ms-disk-resource-uri"]), DiskAccessTier = tostring(parse_json(message)["x-ms-access-tier"]), 
                    EnhancedConnectionVersion = tostring(parse_json(message)["x-ms-enhancedconnectionversion"])
            | summarize arg_max(PreciseTimeStamp, *) by ArmId
        ) on ArmId
        | extend DiskAccessTier = case(isnotempty(DiskAccessTier2), DiskAccessTier2, isnotempty(DiskAccessTier1), DiskAccessTier1, DiskAccessTier),
                EnhancedConnectionVersion = case(isnotempty(EnhancedConnectionVersion2), EnhancedConnectionVersion2, isnotempty(EnhancedConnectionVersion1), EnhancedConnectionVersion1, EnhancedConnectionVersion)
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
        | join kind = leftouter (
            cluster('storageclient.eastus.kusto.windows.net').database('Fa').StorageTracingEventTable
            | where PreciseTimeStamp between ((VMCreationTime - 1h) .. (VMCreationTime + 1h)) and NodeId == _nodeId
            | where Message contains "LeaseOwner is set as Node for blob"
            | extend message = parse_json(Message)
            | extend lonmsg = message.message
            | project lonmsg
            | parse lonmsg with "LeaseOwner is set as Node for blob XDISK:0.0.0.0:8080/" BlobpathWithoutQueryParam "?sr=" restBlobpath
            | project BlobpathWithoutQueryParam
        ) on $left.BlobPath == $right.BlobpathWithoutQueryParam
        | extend LeaseManagedBy = case(isnotempty(BlobpathWithoutQueryParam), "Node(DAL)", CachePolicy == "LocalDisk", "NoLease", "CRP" )
        | project-away BlobpathWithoutQueryParam
        //
        //
        // ADD CLEAN SURFACE NAME JOIN KEY BASED ON SURFACE NAME
        | extend IsVhd = SurfaceName endswith ".vhd"
        | extend CleanSurfaceName = trim_end(".vhd", SurfaceName)
    };
//
// Translate exisiting Rakki VM DISK QUERY into a view so we can append ASAP logical portions. If someone decides they don't want ASAP mapping, easier to comment out
//
// Fetch the Overlake version on the input node and cluster.
//
let OverlakeVersion = toscalar(cluster('storageclient.eastus.kusto.windows.net').database('Fa').GetAllAsapClustersExtendedOverlakeDCM()
                 | where Cluster == _cluster //cluster is available in ASI as param
                 | project Overlake
                 );
//
//
//print OverlakeVersion; // DEBUG OUTPUT
//
//
// CALL RESPECTIVE ASAP FUNCTIONS 
//
//
let AsapMapVmToDiskOutput = 
    union
    (
         cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL1(_nodeId,  _containerId, _startTime, _endTime) // Function available once we post this 
        //
        // PROJECT ONLY RELEVANT COLUMNS FOR OUR ASI QUERY
        //
        | project VfId, NsId, NsIndex, DiskType, SurfaceName, OvlVersion
    ),
    (
        cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(_nodeId,  _containerId, _startTime, _endTime) // Function available once we post this 
        //
        // PROJECT ONLY RELEVANT COLUMNS FOR OUR ASI QUERY
        //
        | project VfId, NsId, NsIndex, DiskType, SurfaceName, OvlVersion
        //
        // NOTE FOR LOGIC: if both functions return data by chance, meaning given Node has Union Data from both : ETW & Tracelog, we must find wha OvelrakeVersion Node belongs to and retain respectve function output
        //
        //| where OvlVersion == OverlakeVersion 
    )
    // END OF UNION: NEED EXTRA PROCESSING
    //
//     | extend NsNameJoinKey = iff (
//                                         DiskType != 'XIO', substring(NamespaceName, indexof(NamespaceName, "_") + 1) // If Disk type of data disk is DD, then we trim the containerID part from NS NAME TO MATCH WITH SURFACE NAME
//                                         ,NamespaceName // FOR XIO Data disks and OS disks (which is also xio) we retain same NS NAME as it already matches Surface name
//                                 )
    ;
//
VmDisksView
    | join kind= leftouter AsapMapVmToDiskOutput on $left.SurfaceName == $right.SurfaceName
    | project-away SurfaceName1, OvlVersion, IsVhd,  CleanSurfaceName, DiskType1 // remove extra columns after join successfully done.
    | as VmDisksWithAsapDiskVFMapping
;
```

**Params:** `{_containerId}`, `{_startTime}`, `{_endTime}`, `{_nodeId}`, `{_cluster}`, `{_vmId}`

**Signal filters seen in KQL:** `CachePolicy != "None"` · `Message contains "LeaseOwner is set as Node for blob"`

---
