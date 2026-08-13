# VM Properties & Disk Surface Queries — EEE-Style VM Diagnostics

These queries replicate the **EEE (RDOS HostNode) diagnostic portal** VM overview panels.
Use them when the user asks for VM information, VM properties, VM metadata, disk details,
or anything matching the EEE "VM Properties" / "VM Disks" views.

**When to use:**
- User asks: "what VM size / memory / disk controller / guest OS / region / cluster?"
- User asks: "show me the VM info / VM properties / VM metadata"
- User asks: "what disks are attached to the VM?"
- User asks: "show me disk details / disk surfaces / cache policy / storage tenant"
- User shares screenshots showing VM Properties or VM Disk tables from the EEE portal

---

## Prerequisites

Both queries require the following VM identifiers (obtain from `LogContainerSnapshot` first):

| Variable | Source | Description |
|----------|--------|-------------|
| `_containerId` | LogContainerSnapshot → `containerId` | Container GUID |
| `_nodeId` | LogContainerSnapshot → `nodeId` | Host node GUID |
| `_cluster` | LogContainerSnapshot → `Tenant` | Compute cluster name (e.g., `PHX71PrdApp12`) |
| `_vmId` | LogContainerSnapshot → `virtualMachineUniqueId` | VM unique ID |
| `_startTime` | Issue time - 1h | Query window start |
| `_endTime` | Issue time + 1h | Query window end |

If you only have the **Resource ID**, first run the `LogContainerSnapshot` query from
`azurecm-queries.md` to get containerId, nodeId, and cluster.

---

## Query 1: VM Metadata / Properties

**Cluster:** `azurecm.kusto.windows.net`
**Database:** `AzureCM`

**Tables used (cross-cluster):**
- `AzureCM.LogContainerSnapshot` — VM name, container ID, node ID, VM unique ID, tenant name, creation time
- `storageclient.eastus.kusto.windows.net / AzureCP.MycroftContainerSnapshot` — VM size, memory
- `AzureCM.LogContainerPolicySnapshot` — Disk controller type, colocation type, Gen2 flag
- `AzureCM.LogClusterSnapshot` — Region, shoebox
- `AzureCM.GuestOSDetail` — Guest OS, OS kernel version

**Output fields:**
| Field | Description |
|-------|-------------|
| VM Name | `roleInstanceName` from LogContainerSnapshot |
| VM Unique ID | `virtualMachineUniqueId` |
| Container ID | `containerId` |
| Node ID | `nodeId` |
| VM Size | `RoleSize` from Mycroft (e.g., Standard_D8s_v5) |
| Memory | `MemoryInMB` from Mycroft |
| Cluster | `Tenant` from LogContainerSnapshot |
| Region | From LogClusterSnapshot |
| Shoebox | From LogClusterSnapshot |
| Creation Time | `creationTime` from LogContainerSnapshot |
| Disk Controller | `DiskControllerType` from LogContainerPolicySnapshot (SCSI/NVMe) |
| Colocation Type | From LogContainerPolicySnapshot (e.g., XIO) |
| Is Gen2 VM | From LogContainerPolicySnapshot |
| Guest OS | `osDescription` from GuestOSDetail |
| OS Kernel Version | `kernelVersion` from GuestOSDetail |
| VM Type | `containerType` from LogContainerSnapshot (e.g., IaaSDurable) |

