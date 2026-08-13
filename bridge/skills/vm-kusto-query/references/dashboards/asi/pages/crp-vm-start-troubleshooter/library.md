# CRP — VM Start Troubleshooter: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:18:21.284Z.
> Total: 4 unique KQL queries across 3 panels (4 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "VM Start Troubleshooter" | ResourceGet | azcrp | crp_allprod | globalFrom, globalTo, local_vMId |
| 2 | Start Operations | Filter | azcrp | crp_allprod | queryFrom, queryTo, queryVmId |

### Component and Compute Allocations for {{operationId}}
Path: `Component and Compute Allocations for {{operationId}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP Allocation and Component Events | Table | azcrp | crp_allprod | queryFrom, queryTo, queryOperationId |

### Control Plane Traces
Path: `Control Plane Traces`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Ocular Summary Logs with Resource Name | CoBeTimeline | ocularcentralus.centralus | FunctionDB | querySubscriptionId, queryResourceGroupName, queryResourceName, queryFrom, queryTo |
