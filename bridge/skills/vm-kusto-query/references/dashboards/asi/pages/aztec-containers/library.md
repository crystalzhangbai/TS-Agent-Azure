# Aztec — Containers: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T11:19:31.550Z.
> Total: 30 unique KQL queries across 20 panels (30 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 10

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Containers" | ResourceGet | azurecm | AzureCM | globalFrom, globalTo, local_containerId, local_nodeId, local_subscriptionId, local_tenantName, local_virtualMachineUniqueId |
| 2 | Lookup AzCompute Shoebox Account | Single | azurecm | AzureCM | queryRegionName |
| 3 | Lookup AzNw Region Code | Single | azurecm | AzureCM | queryRegionName |
| 4 | VM Context | Single | Vmainsight | CAD | queryContainerId, queryFrom, queryTo |
| 5 | Node TOR Info | Single | Vmainsight | AzureGraph | queryNodeId |
| 6 | VM Impacting Events | Timeline | vmainsight | vmadb | queryContainerId |
| 7 | VMA | Timeline | vmainsight | vmadb | queryContainerId, queryFrom, queryTo, queryTenantName |
| 8 | Air Managed Events | Timeline | vmainsight | Air | queryContainerId, queryFrom, queryTo |
| 9 | Query DCMNMAgentProgrammingDurationEtwTable | MultiRow | azurecm | azurecm | queryFrom, queryTo, queryContainerId |
| 10 | Container DNS Queries | Table | azcore.centralus | PrivateDnsRr | queryFrom, queryTo, queryContainerId |

### Change Profiling Events > Change Profiling Events
Path: `Change Profiling Events > Change Profiling Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Change Profiling Events | Table | azurecm | AzureCM | queryContainerId |

### Container Isolation & Role Instance Cleanup > Container Isolation - TMMgmtContainerIsolationStatusEtwTable
Path: `Container Isolation & Role Instance Cleanup > Container Isolation - TMMgmtContainerIsolationStatusEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtContainerIsolationStatusEtwTable | Table | azcore.centralus | Fc | queryFrom, queryTo, queryContainerId |

### Container Isolation & Role Instance Cleanup > Role Instance Cleanup Events
Path: `Container Isolation & Role Instance Cleanup > Role Instance Cleanup Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Role Instance Cleanup Events | Table | azcore.centralus | Fc | queryContainerId, queryFrom, queryTo |

### Container State
Path: `Container State`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AggregateState | Filter | azurecm | AzureCM | - |
| 2 | Query LogContainerHealthSnapshot by ContainerId | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryFilter, queryContainerId |

### Container State > Role Instance State - LogRoleInstanceSnapshot
Path: `Container State > Role Instance State - LogRoleInstanceSnapshot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query LogRoleInstanceSnapshot | Table | azcore.centralus | Fc | queryFrom, queryTo, queryContainerId |

### Counters > CPU, Memory, Network & Disk
Path: `Counters > CPU, Memory, Network & Disk`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Counters | TimeSeries | azcore.centralus | Fa | queryContainerId, queryStart, queryEnd |

### Eviction > LowPriorityVmPreemptionEvent 
Path: `Eviction > LowPriorityVmPreemptionEvent `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query LowPriorityVmPreemptionEvent | Table | azcore.centralus | Fc | queryFrom, queryTo, queryContainerId, queryTenantName, queryRoleInstanceName |

### Fault Handling Container Recovery Event
Path: `Fault Handling Container Recovery Event`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Fault Handling Container Recovery Event | Table | azurecm | AzureCM | queryContainerId |

### Guest Agent Events > Guest Agent Extension Events
Path: `Guest Agent Events > Guest Agent Extension Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Guest Agent Extension Events | Table | azcore.centralus | Fa | queryContainerId, global_startTime, global_endTime |

### Guest Agent Generic Logs > Guest Agent Generic Logs
Path: `Guest Agent Generic Logs > Guest Agent Generic Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Guest Agent Generic Logs | Table | azcore.centralus | Fa | queryContainerId |

### Networking > Networking Links
Path: `Networking > Networking Links`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Container Info | Single | AzureCM | AzureCM | queryFrom, queryTo, qContainer |

### Networking > NM Agent Health (1 is Health)
Path: `Networking > NM Agent Health (1 is Health)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container NMAgent | TimeSeries | azurecm | AzureCM | queryContainerId, queryFrom, queryTo |

### Reuse Rejection Reason > Reuse Rejection Reason
Path: `Reuse Rejection Reason > Reuse Rejection Reason`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Reuse Rejection Reason | Table | azurecm | AzureCM | queryContainerId |

### Service Healing > Not Triggered Reasons
Path: `Service Healing > Not Triggered Reasons`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Service Healing Not Triggered Reasons | Table | azurecm | AzureCM | queryNodeId, queryContainerId, queryStart |

### Service Healing > Service Healing Result
Path: `Service Healing > Service Healing Result`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Service Healing Result Events | Table | accp.centralus | AZSM | queryFrom, queryTo, queryContainerId |

### Service Healing > Tenant Triggered Fault Reason
Path: `Service Healing > Tenant Triggered Fault Reason`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Service Healing - TriggeredFaultReason | Table | azurecm | AzureCM | queryTenantName, queryFrom |

### Sla Measurement Event
Path: `Sla Measurement Event`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Sla Measurement Event | Table | azurecm | AzureCM | queryContainerId |

### TMMgmtContainerTraceEtwTable
Path: `TMMgmtContainerTraceEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtContainerTraceEtwTable | Table | azcore.centralus | Fc | queryFrom, queryTo, queryContainerId |

### TMMgmtLeaseManagerEtwTable
Path: `TMMgmtLeaseManagerEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtLeaseManagerEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryContainerId |
