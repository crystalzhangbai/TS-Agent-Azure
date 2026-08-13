# NRP — DELETE VMScaleSet operation drilldown: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:54.079Z.
> Total: 9 unique KQL queries across 9 panels (9 widget refs).

## Page inputs (URL params)


## Panels

### Region level > Latency
Path: `Region level > Latency`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Latency | TimeSeries | https://nrp | mdsnrp | queryFrom, queryTo, region |

### Region level > Sub lock duration
Path: `Region level > Sub lock duration`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DeleteVmssSubLockRegion | TimeSeries | https://nrp | mdsnrp | queryFrom, queryTo, region |

### Region level > Success rate
Path: `Region level > Success rate`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DeleteVmssSuccess | TimeSeries | https://nrp | mdsnrp | queryFrom, queryTo, region |

### Region level > Top Subscriptions
Path: `Region level > Top Subscriptions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DeleteVmssTopSubs | Table | https://nrp | mdsnrp | queryFrom, queryTo, region |

### Region level > Transaction stats (KB)
Path: `Region level > Transaction stats (KB)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DeleteVmssTransactionStatsRegion | TimeSeries | https://nrp | mdsnrp | queryFrom, queryTo, region |

### Sub level > Delete VMSS Ip configurations reads
Path: `Sub level > Delete VMSS Ip configurations reads`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DeleteVmssIpConfigReads | TimeSeries | https://nrp | mdsnrp | queryFrom, queryTo, region, subId |

### Sub level > Delete VMSS Subnet reads
Path: `Sub level > Delete VMSS Subnet reads`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DeleteVmssSubnetReadsSub | TimeSeries | https://nrp | mdsnrp | queryFrom, queryTo, region, subId |

### Sub level > Sub lock duration
Path: `Sub level > Sub lock duration`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DeleteVmssSubLockSub | TimeSeries | https://nrp | mdsnrp | queryFrom, queryTo, region, subId |

### Sub level > Transaction stats (KB)
Path: `Sub level > Transaction stats (KB)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DeleteVmssTransactionStatsSub | TimeSeries | https://nrp | mdsnrp | queryFrom, queryTo, region, subId |
