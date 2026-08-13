# CRP — Debug Allocations: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:18:20.061Z.
> Total: 20 unique KQL queries across 20 panels (20 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Allocation from AllocatorAllocationResult | Single | azureallocator.westcentralus | AzureAllocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Allocation Request Traits > Allocation Request Traits
Path: `AzAllocator > Allocation Request Traits > Allocation Request Traits`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Allocation Request Trait | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Cluster Selection > ActiveClusterSelectionRules 
Path: `AzAllocator > Cluster Selection > ActiveClusterSelectionRules `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorActiveClusterSelectionRules | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Cluster Selection > Cluster Select Results
Path: `AzAllocator > Cluster Selection > Cluster Select Results`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Cluster Select Results | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Cluster Selection > Rejected Clusters from AllocatorRejectedClusterInfo
Path: `AzAllocator > Cluster Selection > Rejected Clusters from AllocatorRejectedClusterInfo`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Rejected Clusters | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Container Steps & Reuse > AllocatorContainerReuseStep 
Path: `AzAllocator > Container Steps & Reuse > AllocatorContainerReuseStep `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorContainerReuseStep | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Container Steps & Reuse > Container Results
Path: `AzAllocator > Container Steps & Reuse > Container Results`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Allocator Container Result | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Container Steps & Reuse > Container Reuse Rejection Reason
Path: `AzAllocator > Container Steps & Reuse > Container Reuse Rejection Reason`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorContainerReuseRejectionReason | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Limit Checks > AllocatorClusterSelectionNodeLimitCheckInfo
Path: `AzAllocator > Limit Checks > AllocatorClusterSelectionNodeLimitCheckInfo`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorClusterSelectionNodeLimitCheckInfo | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Limit Checks > AllocatorClusterSelectionUtilLimitCheckInfo
Path: `AzAllocator > Limit Checks > AllocatorClusterSelectionUtilLimitCheckInfo`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorClusterSelectionUtilLimitCheckInfo | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Limit Checks > VmLimitCheckInfo
Path: `AzAllocator > Limit Checks > VmLimitCheckInfo`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorVmLimitCheckInfo | Single | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Node Selection > Rejected Node Lists
Path: `AzAllocator > Node Selection > Rejected Node Lists`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Rejected Node Lists | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### AzAllocator > Node Selection > Rejected Nodes
Path: `AzAllocator > Node Selection > Rejected Nodes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Rejected Nodes | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### Capacity
Path: `Capacity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Request VM Size | Single | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryAllocationId |

### Capacity > Capacity from AllocatorMonitoringLogAllocableVMCount
Path: `Capacity > Capacity from AllocatorMonitoringLogAllocableVMCount`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorMonitoringLogAllocableVMCount | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryVMSize, queryCluster |

### CRP
Path: `CRP`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Operation from ApiQosEvent | Single | azcrp | crp_allprod | queryFrom, queryTo, queryOperationId |

### CRP > Allocation
Path: `CRP > Allocation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP Allocation Request  | MultiRow | azcrp | crp_allprod | queryFrom, queryTo, queryOperationId |

### CRP > Allocations from this Operation
Path: `CRP > Allocations from this Operation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Allocations from AllocatorAllocationResult | Table | azureallocator.westcentralus | azureallocator | queryFrom, queryTo, queryActivityId |

### CRP > Cluster Filtering in ComputeAllocationActivity > Cluster Filtering in ComputeAllocationActivity
Path: `CRP > Cluster Filtering in ComputeAllocationActivity > Cluster Filtering in ComputeAllocationActivity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Stamp Filtering in ComputeAllocationActivity | Table | azcrp | crp_allprod | queryFrom, queryTo, queryOperationId |

### CRP > Details Logs
Path: `CRP > Details Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Allocation Activity | Table | azcrp | crp_allprod | queryFrom, queryTo, queryActivityId |
