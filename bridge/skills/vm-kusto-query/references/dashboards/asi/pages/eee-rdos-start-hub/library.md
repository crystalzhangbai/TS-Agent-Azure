# EEE RDOS — Start Hub: KQL Query Library

> Auto-extracted from ASI EEE RDOS Start Hub page on 2026-05-13T05:18:09.175Z.
> Total: 166 unique KQL queries across 31 panels (172 widget refs).

## Usage

Pass a panel name (or substring) to `eee_replay.py` along with VM placement context (vmid, containerid, nodeid, cluster, tenantname, roleInstanceName) and a time range. The script:
1. Looks up matching panels in `eee-start-hub-queries.json`
2. Substitutes parameters from the placement context (using `paramAliases`)
3. Runs each KQL query against its native cluster via `kusto_runner.py`
4. Returns structured results — no need to read graphs.

## Page inputs (URL params)

- `cluster` — Compute cluster (Tenant) name, e.g. IAD03PrdGPC06
- `containerid` — Container GUID
- `nodeid` — Physical node GUID
- `roleInstanceName` — Role instance name, e.g. _xxx-yyy-001
- `tenantname` — Tenant (NIC tenant) GUID
- `vmid` — Virtual machine unique ID (GUID)
- `globalFrom` — ISO datetime UTC, e.g. 2026-05-07T23:00:00.000Z
- `globalTo` — ISO datetime UTC, e.g. 2026-05-08T01:00:00.000Z

## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Start Hub" | ResourceGet | azcore.centralus | azurecp | globalFrom, globalTo, local_cluster, local_containerid, local_nodeid, local_roleInstanceName, local_tenantname, local_vmid |
| 2 | OverlakeNodeMap | Single | overlakedata.southcentralus | overlake-syslog | queryFrom, queryTo, queryNodeId |
| 3 | GetShoeboxAccount | Single | azurecm | AzureCM | queryFrom, queryTo, queryCluster |

### AI Tool
Path: `AI Tool`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AIPromptGenerator | Single | azcore.centralus | AzureCP | queryFrom, queryTo, queryVmId |

### At-A-Glance Availability > Cluster Health
Path: `At-A-Glance Availability > Cluster Health`  ·  Queries: 5

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Fabricator Instance | Timeline | azurecm | AzureCM | starttime, endtime, cluster |
| 2 | Fabricator Downtime | Timeline | AzureCM | AzureCM | starttime, endtime, cluster |
| 3 | Allocatable State | Timeline | azurecm | AzureCM | starttime, endtime, cluster |
| 4 | Cluster Planned Maintenance | Timeline | azurecm | AzureCM | queryFrom, queryTo, queryClusterName |
| 5 | Cluster Service Healing | Timeline | aplat.westcentralus | Aplat | queryFrom, queryTo, queryClusterName |

### At-A-Glance Availability > Container / Tenant Health
Path: `At-A-Glance Availability > Container / Tenant Health`  ·  Queries: 22

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container State | Timeline | azcore.centralus | AzureCP | starttime, endtime, _vmid, _containerid |
| 2 | Container OS State | Timeline | azcore.centralus | azurecp | starttime, endtime, _vmid, _containerid |
| 3 | Hyper-V Heartbeat State | Timeline | azcore.centralus | Fa | queryStart, queryEnd, queryVmUniqueId, queryContainerId |
| 4 | Hyper-V Power State | Timeline | azcore.centralus | Fa | queryStart, queryEnd, queryVmUniqueId, queryContainerId |
| 5 | VMAvailabilityMetric | Timeline | azurecm | AzureCM | queryFrom, queryTo, queryCluster, queryVmId |
| 6 | Container Lifecycle | Timeline | azcore.centralus | AzureCP | starttime, endtime, _vmid, _containerid |
| 7 | Container Fault | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, queryContainerId, queryVMID |
| 8 | Node Service Error - Container | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerId |
| 9 | VMAL Ops | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryContainerId, queryNodeId |
| 10 | Hyper-V Events | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryContainerId, queryNodeId |
| 11 | Hyper-V StorageStack | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryContainerId, queryNodeId |
| 12 | Tenant Scheduled Events | Timeline | azpe | azpe | queryFrom, queryTo, queryTenantName, queryInstanceName |
| 13 | Anvil Event - Container | Timeline | aplat.westcentralus | APlat | starttime, endtime, _nodeid, _containerid, _tenantname |
| 14 | Container Live Migration | Timeline | storageclient.eastus | Fc | queryFrom, queryTo, vmid, queryContainerId |
| 15 | Service Healing(TM) | Timeline | azcore.centralus | Fc | starttime, endtime, roleInstanceName, tenantName |
| 16 | Service Healing(AzSM) | Timeline | accp.centralus | AZSM | starttime, endtime, queryTenantName, queryContainerId |
| 17 | Planned Maintenance | Timeline | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName, queryRoleInstanceName, queryClusterName |
| 18 | Holmes Events | Timeline | azurecm | AzureCM | queryFrom, queryTo, queryContainerId |
| 19 | RH Annotation Report | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryVMId, queryContainerId |
| 20 | VMA Event | Timeline | vmainsight | vmadb | queryFrom, queryTo, vmid, queryContainerId |
| 21 | AIR Events | Timeline | vmainsight | Air | queryFrom, queryTo, queryVmId |
| 22 | ICM Report | Timeline | icmcluster | IcMDataWarehouse | queryFrom, queryTo, queryContainerId, queryNodeId, queryTenantName, queryCluster |

### At-A-Glance Availability > Container Transition
Path: `At-A-Glance Availability > Container Transition`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ContainerStateTransition | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, queryVmId, queryContainerId |
| 2 | ContainerOSStateTransition | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, queryVmId, queryContainerId |

### At-A-Glance Availability > Container Transition > Extended Error Details (If Any)
Path: `At-A-Glance Availability > Container Transition > Extended Error Details (If Any)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Extended Container Error Details | Table | azurecm | azurecm | qFrom, qTo, qContainer |

### At-A-Glance Availability > CRP Operation
Path: `At-A-Glance Availability > CRP Operation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP Operation Timeline | Timeline | azcrp | crp_allprod | starttime, endtime, vmid, queryInstanceName, querySubId |

### At-A-Glance Availability > Guest Agent & Extension Provisioning
Path: `At-A-Glance Availability > Guest Agent & Extension Provisioning`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GuestAgentAndExtensionTimeline | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryContainerid |

### At-A-Glance Availability > Host Available Memory (MB)
Path: `At-A-Glance Availability > Host Available Memory (MB)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | EEERDOSHostMemoryPerformance | TimeSeries | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### At-A-Glance Availability > Host CPU Utilization (%)
Path: `At-A-Glance Availability > Host CPU Utilization (%)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostCPUPerformance | TimeSeries | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### At-A-Glance Availability > HumanInvestigate Node Count / Hour
Path: `At-A-Glance Availability > HumanInvestigate Node Count / Hour`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeStateHumanInvestigateCount | TimeSeries | azurecm | AzureCM | starttime, endtime, cluster |
| 2 | NodeStateReadyCount | TimeSeries | storageclient.eastus | Fc | starttime, endtime, cluster |

