# Aztec — Tenant {{tenantName}}: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:20:39.684Z.
> Total: 72 unique KQL queries across 62 panels (77 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Tenants" | ResourceGet | azcore.centralus | Fc | local_tenantName, globalFrom, globalTo |
| 2 | Tenant Features | FeatureList | azcore.centralus | Fc | queryTenantName |
| 3 | Tenant AzSM Features | FeatureList | accp.centralus | AZSM | queryTenantName |

### Allocations > Allocations > Allocator > Allocator > AllocatorAllocationResult
Path: `Allocations > Allocations > Allocator > Allocator > AllocatorAllocationResult`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorAllocationResult | Table | https://azureallocator.westcentralus | Azureallocator | queryFrom, queryTo, queryTenantName |

### Allocations > Allocations > Allocator > Allocator > AllocatorClusterSelectionResult
Path: `Allocations > Allocations > Allocator > Allocator > AllocatorClusterSelectionResult`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorClusterSelectionResult | Table | azureallocator.westcentralus | AzureAllocator | queryFrom, queryTo, queryTenantName |

### Allocations > Allocations > Allocator > Allocator > AllocatorContainerResult 
Path: `Allocations > Allocations > Allocator > Allocator > AllocatorContainerResult `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorContainerResult | Table | azureallocator.westcentralus | AzureAllocator | queryFrom, queryTo, queryTenantName |

### Allocations > Allocations > Allocator > Allocator > AllocatorContainerReuseRejectionReason
Path: `Allocations > Allocations > Allocator > Allocator > AllocatorContainerReuseRejectionReason`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AllocatorContainerReuseRejectionReason | Table | azureallocator.westcentralus | AzureAllocator | queryFrom, queryTo, queryTenantName |

### Allocations > Allocations > Allocator > Allocator > AllocatorRejectedClusterInfo
Path: `Allocations > Allocations > Allocator > Allocator > AllocatorRejectedClusterInfo`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AllocatorRejectedClusterInfo | Table | https://azureallocator.westcentralus | AzureAllocator | queryFrom, queryTo, queryTenantName |

### Allocations > Allocations > Allocator > Allocator > AllocatorRejectedNodeInfo
Path: `Allocations > Allocations > Allocator > Allocator > AllocatorRejectedNodeInfo`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AllocatorRejectedNodeInfo | Table | azureallocator.westcentralus | AzureAllocator | queryFrom, queryTo, queryTenantName |

### Allocations > Allocations > AzAllocatorClient > AzAllocatorClient > AzAllocatorClientEvents (AzSM)
Path: `Allocations > Allocations > AzAllocatorClient > AzAllocatorClient > AzAllocatorClientEvents (AzSM)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzAllocatorClientEvents | Table | accp.centralus | AZSM | queryTenantName, queryFrom, queryTo |

### Allocations > Allocations > AzAllocatorClient > AzAllocatorClient > CRP - ComputeAllocationActivity
Path: `Allocations > Allocations > AzAllocatorClient > AzAllocatorClient > CRP - ComputeAllocationActivity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query ComputeAllocationActivity | Table | Azcrp | crp_allprod | queryFrom, queryTo, queryTenantName |

### ApiUnexpectedFailures IcMs > ApiUnexpectedFailures IcMs > ApiUnexpectedFailures in IcMDataWarehouse
Path: `ApiUnexpectedFailures IcMs > ApiUnexpectedFailures IcMs > ApiUnexpectedFailures in IcMDataWarehouse`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query ApiUnexpectedFailures in IcMDataWarehouse | Table | icmcluster | IcMDataWarehouse | queryFrom, queryTo, queryRegionName |

### At-A-Glance Health
Path: `At-A-Glance Health`  ·  Queries: 7

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant Upgrade Rollouts | Timeline | azcsupfollower | AzureCM | queryTenantName, queryFrom, queryTo |
| 2 | Tenant Container Health Faults | Timeline | azurecm | azurecm | queryTenantName, qSub, qFrom, qTo |
| 3 | VMA | Timeline | vmainsight | vmadb | queryContainerId, queryFrom, queryTo, queryTenantName |
| 4 | ICM Outages | Timeline | azurecm | azurecm | querySubscriptionId, queryRegion, queryFrom, queryTo |
| 5 | FC Downtime | Timeline | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName |
| 6 | FC Failover | Timeline | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName |
| 7 | Tenant State | Timeline | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### At-A-Glance Health > Extended Error Details
Path: `At-A-Glance Health > Extended Error Details`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Explode LogContainerHealthSnapshot ExtendedDetails | Table | azurecm | azurecm | qExtendedDetails |

### AzPE
Path: `AzPE`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzPETenantSnapshot | FeatureList | azpe | azpe | queryFrom, queryTo, queryTenantName |

### AzPE > AzPE > AzPEWorkflowEvent
Path: `AzPE > AzPE > AzPEWorkflowEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AzPEWorkflowEvent | Table | azpe | azpe | queryFrom, queryTo, queryTenantName |

### AzPE > AzPE > MR Events
Path: `AzPE > AzPE > MR Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query MREvents | Table | azpe | azpe | queryFrom, queryTo, queryTenantName |

### AzPE > AzPENotificationStepResultEvents
Path: `AzPE > AzPENotificationStepResultEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzPENotificationStepResultEvents | Table | accp.centralus | azsm | queryFrom, queryTo, tenantNames |

### AzSM
Path: `AzSM`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant AzSM Application | Single | accp.centralus | AZSM | queryTenantName, queryTenantTimestamp |

### AzSM Events & Traces > AzSM Events & Traces > AzSM Exceptions Events > AzSM Exceptions Events > AzSMExceptionsEvents
Path: `AzSM Events & Traces > AzSM Events & Traces > AzSM Exceptions Events > AzSM Exceptions Events > AzSMExceptionsEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AzSMExceptionsEvents | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName |

### AzSM Events & Traces > AzSM Events & Traces > AzSM Service Traces Events > AzSM Service Traces Events > AzSMServiceTracesEvents 
Path: `AzSM Events & Traces > AzSM Events & Traces > AzSM Service Traces Events > AzSM Service Traces Events > AzSMServiceTracesEvents `  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AzSMServiceTracesEvents | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName, queryFilterValue |
| 2 | FilterMessages | Filter | azurecm | AzureCM | - |

### AzSM Events & Traces > AzSM Events & Traces > AzSM State Machine Events > AzSM State Machine Events > AzSMTenantStatemachineEvents
Path: `AzSM Events & Traces > AzSM Events & Traces > AzSM State Machine Events > AzSM State Machine Events > AzSMTenantStatemachineEvents`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant AzSM State Machine Events | Table | accp.centralus | AZSM | queryTenantName, queryFrom, queryTo, queryFilterValue |
| 2 | FilterMessages | Filter | azurecm | AzureCM | - |

### AzSM Events & Traces > AzSM Events & Traces > AzSM State Machine Events > AzSM State Machine Events > state machine timeline
Path: `AzSM Events & Traces > AzSM Events & Traces > AzSM State Machine Events > AzSM State Machine Events > state machine timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant AzSM State Machine Events timeline | Timeline | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName |

### AzSM Events & Traces > AzSM Events & Traces > AzSM Tenant Events > AzSM Tenant Events > Tenant Events
Path: `AzSM Events & Traces > AzSM Events & Traces > AzSM Tenant Events > AzSM Tenant Events > Tenant Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant AzSM Events | Table | accp.centralus | AZSM | queryTenantName, queryFrom, queryTo |

### AzSM Events & Traces > AzSM Events & Traces > AzSM Update Tenant Events > AzSM Update Tenant Events
Path: `AzSM Events & Traces > AzSM Events & Traces > AzSM Update Tenant Events > AzSM Update Tenant Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AzSMUpdateTenantEvents | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName |

### Cleanup > Cleanup > AzSM Cleanup Events
Path: `Cleanup > Cleanup > AzSM Cleanup Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant AzSM Cleanup Events | Table | accp.centralus | AZSM | queryTenantName, queryFrom, queryTo |

### Cleanup > Cleanup > Formatted FRIC from RnmOperationEvents
Path: `Cleanup > Cleanup > Formatted FRIC from RnmOperationEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query FRIC from RnmOperationEvents | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName |

### Cleanup > Cleanup > LogRoleInstanceCleanupEvent
Path: `Cleanup > Cleanup > LogRoleInstanceCleanupEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query LogRoleInstanceCleanupEvent by TenantName | Table | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName |

### Cleanup > Cleanup > RnmOperationEvents > RnmOperationEvents
Path: `Cleanup > Cleanup > RnmOperationEvents > RnmOperationEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Rnm Operation Events | Table | accp.centralus | AZSM | queryTenantName, queryFrom, queryTo |

### Cleanup > Cleanup > Tenant Cleanup Events
Path: `Cleanup > Cleanup > Tenant Cleanup Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant Cleanup Events | Table | azcsupfollower | azurecm | queryTenantName, queryFrom, queryTo |

### Containers > Containers > Container Health
Path: `Containers > Containers > Container Health`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AggregateState | Filter | azurecm | AzureCM | - |
| 2 | Query LogContainerHealthSnapshot | Table | Azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName, queryFilter, queryContainerId |

### Containers > Containers > Container Health Timeline > Container Health Timeline
Path: `Containers > Containers > Container Health Timeline > Container Health Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Health | Timeline | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### Containers > Containers > Containers
Path: `Containers > Containers > Containers`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant Containers | Table | azcsupfollower | AzureCM | queryTenantName, queryFrom, queryTo |

### Containers > Containers > Role Instance Count - LogTenantSnapshot
Path: `Containers > Containers > Role Instance Count - LogTenantSnapshot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant Instance Count | TimeSeries | azcsupfollower | azurecm | queryTenantName, queryFrom, queryTo |

### Containers > Containers > Role State Timeline for PaaS Containers
Path: `Containers > Containers > Role State Timeline for PaaS Containers`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RoleState for PaaS Containers | Timeline | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### Jobs > Jobs > TMMgmtMRJobSnapshotEtwTable
Path: `Jobs > Jobs > TMMgmtMRJobSnapshotEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtMRJobSnapshotEtwTable | Table | Azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### Jobs > Jobs > TMMgmtTenantManagementJobInfoEtwTable
Path: `Jobs > Jobs > TMMgmtTenantManagementJobInfoEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant Job Info | Table | azcsupfollower | AzureCM | queryTenantName, queryFrom, queryTo |

### RNM & NSM Logs > RNM & NSM Logs > Aznwmds - DeleteResourceEvent
Path: `RNM & NSM Logs > RNM & NSM Logs > Aznwmds - DeleteResourceEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query DeleteResourceEvent | Table | aznwsdn | aznwmds | queryFrom, queryTo, queryTenantName |

### RNM & NSM Logs > RNM & NSM Logs > ResourceReleaseEvent
Path: `RNM & NSM Logs > RNM & NSM Logs > ResourceReleaseEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query ResourceReleaseEvent | Table | aznwsdn | aznwmds | queryFrom, queryTo, queryTenantName, queryRegion |

### RNM & NSM Logs > RNM & NSM Logs > ServiceExecutionEvent
Path: `RNM & NSM Logs > RNM & NSM Logs > ServiceExecutionEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query ServiceExecutionEvent | Table | aznwsdn | aznwmds | queryFrom, queryTo, queryTenantName, queryRegionName |

### Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing
Path: `Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSMServiceHealingStepResultEvents | Timeline | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName |

### Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing > AzSMServiceHealingResultEvents
Path: `Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing > AzSMServiceHealingResultEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSMServiceHealingResultEvents | Table | accp.centralus | AZSM | queryTenantName, queryFrom, queryTo |

### Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing > AzSMServiceHealingStepResultEvents
Path: `Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing > AzSMServiceHealingStepResultEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSMServiceHealingStepResultEvents | Table | accp.centralus | AZSM | queryTenantName, queryFrom, queryTo |

### Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing > AzSMServiceHealingTriggerEvents
Path: `Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing > AzSMServiceHealingTriggerEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSMServiceHealingTriggerEvents | Table | accp.centralus | AZSM | queryTenantName, queryFrom, queryTo |

### Service Healing > Service Healing > Service Healing > Service Healing > ServiceHealingTenantStatusEtwTable
Path: `Service Healing > Service Healing > Service Healing > Service Healing > ServiceHealingTenantStatusEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query ServiceHealingTenantStatusEtwTable | Table | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName |

### Service Healing > Service Healing > Service Healing > Service Healing > ServiceHealingTriggerEtwTable
Path: `Service Healing > Service Healing > Service Healing > Service Healing > ServiceHealingTriggerEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query ServiceHealingTriggerEtwTable | Table | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName |

### Target Resource
Path: `Target Resource`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Locate Resource by Tenant Name | Table | azcrp | crp_allprod | queryFrom, queryTo, queryFabricTenantName |

### Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > Tenant Change Profiling Events
Path: `Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > Tenant Change Profiling Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant Change Profiling Events | Table | azcsupfollower | AzureCM | queryTenantName, queryFrom, queryTo |

### Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > Tenant SLA Events - TMMgmtSlaMeasurementEventEtwTable
Path: `Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > Tenant SLA Events - TMMgmtSlaMeasurementEventEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Qury TMMgmtSlaMeasurementEventEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > TMMgmtHighLatencyUDWalkEtwTable
Path: `Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > TMMgmtHighLatencyUDWalkEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtHighLatencyUDWalkEtwTable | Table | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName |

### Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > UD Walk for IaaS > TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable
Path: `Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > UD Walk for IaaS > TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > UD Walk for PaaS > TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable
Path: `Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > UD Walk for PaaS > TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### Tenant Logs > Tenant Logs > Node Events > Node Events
Path: `Tenant Logs > Tenant Logs > Node Events > Node Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query all TMMgmtNodeEventsEtwTable in the one tenant | Table | azcore.centralus | AzureCP | queryFrom, queryTo, queryTenantName |

### Tenant Logs > Tenant Logs > Tenant Audit Events > Tenant Audit Events > Audit Events from TMMgmtTenantEventsEtwTable
Path: `Tenant Logs > Tenant Logs > Tenant Audit Events > Tenant Audit Events > Audit Events from TMMgmtTenantEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TenantAuditEvents | Table | azurecm | AzureCM | tenantName |

### Tenant Logs > Tenant Logs > Tenant Events > Tenant Events
Path: `Tenant Logs > Tenant Logs > Tenant Events > Tenant Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtTenantEventsEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### Tenant Logs > Tenant Logs > Tenant Events and Node Events > Tenant Events and Node Events > Tenant Logs from TMMgmtNodeEventsEtwTable + TMMgmtTenantEventsEtwTable
Path: `Tenant Logs > Tenant Logs > Tenant Events and Node Events > Tenant Events and Node Events > Tenant Logs from TMMgmtNodeEventsEtwTable + TMMgmtTenantEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant Logs | Table | azcsupfollower | azurecm | queryTenantName, queryFrom, queryTo |

### Tenant QoS > Tenant QoS > Fabric Calls > Fabricator Calls from TMClusterFabricAuditEtwTable
Path: `Tenant QoS > Tenant QoS > Fabric Calls > Fabricator Calls from TMClusterFabricAuditEtwTable`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMClusterFabricAuditEtwTable | Table | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName, queryFilterValue |
| 2 | FilterGetOperations | Filter | azurecm | Azurecm | - |

### Tenant QoS > Tenant QoS > Requests by CRP > Fabric Operations submit by CRP - ComponentQoSEvent 
Path: `Tenant QoS > Tenant QoS > Requests by CRP > Fabric Operations submit by CRP - ComponentQoSEvent `  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query ComponentQoSEvent | Table | azcrp | crp_allprod | queryFrom, queryTo, queryTenantName, queryFilterValue |
| 2 | FilterGetOperations | Filter | azurecm | Azurecm | - |

### Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > CommonWebOperationEnd > Operations from CommonWebOperationEnd
Path: `Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > CommonWebOperationEnd > Operations from CommonWebOperationEnd`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Operations in CommonWebOperationEnd | Table | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName, queryFilterValue |
| 2 | FilterGetOperations | Filter | azurecm | Azurecm | - |

### Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > GatewayService > GatewayService > GatewayRequestCompleted
Path: `Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > GatewayService > GatewayService > GatewayRequestCompleted`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query GatewayRequestCompleted | Table | azcpplatform.westcentralus | azcpplatform | queryFrom, queryTo, queryTenantName |

### Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > GatewayService > GatewayService > GatewayServiceTraceEvent
Path: `Tenant QoS > Tenant QoS > Tenant Operations > Tenant Operations > GatewayService > GatewayService > GatewayServiceTraceEvent`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query GatewayServiceTraceEvent | Table | azcpplatform.westcentralus | azcpplatform | queryFrom, queryTo, queryTenantName, queryFilterValue |
| 2 | FilterMessages | Filter | azurecm | AzureCM | - |

### Tenant Settings > AzPETenantSettingsSnapshot 
Path: `Tenant Settings > AzPETenantSettingsSnapshot `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AzPETenantSettingsSnapshot | Table | Azpe | Azpe | queryFrom, queryTo, queryTenantName |

### Tenant Settings > LogTenantOverridableSettingsSnapshot
Path: `Tenant Settings > LogTenantOverridableSettingsSnapshot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query LogTenantOverridableSettingsSnapshot | Table | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName |

### VIPs
Path: `VIPs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant VIPs | Table | Azcsupfollower | AzureCM | queryTenantName, queryTenant |
