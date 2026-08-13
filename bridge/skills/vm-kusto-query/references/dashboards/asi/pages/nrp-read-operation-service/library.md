# NRP — ReadOperationService: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:54.189Z.
> Total: 9 unique KQL queries across 7 panels (9 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ReadOperationService OperationCount | DataSummary | nrp | mdsnrp | queryFrom, queryTo |
| 2 | ReadOperationService OperationReliability | DataSummary | nrp | mdsnrp | queryFrom, queryTo |
| 3 | ReadOperationService GatewayReliability | DataSummary | nrp | mdsnrp | queryFrom, queryTo |

### 5xx Error Frequencies
Path: `5xx Error Frequencies`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ReadOperationService Errors | Table | nrp | mdsnrp | queryFrom, queryTo |

### 5xx Error Rates
Path: `5xx Error Rates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ReadOperationService ErrorRates | TimeSeries | nrp | mdsnrp | queryFrom, queryTo |

### Enablement Status
Path: `Enablement Status`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ReadOperationService OperationEnablement | Table | nrp | mdsnrp | queryFrom, queryTo |

### GetVirtualNetworkOperation Concurrency Cirrus Runs
Path: `GetVirtualNetworkOperation Concurrency Cirrus Runs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ReadOperationService GetVnet Cirrus | Table | nrp | mdsnrp | queryFrom, queryTo, vnetSize |

### ReadOperationService Load
Path: `ReadOperationService Load`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ReadOperationService OperationTimeseries | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, granularity |

### RemoteDataAccess RPC Latencies
Path: `RemoteDataAccess RPC Latencies`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ReadOperationService RPC Latency | Table | nrp | mdsnrp | queryFrom, queryTo |
