# CRP — OperationId: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:18:25.102Z.
> Total: 19 unique KQL queries across 15 panels (21 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Operation Id" | ResourceGet | azcrp | crp_allprod | globalFrom, globalTo, local_endDate, local_operationId, local_startDate |
| 2 | CSS Insight for NetworkingInternalOperation | IssueDetector | azcrp | crp_allprod | startTime, endTime, queryOperationId |
| 3 | CSS Insight for WaitForOngoingAllocation | IssueDetector | Azcrp | crp_allprod | queryFrom, queryTo, queryOperationId |

### Allocation Activity > Allocation Activity > Compute Allocation Activity
Path: `Allocation Activity > Allocation Activity > Compute Allocation Activity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Compute Allocation Activity - ActivityId | Table | azcrp | crp_allprod | queryActivityId, queryOperationTime |

### ApiQosEvent > ApiQosEvent > ApiQosEvent - operationId {{operationId}}
Path: `ApiQosEvent > ApiQosEvent > ApiQosEvent - operationId {{operationId}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ExecutionGraph | Single | egpublic.westus | eg | queryFrom, queryTo, queryOperationId |

### ComponentQosEvent > ComponentQosEvent
Path: `ComponentQosEvent > ComponentQosEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | API QoS | CoBeTimeline | azcrp | crp_allprod | operationId, timeStamp |

### ComponentQosEvent > ComponentQosEvent > ComponentQoSEvent
Path: `ComponentQosEvent > ComponentQosEvent > ComponentQoSEvent`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FilterGets | Filter | Azcrp | crp_allprod | - |
| 2 | Query ComponentQoSEvent | Table | azcrp | crp_allprod | queryOperationId, queryBegin, queryEnd, queryFilter |

### ContextActivity > ContextActivity > ContextActivity - operationId {{operationId}}
Path: `ContextActivity > ContextActivity > ContextActivity - operationId {{operationId}}`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OperationId ContextActivity | Table | azcrp | crp_allprod | local_operationId, queryFilter, queryOpStartTime, queryOpEndTime |
| 2 | Filter - All or Errors | Filter | Azcrp | crp_allprod | - |

### Execution Graph > Execution Graph
Path: `Execution Graph > Execution Graph`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Lookup up EG | Single | https://egpublic.westus | eg | queryCorrelationOrOperationId |

### Extract SVD
Path: `Extract SVD`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Extract SVD | ResourceGet | azcsupfollower2.centralus | crp_allprod | queryFrom, queryTo, queryStart, queryEnd, queryOperationId |

### GatewayApiQoSEvent > GatewayApiQoSEvent > GatewayApiQoSEvent - operationId {{operationId}}
Path: `GatewayApiQoSEvent > GatewayApiQoSEvent > GatewayApiQoSEvent - operationId {{operationId}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OperationId GatewayApiQoSEvent GET | Single | azcrp | crp_allprod | local_operationId, local_endDate, local_startDate |

### Preemption State
Path: `Preemption State`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Preemption | Single | azcrp | crp_allprod | starttime, endtime, operationid |

### Target Resource - VM
Path: `Target Resource - VM`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get VM from VMApiQosEvent | Single | azcrp | crp_allprod | queryFrom, queryTo, queryOperationId |
| 2 | OperationId GatewayApiQoSEvent GET | Single | azcrp | crp_allprod | local_operationId, local_endDate, local_startDate |

### Target Resource - VMSS
Path: `Target Resource - VMSS`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get VMSS from GatewayApiQoSEvent | Single | azcrp | crp_allprod | queryFrom, queryTo, queryOperationId |

### VMApiQosEvent > VMApiQosEvent > VMApiQosEvent - operationId {{operationId}}
Path: `VMApiQosEvent > VMApiQosEvent > VMApiQosEvent - operationId {{operationId}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OperationId VMApiQosEvent GET | Single | azcrp | crp_allprod | local_operationId, local_endDate, local_startDate |

### VmssVMApiQosEvent > VmssVMApiQosEvent > VmssVMApiQosEvent - operationId {{operationId}}
Path: `VmssVMApiQosEvent > VmssVMApiQosEvent > VmssVMApiQosEvent - operationId {{operationId}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OperationId VmssVMApiQosEvent GET | Single | azcrp | crp_allprod | local_operationId, local_endDate, local_startDate |

### VmssVMGoalSeekingActivity > VmssVMGoalSeekingActivity > VmssVMGoalSeekingActivity - operationId {{operationId}}
Path: `VmssVMGoalSeekingActivity > VmssVMGoalSeekingActivity > VmssVMGoalSeekingActivity - operationId {{operationId}}`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OperationId VmssVMGoalSeekingActivity | Table | azcrp | crp_allprod | local_operationId, local_endDate, local_startDate, queryFilter, qMaxLevel |
| 2 | Filter - All or Errors | Filter | Azcrp | crp_allprod | - |