```kusto
let _subscriptionId = "{SubscriptionId}";
let _vmName = "{VMName}";
let _startTime = datetime("{StartTime}");
let _endTime = datetime("{EndTime}");
//
// Step 1: Container placement from LogContainerSnapshot
//
let ContainerSnap = 
    cluster('azurecm.kusto.windows.net').database('AzureCM').LogContainerSnapshot
    | where PreciseTimeStamp between ((_startTime - 2h) .. (_endTime + 1h))
    | where subscriptionId == _subscriptionId and roleInstanceName has _vmName
    | summarize arg_max(PreciseTimeStamp, *) by containerId
    | project ContainerId=containerId, NodeId=nodeId, VMName=roleInstanceName,
        VirtualMachineUniqueId=virtualMachineUniqueId, Cluster=Tenant,
        TenantName=tenantName, CreationTime=todatetime(creationTime),
        ContainerType=containerType, SubscriptionId=subscriptionId;
//
// Step 2: VM size & memory from Mycroft
//
let MycroftInfo = 
    cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
    | where PreciseTimeStamp between ((_startTime - 2h) .. (_endTime + 1h))
    | where ContainerId in ((ContainerSnap | project ContainerId))
    | summarize arg_max(PreciseTimeStamp, *) by ContainerId
    | project ContainerId, VMSize=RoleSize, MemoryMB=MemoryInMB;
//
// Step 3: Disk controller, colocation, Gen2 from policy snapshot
//
let PolicyInfo = 
    cluster('azurecm.kusto.windows.net').database('AzureCM').LogContainerPolicySnapshot
    | where PreciseTimeStamp between ((_startTime - 2h) .. (_endTime + 1h))
    | where containerId in ((ContainerSnap | project ContainerId))
    | summarize arg_max(PreciseTimeStamp, *) by containerId
    | project ContainerId=containerId, DiskControllerType, CollocationType=collocationType, IsGen2VM;
//
// Step 4: Cluster region & shoebox from LogClusterSnapshot
//
let ClusterInfo = 
    cluster('azurecm.kusto.windows.net').database('AzureCM').LogClusterSnapshot
    | where PreciseTimeStamp between ((_startTime - 2h) .. (_endTime + 1h))
    | where Tenant in ((ContainerSnap | project Cluster))
    | summarize arg_max(PreciseTimeStamp, *) by Tenant
    | project Cluster=Tenant, Region, Shoebox=shoeBox;
//
// Step 5: Guest OS details
//
let GuestOS = 
    cluster('azurecm.kusto.windows.net').database('AzureCM').GuestOSDetail
    | where PreciseTimeStamp between ((_startTime - 2h) .. (_endTime + 1h))
    | where containerId in ((ContainerSnap | project ContainerId))
    | summarize arg_max(PreciseTimeStamp, *) by containerId
    | project ContainerId=containerId, GuestOS=osDescription, OSKernelVersion=kernelVersion;
//
// Join all together
//
ContainerSnap
| join kind=leftouter MycroftInfo on ContainerId
| join kind=leftouter PolicyInfo on ContainerId
| join kind=leftouter (ClusterInfo) on $left.Cluster == $right.Cluster
| join kind=leftouter GuestOS on ContainerId
| project VMName, VirtualMachineUniqueId, ContainerId, NodeId, VMSize, MemoryMB,
    Cluster, Region, Shoebox, CreationTime, DiskControllerType, CollocationType,
    IsGen2VM, GuestOS, OSKernelVersion, ContainerType, TenantName
```

> **Note:** Column names (e.g., `collocationType`, `IsGen2VM`, `shoeBox`) reflect the observed
> EEE schema. If a column doesn't resolve, check the exact column names by running:
> `LogContainerPolicySnapshot | getschema` or `LogClusterSnapshot | getschema`

---

## Query 2: VM Disk Surface Details

**Cluster:** `azurecm.kusto.windows.net`
**Database:** `AzureCM`

**Tables used (cross-cluster to `storageclient.eastus.kusto.windows.net`):**
- `storageclient / AzureCP.MycroftContainerSnapshot` — VM creation time
- `storageclient / AzureCP.MycroftClusterSnapshot` — Cluster availability zone info
- `storageclient / Fa.OsXIOSurfaceCounterTable` — XIO disk surfaces (Premium SSD)
- `storageclient / Fa.OsUltraSSDCounterTable` — Ultra SSD disk surfaces
- `storageclient / Fa.OsConfigTable` — Blob properties (access tier, enhanced connection)
- `storageclient / Fa.VhdDiskEtwEventTable` — VHD disk events (fallback for blob properties)
- `storageclient / Fa.XdiskSvcEvent` — Xdisk service events (access tier, enhanced connection)
- `storageclient / Fa.StorageTracingEventTable` — Lease ownership (DAL vs CRP)
- `storageclient / Fa.GetAllAsapClustersExtendedOverlakeDCM()` — Overlake version
- `storageclient / Fa.AsapMapVmToDiskOVL1/OVL2()` — ASAP disk-to-VF mapping

