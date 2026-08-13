# Managed Disk — Disks: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:27:08.072Z.
> Total: 6 unique KQL queries across 3 panels (6 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Disks" | ResourceGet | disksbi | disksbi | local_diskName, local_DisksId, local_resourceGroup, local_subscriptionId, globalFrom, globalTo |
| 2 | Query DiskEncryptionSet | Single | disksbi | DisksBi | queryFrom, queryTo, queryDESKey |
| 3 | Query Goal State of Managed Disk | Single | azcrpbifollower | bi_allprod | queryFrom, queryTo, queryDiskId |

### DiskManagerApiQoSEvent
Path: `DiskManagerApiQoSEvent`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query DiskManagerApiQoSEvent | Table | Disks | Disks | queryFrom, queryTo, querySubId, queryResourceGroupName, queryDiskName, queryOpsFilter |
| 2 | FilterOperations | Filter | Azcrp | crp_allprod | queryFrom, queryTo |

### DiskRPResourceLifecycleEvent
Path: `DiskRPResourceLifecycleEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query DiskRPResourceLifecycleEvent | Table | Disks | Disks | queryFrom, queryTo, querySubId, queryResourceGroup, queryDiskName |
