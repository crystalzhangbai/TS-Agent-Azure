# (top-level)

> Source: **Managed Disk - Disks** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Disks"

Cluster: `disksbi` · Database: `disksbi` · Type: `ResourceGet` · Widget: `Container`

```kusto
Disk
| where PreciseTimeStamp between (globalFrom .. globalTo)
| where DisksId == local_DisksId
| where SubscriptionId =~ local_subscriptionId
| where ResourceGroup =~ local_resourceGroup
| where DisksName =~ local_diskName 
| summarize SnapshotTime = arg_max(PreciseTimeStamp, *)
| extend ownerVM = tolower(url_decode(substring(OwnerReferenceKey, 69)))
| extend owernVMSubId  =  tostring(split(ownerVM, "/")[2])
| extend owernVMResourceGroup  =  tostring(split(ownerVM, "/")[4])
| extend owernVMName  =  tostring(split(ownerVM, "/")[8])
| extend jarvisActionGetDisk = strcat('https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=',
 'Public', 
 '&managementOpen=false&selectedNodeType=3&extension=Compute%20Platform%20Disks&group=Disk%20Operations&operationId=GetDisk&operationName=Get%20Disk&inputMode=single&params='
 '{"wellknownsubscriptionid":"', local_subscriptionId,
 '","smeregionarmnameparameter":"', GeoLocation, 
 '","smeresourcegroupnameparameter":"', local_resourceGroup, 
 '","smedisknameparameter":"', local_diskName, 
 '","smeapiversionparameter":""}&actionEndpoint=Prod&genevatraceguid=ddf95797-99a9-4f9e-b0ab-4868cd877d8b")')
```

**Params:** `{local_diskName}`, `{local_DisksId}`, `{local_resourceGroup}`, `{local_subscriptionId}`, `{globalFrom}`, `{globalTo}`

---

### Query DiskEncryptionSet

_Widget purpose:_ Disk Encryption Set

Cluster: `disksbi` · Database: `DisksBi` · Type: `Single` · Widget: `Card`

```kusto
DiskEncryptionSet
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Key =~ queryDESKey
| top 1 by PreciseTimeStamp desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryDESKey}`

---

### Query Goal State of Managed Disk

_Widget purpose:_ Goal State - CRP BI

Cluster: `azcrpbifollower.kusto.windows.net` · Database: `bi_allprod` · Type: `Single` · Widget: `Card`

```kusto
let CrpDiskId = toscalar(cluster("DisksBi").database("DisksBi").Disk
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where DisksId == queryDiskId
| summarize arg_max(PreciseTimeStamp, CrpDiskId)
| project CrpDiskId);
VMManagedDisksAllocationInfo
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where DiskId == CrpDiskId
| summarize SnapshotTime = arg_max(PreciseTimeStamp, *) 
| extend CrpDiskId = DiskId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryDiskId}`

---
