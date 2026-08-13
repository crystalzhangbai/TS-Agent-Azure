# Managed Disk — Correlation Id: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:27:08.044Z.
> Total: 9 unique KQL queries across 7 panels (9 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Correlation Id" | ResourceGet | Disks | Disks | local_correlationId, globalFrom, globalTo |
| 2 | CRP | Single | Disks | Disks | queryTime, queryCorrelationId, queryOperationId |
| 3 | Fabric & Aztec | Single | Disks | Disks | queryTime, queryCorrelationId |

### ApiQosEvent
Path: `ApiQosEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ApiQosEvent | Table | azcrp | crp_allprod | queryTime, queryCorrelationId |

### DiskManagerApiQoSEvent
Path: `DiskManagerApiQoSEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DiskManagerApiQoSEvent | Table | Disks | Disks | queryTime, queryCorrelationId |

### DiskManagerContextActivityEvent
Path: `DiskManagerContextActivityEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DiskManagerContextActivityEvent | Table | Disks | Disks | queryTime, queryCorrelationId |

### DiskRPResourceLifecycleEvent
Path: `DiskRPResourceLifecycleEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DiskRPResourceLifecycleEvent | Table | Disks | Disks | queryTime, queryCorrelationId |

### HttpIncomingRequests
Path: `HttpIncomingRequests`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HttpIncomingRequests | Table | armprodeus.eastus | Requests | queryTime, queryCorrelationId |

### HttpOutgoingRequests
Path: `HttpOutgoingRequests`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HttpOutgoingRequests | Table | armprodeus.eastus | Requests | queryTime, queryCorrelationId |