### At-A-Glance Availability > Network Health
Path: `At-A-Glance Availability > Network Health`  ·  Queries: 17

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ToR-Hosts PingMesh | Timeline | aznwsdn | aznwmds | queryFrom, queryTo, nodeid |
| 2 | Host-ToR PingMesh | Timeline | aznwsdn | aznwmds | starttime, endtime, nodeid |
| 3 | ToR Health Event | Timeline | azphynet | azdhmds | queryFrom, queryTo, nodeid |
| 4 | ToR Update | Timeline | azwan | FUSE | queryFrom, queryTo, queryNodeId |
| 5 | ToR - Anvil Event | Timeline | aplat.westcentralus | aplat | queryFrom, queryTo, queryNodeId |
| 6 | Wireserver Heartbeat | Timeline | azcore.centralus | Fa | nodeid, starttime, endtime |
| 7 | NMAgent Health | Timeline | aznwsdn | aznwmds | queryFrom, queryTo, queryContainerId, queryNodeId |
| 8 | NMAgent Event | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |
| 9 | NM Programming | Timeline | aznwsdn | aznwmds | queryFrom, queryTo, queryNodeId, queryContainerId |
| 10 | SoC OS Update | Timeline | azurehn | Azurehn | queryFrom, queryTo, queryNodeId |
| 11 | SoC Pilot Fish State | Timeline | azuredcm | AzureDCMDb | queryFrom, queryTo, queryNodeId |
| 12 | SoC PF Update | Timeline | azcore.centralus | OvlProd | queryFrom, queryTo, queryNodeId, querySocNodeId |
| 13 | SoC Signal Event | Timeline | overlakedata.southcentralus | overlake-syslog | queryFrom, queryTo, queryNodeId |
| 14 | SoC Azure Watson | Timeline | azurewatsoncustomer | AzureWatsonCustomer | queryFrom, queryTo, queryNodeId, querySocNodeId |
| 15 | SoC - Anvil Event | Timeline | aplat.westcentralus | aplat | queryFrom, queryTo, queryNodeId, querySocNodeId |
| 16 | SoC VNetAgent Event | Timeline | azcore.centralus | OvlProd | queryFrom, queryTo, queryContainerId, queryNodeId, querySocNodeId |
| 17 | SoC Systemd Event | Timeline | azcore.centralus | OvlProd | queryFrom, queryTo, queryNodeId, querySocNodeId |

### At-A-Glance Availability > Node Health
Path: `At-A-Glance Availability > Node Health`  ·  Queries: 21

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DCM Node State | Timeline | azuredcm | AzureDCMDb | starttime, endtime, nodeid |
| 2 | DCM Node Fault | Timeline | azuredcm | AzureDCMDb | queryFrom, queryTo, queryNodeId |
| 3 | DCM SEL (Sparkle) | Timeline | sparkle.eastus | defaultdb | queryFrom, queryTo, queryNodeId |
| 4 | DCM SEL | Timeline | azuredcm | AzureDCMDb | queryFrom, queryTo, queryNodeId |
| 5 | Root Update Alloc Type | Timeline | azurecm | AzureCM | queryFrom, queryTo, nodeid |
| 6 | Node State | Timeline | azcore.centralus | AzureCP | starttime, endtime, nodeid |
| 7 | Node Availability | Timeline | azcore.centralus | AzureCP | starttime, endtime, nodeid |
| 8 | Node Fault | Timeline | azcore.centralus | AzureCP | starttime, endtime, nodeid |
| 9 | Node WillBe Channel Health Status | Timeline | azurecm | AzureCM | queryFrom, queryTo, queryNodeId |
| 10 | Node WasChannel Health Status | Timeline | AzureCM | AzureCM | queryFrom, queryTo, queryNodeId |
| 11 | Node Service Error | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |
| 12 | VMAL Error | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |
| 13 | Node Live Migration | Timeline | azcore.centralus | Fc | queryFrom, queryTo, nodeid |
| 14 | Anvil Event - Node | Timeline | aplat.westcentralus | APlat | queryFrom, queryTo, queryNodeId |
| 15 | Kernel/Driver Events | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |
| 16 | Remarkable Event - Disk | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |
| 17 | Remarkable Event - WHEA | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |
| 18 | Remarkable Event - Memory | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |
| 19 | Remarkable Event - HyperV | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |
| 20 | Azure Watson | Timeline | azurewatsoncustomer | AzureWatsonCustomer | queryFrom, queryTo, queryNodeId |
| 21 | Hyper-V State | Timeline | azcore.centralus | fa | queryFrom, queryTo, queryNodeId |

### At-A-Glance Availability > Node Update
Path: `At-A-Glance Availability > Node Update`  ·  Queries: 5

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PF Update | Timeline | azurecm | AzureCM | queryFrom, queryTo, queryNodeId |
| 2 | Host Update | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |
| 3 | CM Node Update | Timeline | azurecm | AzureCM | queryFrom, queryTo, queryNodeId |
| 4 | AzPE Update | Timeline | azpe | azpe | queryFrom, queryTo, queryNodeId |
| 5 | FPGA Update | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |

### At-A-Glance Availability > OutForRepair Node Count / Hour
Path: `At-A-Glance Availability > OutForRepair Node Count / Hour`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeStateOFRCount | TimeSeries | storageclient.eastus | Fc | starttime, endtime, cluster |

### At-A-Glance Availability > Ready Node Count
Path: `At-A-Glance Availability > Ready Node Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeStateReadyCount | TimeSeries | storageclient.eastus | Fc | starttime, endtime, cluster |

### At-A-Glance Availability > Services on Node
Path: `At-A-Glance Availability > Services on Node`  ·  Queries: 8

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node WasChannel Health Status | Timeline | AzureCM | AzureCM | queryFrom, queryTo, queryNodeId |
| 2 | Node WillBe Channel Health Status | Timeline | azurecm | AzureCM | queryFrom, queryTo, queryNodeId |
| 3 | PfAgent Status | Timeline | azuredcm | AzureDCMDb | queryFrom, queryTo, queryNodeId |
| 4 | PilotFish State | Timeline | azuredcm | AzureDCMDb | starttime, endtime, nodeid |
| 5 | ApSvcMgr Status | Timeline | azuredcm | AzureDCMDb | queryFrom, queryTo, queryNodeId |
| 6 | ApLauncher Status | Timeline | azuredcm | AzureDCMDb | queryFrom, queryTo, queryNodeId |
| 7 | Node Service Status | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |
| 8 | WireService Status | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### At-A-Glance Availability > Unhealthy Node Count
Path: `At-A-Glance Availability > Unhealthy Node Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Unhealthy Node Count | TimeSeries | storageclient.eastus | Fc | starttime, endtime, cluster |

### At-A-Glance Performance > Performance Metrics (Node View)
Path: `At-A-Glance Performance > Performance Metrics (Node View)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ContainerPerformance | TimeSeries | azcore.centralus | Fa | starttime, endtime, containerid |

### At-A-Glance Performance > Performance Metrics (Shoebox View)
Path: `At-A-Glance Performance > Performance Metrics (Shoebox View)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Performance Shoebox | TimeSeries | azcore.centralus | Fa | starttime, endtime, nodeid, containerid |

