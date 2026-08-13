# Managed Disk — Operation Id: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:27:08.042Z.
> Total: 4 unique KQL queries across 3 panels (4 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Operation Id" | ResourceGet | disks | Disks | local_operationId, globalFrom, globalTo |
| 2 | Target Disks from RequestEntity | Table | Disks | Disks | queryFrom, queryTo, queryOperationId |

### DiskManagerContextActivityEvent > DiskManagerContextActivityEvent 
Path: `DiskManagerContextActivityEvent > DiskManagerContextActivityEvent `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query DiskManagerContextActivityEvent | Table | Disks | Disks | queryStartTime, queryEndTime, queryOperationId |

### DiskRPResourceLifecycleEvent
Path: `DiskRPResourceLifecycleEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DiskRPResourceLifecycleEvent | Table | Disks | Disks | queryFrom, queryTo, operationId |
