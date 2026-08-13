# CRP — VMs: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:29:30.228Z.
> Total: 24 unique KQL queries across 14 panels (25 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 9

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "VMs" | ResourceGet | azcrpbifollower | bi_allprod | globalFrom, globalTo, local_resourceGroupName, local_resourceName, local_subscriptionId, local_VMId |
| 2 | Get AzCoreSpoke | Single | azcore.centralus | Fa | qFrom, qTo, qVM |
| 3 | Query VM Placement History | Table | azcrpbifollower | bi_allprod | queryFrom, queryTo, querySubId, queryResourceGroup, queryVMName |
| 4 | CRP-SingleVM-NetworkProfile | Single | argwus2nrpone.westus2 | AzureResourceGraph | local_networkProfile |
| 5 | VMAllocationInfo | Single | azcrpbifollower | bi_allprod | queryFrom, queryTo, queryRGName, querySubId, queryResourceName |
| 6 | Query VM Extension | Table | Azcrpbifollower | bi_allprod | queryFrom, queryTo, queryVMId |
| 7 | Query VMs in AvailabilitySet | Table | azcrpbifollower | bi_allprod | queryFrom, queryTo, queryAvailabilitySetKey |
| 8 | query Communications in AlbnTargets | Table | Icmcluster | ACM.Publisher | queryFrom, queryTo, querySubId |
| 9 | Examine VM by ContainerId | Filter | Azcsupfollower | AzureCM | queryFrom, queryTo, queryVmId |

### Allocation Info (Goal Seek State)
Path: `Allocation Info (Goal Seek State)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GoalState | Timeline | azcrpbifollower | bi_allprod | queryFrom, queryTo, querySubId, queryResourceGroupName, queryResourceName |
| 2 | Error from AllocationInfo | Timeline | azcrpbifollower | bi_allprod | queryFrom, queryTo, querySubId, queryResourceGroupName, queryResourceName |

### Allocation Info (Goal Seek State) > Allocation Info
Path: `Allocation Info (Goal Seek State) > Allocation Info`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMAllocationInfo Details | Table | azcrpbifollower | bi_allprod | queryFrom, queryTo, querySubId, queryResourceGroupName, queryResourceName |

### Container Transition
Path: `Container Transition`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ContainerStateTransition | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, queryVmId, queryContainerId |
| 2 | ContainerOSStateTransition | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, queryVmId, queryContainerId |

### Container Transition > Extended Error Details (If Any)
Path: `Container Transition > Extended Error Details (If Any)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Extended Container Error Details | Table | azurecm | azurecm | qFrom, qTo, qContainer |

### Containers > Fabric Placements
Path: `Containers > Fabric Placements`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM Fabric Containers | Table | Azcsupfollower | AzureCM | querySubscriptionId, queryVmId, global_startTime, global_endTime |

### Counters > Counters
Path: `Counters > Counters`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM Counters | TimeSeries | {{qAzCoreCluster}} | Fa | qVM, qAzCoreCluster, qFrom, qTo |

### CRP Operations in ApiQosEvent
Path: `CRP Operations in ApiQosEvent`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FilterOperations | Filter | Azcrp | crp_allprod | queryFrom, queryTo |
| 2 | Query VM Operations in ApiQosEvent | Table | Azcrp | crp_allprod | queryFrom, queryTo, querySubId, queryResourceGroup, queryResourceName, queryOpsFilter |

### Disks from CRP BI
Path: `Disks from CRP BI`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query VMManagedDisksAllocationInfo | Table | Azcrpbifollower | bi_allprod | queryFrom, queryTo, queryVMId |

### MeteredUsageEvent 
Path: `MeteredUsageEvent `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query MeteredUsageEvent | Table | azcrp | monetaprod | queryFrom, queryTo, queryResourceId |

### Networking
Path: `Networking`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP-SingleVM-NetworkProfile | Single | argwus2nrpone.westus2 | AzureResourceGraph | local_networkProfile |

### Networking > NICs
Path: `Networking > NICs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP-SingleVM-NetworkProfile-Expand | Table | argwus2nrpone.westus2 | AzureResourceGraph | data |

### ResourceHealthAzureActivityLogEvent
Path: `ResourceHealthAzureActivityLogEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query ResourceHealthAzureActivityLogEvent | Table | icmbrain | AzureResourceHealth | queryFrom, queryTo, queryResourceId, querySubId |

### Scheduled Events
Path: `Scheduled Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Scheduled Events in AzPEWorkflowEvent | Table | azpe | azpe | queryFrom, queryTo, queryVMId |