**Output fields:**
| Field | Description |
|-------|-------------|
| CachePolicy | None, ReadOnly, ReadWrite, LocalDisk |
| DiskType | OS Disk, Data Disk, Temp Disk, Ephemeral OS Disk Base |
| DiskSkuType | Premium SSD, Standard SSD, Standard HDD, UltraSSD, Premium SSD V2 |
| DiskName | ARM disk resource name |
| SurfaceName | Internal surface identifier |
| BlobPath | Storage blob path |
| StorageTenant | Storage cluster hosting the disk |
| DiskAccessTier | Performance tier (P6, P50, etc.) |
| FastPathEnabled | Whether enhanced connection (FastPath) is active |
| LUN | Logical Unit Number (NA for OS/Temp) |
| BSId / WSId | Block store / Write store IDs |
| StorageAccount | Managed disk storage account |
| AZColocation | Whether compute & storage are in same AZ |
| ArmId | Full ARM resource ID of the disk |
| LeaseManagedBy | Node(DAL) or CRP — who manages the blob lease |
| VfId / NsId | ASAP virtual function & namespace mapping |

**Input variables required:** `_containerId`, `_startTime`, `_endTime`, `_nodeId`, `_cluster`, `_vmId`

```kusto
let _containerId = "{ContainerId}";
let _startTime = datetime("{StartTime}");
let _endTime = datetime("{EndTime}");
let _nodeId = "{NodeId}";
let _cluster = "{Cluster}";
let _vmId = "{VMId}";

let VMCreationTime = todatetime(toscalar(cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
    | where PreciseTimeStamp between ((_startTime - 2h) .. (_endTime + 1h)) and ContainerId == _containerId
    | distinct CreationTime));
let ClusterInfo = cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftClusterSnapshot
    | where PreciseTimeStamp between ((_startTime - 2h) .. (_endTime + 1h))
    | distinct Tenant = ClusterName, AvailabilityZone;
let VmDisksView= view()
    {
        cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
        | where PreciseTimeStamp between (_startTime .. _endTime) and NodeId == _nodeId and Cluster == _cluster
        | extend ContainerId = tostring(split(split(SurfaceName, "_")[0], "~")[0])
        | where ContainerId == _containerId or SurfaceName contains _vmId
        | union (cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsUltraSSDCounterTable | where PreciseTimeStamp between (_startTime .. _endTime) and NodeId == _nodeId and Cluster == _cluster and ContainerId contains _containerId)
        | parse ArmId with * "/disks/" DiskName
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
        | extend DiskType = case(DiskType == 1, "OS Disk", DiskType == 2, "Temp Disk", DiskType == 3 or BlobPath contains "md-dd", "Data Disk", SurfaceName startswith "BASE_", "Ephemeral OS Disk Base", "")
        | extend DiskType = case(Type == 4, strcat(DiskType, " (WriteAccelerator)"), DiskType)
        | extend AZColocation = case(CachePolicy == 5, "", AvailabilityZone  == StorageClusterAvailabilityZone, "Yes", isnotempty(AvailabilityZone) or isnotempty(StorageClusterAvailabilityZone), "No", "Unknown")
        | extend LUN = case(DiskType == "OS Disk" or DiskType == "Temp Disk", "NA", tostring(SlotId))
        | project CachePolicy, EncryptionFlags, DiskType, DiskSkuType, DiskName, SurfaceName, BlobPath, StorageTenant, DiskAccessTier, FastPathEnabled = case(DiskType == "Temp Disk", "", EnhancedConnectionVersion == "Unknown", "Unknown", tostring(isnotempty(EnhancedConnectionVersion))), LUN, BSId, WSId, ThrottleIndices, BlobProperties, StorageAccount, AZColocation, ArmId, NodeId
        | extend CachePolicy = case(CachePolicy == 0, "None", CachePolicy == 1, "ReadOnly", CachePolicy == 2, "ReadWrite", CachePolicy == 5, "LocalDisk", BlobPath contains "md-dd", "None", tostring(CachePolicy))
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
        | extend IsVhd = SurfaceName endswith ".vhd"
        | extend CleanSurfaceName = trim_end(".vhd", SurfaceName)
    };
let OverlakeVersion = toscalar(cluster('storageclient.eastus.kusto.windows.net').database('Fa').GetAllAsapClustersExtendedOverlakeDCM()
                 | where Cluster == _cluster
                 | project Overlake
                 );
let AsapMapVmToDiskOutput =
    union
    (
         cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL1(_nodeId,  _containerId, _startTime, _endTime)
        | project VfId, NsId, NsIndex, DiskType, SurfaceName, OvlVersion
    ),
    (
        cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(_nodeId,  _containerId, _startTime, _endTime)
        | project VfId, NsId, NsIndex, DiskType, SurfaceName, OvlVersion
    )
    ;
VmDisksView
    | join kind= leftouter AsapMapVmToDiskOutput on $left.SurfaceName == $right.SurfaceName
    | project-away SurfaceName1, OvlVersion, IsVhd,  CleanSurfaceName, DiskType1
    | as VmDisksWithAsapDiskVFMapping
;
```

