# CRP — CorrelationId: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:18:21.934Z.
> Total: 3 unique KQL queries across 3 panels (3 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Correlation Id" | ResourceGet | azcrp | crp_allprod | globalFrom, globalTo, local_correlationId, local_endDate, local_startDate |

### ApiQosEvent > ApiQosEvent
Path: `ApiQosEvent > ApiQosEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CorrelationId - ApiQosEvent | Table | azcrp | crp_allprod | local_correlationId, local_endDate, local_startDate |

### ApiQosEvent_nonGet > ApiQosEvent_nonGet
Path: `ApiQosEvent_nonGet > ApiQosEvent_nonGet`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CorrelationId - ApiQosEvent_nonGet | Table | azcrp | crp_allprod | local_correlationId, local_endDate, local_startDate |
