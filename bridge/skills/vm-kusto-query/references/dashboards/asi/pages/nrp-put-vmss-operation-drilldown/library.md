# NRP — PUT VMScaleSet Operation drill down: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:54.073Z.
> Total: 30 unique KQL queries across 29 panels (30 widget refs).

## Page inputs (URL params)


## Panels

### Action categories during Put Vmss for existing resource
Path: `Action categories during Put Vmss for existing resource`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssActionsPerResource | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, location, subId, resourceGroup, resourceName |

### Action categories during PutVmss operation for existing resources
Path: `Action categories during PutVmss operation for existing resources`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssActionsPerSub | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, sub |

### Batch manager resource lock acquisition failures
Path: `Batch manager resource lock acquisition failures`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | BatchManagerResourceLockingTransactionAquisitionFailurePerSub | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### BatchManager transaction job dequeue times (ms)
Path: `BatchManager transaction job dequeue times (ms)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | BatchManagerDequeueJobTimesPerSub | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### Put Vmss Compute only updates
Path: `Put Vmss Compute only updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CoUPerSubscription | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### PUT Vmss Compute-only updates per region
Path: `PUT Vmss Compute-only updates per region`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ComputeOnlyUpdatesPerRegion | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region |

### Put Vmss latency (ms)
Path: `Put Vmss latency (ms)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssLatencyPerSub | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### Put Vmss Latency (P90 ms) by region 
Path: `Put Vmss Latency (P90 ms) by region `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssP90Latency | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region |

### Put Vmss operation failures
Path: `Put Vmss operation failures`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssFailuresPerSub | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### Put Vmss resource type read stats
Path: `Put Vmss resource type read stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssResourceTypeReadStats | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### Put Vmss sub lock duration ms (COU vs non-COU) per 5 mins
Path: `Put Vmss sub lock duration ms (COU vs non-COU) per 5 mins`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssLockDurationCouVsNonCOU | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |
| 2 | PutVmssSubLockCouVsNonCouPerRes | MultiRow | nrp | mdsnrp | queryFrom, queryTo, region, subId, resourceGroup, resourceName |

### Put Vmss sub lock for Peregrine scale down
Path: `Put Vmss sub lock for Peregrine scale down`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssSubLockPeregrineScaleDownPerSub | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### Put Vmss subscription lock duration (ms) per 5 mins
Path: `Put Vmss subscription lock duration (ms) per 5 mins`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssSubLockPerSub | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### Put Vmss top 5 errors 
Path: `Put Vmss top 5 errors `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssFailurePerRegion | Table | nrp | mdsnrp | queryFrom, queryTo, region |

### Put Vmss transaction stats (KB) per 5 mins
Path: `Put Vmss transaction stats (KB) per 5 mins`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssTransactionStatsPerSub | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### PutVMScaleSet operation failures
Path: `PutVMScaleSet operation failures`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssFailuresPerRegion | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region |

### PutVmss errors
Path: `PutVmss errors`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssFailuresPerVmss | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, subId, region, resourceGroup, resourceName |

### PutVmss Ipconfigurations reads
Path: `PutVmss Ipconfigurations reads`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssIpConfigsPerSubRead | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### PutVmss P50 latency (ms) by region
Path: `PutVmss P50 latency (ms) by region`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssLatencyPerRegion | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region |

### PutVmss sub lock COU vs Non-COU ms (per 5min)
Path: `PutVmss sub lock COU vs Non-COU ms (per 5min)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssSubLockCouVsNonCouPerRes | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId, resourceGroup, resourceName |

### PutVmss sub lock duration (ms) by region
Path: `PutVmss sub lock duration (ms) by region`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssSubLockPerRegion | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region |

### PutVmss sub lock duration for Peregrine vmss downscale
Path: `PutVmss sub lock duration for Peregrine vmss downscale`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssSubLockPeregrineVmssScaleDown | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region |

### PutVmss Subnet read stats
Path: `PutVmss Subnet read stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssSubnetReadStats | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### PutVmss subscription lock ms (per 5min)
Path: `PutVmss subscription lock ms (per 5min)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssSubLockPerResource | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region, subId, resourceGroup, resourceName |

### PutVmss transaction stats (KB) by region
Path: `PutVmss transaction stats (KB) by region`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssTransactionStatsPerRegion | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, region |

### Top 10 impacted subscriptions with error codes
Path: `Top 10 impacted subscriptions with error codes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssFailuresTopSubs | Table | nrp | mdsnrp | queryFrom, queryTo, region |

### Top 15 VMSS resources undergoing updates
Path: `Top 15 VMSS resources undergoing updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TopVmssResourcesPerSub | Table | nrp | mdsnrp | queryFrom, queryTo, region, subId |

### Top 20 Put Vmss Compute-only updates per region
Path: `Top 20 Put Vmss Compute-only updates per region`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TopPutVmssCouPerRegion | Table | nrp | mdsnrp | queryFrom, queryTo, region |

### Top 5 error stacks
Path: `Top 5 error stacks`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PutVmssFailureErrorCodes | Table | nrp | mdsnrp | queryFrom, queryTo, region, subId |