### How to run

Both queries run against `azurecm.kusto.windows.net` / `AzureCM` (the cross-cluster references resolve automatically):

```bash
# Query 1 — VM Properties
python .github/skills/VM_Kusto_Query/scripts/kusto_runner.py \
    --cluster "azurecm.kusto.windows.net" --database "AzureCM" \
    --query "<query_with_substituted_variables>" --format kv

# Query 2 — Disk Surfaces (save to file first due to query size)
# 1. Save query to a .kql file with variables substituted
# 2. Run:
python .github/skills/VM_Kusto_Query/scripts/kusto_runner.py \
    --cluster "azurecm.kusto.windows.net" --database "AzureCM" \
    --query-file "path/to/disk_query.kql" --format kv
```

### Workflow: from Resource ID to full VM diagnostics

1. Parse Resource ID → extract subscription ID and VM name
2. Run `LogContainerSnapshot` query (from `azurecm-queries.md`) → get `containerId`, `nodeId`, `cluster`, `vmId`
3. Run **Query 1** (VM Properties) → get VM size, memory, region, disk controller, guest OS, etc.
4. Run **Query 2** (Disk Surfaces) → get attached disks, cache policy, storage tenant, AZ colocation, etc.

---

## Query 3: StorageTenant Lookup for E17 Impacted Blobs (Batch)

When investigating E17 (IaaSxStoreOutage) events across multiple VMs, use this query to find the **XStore storage stamp (StorageTenant)** for all impacted blobs in batch.

**Cluster:** `storageclient.eastus.kusto.windows.net`
**Database:** `Fa`

**Table:** `OsXIOSurfaceCounterTable`

> **Key insight:** `OsXIOSurfaceCounterTable` records **all** disk types (Premium SSD, Standard SSD, Standard HDD), not just XIO/Premium disks — the table name is misleading. The `StorageTenant` column gives the XStore storage stamp name directly.

> **Important:** This table does NOT have a `ContainerId` column. The ContainerId is embedded in `SurfaceName` and must be parsed out:
> ```kql
> extend ContainerId = tostring(split(split(SurfaceName, "_")[0], "~")[0])
> ```