### Automated Detector
Path: `Automated Detector`  ·  Queries: 59

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | IssueDetector_NetworkIssues | IssueDetector | icmcluster | IcmDataWarehouse | queryFrom, queryTo, queryNodeId, queryContainerId, queryRoleInstanceName, queryTenantName, querySubId |
| 2 | IssueDetector_AzSMServiceHealing | IssueDetector | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName, queryContainerId |
| 3 | IssueDetector_TooManyUnhealthyNode | IssueDetector | icmcluster | IcMDataWarehouse | queryFrom, queryTo, queryCluster |
| 4 | IssueDetector_EI_StopDestroy Fails with STORVSP_VspDeviceCreate* | IssueDetector | azurewatsoncustomer | AzureWatsonCustomer | queryFrom, queryTo, NodeId, querySubscription, containerId, roleInstanceName, tenantName, Tenant, virtualMachineUniqueId |
| 5 | IssueDetector_SoC_Crash | IssueDetector | azurewatsoncustomer | AzureWatsonCustomer | queryStart, queryEnd, queryNodeId, queryContainerId, queryCluster, queryRoleInstanceName, queryTenantName, queryVmId |
| 6 | IssueDetector_EI_RHSendsIncorrectVMAvailableStateRepeatedly | IssueDetector | storageclient.eastus | Fc | queryFrom, queryTo, NodeId, querySubscription, Tenant, containerId, roleInstanceName, tenantName, VMId |
| 7 | IssueDetector_EI_DppPluginOrPfDatapathServiceRequired | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, query_NodeId, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 8 | IssueDetector_EI_CreateContainer_fails_with_0x80070002_L-Series | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, querySubscription, roleInstanceName, queryContainerId, queryNodeId, tenantName, virtualMachineUniqueId, Tenant |
| 9 | IssueDetector_EI_CreateContainer_failed_with_0xc3510153 | IssueDetector | azcore.centralus | Fa | startTime, endTime, nodeId, querySubscription, roleInstanceName, queryContainerId, tenantName, virtualMachineUniqueId, Tenant |
| 10 | IssueDetector_EI_VM reboot when trying to detach disks  | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, vmName, virtualMachineID, containerId, nodeId, querySubscription, subId, roleInstanceName, tenantName, virtualMachineUniqueId, Tenant |
| 11 | IssueDetector_EI_EQ stuck_on_EQn_0x4 | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, query_NodeId, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 12 | IssueDetector_EI_AirDiskBlip_BlobCache_Write_during_Congestion | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, query_NodeId, queryroleInstanceName, querySubscription, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 13 | IssueDetector_EI_NV6_v5_VMs_Fail_to_Start_due_to_Low_Memory | IssueDetector | storageclient.eastus | Fc | queryFrom, queryTo, query_NodeId, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 14 | IssueDetector_EI_CRUD operationFailuresDueToContainerWorkflow* | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, querySubscription, Tenant, containerId, NodeID, roleInstanceName, tenantName, virtualMachineUniqueId |
| 15 | IssueDetector_EI_Resource_Health_Unavailable_for_Linux_6.2Kernel | IssueDetector | Vmainsight | CAD | queryFrom, queryTo, query_NodeId, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 16 | IssueDetector_EI_High_Flush_latencies_due_to_driver_issue | IssueDetector | storageclient.eastus | Fa | queryFrom, queryTo, query_NodeId, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant, blobPath, Cloud |
| 17 | IssueDetector_EI_NetAssistMonitorTriggers_LM | IssueDetector | storageclient.eastus | Fc | queryFrom, queryTo, querySubscription, query_NodeId, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 18 | IssueDetector_TORFailures | IssueDetector | azuredcm | AzureDCMDb | queryFrom, queryTo, queryNodeId |
| 19 | IssueDetector_TOR_DegradedUnhealthyEvents | IssueDetector | azphynet | azdhmds | queryFrom, queryTo, nodeid |
| 20 | IssueDetector_SoC_Update | IssueDetector | azcore.centralus | OvlProd | queryFrom, queryTo, querySocNodeId |
| 21 | IssueDetector_EI_HostNetworkIssue_FPGA_GFT_Unhealthy_on_Overlake | IssueDetector | vmainsight | vmadb | queryFrom, queryTo, query_NodeId, querytenantName, querySubscription, queryroleInstanceName, querycontainerId, queryTenant, queryvirtualMachineUniqueId |
| 22 | IssueDetector_EI_LM_failure_VFPRestoreFailure_NmAgentEventDelay | IssueDetector | vmainsight | vmadb | queryFrom, queryTo, queryTenant, queryvirtualMachineUniqueId, query_NodeId, querytenantName, querycontainerId, queryroleInstanceName, querySubscription |
| 23 | IssueDetector_EI_Standard_ND96isr_H100_v5_HardwareFault_pCIfata | IssueDetector | vmainsight | vmadb | queryFrom, queryTo, queryroleInstanceName, querySubscription, querycontainerId, querytenantName, query_NodeId, queryvirtualMachineUniqueId, queryTenant |
| 24 | IssueDetector_EI_Attaching_Multiple_DataDisks_Over_Nvme_restart | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, querySubscription, queryroleInstanceName, queryContainerId, querytenantName, queryNodeId, queryvirtualMachineUniqueId, queryTenant |
| 25 | IssueDetector_EI_OSProvisioningTimedOut_failure_DHCP_lease | IssueDetector | storageclient.eastus | Fc | queryFrom, queryTo, queryContainerId, querySubscription, queryroleInstanceName, querytenantName, query_NodeId, queryvirtualMachineUniqueId, queryTenant |
| 26 | IssueDetector_EI_AKS_Linux_instances_are_reported_as_Windows | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerId, querySubscription, queryroleInstanceName, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 27 | IssueDetector_EI_Dalds_v6_Windows_2025_datadisk_perf | IssueDetector | storageclient.eastus | Fc | queryFrom, queryTo, queryVmid, querySubscription, queryroleInstanceName, queryContainerId, querytenantName, queryNodeId, queryvirtualMachineUniqueId, queryTenant |
| 28 | IssueDetector_EI_LM_VFPRestoreFailure_Deserialization_Issue_Port | IssueDetector | vmainsight | Air | queryFrom, queryTo, querySubscription, queryVMName, querycontainerId, querytenantName, queryNodeId, queryvirtualMachineUniqueId, queryTenant |
| 29 | IssueDetector_NVME_HW_troubleshooting | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 30 | IssueDetector_EI_node_bugcheck_0x50_netdatapath | IssueDetector | overlakedata.southcentralus | overlake-syslog | queryFrom, queryTo, queryNodeId, queryContainerId, querySubscription, queryroleInstanceName, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 31 | IssueDetector_EI_StagingNodeImagesGen9 | IssueDetector | azcore.centralus | Fc | queryFrom, queryTo, queryNodeId, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 32 | IssueDetector_EI_Backplane_service_crash_on_SoC_impacts_VM | IssueDetector | vmainsight | vmadb | queryFrom, queryTo, querycontainerId, querySubscriptionId, queryVMName, querytenantName, query_NodeId, queryvirtualMachineUniqueId, queryTenant |
| 33 | IssueDetector_EI_Node Crash_due_to_0xBC0000D6_BlobCache!BcRefere | IssueDetector | azurewatsoncustomer | AzureWatsonCustomer | queryFrom, queryTo, querySubscription, queryroleInstanceName, queryNodeId, queryContainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 34 | IssueDetector_EI_GPC_VMs_Fail_to_Start_IBManagerError_0x800704c | IssueDetector | storageclient.eastus | Fc | queryFrom, queryTo, queryVmId, queryContainerId, querySubscription, queryroleInstanceName, querytenantName, query_NodeId, queryTenant |
| 35 | IssueDetector_EI_Ultra_PremV2_DiskBlip_during_VDC_driver_update | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, queryContainerId, queryNodeId, querySubscription, queryroleInstanceName, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 36 | IssueDetector_EI_v6VM_TPM_fails_start_due_to_Underhill_VM | IssueDetector | storageclient.eastus | Fc | queryFrom, queryTo, queryVMID, queryContainerId, queryNodeId, querySubscription, queryroleInstanceName, querytenantName, queryTenant |
| 37 | IssueDetector_EI_node bugcheck_0xd1_AV_blobcache!BcPfnReferenc | IssueDetector | vmainsight | vmadb | queryFrom, queryTo, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, query_NodeId, queryvirtualMachineUniqueId, queryTenant |
| 38 | IssueDetector_EI_Unable_to_create_VM_VMAL_error_0x8000ffff | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, query_NodeId, querycontainerId, querySubscription, queryroleInstanceName, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 39 | IssueDetector_TOR_Update | IssueDetector | azphynet | azdhmds | queryFrom, queryTo, querynodeid |
| 40 | IssueDetector_Node_Restart_Due_to_Planned_Maintenance | IssueDetector | vmainsight | vmadb | queryFrom, queryTo, query_SubscriptionId, query_VMName |
| 41 | IssueDetector_EI_UnallocatableNode_DestroyContainer_0x8abc0503 | IssueDetector | aplat.westcentralus | APlat | queryFrom, queryTo, query_NodeId, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 42 | IssueDetector_EI_bugcheck_0xd1_AV_Barbera!HbLldCompleteIrpOve | IssueDetector | vmainsight | vmadb | queryFrom, queryTo, queryvirtualMachineUniqueId, querycontainerId, querySubscription, queryroleInstanceName, querytenantName, query_NodeId, queryTenant |
| 43 | IssueDetector_EI_Unallocatable_Node_due_to_XDisk_leaks | IssueDetector | storageclient.eastus | Fc | queryFrom, queryNodeId, queryContainerId, querySubscription, queryroleInstanceName, querytenantName, queryvirtualMachineUniqueId, queryTenant, queryTo |
| 44 | IssueDetector_EI_Local_NVMe_Disks_Are_Missing_In_Lv4_Series | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerId, querySubscription, queryroleInstanceName, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 45 | IssueDetector_EI_LM_SH_due_to_NVMe_Device_End_of_Life | IssueDetector | storageclient.eastus | Fc | queryFrom, queryTo, queryNodeId, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 46 | IssueDetector_EI_LMFailed_FlexibleIODeviceRestore | IssueDetector | vmainsight | vmadb | queryFrom, queryTo, querySubscription, queryroleInstanceName, queryContainerId, querytenantName, queryNodeId, queryvirtualMachineUniqueId, queryTenant |
| 47 | IssueDetector_EI_NetworkContainer_AllocationIncarnation | IssueDetector | azureallocator.westcentralus | AzureAllocator | queryFrom, queryTo, querycontainerId, querySubscription, queryroleInstanceName, querytenantName, query_NodeId, queryvirtualMachineUniqueId, queryTenant |
| 48 | IssueDetector_EI_LMFailed_VFPSerializationIssue_0x5aa | IssueDetector | vmainsight | vmadb | queryFrom, queryTo, querySubscription, queryroleInstanceName, queryContainerId, querytenantName, queryNodeId, queryvirtualMachineUniqueId, queryTenant |
| 49 | IssueDetector_EI_NVMeVmHighDiskLatency_due_to_CacheHint | IssueDetector | storageclient.eastus | SharedWorkspace | startTime, endTime, query_NodeId, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant, querySubscription, queryroleInstanceName |
| 50 | IssueDetector_Sudden_Power_Loss_of_host_node | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, _nodeId |
| 51 | IssueDetector_Booting_of_host_node_detected | IssueDetector | storageclient.eastus | Fc | queryFrom, queryTo, _nodeId |
| 52 | IssueDetector_HighHostCPU_temp_throttle | IssueDetector | sparkle.eastus | defaultdb | queryFrom, queryTo, query_NodeId |
| 53 | IssueDetector_HighHostCPU_throttle | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, _nodeId |
| 54 | IssueDetector_EI_NVMe_Controller_VM_experience_stornvme_reset | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, query_NodeId, queryvirtualMachineUniqueId, querytenantName, querycontainerId, queryroleInstanceName, querySubscription, queryTenant |
| 55 | IssueDetector_EI_VMA_bugcheck_0x20001_HYPERVISOR_ERROR | IssueDetector | vmainsight | vmadb | queryFrom, queryTo, queryvirtualMachineUniqueId, queryContainerId, querySubscription, queryroleInstanceName, querytenantName, queryNodeId, queryTenant |
| 56 | IssueDetector_EI_AW_bugcheck_0x20001_HYPERVISOR_ERROR | IssueDetector | azurewatsoncustomer | AzureWatsonCustomer | queryFrom, queryTo, querySubscription, queryNodeId, queryroleInstanceName, queryContainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 57 | IssueDetector_EI_LMFailed_VFPSerializationIssue_0x5aa_2 | IssueDetector | vmainsight | Air | queryFrom, queryTo, queryContainerId, queryvirtualMachineUniqueId, querySubscription, queryroleInstanceName, querytenantName, queryNodeId, queryTenant |
| 58 | IssueDetector_EI_VM_creation_failure_0xc3510224_VMAL_ASAPPF | IssueDetector | azcore.centralus | Fc | queryFrom, queryTo, queryNodeId, querySubscription, queryroleInstanceName, queryContainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant |
| 59 | IssueDetector_E17_Key_Vault_Encryption_Key_not_found | IssueDetector | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_containerid, query_nodeid |

