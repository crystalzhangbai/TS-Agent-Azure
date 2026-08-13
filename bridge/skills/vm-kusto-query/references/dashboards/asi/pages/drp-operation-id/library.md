# DRP — Operation Id: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:43:25.590Z.
> Total: 2 unique KQL queries across 2 panels (3 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Operation Id" | ResourceGet | disks | Disks | globalFrom, globalTo, local_operationId |

### DiskManagerContextActivityEvent 
Path: `DiskManagerContextActivityEvent `  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query DiskManagerContextActivityEvent | Table | Disks | Disks | queryStartTime, queryEndTime, queryOperationId |
| 2 | Retrieve Resource "Operation Id" | ResourceGet | disks | Disks | globalFrom, globalTo, local_operationId |