### Single VM — Get StorageTenant for all disks

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId == "{NodeId}"
| where Cluster == "{Cluster}"
| extend ContainerId = tostring(split(split(SurfaceName, "_")[0], "~")[0])
| where ContainerId == "{ContainerId}" or SurfaceName contains "{VmId}"
| summarize arg_max(PreciseTimeStamp, *) by SurfaceName
| project SurfaceName, BlobPath, StorageTenant, DiskType, CachePolicy, IsXIOdisk
```

**Input:** `NodeId`, `Cluster`, `ContainerId`, `VmId` (from `LogContainerSnapshot`), time window around the E17 event.

**Output fields:**
| Field | Description |
|-------|-------------|
| StorageTenant | XStore storage stamp name (e.g., `db5prdstr10a`) |
| BlobPath | Full blob path including SAS token |
| DiskType | 1 = OS Disk, 2 = Temp Disk, 3 = Data Disk |
| CachePolicy | 0 = None, 1 = ReadOnly, 2 = ReadWrite, 5 = LocalDisk |
| IsXIOdisk | 1 = Premium SSD (XIO), 0 = Standard HDD/SSD |

### Batch — StorageTenant for E17 blobs across multiple VMs

When you have the E17 impacted storage account names (from `LogContainerHealthSnapshot` faultInfo) and the NodeIds of all affected VMs:

```kusto
let e17StorageAccounts = dynamic(['{StorageAccount1}', '{StorageAccount2}', ...]);
let nodeIds = dynamic(['{NodeId1}', '{NodeId2}', ...]);
cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId in (nodeIds)
| where BlobPath has_any (e17StorageAccounts)
| extend StorageAccount = tostring(split(split(BlobPath, "/")[1], "/")[0])
| summarize arg_max(PreciseTimeStamp, StorageTenant, BlobPath, Cluster, SurfaceName) by StorageAccount
| project StorageAccount, StorageTenant, Cluster
```

**Use case:** Given a batch of VMs with E17 events (e.g., from `LogContainerHealthSnapshot` faultInfo containing `IaaSxStoreOutage` + `E17Detail`), determine if all impacted blobs land on the **same storage stamp** — which would indicate a storage-side root cause rather than compute-side.

### How to get E17 blob details from faultInfo

E17 impacted blob paths come from `LogContainerHealthSnapshot.faultInfo` (JSON):

```kusto
cluster('Azcsupfollower').database('AzureCM').LogContainerHealthSnapshot
| where PreciseTimeStamp >= ago(3d)
| where containerId in (containerIds)
| where faultInfo has "E17Detail"
| extend faultJson = parse_json(faultInfo)
| extend E17Time = tostring(faultJson.Time)
| extend detailsStr = tostring(faultJson.Details)
| extend detailsJson = parse_json(detailsStr)
| extend BlobPath = tostring(detailsJson.E17Detail.BlobPath)
| extend StorageErrorCode = tostring(detailsJson.E17Detail.StorageErrorCode)
| summarize E17Count = count(), FirstE17 = min(todatetime(E17Time)), LastE17 = max(todatetime(E17Time)),
            BlobPaths = make_set(BlobPath)
  by roleInstanceName, containerId, nodeId, Tenant, tenantName
```

The `BlobPath` format is `XDISK:0.0.0.0:8080/{StorageAccount}/{ContainerBlob}/abcd`. Extract the storage account name with:
```kql
extend StorageAccount = tostring(split(BlobPath, "/")[1])
```

### Workflow: E17 batch investigation

1. Get VM identities from `LogContainerSnapshot` (containerId, nodeId, cluster)
2. Get E17 faultInfo from `LogContainerHealthSnapshot` → extract impacted blob paths & storage account names
3. **Run this batch query** on `OsXIOSurfaceCounterTable` with all nodeIds + storage account names → get `StorageTenant`
4. If all blobs map to the **same StorageTenant** → storage stamp-side issue (escalate to XStore)
5. If blobs spread across **multiple StorageTenants** → likely compute-side or cross-stamp issue