### General Tool Links
Path: `General Tool Links`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | JarvisDashTimeHelper | Single | azurecm | azurecm | queryFrom, queryTo |
| 2 | VmssIdHelper | Single | azurecm | azurecm | queryFrom, queryTo, queryContainerProperties |
| 3 | Unix Time Helper | Single | azurecm | AzureCM | queryFrom, queryTo |

### Network / TOR
Path: `Network / TOR`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TorDeviceInfo | Single | azphynet | azdhmds | queryFrom, queryTo, nodeid |
| 2 | Unix Time Helper | Single | azurecm | AzureCM | queryFrom, queryTo |
| 3 | vfpMDM | Single | azurehn | azurehn | queryCluster |

### Node (Physical)
Path: `Node (Physical)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Hardware Properties | Single | azuredcm | AzureDCMDb | starttime, endtime, nodeid |

### Overlake / SoC
Path: `Overlake / SoC`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OverlakeNodeMap | Single | azcore.centralus | OvlProd | queryFrom, queryTo, queryNodeId |

### Tenant / Container / Node
Path: `Tenant / Container / Node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Features | FeatureList | azurecm | azurecm | queryFrom, queryTo, queryContainer |

### VM
Path: `VM`  ·  Queries: 4

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PageInputHelper | Single | azurecm | AzureCM | queryFrom, queryTo, queryCluster, queryContainerId, queryNodeId, queryRoleInstanceName, queryTenantName, queryVmId, queryRegion, queryContainerType, queryContainerProperties |
| 2 | GetARMResourceId | Single | azcrpbifollower | bi_allprod | queryFrom, queryTo, querySubId, queryVMId, queryRoleInstanceName, queryProperties |
| 3 | GetShoeboxAccount | Single | azurecm | AzureCM | queryFrom, queryTo, queryCluster |
| 4 | VmssIdHelper | Single | azurecm | azurecm | queryFrom, queryTo, queryContainerProperties |

### VM > Attached Disks
Path: `VM > Attached Disks`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Blobs | Table | storageclient.eastus | SharedWorkspace | startTime, endTime, containerId, cluster, nodeId, vmId |

### VM > Billing
Path: `VM > Billing`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Compute Hour Usage Table | TimeSeries | azcore.centralus | Fa | queryFrom, queryTo, queryVMId, queryContainerId |

### VM > Container Policy > Container Definition
Path: `VM > Container Policy > Container Definition`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ContainerPolicyQuery | Single | azurevmcentral.westus2 | azurevmcentral | queryFrom, queryTo, queryPolicyName |

### VM > VM CRP Entry > VM Entry
Path: `VM > VM CRP Entry > VM Entry`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP VM Snapshot | Single | azcrpbifollower | bi_allprod | queryFrom, queryTo, vmid, queryRoleInstanceName |
