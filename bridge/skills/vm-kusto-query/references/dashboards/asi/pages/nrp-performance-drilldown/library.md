# NRP — Nrp Performance Drilldown: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:54.061Z.
> Total: 19 unique KQL queries across 19 panels (19 widget refs).

## Page inputs (URL params)


## Panels

### Batch Manager Summary > Batch Job Durations
Path: `Batch Manager Summary > Batch Job Durations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Batch Job Durations | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |

### Batch Manager Summary > Batch Queue Processing Percentiles
Path: `Batch Manager Summary > Batch Queue Processing Percentiles`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Batch Manager Queue Processing Percentiles | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |

### Batch Manager Summary > Batch Sizes
Path: `Batch Manager Summary > Batch Sizes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Batch Sizes | CategoryChart | https://nrp | mdsnrp | queryFrom, queryTo, region, subscriptionId |

### Batch Manager Summary > Commit Duration
Path: `Batch Manager Summary > Commit Duration`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Commit Duration | Table | https://nrp | mdsnrp | queryFrom, queryTo, region, subscriptionId |

### Batch Manager Summary > Long Running Jobs
Path: `Batch Manager Summary > Long Running Jobs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Long Running Jobs | TimeSeries | https://nrp | mdsnrp | queryFrom, queryTo, subscription, region |

### Batch Manager Summary > Worst-Performing Non-Tenant Operations
Path: `Batch Manager Summary > Worst-Performing Non-Tenant Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Worst Performing Non-Tenant Operations | CategoryChart | https://nrp | mdsnrp | queryFrom, queryTo, subscriptionId, region |

### Batch Manager Summary > Worst-Performing Tenant Operations
Path: `Batch Manager Summary > Worst-Performing Tenant Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Worst Performing Tenant Operations | CategoryChart | https://nrp | mdsnrp | queryFrom, queryTo, region, subscriptionId |

### EG Breakdown > NRP EG Exclusive Times
Path: `EG Breakdown > NRP EG Exclusive Times`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NRP EG Percentile Times | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |

### Exclusive Write Attribution > Exclusive Write Time Distribution
Path: `Exclusive Write Attribution > Exclusive Write Time Distribution`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ExclusiveWriteTimes | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |

### QOS Overview > QOS Overview
Path: `QOS Overview > QOS Overview`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | QOS Overview | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |

### Resource Locking Summary > Resource Locks Acquired
Path: `Resource Locking Summary > Resource Locks Acquired`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Resource Locks Acquired | Table | nrp | mdsnrp | subscriptionId, region, operationId, correlationId, startTime, endTime |

### Resource Locking Summary > Resource Locks Acquisition Failures
Path: `Resource Locking Summary > Resource Locks Acquisition Failures`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Resource Lock Acquisition Failures | Table | nrp | mdsnrp | subscriptionId, region, operationId, correlationId, startTime, endTime |

### Subscription Lock Summary > Subscription Lock Durations
Path: `Subscription Lock Summary > Subscription Lock Durations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription Lock Durations | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |

### Top Possible Perf Issues > Highest Reading Operations
Path: `Top Possible Perf Issues > Highest Reading Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Highest Read Size Operations | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |

### Top Possible Perf Issues > Longest EG Frames
Path: `Top Possible Perf Issues > Longest EG Frames`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Longest EG Frames | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |

### Top Possible Perf Issues > Longest Subscription Locks
Path: `Top Possible Perf Issues > Longest Subscription Locks`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Longest Sub Locks | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |

### Top Possible Perf Issues > Slowest Batch Jobs
Path: `Top Possible Perf Issues > Slowest Batch Jobs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Slowest Batch Jobs | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |

### Transaction Stats > Resource Type Read Count
Path: `Transaction Stats > Resource Type Read Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Resource Type Read Count | Table | nrp | mdsnrp | subscriptionId, region, operationId, correlationId, startTime, endTime |

### Transaction Stats > Transaction Stats
Path: `Transaction Stats > Transaction Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Transaction Stats | Table | nrp | mdsnrp | correlationId, operationId, region, subscriptionId, startTime, endTime |
