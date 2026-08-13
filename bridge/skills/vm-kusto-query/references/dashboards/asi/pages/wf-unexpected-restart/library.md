# EEE RDOS — WF Unexpected Restart: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T07:39:36.520Z.
> Total: 204 unique KQL queries across 185 panels (208 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 15

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM stop check | IssueDetector | azcore.centralus | Fc | queryFrom, queryTo, queryNodeId, queryContainerId |
| 2 | VM shutdown check | IssueDetector | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId, queryContainerId |
| 3 | VM guest OS shutdown | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, query_NodeId, queryContainerId |
| 4 | Sudden power loss logged | IssueDetector | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |
| 5 | Power Supply input lost | IssueDetector | sparkle.eastus | defaultdb | query_BeginTime, query_EndTime, query_NodeId |
| 6 | VmStart_failed_Host_LowMem | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |
| 7 | Container Info_UnexpectedRestart DS | Single | azcore.centralus | AzureCP | query_BeginTime, query_EndTime, query_ContainerId |
| 8 | Retrieve Resource "VM" Unexpected Restart DS | ResourceGet | azcore.centralus | Fa | local_ContainerId, local_NodeId, local_TenantName, local_vmId |
| 9 | vfpMDM | Single | azurehn | azurehn | queryCluster |
| 10 | TimeCalcFrom | Single | azcore.centralus | Fc | queryFrom |
| 11 | TimeCalcTo | Single | azcore.centralus | Fc | queryTo |
| 12 | Unix Time Helper | Single | azcore.centralus | Fc | queryFrom, queryTo |
| 13 | LM check | IssueDetector | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_ContainerId |
| 14 | SOCNodeId | Single | overlakedata.southcentralus | overlake-syslog | queryFrom, queryTo, queryNodeId |
| 15 | OverlakeNodeMap | Single | azcore.centralus | OvlProd | queryFrom, queryTo, queryNodeId |

### Container Investigation > CAD > CAD events
Path: `Container Investigation > CAD > CAD events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CAD_UnexpectedRestart DS | Table | vmainsight | CAD | query_BeginTime, query_EndTime, query_ContainerId |

### Container Investigation > Container Health > Container health state investigation
Path: `Container Investigation > Container Health > Container health state investigation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LogContainerHealthSnapshot_UnexpectedRestart DS | Table | azcore.centralus | AzureCP | query_ContainerId, query_BeginTime, query_EndTime |

### Container Investigation > Container History > VM placement thru time on host node(s)
Path: `Container Investigation > Container History > VM placement thru time on host node(s)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LogContainerSnapshot_UnexpectedRestart DS | Table | azcore.centralus | AzureCP | query_SubscriptionId, query_VMName |

### Container Investigation > ContainerTrace > Container trace events
Path: `Container Investigation > ContainerTrace > Container trace events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtContainerTraceEtwTable DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_ContainerId |

### Container Investigation > Guest Agent Logs > Guest Agent logs
Path: `Container Investigation > Guest Agent Logs > Guest Agent logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GuestAgentLogs DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_ContainerId |

### Container Investigation > Guest OS Details > Guest OS Details
Path: `Container Investigation > Guest OS Details > Guest OS Details`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GuestOSDetails DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_ContainerId |

### Container Investigation > SLA Table > SLA Table for Container
Path: `Container Investigation > SLA Table > SLA Table for Container`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtSlaMeasurementEventEtwTable_UnexpectedRestart2 DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_ContainerId |

### Container Investigation > TenantChangeProfiling > TMMgmtTenantChangeProfilingEventEtwTable
Path: `Container Investigation > TenantChangeProfiling > TMMgmtTenantChangeProfilingEventEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtTenantChangeProfilingEventEtwTable | Table | azcore.centralus | Fc | queryFrom, queryTo, queryContainerId |

### Container Investigation > TenantEvents > Tenant events investigation
Path: `Container Investigation > TenantEvents > Tenant events investigation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtTenantEventsEtwTable DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_TenantName |

### Container Investigation > VM Restart Events > VM Restart Events
Path: `Container Investigation > VM Restart Events > VM Restart Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GetVMRestartEvents DS | Table | moseisley | Air | query_BeginTime, query_EndTime, query_vmId |

### Container Investigation > VMA > VM Availability analysis
Path: `Container Investigation > VMA > VM Availability analysis`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMA5 DS | Table | vmainsight | vmadb | _startDateTime, _endDateTime, _vmid, _containerId |

### Container Investigation > VMHealthState > VM health state investigation
Path: `Container Investigation > VMHealthState > VM health state investigation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VmHealthRawStateEtwTable_UnexpectedRestart DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_ContainerId |

### Container Investigation > VmServiceContainerOperations
Path: `Container Investigation > VmServiceContainerOperations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VmServiceContainerOperations | Table | azcore.centralus | Fa | queryFrom, queryTo, queryContainerId |

### Emerging Issues >  Resource Health Sends Incorrect VM Availability state repeatedly
Path: `Emerging Issues >  Resource Health Sends Incorrect VM Availability state repeatedly`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 |  RH Sends Incorrect VM Availability state repeatedly | Table | storageclient.eastus | Fc | queryFrom, queryTo, VMId |

### Emerging Issues > "EQ stuck" on EQn 0x4 > "EQ stuck" on EQn 0x4
Path: `Emerging Issues > "EQ stuck" on EQn 0x4 > "EQ stuck" on EQn 0x4`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | "EQ stuck" on EQn 0x4 DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Emerging Issues > AirDiskBlip BlobCache Write during Congestion > HyperVStorageStack and BlobcacheInternal
Path: `Emerging Issues > AirDiskBlip BlobCache Write during Congestion > HyperVStorageStack and BlobcacheInternal`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVStorageStackAndBlobcacheInternal_EE | Table | azcore.centralus | Fa | startTime, endTime, nodeId, containerId |

### Emerging Issues > AKS Linux instances are reported as running Windows
Path: `Emerging Issues > AKS Linux instances are reported as running Windows`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AKS_Linux_instances_are_reported_as_Windows | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerId |

### Emerging Issues > Attaching Multiple Data Disks Over Nvme may lead to VM Restart
Path: `Emerging Issues > Attaching Multiple Data Disks Over Nvme may lead to VM Restart`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Attaching_Multiple_DataDisks_Over_Nvme_may_lead_to_VM_Restart | Table | azcore.centralus | Fa | queryFrom, queryTo, queryContainerId, queryNodeId |

### Emerging Issues > Backplane service crash on SoC impacts VM accessibility
Path: `Emerging Issues > Backplane service crash on SoC impacts VM accessibility`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SoC_impacts_VM_accessibility | Table | vmainsight | vmadb | queryFrom, queryTo, querySubscriptionId, queryVMName |

### Emerging Issues > ContainerWorkflow is blocked due to DppPluginOrPfDatapathServiceRequired
Path: `Emerging Issues > ContainerWorkflow is blocked due to DppPluginOrPfDatapathServiceRequired`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DppPluginOrPfDatapathServiceRequired | Table | azcore.centralus | Fa | queryFrom, queryTo, query_NodeId |

### Emerging Issues > CreateContainer failed with 0xc3510153
Path: `Emerging Issues > CreateContainer failed with 0xc3510153`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CreateContainer_failed_with_0xc3510153 | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Emerging Issues > CreateContainer fails with "0x80070002 HRESULT_FROM_WIN32(ERROR_FILE_NOT_FOUND)" on L-Series VMs
Path: `Emerging Issues > CreateContainer fails with "0x80070002 HRESULT_FROM_WIN32(ERROR_FILE_NOT_FOUND)" on L-Series VMs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CreateContainer fails with 0x80070002 ERROR_FILE_NOT_FOUND | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerId |

### Emerging Issues > CRUD operation failures due to container workflow blocker "MissingStorageConfigurationsWillbe"
Path: `Emerging Issues > CRUD operation failures due to container workflow blocker "MissingStorageConfigurationsWillbe"`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRUDoperationFailuresDueTo"MissingStorageConfigurationsWillbe" | Table | azcore.centralus | Fa | queryFrom, queryTo, NodeID |

### Emerging Issues > Dalds_v6: Windows 2025 Azure edition Sluggish after adding data disk > Basic Check
Path: `Emerging Issues > Dalds_v6: Windows 2025 Azure edition Sluggish after adding data disk > Basic Check`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Dalds_v6_Windows_2025_datadisk_perf  | Table | storageclient.eastus | Fc | queryFrom, queryTo, queryvmid |

### Emerging Issues > Dalds_v6: Windows 2025 Azure edition Sluggish after adding data disk > Details Check
Path: `Emerging Issues > Dalds_v6: Windows 2025 Azure edition Sluggish after adding data disk > Details Check`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ASAP_completed_IOs | Table | storageclient.eastus | Fa | queryFrom, queryTo, queryNodeId |

### Emerging Issues > GPC VMs Fail to Start: IBManagerError 0x800704cd
Path: `Emerging Issues > GPC VMs Fail to Start: IBManagerError 0x800704cd`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GPC_VMs_Fail_to_Start_IBManagerError_0x800704cd | Table | storageclient.eastus | Fc | queryFrom, queryTo, queryContainerId, queryVmId |

### Emerging Issues > High Flush latencies due to driver issue
Path: `Emerging Issues > High Flush latencies due to driver issue`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HighFlushLatenciesDueToDriverIssue | Table | storageclient.eastus | Fa | queryFrom, queryTo, query_NodeId, querySubscription, queryroleInstanceName, querycontainerId, querytenantName, queryvirtualMachineUniqueId, queryTenant, blobPath, Cloud |

### Emerging Issues > HostNetworkIssue_FPGA_GFT_Unhealthy on Overlake Nodes
Path: `Emerging Issues > HostNetworkIssue_FPGA_GFT_Unhealthy on Overlake Nodes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostNetworkIssue_FPGA_GFT_Unhealthy | Table | Vmainsight | vmadb | queryFrom, queryTo, querynodeid |

### Emerging Issues > Impact of Staging Node Images download on Gen9.0 host
Path: `Emerging Issues > Impact of Staging Node Images download on Gen9.0 host`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | stagingnodeimagesGen9 | Table | azcore.centralus | Fc | queryFrom, queryTo, queryNodeId |

### Emerging Issues > LiveMigrationFailed due to Flexible IO Device Restore Failure
Path: `Emerging Issues > LiveMigrationFailed due to Flexible IO Device Restore Failure`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LMFailed_FlexibleIODeviceRestoreFailure | Table | vmainsight | vmadb | query_BeginTime, query_EndTime, query_SubscriptionId, query_VMName |

### Emerging Issues > LM / SH due to NVMe Device End of Life
Path: `Emerging Issues > LM / SH due to NVMe Device End of Life`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LMSHduetoNVMeDeviceEndofLife | Table | storageclient.eastus | Fc | queryFrom, queryTo, queryNodeId |

### Emerging Issues > LM failure - VFPRestoreFailure_Serialization_Issue_0x5aa > LM failure check
Path: `Emerging Issues > LM failure - VFPRestoreFailure_Serialization_Issue_0x5aa > LM failure check`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LMfailure_VFPRestoreFailure_Serialization_Issue_0x5aa_2 | Table | vmainsight | Air | queryStartTime, queryEndTime, queryContainerId, queryVMId |

### Emerging Issues > LM failure - VFPRestoreFailure_Serialization_Issue_0x5aa > VMA check
Path: `Emerging Issues > LM failure - VFPRestoreFailure_Serialization_Issue_0x5aa > VMA check`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LMfailure_VFPRestoreFailure_Serialization_Issue_0x5aa | Table | vmainsight | vmadb | queryFrom, queryTo, querySubscription, queryroleInstanceName |

### Emerging Issues > LM failure due to VFPRestoreFailure_Deserialization_Issue_Port_0x51a
Path: `Emerging Issues > LM failure due to VFPRestoreFailure_Deserialization_Issue_Port_0x51a`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VFPRestoreFailure_Deserialization_Issue_Port_0x51a | Table | vmainsight | Air | queryFrom, queryTo, queryVMName, queryNodeId |

### Emerging Issues > LM failure due to VFPRestoreFailure_NmAgentEventDelay
Path: `Emerging Issues > LM failure due to VFPRestoreFailure_NmAgentEventDelay`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LM_failure_due_to_VFPRestoreFailure_NmAgentEventDelay | Table | Vmainsight | vmadb | query_BeginTime, query_EndTime, query_SubscriptionId, query_VMName |

### Emerging Issues > Local NVMe disks are missing in Lv4 series
Path: `Emerging Issues > Local NVMe disks are missing in Lv4 series`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LocalNVMeDisksAreMissingInLv4series | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerId |

### Emerging Issues > Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR > AzureWatson Check
Path: `Emerging Issues > Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR > AzureWatson Check`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | IssueDetector_EI_AW_Check_0x20001_HYPERVISOR_ERROR | Table | azurewatsoncustomer | AzureWatsonCustomer | query_BeginTime, query_EndTime, query_NodeId |

### Emerging Issues > Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR > VMA Check
Path: `Emerging Issues > Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR > VMA Check`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | IssueDetector_EI_VMA_Check_Multiple_host_nodes_crashed_with_0x20 | Table | https://vmainsight | vmadb | queryFrom, queryTo, _vmid, _containerId |

### Emerging Issues > NetAssist Monitor triggers Node Fault UnhealthyLinkWithLowSeverity leading to excessive LM
Path: `Emerging Issues > NetAssist Monitor triggers Node Fault UnhealthyLinkWithLowSeverity leading to excessive LM`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NetAssist_LM | Table | storageclient.eastus | Fc | queryFrom, queryTo, query_NodeId |

### Emerging Issues > Node bugcheck 0x50 (PAGE_FAULT_IN_NONPAGED_AREA) in netdatapathagent_1908_app_model_5_0_5_12_v_5_0_0_441
Path: `Emerging Issues > Node bugcheck 0x50 (PAGE_FAULT_IN_NONPAGED_AREA) in netdatapathagent_1908_app_model_5_0_5_12_v_5_0_0_441`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | nodebugcheck_after_netdatapathupdate | Table | overlakedata.southcentralus | overlake-syslog | queryFrom, queryTo, queryNodeId, queryContainerId |

### Emerging Issues > Node Crash due to 0xBC0000D6_BlobCache!BcReferenceTailPfnList
Path: `Emerging Issues > Node Crash due to 0xBC0000D6_BlobCache!BcReferenceTailPfnList`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeCrash_0xBC0000D6_BlobCache!BcReferenceTailPfnList | Table | azurewatsoncustomer | AzureWatsonCustomer | queryFrom, queryTo, queryNodeId |

### Emerging Issues > NV6 v5 VMs Fail to Start due to Low Memory
Path: `Emerging Issues > NV6 v5 VMs Fail to Start due to Low Memory`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NV6_v5_VMs_Fail_to_Start_due_to_Low_Memory | Table | storageclient.eastus | Fc | queryFrom, queryTo, query_NodeId, querycontainerId |

### Emerging Issues > NVMe controller VM experience stornvme reset or bugcheck due to IOTimeoutValue too short > WindowsEventTable
Path: `Emerging Issues > NVMe controller VM experience stornvme reset or bugcheck due to IOTimeoutValue too short > WindowsEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NVMeControllerVMexperienceStornvmeResetOrBugcheck | Table | azcore.centralus | Fa | _startDateTime, _endDateTime, _nodeId |

### Emerging Issues > NVMe VM high disk latency due to Cache Hint Noisy Neighbor
Path: `Emerging Issues > NVMe VM high disk latency due to Cache Hint Noisy Neighbor`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NVMeVMhighdisklatency_dueto_CacheHintNoisyNeighbor | Table | storageclient.eastus | SharedWorkspace | startTime, endTime, containerId, nodeId |

### Emerging Issues > OSProvisioningTimedOut due to failure to obtain DHCP lease with Vnet encryption enabled
Path: `Emerging Issues > OSProvisioningTimedOut due to failure to obtain DHCP lease with Vnet encryption enabled`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OSProvisioningTimedOut_DHCP_VNET_encryption_enabled | Table | storageclient.eastus | Fc | queryFrom, queryTo, queryContainerId |

### Emerging Issues > Resource Health Unavailable for Linux 6.2 Kernel
Path: `Emerging Issues > Resource Health Unavailable for Linux 6.2 Kernel`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RH_Unavailable_Linux_6_2 | Table | Vmainsight | CAD | query_BeginTime, query_EndTime, query_ContainerId |

### Emerging Issues > Staging Node Images
Path: `Emerging Issues > Staging Node Images`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | StagingNodeImages | Table | azcore.centralus | Fc | query_BeginTime, query_NodeId |

### Emerging Issues > Standard_ND96isr_H100_v5_HardwareFault_pCIfata
Path: `Emerging Issues > Standard_ND96isr_H100_v5_HardwareFault_pCIfata`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Standard_ND96isr_H100_v5_HardwareFault_pCIfata | Table | vmainsight | vmadb | queryFrom, queryTo, queryRoleInstanceName |

### Emerging Issues > StopDestroy Fails with STORVSP_VspDeviceCreate_ParserOverride_Avhdparser
Path: `Emerging Issues > StopDestroy Fails with STORVSP_VspDeviceCreate_ParserOverride_Avhdparser`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | StopDestroy:STORVSP_VspDeviceCreate_ParserOverride_Avhdparser | Table | azurewatsoncustomer | AzureWatsonCustomer | queryFrom, queryTo, NodeId |

### Emerging Issues > Ultra / Premium SSDv2 Disk Blip during VDC driver update
Path: `Emerging Issues > Ultra / Premium SSDv2 Disk Blip during VDC driver update`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Ultra_PremV2_DiskBlip_during_VDC_driver_update | Table | azcore.centralus | Fa | startTime, endTime, nodeId, containerId |

### Emerging Issues > Unable to create a VM with a VMAL error 0x8000ffff
Path: `Emerging Issues > Unable to create a VM with a VMAL error 0x8000ffff`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMAL_error_0x8000ffff | Table | azcore.centralus | Fa | queryFrom, queryTo, query_NodeId, query_ContainerId |

### Emerging Issues > Unallocatable Node due to "XDisk leaks. Datapath from Azure Host Storage cannot update."
Path: `Emerging Issues > Unallocatable Node due to "XDisk leaks. Datapath from Azure Host Storage cannot update."`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | UnallocatableNode_XDiskleaks | Table | storageclient.eastus | Fc | queryFrom, queryNodeId |

### Emerging Issues > UnallocatableNode due to DestroyContainer workflow stuck with 0x8abc0503 (E_DELETETHROTTLE)
Path: `Emerging Issues > UnallocatableNode due to DestroyContainer workflow stuck with 0x8abc0503 (E_DELETETHROTTLE)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | UnallocatableNode_DestroyContainer_0x8abc0503 | Table | aplat.westcentralus | APlat | queryFrom, queryTo, queryNodeid |

### Emerging Issues > Unexpected Reboot due to node bugcheck 0xd1 - AV_Barbera!HbLldCompleteIrpOverlay
Path: `Emerging Issues > Unexpected Reboot due to node bugcheck 0xd1 - AV_Barbera!HbLldCompleteIrpOverlay`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | bugcheck_0xd1_AV_Barbera!HbLldCompleteIrpOverlay | Table | vmainsight | vmadb | queryFrom, queryTo, queryvmid, queryContainerId |

### Emerging Issues > Unexpected Reboot due to node bugcheck 0xd1 - AV_blobcache!BcPfnReferenceByCacheStorePfnAndIndex
Path: `Emerging Issues > Unexpected Reboot due to node bugcheck 0xd1 - AV_blobcache!BcPfnReferenceByCacheStorePfnAndIndex`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | node_bugcheck_0xd1_AV_blobcache!BcPfnReferenceByCacheStorePfnA | Table | vmainsight | vmadb | queryFrom, queryTo, query_SubscriptionId, query_VMName |

### Emerging Issues > Unexpected Restart of VMs when PATCH/PUT operation is triggered to VMs
Path: `Emerging Issues > Unexpected Restart of VMs when PATCH/PUT operation is triggered to VMs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | EI_NetworkContainerAllocationIncarnation | Table | azureallocator.westcentralus | AzureAllocator | queryFrom, queryTo, query_ContainerId |

### Emerging Issues > v6 VM using TPM fails to start due to Underhill VM initialization failure
Path: `Emerging Issues > v6 VM using TPM fails to start due to Underhill VM initialization failure`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | v6VM_TPM_fails_start_due_to_Underhill_VM_initialization | Table | storageclient.eastus | Fc | queryFrom, queryTo, queryNodeId, queryContainerId, queryVMID |

### Emerging Issues > VM creation failure due to 0xc3510224 VMAL_ASAPPF_NOT_RUNNING
Path: `Emerging Issues > VM creation failure due to 0xc3510224 VMAL_ASAPPF_NOT_RUNNING`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM_creation_failure_0xc3510224_VMAL_ASAPPF_NOT_RUNNING | Table | azcore.centralus | Fc | queryFrom, queryTo, querynodeId |

### Emerging Issues > VM Impacted after Host Agent Update > Check LogContainerHealthSnapshot
Path: `Emerging Issues > VM Impacted after Host Agent Update > Check LogContainerHealthSnapshot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LogContainerHealthSnapshot | Table | storageclient.eastus | Fc | queryFrom, queryTo, queryContainerId |

### Emerging Issues > VM Impacted after Host Agent Update > Check TMMgmtNodeEventsEtwTable > TMMgmtNodeEventsEtwTable
Path: `Emerging Issues > VM Impacted after Host Agent Update > Check TMMgmtNodeEventsEtwTable > TMMgmtNodeEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtNodeEventsEtwTable_UnexpectedRestart DS | Table | azcore.centralus | Fc | query_StartTime, query_EndTime, query_NodeId |

### Emerging Issues > VM Impacted after Host Agent Update > Check VMA > VMA
Path: `Emerging Issues > VM Impacted after Host Agent Update > Check VMA > VMA`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMA2 DS | Table | Vmainsight | vmadb | query_StartTime, query_EndTime, query_NodeId |

### Emerging Issues > VM Metric Drops due to HyperVStorageStack Overlogging > HyperVStorageStackTable_all
Path: `Emerging Issues > VM Metric Drops due to HyperVStorageStack Overlogging > HyperVStorageStackTable_all`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVStorageStackTable_all DS | Table | azcore.centralus | Fa | query_startTime, query_endTime, query_node |

### Emerging Issues > VM Metric Drops due to HyperVStorageStack Overlogging > HyperVStorageStackTable_vhdmp
Path: `Emerging Issues > VM Metric Drops due to HyperVStorageStack Overlogging > HyperVStorageStackTable_vhdmp`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVStorageStackTable_vhdmp DS | Table | azcore.centralus | Fa | query_startTime, query_endTime, query_node |

### Emerging Issues > VM Metric Drops due to HyperVStorageStack Overlogging > HyperVStorageStackTable_writeError
Path: `Emerging Issues > VM Metric Drops due to HyperVStorageStack Overlogging > HyperVStorageStackTable_writeError`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVStorageStackTable_writeError DS | Table | azcore.centralus | Fa | query_startTime, query_endTime, query_node |

### Emerging Issues > VM reboot when trying to detach disks (UpdateContainer failure 0x80070961)
Path: `Emerging Issues > VM reboot when trying to detach disks (UpdateContainer failure 0x80070961)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM reboot when trying to detach disks | Table | azcore.centralus | Fa | startTime, endTime, query_NodeId, query_ContainerId |

### Emerging Issues > VM Restarts after Internal Shutdown > Check CAD > CAD
Path: `Emerging Issues > VM Restarts after Internal Shutdown > Check CAD > CAD`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CAD_StandardStorage DS | Table | vmainsight | CAD | query_BeginTime, query_EndTime, query_ContainerId |

### Emerging Issues > VM Restarts after Internal Shutdown > Check WindowsEventTable > WindowsEventTable
Path: `Emerging Issues > VM Restarts after Internal Shutdown > Check WindowsEventTable > WindowsEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WindowsEvents_Internalrestart DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId, query_ContainerId |

### Hardware Investigation > Cluster Investigation > Fault Descriptions
Path: `Hardware Investigation > Cluster Investigation > Fault Descriptions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FaultDescriptions | Table | Azuredcm | AzureDCMDb | queryCluster |

### Hardware Investigation > Cluster Investigation > Number of Hosts in Cluster
Path: `Hardware Investigation > Cluster Investigation > Number of Hosts in Cluster`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NumbHostsCluster | Table | Azuredcm | AzureDCMDb | queryCluster |

### Hardware Investigation > Cluster Investigation > Number of Hosts in Cluster not in Production
Path: `Hardware Investigation > Cluster Investigation > Number of Hosts in Cluster not in Production`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NumbHostsClusterNotProd | Table | Azuredcm | AzureDCMDb | queryCluster |

### Hardware Investigation > DCM HW Events > DCM HW Events
Path: `Hardware Investigation > DCM HW Events > DCM HW Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DCM HW Events DS | Table | azuredcm | AzureDCMDb | query_BeginTime, query_EndTime, query_NodeId |

### Hardware Investigation > DCM Repair Events 1 > DCM Repair Events 1
Path: `Hardware Investigation > DCM Repair Events 1 > DCM Repair Events 1`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HW Repair Events DS | Table | azuredcm | AzureDCMDb | query_NodeId, query_StartTime |

### Hardware Investigation > DCM Repair Events 2 > DCM Repair Events 2
Path: `Hardware Investigation > DCM Repair Events 2 > DCM Repair Events 2`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ResourceSnapshotHistoryV1_Unfiltered DS | Table | Azuredcm | AzureDCMDb | query_StartTime, query_NodeId |

### Hardware Investigation > HW Memory Errors
Path: `Hardware Investigation > HW Memory Errors`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | BladeMemoryCorrectedFull | Table | sparkle.eastus | defaultdb | query_BeginTime, query_EndTime, query_NodeId |

### Hardware Investigation > NVME HW Troubleshooting > NVME controller failures due HW issues
Path: `Hardware Investigation > NVME HW Troubleshooting > NVME controller failures due HW issues`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NVMEHWissues | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Hardware Investigation > NVME HW Troubleshooting > NVME DevRCA
Path: `Hardware Investigation > NVME HW Troubleshooting > NVME DevRCA`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NVMEDevRCA | Table | sparkle.eastus | defaultdb | queryFrom, queryTo, queryNodeId |

### Hardware Investigation > NVME HW Troubleshooting > NVMeHealthLog
Path: `Hardware Investigation > NVME HW Troubleshooting > NVMeHealthLog`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NVMeHealthLog | Table | sparkle.eastus | defaultdb | queryFrom, queryTo, querynodeId |

### Hardware Investigation > RhwChassisSelItemEtwTable > RhwChassisSelItemEtwTable
Path: `Hardware Investigation > RhwChassisSelItemEtwTable > RhwChassisSelItemEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RhwChassisSelItemEtwTable DS | Table | azuredcm | AzureDCMDb | query_BeginTime, query_EndTime, query_NodeId |

### Hardware Investigation > SEL > SEL logs
Path: `Hardware Investigation > SEL > SEL logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SparkleSEL DS | Table | sparkle.eastus | defaultdb | query_BeginTime, query_EndTime, query_NodeId |

### Hardware Investigation > SEL filtered > SEL filtered
Path: `Hardware Investigation > SEL filtered > SEL filtered`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SEL filtered DS | Table | sparkle.eastus | defaultdb | query_BeginTime, query_EndTime, query_NodeId |

### Hardware Investigation > WHEA > WHEA
Path: `Hardware Investigation > WHEA > WHEA`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Whea DS | Table | sparkle.eastus | defaultdb | query_BeginTime, query_EndTime, query_NodeId |

### Hardware Investigation > WindowsEventsHW > WindowsEventsHW
Path: `Hardware Investigation > WindowsEventsHW > WindowsEventsHW`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WindowsEventsFilteredHW DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Hardware Investigation > WindowsStorageEvents
Path: `Hardware Investigation > WindowsStorageEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WindowsStorageEvents | Table | sparkle.eastus | defaultdb | queryFrom, queryTo, queryNodeId |

### Live Migration > AirLiveMigrationEvents
Path: `Live Migration > AirLiveMigrationEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AirLiveMigrationEventsL30d | Table | vmainsight | Air | querySubscriptionid, queryVMName |

### Live Migration > Check LM Disabled for Sub
Path: `Live Migration > Check LM Disabled for Sub`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HolmesSubscriptionMetadataEvents | Table | azurecm | azurecm | queryFrom, queryTo, query_sub |

### Live Migration > Holmes Events > Especial case: Triggertype PlannedMaintenance > HolmesEvents
Path: `Live Migration > Holmes Events > Especial case: Triggertype PlannedMaintenance > HolmesEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HolmesEvents | Table | azcore.centralus | AzureCP | queryFrom, queryTo, queryContainerId |

### Live Migration > Holmes Events > Especial case: Triggertype PlannedMaintenance > HolmesRHMNodeVacateStatusEvent
Path: `Live Migration > Holmes Events > Especial case: Triggertype PlannedMaintenance > HolmesRHMNodeVacateStatusEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HolmesRHMNodeVacateStatusEvent | Table | azurecm | AzureCM | queryFrom, queryTo, queryNodeId |

### Live Migration > Holmes Events > LiveMigrationSessionValidationCriticalEventLog > HolmesGoalStateManagerEvent
Path: `Live Migration > Holmes Events > LiveMigrationSessionValidationCriticalEventLog > HolmesGoalStateManagerEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HolmesGoalStateManagerEvent | Table | azcore.centralus | AzureCP | queryFrom, queryTo, queryContainerId |

### Live Migration > Holmes Events > LiveMigrationSessionValidationCriticalEventLog > Provides validation information at the time of triggering Live Migration
Path: `Live Migration > Holmes Events > LiveMigrationSessionValidationCriticalEventLog > Provides validation information at the time of triggering Live Migration`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LiveMigrationSessionValidationCriticalEventLog-cl | Table | azcore.centralus | Fc | queryFrom, queryTo, containerId |

### Live Migration > LiveMigration Failures
Path: `Live Migration > LiveMigration Failures`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LmFailures | Single | vmainsight | Air | queryFrom, queryTo, query_SubscriptionId |

### Live Migration > LiveMigration Failures > LM failures by Subscription
Path: `Live Migration > LiveMigration Failures > LM failures by Subscription`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LiveMigrationFailures | Table | vmainsight | Air | queryFrom, queryTo, query_subscriptionId |

### Live Migration > LiveMigrationContainerDetails-New
Path: `Live Migration > LiveMigrationContainerDetails-New`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LiveMigrationEvents | Table | Vmainsight | Air | queryContainerId, queryStartTime, queryEndTime, querySubscriptionId, queryVMId, queryContainerList |

### Live Migration > LiveMigrationContainerDetailsEventLog
Path: `Live Migration > LiveMigrationContainerDetailsEventLog`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LiveMigrationContainerDetailsEventLog DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_ContainerId |

### Live Migration > LiveMigrations for Subscription
Path: `Live Migration > LiveMigrations for Subscription`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AirLiveMigrationEvents DS | Table | vmainsight | Air | querySubscriptionId |

### Live Migration > LiveMigrationSessionCompleteLog
Path: `Live Migration > LiveMigrationSessionCompleteLog`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LiveMigrationSessionCompleteLog DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_ContainerId |

### Live Migration > LiveMigrationSessionCreatedLog
Path: `Live Migration > LiveMigrationSessionCreatedLog`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LiveMigrationSessionCreatedLog DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_ContainerId |

### Live Migration > LiveMigrationSessionCriticalLog
Path: `Live Migration > LiveMigrationSessionCriticalLog`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LiveMigrationSessionCriticalLog DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_ContainerId |

### Live Migration > LiveMigrationSessionStatusEventLog
Path: `Live Migration > LiveMigrationSessionStatusEventLog`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LiveMigrationSessionStatusEventLog DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_ContainerId |

### Live Migration > LiveMigrationSessionStatusEventLog_Errors
Path: `Live Migration > LiveMigrationSessionStatusEventLog_Errors`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LiveMigrationSessionStatusEventLog_Error DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_ContainerId |

### Live Migration > LiveMigrationSubscriptionDetails-New
Path: `Live Migration > LiveMigrationSubscriptionDetails-New`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LiveMigrationEventsOnSubscription | Table | Vmainsight | Air | querySubscriptionId, queryStartTime, queryEndTime |

### Live Migration > LMSupportCaseCorrelation-New
Path: `Live Migration > LMSupportCaseCorrelation-New`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LMSupportCases | Table | https://supportrptwus3prod.westus3 | AceHubSupportData | queryBeginTime, queryEndTime, querySubscriptionId, queryCaseNumber |

### Live Migration > VM eligible for LM > LmApplicableVms
Path: `Live Migration > VM eligible for LM > LmApplicableVms`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LmApplicableVms | Table | moseisley | Air | queryContainerId |

### Node Investigation > Anvil > Anvil events
Path: `Node Investigation > Anvil > Anvil events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Anvil DS | Table | aplat.westcentralus | APlat | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > ASC HA Runs > ASC HA Runs
Path: `Node Investigation > ASC HA Runs > ASC HA Runs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HAruns DS | Table | Azds | adsmds | startTime, endTime, nodeId |

### Node Investigation > Azure Profiler > Azure Profiler
Path: `Node Investigation > Azure Profiler > Azure Profiler`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WF_UR_AzureProfiler | Table | azureprofilerfollower.westus2 | azureprofiler | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > Azure Watson > Azure Watson
Path: `Node Investigation > Azure Watson > Azure Watson`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzureWatson DS | Table | Azurewatsoncustomer | AzureWatsonCustomer | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > E17 > DiskFailureXStoreTriage
Path: `Node Investigation > E17 > DiskFailureXStoreTriage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DiskFailureXStoreTriage DS | Table | Xlivesite | XHealthDiskTriage | query_StartTime, query_EndTime, query_NodeId |

### Node Investigation > E17 > E17s for container > E17s for container
Path: `Node Investigation > E17 > E17s for container > E17s for container`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | E17_for_container DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_nodeid, query_containerid |

### Node Investigation > E17 > E17s on host node  > E17s on host node 
Path: `Node Investigation > E17 > E17s on host node  > E17s on host node `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Event17 DS | Table | vmainsight | vmadb | dateTime_StartTime, dateTime_EndTime, query_NodeId |

### Node Investigation > E17 > RDOS E17 Triage > RDOS E17 Triage
Path: `Node Investigation > E17 > RDOS E17 Triage > RDOS E17 Triage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RDOSE17Triage | Table | Rdosdata | rdosdatapath | queryFrom, queryTo, queryCluster, queryNode |

### Node Investigation > E17 > VDC E17
Path: `Node Investigation > E17 > VDC E17`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VDC_E17 | Table | azcore.centralus | Fa | queryFrom, queryTo, querynodeId |

### Node Investigation > E17 > VhdDiskEtwEventTable
Path: `Node Investigation > E17 > VhdDiskEtwEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DiskEventsQuery | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node Investigation > E17 > VhdumXdiskLeaseOperations
Path: `Node Investigation > E17 > VhdumXdiskLeaseOperations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DiskLeaseOperations | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node Investigation > FaultHandlingRecoveryEvents
Path: `Node Investigation > FaultHandlingRecoveryEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FaultHandlingRecoveryEvent DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > Hawkeye > Hawkeye
Path: `Node Investigation > Hawkeye > Hawkeye`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WF_UR_Hawkeye | Table | hawkeyedataexplorer.westus2 | HawkeyeLogs | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > HostAgentEventsETW
Path: `Node Investigation > HostAgentEventsETW`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostAgentEventsETW | Table | azcore.centralus | fa | queryFrom, queryTo, queryNodeId |

### Node Investigation > HyperVAnalyticEvents > HyperVAnalyticEvents
Path: `Node Investigation > HyperVAnalyticEvents > HyperVAnalyticEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVAnalyticEvents DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > HyperVStorageStack > HyperVStorageStack
Path: `Node Investigation > HyperVStorageStack > HyperVStorageStack`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVStorageStackTable DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId, query_ContainerId, query_vmId |

### Node Investigation > HyperVWorker > HyperVWorker
Path: `Node Investigation > HyperVWorker > HyperVWorker`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVWorkerTable DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId, query_ContainerId, query_vmId |

### Node Investigation > ICMs for Host Node > ICMs for host node
Path: `Node Investigation > ICMs for Host Node > ICMs for host node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Incidents DS | Table | icmcluster | IcmDataWarehouse | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > LogNodeSnapshot > Node Snapshot Table
Path: `Node Investigation > LogNodeSnapshot > Node Snapshot Table`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LogNodeSnapshot DS | Table | storageclient.eastus | Fc | query_BeginTime, query_NodeId |

### Node Investigation > Low Host Memory Investigation
Path: `Node Investigation > Low Host Memory Investigation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OSCo | Single | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node Investigation > Low Host Memory Investigation > HawkeyeRCAEvents
Path: `Node Investigation > Low Host Memory Investigation > HawkeyeRCAEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HawkeyeRCAEvents_lowmemory | Table | hawkeyedataexplorer.westus2 | HawkeyeLogs | queryFrom, queryTo, queryNodeId |

### Node Investigation > Low Host Memory Investigation > Host overview
Path: `Node Investigation > Low Host Memory Investigation > Host overview`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | kaconfig | Single | azcore.centralus | KernelAgent | queryFrom, queryTo, queryNodeId |
| 2 | OSConf | Single | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |
| 3 | GetSnapshot | Single | gandalfnodehealth.centralus | gandalfdev | queryFrom, queryTo, query_NodeId, queryHostGen, queryOSVer |

### Node Investigation > Low Host Memory Investigation > HostResourceManagerResourceSnapshotMetadata
Path: `Node Investigation > Low Host Memory Investigation > HostResourceManagerResourceSnapshotMetadata`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostResourceManagerResourceSnapshotMetadata | Table | azcore.centralus | KernelAgent | queryFrom, queryTo, queryNodeId |

### Node Investigation > Low Host Memory Investigation > KaHostSummaryMetrics
Path: `Node Investigation > Low Host Memory Investigation > KaHostSummaryMetrics`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | KaHostSummary_lowmemory2 | Table | azcore.centralus | KernelAgent | queryFrom, queryTo, queryNodeId |

### Node Investigation > Low Host Memory Investigation > LeakDetection
Path: `Node Investigation > Low Host Memory Investigation > LeakDetection`  ·  Queries: 4

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | KaHost | Single | azcore.centralus | KernelAgent | queryFrom, queryTo, queryNodeId |
| 2 | leakdetection | Table | gandalfnodehealth.centralus | gandalfdev | queryFrom, queryTo, query_NodeId, queryHostGen, queryOSVer, querySnapshotId |
| 3 | GetSnapshot | Single | gandalfnodehealth.centralus | gandalfdev | queryFrom, queryTo, query_NodeId, queryHostGen, queryOSVer |
| 4 | kaconfig | Single | azcore.centralus | KernelAgent | queryFrom, queryTo, queryNodeId |

### Node Investigation > NodeEvents > Node Events
Path: `Node Investigation > NodeEvents > Node Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtNodeEventsEtwTable_UnexpectedRestart2 DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > NodeFaultEvents > Node Fault Events
Path: `Node Investigation > NodeFaultEvents > Node Fault Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeFaultEvents DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > NodeServiceEvents > Node Service Events
Path: `Node Investigation > NodeServiceEvents > Node Service Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeServiceEventEtwTable DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > NodeServiceOperation > Node Service Operations
Path: `Node Investigation > NodeServiceOperation > Node Service Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeServiceOperationEtwTable DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > NodeStateChanges > Node State Changes
Path: `Node Investigation > NodeStateChanges > Node State Changes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtNodeStateChangedEtwTable DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > NodeTraceEvents > TMMgmtNodeTraceEtwTable
Path: `Node Investigation > NodeTraceEvents > TMMgmtNodeTraceEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtNodeTraceEtwTable DS | Table | azcore.centralus | Fc | startTime, endTime, nodeId |

### Node Investigation > NVME troubleshooting > DirectAccessEvent
Path: `Node Investigation > NVME troubleshooting > DirectAccessEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DirectAccessEvent | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerId |

### Node Investigation > NVME troubleshooting > HyperVEventsV2
Path: `Node Investigation > NVME troubleshooting > HyperVEventsV2`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVEventsV2 | Table | azcore.centralus | SharedWorkspace | queryFrom, queryTo, queryNodeId, queryContainerId |

### Node Investigation > NVME troubleshooting > HyperVStorageStackErrors
Path: `Node Investigation > NVME troubleshooting > HyperVStorageStackErrors`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVStorageStackErrors | Table | azcore.centralus | SharedWorkspace | queryFrom, queryTo, queryNodeId |

### Node Investigation > NVME troubleshooting > HyperVStorageStackTable
Path: `Node Investigation > NVME troubleshooting > HyperVStorageStackTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVStorageStackTable_NVME | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node Investigation > NVME troubleshooting > HyperVStorageStackTable Controller
Path: `Node Investigation > NVME troubleshooting > HyperVStorageStackTable Controller`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVStorageStackTable_filter_controller | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node Investigation > NVME troubleshooting > NVME events on WindowsEventsTable
Path: `Node Investigation > NVME troubleshooting > NVME events on WindowsEventsTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WindowseEventsNVME | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node Investigation > OsAnalyzerTable
Path: `Node Investigation > OsAnalyzerTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OsAnalyzer Host Node Analysis DS | Table | azcore.centralus | Fa | query_startTime, query_endTime, query_nodeId |

### Node Investigation > OsLoggerTable > OsLoggerTable
Path: `Node Investigation > OsLoggerTable > OsLoggerTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OsLogger DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > RdAgent Tables > Host Agent Events > HostAgentEventsEtw
Path: `Node Investigation > RdAgent Tables > Host Agent Events > HostAgentEventsEtw`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostAgentEventsEtwTable DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > RdAgent Tables > VMAL Container Operations > VmServiceContainerOperations
Path: `Node Investigation > RdAgent Tables > VMAL Container Operations > VmServiceContainerOperations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMAL Container Operations DS | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Node Investigation > RdAgent Tables > VMAL Disk Lease Operations > VmServiceLeaseManagementOperation
Path: `Node Investigation > RdAgent Tables > VMAL Disk Lease Operations > VmServiceLeaseManagementOperation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VmServiceLeaseManagementOperation DS | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Node Investigation > RdAgent Tables > VMAL Disk Operations > VmServiceVirtualDiskOperations
Path: `Node Investigation > RdAgent Tables > VMAL Disk Operations > VmServiceVirtualDiskOperations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMAL Disk Service Table DS | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Node Investigation > RdAgent Tables > VMAL Service Events > VmServiceEventsEtwTable
Path: `Node Investigation > RdAgent Tables > VMAL Service Events > VmServiceEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VmServiceEventsEtwTable DS | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Node Investigation > RdAgent Tables > VMAL Service Init > VmServiceInitialization
Path: `Node Investigation > RdAgent Tables > VMAL Service Init > VmServiceInitialization`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMAL Service Init DS | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Node Investigation > SLA Table > SLA Table for Node
Path: `Node Investigation > SLA Table > SLA Table for Node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtSlaMeasurementEventEtwTable_UnexpectedRestart DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > VMA > VM Availability analysis
Path: `Node Investigation > VMA > VM Availability analysis`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMA4 DS | Table | vmainsight | vmadb | query_BeginTime, query_EndTime, query_NodeId |

### Node Investigation > WindowsEvents > Windows Events from host node
Path: `Node Investigation > WindowsEvents > Windows Events from host node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WF_UR_WindowsEvents | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Planned Maintenance > Control Events for VM > GetCurrentMaintenanceStatus
Path: `Planned Maintenance > Control Events for VM > GetCurrentMaintenanceStatus`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Control Events for VM DS | Table | Azdeployer | AzDeployerKusto | query_SubscriptionId, query_VMName, query_TenantName |

### Planned Maintenance > Control History for VM > GetMaintenanceHistory
Path: `Planned Maintenance > Control History for VM > GetMaintenanceHistory`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Control History for VM DS | Table | Azdeployer | AzDeployerKusto | query_SubscriptionId, query_VMName, query_TenantName, query_BeginTime, query_EndTime |

### Planned Maintenance > Customer Notification1 > Customer Notification1
Path: `Planned Maintenance > Customer Notification1 > Customer Notification1`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CustomerNotification1 DS | Table | icmcluster | ACM.Publisher | query_SubscriptionId |

### Planned Maintenance > Customer Notification2 > Customer Notification2
Path: `Planned Maintenance > Customer Notification2 > Customer Notification2`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CustomerNotification2 DS | Table | Icmcluster | ACM.Publisher | query_BeginTime, query_SubscriptionId |

### Planned Maintenance > Events for VM > GetCurrentMaintenanceStatus
Path: `Planned Maintenance > Events for VM > GetCurrentMaintenanceStatus`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Events for VM DS | Table | Azdeployer | AzDeployerKusto | query_SubscriptionId, query_VMName, query_TenantName |

### Planned Maintenance > History for VM > GetMaintenanceHistory
Path: `Planned Maintenance > History for VM > GetMaintenanceHistory`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | History for VM DS | Table | Azdeployer | AzDeployerKusto | query_BeginTime, query_EndTime, query_SubscriptionId, query_VMName, query_TenantName |

### Planned Maintenance > MaintenancePhaseDetails
Path: `Planned Maintenance > MaintenancePhaseDetails`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PendingMaintenanceOperationDetails DS | Table | azcore.centralus | Fc | query_SubscriptionId, query_TenantName |
| 2 | MaintenancePhaseDetails DS | Table | azcore.centralus | Fc | query_ScheduledMaintenanceId, query_SourceNodeId |

### Planned Maintenance > PendingMaintenanceOperationDetails
Path: `Planned Maintenance > PendingMaintenanceOperationDetails`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PendingMaintenanceOperationDetails DS | Table | azcore.centralus | Fc | query_SubscriptionId, query_TenantName |

### Planned Maintenance > ScheduledEventsEnablementStatus > ScheduledEventsEnablementStatus
Path: `Planned Maintenance > ScheduledEventsEnablementStatus > ScheduledEventsEnablementStatus`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ScheduledEventsEnablementStatus DS | Table | Azpe | azpe | query_BeginTime, query_TenantName |

### Planned Maintenance > ScheduledMaintenanceInformational
Path: `Planned Maintenance > ScheduledMaintenanceInformational`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PendingMaintenanceOperationDetails DS | Table | azcore.centralus | Fc | query_SubscriptionId, query_TenantName |
| 2 | ScheduledMaintenanceInformational DS | Table | azcore.centralus | Fc | query_BeginTime, query_SourceNodeId, query_TenantName |

### Planned Maintenance > TMMgmtTenantEventsEtwTable > TMMgmtTenantEventsEtwTable
Path: `Planned Maintenance > TMMgmtTenantEventsEtwTable > TMMgmtTenantEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TenanteEventsFilteredPM DS | Table | azcore.centralus | Fc | query_BeginTime, query_EndTime, query_TenantName |

### Service Healing > AzSM
Path: `Service Healing > AzSM`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Service Healing Trigger Type | Timeline | accp.centralus | AZSM | queryFrom, queryTo, queryTenantname, queryRI |
| 2 | AzSMServiceHealingStepResultEvents | Timeline | accp.centralus | AZSM | queryFrom, queryTo, querytenantName, RIname |

### Service Healing > AzSM > AzSMServiceHealingResultEvents
Path: `Service Healing > AzSM > AzSMServiceHealingResultEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSMServiceHealingResultEvents_clmendes | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName, queryRIName |

### Service Healing > AzSM > AzSMServiceHealingStepResultEvents
Path: `Service Healing > AzSM > AzSMServiceHealingStepResultEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSMServiceHealingStepResultEvents_clmendes | Table | accp.centralus | AZSM | queryFrom, queryTo, querytenantName, queryRIName |

### Service Healing > AzSM > AzSMServiceHealingTriggerEvents
Path: `Service Healing > AzSM > AzSMServiceHealingTriggerEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSMServiceHealingTriggerEvents_clmendes | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName, queryRIName |

### Service Healing > AzSM > AzSMTenantEvents
Path: `Service Healing > AzSM > AzSMTenantEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSMTenantEvents_clmendes | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName, queryRIName |

### Service Healing > AzSM > AzSMTenantStatemachineEvents
Path: `Service Healing > AzSM > AzSMTenantStatemachineEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSMTenantStatemachineEvents_clmendes | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName, queryRIName |

### Service Healing > Fabric > ServiceHealingTenantStatusEtwTable
Path: `Service Healing > Fabric > ServiceHealingTenantStatusEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ServiceHealingTenantStatusEtwTable_clmendes | Table | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName, queryRIName |

### Service Healing > Fabric > ServiceHealingTriggerEtwTable
Path: `Service Healing > Fabric > ServiceHealingTriggerEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ServiceHealingTriggerEtwTable_clmendes | Table | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName, queryRIName |

### Service Healing > Fabric > TMMgmtTenantManagementJobInfoEtwTable
Path: `Service Healing > Fabric > TMMgmtTenantManagementJobInfoEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtTenantManagementJobInfoEtwTable_clmendes | Table | azcore.centralus | Fc | queryFrom, queryTo, queryRIName, queryTenantName |

### Service Healing > Overview > Detector for Service Healings
Path: `Service Healing > Overview > Detector for Service Healings`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | IssueDetector AzSMServiceHealing | IssueDetector | azcore.centralus | AzureCP | queryFrom, queryTo, queryTenantName, queryRIName |
| 2 | IssueDetector FabricServiceHealing | IssueDetector | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName, queryRIName |

### Update Investigation > AirHostNetworkingUpdateEvents > AirHostNetworkingUpdateEvents
Path: `Update Investigation > AirHostNetworkingUpdateEvents > AirHostNetworkingUpdateEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AirHostNetworkingUpdateEvents DS | Table | vmainsight | Air | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > AirManagedEvents > AirManagedEvents
Path: `Update Investigation > AirManagedEvents > AirManagedEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AirManagedEvents DS | Table | vmainsight | Air | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > AirManagedEventsBrownouts > AirManagedEventsBrownouts
Path: `Update Investigation > AirManagedEventsBrownouts > AirManagedEventsBrownouts`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AirManagedEventsBrownouts DS | Table | vmainsight | Air | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > Combined Query > Combined Query for Host Updates
Path: `Update Investigation > Combined Query > Combined Query for Host Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CombinedQuery DS | Table | storageclient.eastus | AutopilotDeployment | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > HostPlugin Update - TMMgmtNodeEventsEtwTable > HostPlugin Updates
Path: `Update Investigation > HostPlugin Update - TMMgmtNodeEventsEtwTable > HostPlugin Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostPlugin Update - TMMgmtNodeEventsEtwTable DS | Table | https://storageclient.eastus | Fc | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > Node Update Event - Event Log > Node Update Events
Path: `Update Investigation > Node Update Event - Event Log > Node Update Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Update Event - Event Log DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > OSHP FastSave > OSHP FastSave
Path: `Update Investigation > OSHP FastSave > OSHP FastSave`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Fast Restore Events DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > OSHP Timeline Events > OSHP Timeline Events
Path: `Update Investigation > OSHP Timeline Events > OSHP Timeline Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host OSHP Events DS | Table | azcore.centralus | Fa | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > OSHP Update Logs > OSHP Update Logs
Path: `Update Investigation > OSHP Update Logs > OSHP Update Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OSHP Update DS | Table | storageclient.eastus | AutopilotDeployment | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > PF Service Update - ServiceVersionSwitch > PF Service Updates
Path: `Update Investigation > PF Service Update - ServiceVersionSwitch > PF Service Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ServiceVersionSwitch_UnexpectedRestart2 DS | Table | https://storageclient.eastus | AutopilotDeployment | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > Scheduled Event for HostUpdate - AzPEWorkflowEvent > Scheduled Event for HostUpdate
Path: `Update Investigation > Scheduled Event for HostUpdate - AzPEWorkflowEvent > Scheduled Event for HostUpdate`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Scheduled Event for HostUpdate - AzPEWorkflowEvent DS | Table | azpe | azpe | query_BeginTime, query_EndTime, query_NodeId |

### Update Investigation > SoC PF Update
Path: `Update Investigation > SoC PF Update`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SocUpdate | Table | overlakedata.southcentralus | overlake-syslog | queryFrom, queryTo, queryNodeId |

### Update Investigation > VMPhuEvents > VMPhuEvents
Path: `Update Investigation > VMPhuEvents > VMPhuEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMPhuEvents DS | Table | https://moseisley | Air | query_BeginTime, query_EndTime, query_vmid |
