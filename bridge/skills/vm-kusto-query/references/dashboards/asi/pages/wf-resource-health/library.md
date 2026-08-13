# EEE RDOS — WF Resource Health: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:09:24.594Z.
> Total: 29 unique KQL queries across 28 panels (32 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Azure VM" ResourceHealth DS | ResourceGet | storageclient.eastus | Fc | globalFrom, globalTo, local_containerId, local_nodeId, local_virtualMachineUniqueId |
| 2 | LogContainerHealthSnapshot_RH_VMId_CM | Table | Azurecm | AzureCM | query_StartTime, query_EndTime, query_VMId |
| 3 | VmShoeboxCounterTable DS | Single | azcore.centralus | Fa | query_StartTime, query_EndTime, query_ContainerId |

### ActivityLogForProdDiagnosticPipeline > Represents resource health events that have been pushed from GHS (Geneva Health) to customer activity log
Path: `ActivityLogForProdDiagnosticPipeline > Represents resource health events that have been pushed from GHS (Geneva Health) to customer activity log`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ResourceHealthAzureActivityLogEvent_UnexpectedRestart DS | Table | icmbrain | AzureResourceHealth | query_StartTime, query_EndTime, query_ResourceId |
| 2 | VmShoeboxCounterTable DS | Single | azcore.centralus | Fa | query_StartTime, query_EndTime, query_ContainerId |

### AzCiM/LogHealthAnnotationEvent
Path: `AzCiM/LogHealthAnnotationEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LogContainerHealthSnapshot_RH_VMId_CM | Table | Azurecm | AzureCM | query_StartTime, query_EndTime, query_VMId |

### AzCiM/LogHealthAnnotationEvent > Represents emitted annotations from Fabric for the Container Id shared
Path: `AzCiM/LogHealthAnnotationEvent > Represents emitted annotations from Fabric for the Container Id shared`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LogHealthAnnotationEvent DS | Table | Azurecm | AzureCM | query_StartTime, query_EndTime, query_ContainerId |

### KyberAnnotationEvent > Represents the annotations that Kyber receives from AzPubSub - by the containerid
Path: `KyberAnnotationEvent > Represents the annotations that Kyber receives from AzPubSub - by the containerid`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | KyberAnnotationEvent | Table | aplat.westcentralus | Aplat | queryFrom, queryTo, containerId |

### KyberAnnotationEvent by VmId > Represents the annotations that Kyber receives from AzPubSub - by the vmid
Path: `KyberAnnotationEvent by VmId > Represents the annotations that Kyber receives from AzPubSub - by the vmid`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | kyberannotationbyvmid | Table | aplat.westcentralus | APlat | queryFrom, queryTo, queryvmid |

### KyberCoreServiceTrace
Path: `KyberCoreServiceTrace`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | KyberCoreServiceTrace | Table | aplat.westcentralus | Aplat | queryFrom, queryTo, query_ContainerId |

### KyberGHSAnnotationEmissionEvent > Represents the annotations sent from Kyber to Geneva Health
Path: `KyberGHSAnnotationEmissionEvent > Represents the annotations sent from Kyber to Geneva Health`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | KyberGHSAnnotationEmissionEvent | Table | aplat.westcentralus | Aplat | queryFrom, queryTo, containerid |

### KyberVMAHealthSignals
Path: `KyberVMAHealthSignals`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | KyberVMAHealthSignals | Table | aplat.westcentralus | APlat | queryFrom, queryTo, containerId |

### KyberVmAvailabilityMetricEmission > Represents Kyber emitted metric values
Path: `KyberVmAvailabilityMetricEmission > Represents Kyber emitted metric values`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | KyberVmAvailabilityMetricEmission | Table | aplat.westcentralus | Aplat | queryFrom, queryTo, containerId |

### KyberVmAvailabilityMetricEmission by VmId
Path: `KyberVmAvailabilityMetricEmission by VmId`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | KyberVmAvailabilityMetricEmissionByVMID | Table | aplat.westcentralus | APlat | queryFrom, queryTo, queryVmId |

### LogContainerHealthSnapshot
Path: `LogContainerHealthSnapshot`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LogContainerHealthSnapshot_RH_VMId_CM | Table | Azurecm | AzureCM | query_StartTime, query_EndTime, query_VMId |
| 2 | LogContainerHealthSnapshot_ResourceHealth DS | Table | storageclient.eastus | Fc | query_StartTime, query_EndTime, query_ContainerId |

### Node Snapshot Table
Path: `Node Snapshot Table`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LogNodeSnapshot | Table | storageclient.eastus | Fc | query_BeginTime, query_NodeId |

### Node State Changes
Path: `Node State Changes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtNodeStateChangedEtwTable DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_NodeId |

### RdAgentAzPubSubEtwTable > Represents annotations emitted from HostAgent to AzPubSub
Path: `RdAgentAzPubSubEtwTable > Represents annotations emitted from HostAgent to AzPubSub`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RdAgentAzPubSubEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, nodeId, containerId |

### Resource Health Unavailable for Linux 6.2 Kernel
Path: `Resource Health Unavailable for Linux 6.2 Kernel`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RH_Unavailable_Linux_6_2 | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_ContainerId |

### ResourceHealthAnnotationEvent > Represents received annotations from Host/Fabric to GHS
Path: `ResourceHealthAnnotationEvent > Represents received annotations from Host/Fabric to GHS`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ResourceHealthAnnotationEvent DS | Table | icmbrain | AzureResourceHealth | query_StartTime, query_EndTime, query_vmId |

### ResourceHealthAzureActivityLogEvent
Path: `ResourceHealthAzureActivityLogEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ResourceHealthAzureActivityLogEvent | Table | azcore.centralus | Fa | queryFrom, queryTo, query_ContainerId |

### ResourceHealthStatusTransitionEvent > Represents received health reports ( and generating proper health status transitions) from Host to GHS for Virtual Machines
Path: `ResourceHealthStatusTransitionEvent > Represents received health reports ( and generating proper health status transitions) from Host to GHS for Virtual Machines`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ResourceHealthStatusTransitionEvent DS | Table | icmbrain | AzureResourceHealth | query_StartTime, query_EndTime, query_vmId |

### RhcAnnotationReportsEtwTable > Represents emitted annotations from HostAgent
Path: `RhcAnnotationReportsEtwTable > Represents emitted annotations from HostAgent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RhcAnnotationReportsEtwTable DS | Table | azcore.centralus | Fa | query_StartTime, query_EndTime, query_VmId |

### RhcWatchdogReportsErrorEtwTable > Represents errors emitting the watchdog report (calling IfxHealth API)
Path: `RhcWatchdogReportsErrorEtwTable > Represents errors emitting the watchdog report (calling IfxHealth API)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RhcWatchdogReportsErrorEtwTable DS | Table | azcore.centralus | Fa | query_StartTime, query_EndTime, query_ContainerId |

### RoleInstanceDownTimeEvents
Path: `RoleInstanceDownTimeEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RoleInstanceDowntimeEvent | Table | azurecm | AzureCM | queryFrom, queryTo, vmname |

### Scheduled Event Notifications
Path: `Scheduled Event Notifications`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzPEWorkflowEvent | Table | azpe | azpe | startTime, endTime, tenantName, roleInstanceName |

### Tenant Management Events
Path: `Tenant Management Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtTenantEventsEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### VM placement thru time on host node(s)
Path: `VM placement thru time on host node(s)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container History DS | Table | storageclient.eastus | Fc | query_SubscriptionId, query_VMName |

### VMA
Path: `VMA`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMA1 DS | Table | vmainsight | vmadb | query_BeginTime, query_EndTime, query_SubscriptionId, query_VMName |

### VmHealthRawStateEtwTable
Path: `VmHealthRawStateEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VmHealthRawStateEtwTable_ResourceHealth DS | Table | azcore.centralus | Fa | query_StartTime, query_EndTime, query_VMId |

### Windows Events for VM
Path: `Windows Events for VM`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WindowsEventsForVM | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerId |
