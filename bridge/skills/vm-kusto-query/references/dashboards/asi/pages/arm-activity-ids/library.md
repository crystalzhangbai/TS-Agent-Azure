# ARM — Activity Ids: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:23:49.166Z.
> Total: 6 unique KQL queries across 5 panels (6 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Activity Ids" | ResourceGet | armprodgbl.eastus | ARMProd | local_timestamp, local_ActivityId, globalFrom, globalTo |
| 2 | Deployments for Activity Id | Table | armprodgbl.eastus | ARMProd | queryFrom, queryTo, queryActivityId |

### CoBe Timeline
Path: `CoBe Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARMActivityId | CoBeTimeline | armprodgbl.eastus | ARMProd | timeStamp, activityId |

### Errors
Path: `Errors`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Activity Id Errors | Table | armprodgbl.eastus | ARMProd | queryFrom, queryTo, queryActivityId |

### Storage Requests
Path: `Storage Requests`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Storage Requests for Activity Id | Table | armprodgbl.eastus | ARMProd | queryFrom, queryTo, queryActivityId |

### Traces
Path: `Traces`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Activity Id Traces | Table | armprodgbl.eastus | ARMProd | queryFrom, queryTo, queryActivityId |
