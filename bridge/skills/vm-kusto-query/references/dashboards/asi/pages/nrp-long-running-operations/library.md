# NRP — LongRunningOperations: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:54.161Z.
> Total: 4 unique KQL queries across 4 panels (4 widget refs).

## Page inputs (URL params)


## Panels

### GridViewByOperationName
Path: `GridViewByOperationName`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | operationDurationGrid | Table | nrp | mdsnrp | operationName_query_, region_query_, duration_threshold, lookback_days, apply_knownOperations |

### LongRunningOperations
Path: `LongRunningOperations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LongRunningOperations | Table | https://nrp | mdsnrp | queryFrom, queryTo, operationName_query_, region_query_, min_OpertionDurationTHreshold_hr, apply_knownOperations |

### LongRunningOperations > OperationId_Timings
Path: `LongRunningOperations > OperationId_Timings`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | opidTimings | Table | nrp | mdsnrp | queryFrom, queryTo, correlationRequestId |

### LongRunningOperations > OperationNames
Path: `LongRunningOperations > OperationNames`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | expand | Table | https://nrp | mdsnrp | queryFrom, queryTo, op_dict |
