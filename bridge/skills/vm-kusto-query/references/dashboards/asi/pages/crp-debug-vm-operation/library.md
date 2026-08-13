# CRP — Debug VM Operation: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:18:19.594Z.
> Total: 17 unique KQL queries across 15 panels (18 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "VM Operation" | ResourceGet | azcrp | crp_allprod | globalFrom, globalTo, local_correlationId, local_operationId |
| 2 | Preemption | Single | azcrp | crp_allprod | starttime, endtime, operationid |
| 3 | CRP Operation Info | Single | azcrp | crp_allprod | starttime, endtime, operationid |

### Resource Operations > Subscription Operations > Subscription Operations > ARM > ARM > ARM Operation Timeline for Subscription
Path: `Resource Operations > Subscription Operations > Subscription Operations > ARM > ARM > ARM Operation Timeline for Subscription`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARM Operation Timeline | Timeline | armprod | ARMProd | starttime, endtime, subscriptionid |

### Resource Operations > Subscription Operations > Subscription Operations > CRP > CRP > CRP Operations for Subscription
Path: `Resource Operations > Subscription Operations > Subscription Operations > CRP > CRP > CRP Operations for Subscription`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP Operation Table | Table | azcrp | crp_allprod | starttime, endtime, subscriptionid |

### Resource Operations > VM Operations > VM Operations > ARM > ARM > ARM Operation
Path: `Resource Operations > VM Operations > VM Operations > ARM > ARM > ARM Operation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARM Operation for VM | Table | armprod | ARMProd | starttime, endtime, subscriptionid, resourcename |

### Resource Operations > VM Operations > VM Operations > ARM > ARM > ARM Operation Timeline
Path: `Resource Operations > VM Operations > VM Operations > ARM > ARM > ARM Operation Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARM Operation | CoBeTimeline | armprod | ARMProd | starttime, endtime, subscriptionid, resourcename |

### Resource Operations > VM Operations > VM Operations > CRP > CRP > VM CRP Operations
Path: `Resource Operations > VM Operations > VM Operations > CRP > CRP > VM CRP Operations`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP Operations for VM | Table | azcrp | crp_allprod | starttime, endtime, subscriptionid, resourcename, resourcegroupname |
| 2 | Retrieve Resource "VM Operation" | ResourceGet | azcrp | crp_allprod | globalFrom, globalTo, local_correlationId, local_operationId |

### Resource Operations > VM Operations > VM Operations > CRP > CRP > VM Operation Timeline
Path: `Resource Operations > VM Operations > VM Operations > CRP > CRP > VM Operation Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM Operation | Timeline | azcrp | crp_allprod | starttime, endtime, subscriptionid, resourcename |

### VM / VMSS Activity > CRP Operation Log > CRP Operation Log > Component Call History
Path: `VM / VMSS Activity > CRP Operation Log > CRP Operation Log > Component Call History`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Component Call | Table | azcrp | crp_allprod | starttime, endtime, operationid |

### VM / VMSS Activity > CRP Operation Log > CRP Operation Log > CRP Context Activity Log
Path: `VM / VMSS Activity > CRP Operation Log > CRP Operation Log > CRP Context Activity Log`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP Context Operation | Table | azcrp | crp_allprod | starttime, endtime, operationid |

### VM / VMSS Activity > CRP Operation Log > CRP Operation Log > Operation Timeline
Path: `VM / VMSS Activity > CRP Operation Log > CRP Operation Log > Operation Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Component Call | Timeline | azcrp | crp_allprod | queryFrom, queryTo, queryOperationId |

### VM / VMSS Activity > NRP Operation Log > NRP Operation Log > NRP Operation Log
Path: `VM / VMSS Activity > NRP Operation Log > NRP Operation Log > NRP Operation Log`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NRP Operation Log | Table | nrp | mdsnrp | starttime, endtime, crpoperationid |

### VM / VMSS Activity > NRP Operation Log > NRP Operation Log > NRP Operation Timeline
Path: `VM / VMSS Activity > NRP Operation Log > NRP Operation Log > NRP Operation Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NRP Operation Timeline | Timeline | nrp | mdsnrp | starttime, endtime, crpoperationid |

### VM / VMSS Activity > VM Allocation > VM Allocation > VM Allocation
Path: `VM / VMSS Activity > VM Allocation > VM Allocation > VM Allocation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM Allocation in CRP | Table | azcrp | crp_allprod | starttime, endtime, operationid |

### VM / VMSS Activity > VMSS Goal Seeking (VMSS Only) > VMSS Goal Seeking (VMSS Only) > VMSS Container Goal Seeking Timeline
Path: `VM / VMSS Activity > VMSS Goal Seeking (VMSS Only) > VMSS Goal Seeking (VMSS Only) > VMSS Container Goal Seeking Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMSS Container Goal Seeking Timeline | Timeline | azcrp | crp_allprod | starttime, endtime, operationid |

### VM / VMSS Activity > VMSS Goal Seeking (VMSS Only) > VMSS Goal Seeking (VMSS Only) > VMSS Goal Seeking Operation
Path: `VM / VMSS Activity > VMSS Goal Seeking (VMSS Only) > VMSS Goal Seeking (VMSS Only) > VMSS Goal Seeking Operation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMSS Goal Seeking Operation | Table | azcrp | crp_allprod | starttime, endtime, operationid |
