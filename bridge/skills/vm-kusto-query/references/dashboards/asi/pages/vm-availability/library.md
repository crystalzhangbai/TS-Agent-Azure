# EEE RDOS — VM Availability: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:14:01.132Z.
> Total: 282 unique KQL queries across 146 panels (300 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "VM Availability" | ResourceGet | azcore.centralus | azurecp | local_containerId, local_nodeId, local_roleInstanceName, local_Tenant, local_tenantName, local_virtualMachineUniqueId, globalFrom, globalTo |
| 2 | OverlakeNodeMap | Single | overlakedata.southcentralus | overlake-syslog | queryFrom, queryTo, queryNodeId |
| 3 | GetShoeboxAccount | Single | azurecm | AzureCM | queryFrom, queryTo, queryCluster |

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

### Container > Container / Tenant > Anvil Recovery Action > Anvil Recovery Action > Anvil Event
Path: `Container > Container / Tenant > Anvil Recovery Action > Anvil Recovery Action > Anvil Event`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Anvil Event | Table | aplat.westcentralus | APlat | starttime, endtime, nodeid |

### Container > Container / Tenant > Anvil Recovery Action > Anvil Recovery Action > Anvil Event Timeline
Path: `Container > Container / Tenant > Anvil Recovery Action > Anvil Recovery Action > Anvil Event Timeline`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Anvil Operation | Timeline | azcsupfollower | AzureCM | starttime, endtime, nodeid |
| 2 | Anvil Event Trigger | Timeline | azcsupfollower | AzureCM | starttime, endtime, nodeid |

### Container > Container / Tenant > Attached Disks
Path: `Container > Container / Tenant > Attached Disks`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Blobs | Table | storageclient.eastus | SharedWorkspace | startTime, endTime, containerId, cluster, nodeId, vmId |

### Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Change History
Path: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Change History`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query PaaS Container in  LogContainerSnapshot | Table | Azcsupfollower | AzureCM | queryFrom, queryTo, queryContainerId, queryTenantName |

### Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Health for Container Id
Path: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Health for Container Id`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Event | Timeline | azurecm | AzureCM | starttime, endtime, containerid |

### Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Health State
Path: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Health State`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query PaaS Container in LogContainerHealthSnapshot | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryContainerId, queryFilter, queryTenantName |
| 2 | FilterStates | Filter | azcore.centralus | Fa | - |

### Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Performance
Path: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > Container Performance`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Performance for Container Id | TimeSeries | azcore.centralus | Fa | starttime, endtime, containerid |
| 2 | FilterStates | Filter | azcore.centralus | Fa | - |

### Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > LogRoleInstanceSnapshot
Path: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > LogRoleInstanceSnapshot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query LogRoleInstanceSnapshot | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryRoleInstanceName, queryTenantName |

### Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > VmHealthRawStateEtwTable
Path: `Container > Container / Tenant > Classic Cloud Service (Container/Instance) > Classic Cloud Service (Container/Instance) > VmHealthRawStateEtwTable`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query PaaS Container in VmHealthRawStateEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryContainerId, queryTenantName, queryFilter |
| 2 | FilterStates | Filter | azcore.centralus | Fa | - |

### Container > Container / Tenant > Guest OS Logs > Guest OS Logs > Guest Agent & Extension Provisioning
Path: `Container > Container / Tenant > Guest OS Logs > Guest OS Logs > Guest Agent & Extension Provisioning`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GuestAgentAndExtensionTimeline | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryContainerid |

### Container > Container / Tenant > Guest OS Logs > Guest OS Logs > Guest OS Extension Log filter by ContainerId - GuestAgentExtensionEvents
Path: `Container > Container / Tenant > Guest OS Logs > Guest OS Logs > Guest OS Extension Log filter by ContainerId - GuestAgentExtensionEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Guest OS Logs | Table | azcore.centralus | Fa | starttime, endtime, queryContainerId |

### Container > Container / Tenant > Guest OS Logs > Guest OS Logs > Guest OS Log
Path: `Container > Container / Tenant > Guest OS Logs > Guest OS Logs > Guest OS Log`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GuestOSGenericLogs | Table | azcore.centralus | Fa | starttime, endtime, containerid |

### Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > Container Change History
Path: `Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > Container Change History`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Change History | Table | azcore.centralus | AzureCP | starttime, endtime, vmid, queryContainerId |

### Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > Container Health State
Path: `Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > Container Health State`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FilterStates | Filter | azcore.centralus | Fa | - |
| 2 | LogContainerHealthSnapshot | Table | azcore.centralus | AzureCP | queryFrom, queryTo, queryFilter, queryContainerId, vmid |

### Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > HyperV States - VmHealthRawStateEtwTable
Path: `Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > HyperV States - VmHealthRawStateEtwTable`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FilterStates | Filter | azcore.centralus | Fa | - |
| 2 | HyperV states from VmHealthRawStateEtwTable | Table | azcore.centralus | Fa | queryStart, queryEnd, queryVmUniqueId, queryFilter |

### Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > LogRoleInstanceSnapshot
Path: `Container > Container / Tenant > IaaS VM (VM Id) > IaaS VM (VM Id) > LogRoleInstanceSnapshot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query LogRoleInstanceSnapshot | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryRoleInstanceName, queryTenantName |

### Container > Container / Tenant > Others > Billing 
Path: `Container > Container / Tenant > Others > Billing `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query FaComputeHourUsageEventCentralBondTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryContainerId, queryVMId |

### Container > Container / Tenant > Others > Resource Health Annotation > Annotation from LogHealthAnnotationEvent
Path: `Container > Container / Tenant > Others > Resource Health Annotation > Annotation from LogHealthAnnotationEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query LogHealthAnnotationEvent | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryContainerId, queryVMId |

### Container > Container / Tenant > Others > Resource Health Annotation > Annotation from RhcAnnotationReportsEtwTable
Path: `Container > Container / Tenant > Others > Resource Health Annotation > Annotation from RhcAnnotationReportsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query RhcAnnotationReportsEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryVMId, queryContainerId |

### CRP / Operation > Operation > CRP KVS > VM Entity
Path: `CRP / Operation > Operation > CRP KVS > VM Entity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP VM Snapshot | Single | azcrpbifollower | bi_allprod | queryFrom, queryTo, vmid, queryRoleInstanceName |

### CRP / Operation > Operation > CRP Operation > CRP Operation > CRP Operation
Path: `CRP / Operation > Operation > CRP Operation > CRP Operation > CRP Operation`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP Operations | Table | Azcrp | crp_allprod | starttime, endtime, vmid, filterValue, querySubId, queryRoleInstanceName |
| 2 | filterCRP | Filter | azcrp | crp_allprod | - |

### CRP / Operation > Operation > CRP Operation > CRP Operation > CRP Operation Timeline
Path: `CRP / Operation > Operation > CRP Operation > CRP Operation > CRP Operation Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP Operation Timeline | Timeline | azcrp | crp_allprod | starttime, endtime, vmid, queryInstanceName, querySubId |

### CRP / Operation > Operation > CRP Operation > CRP Operation > Fabric Callback
Path: `CRP / Operation > Operation > CRP Operation > CRP Operation > Fabric Callback`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Fabric Callback to CRP | Table | azcrp | crp_allprod | starttime, endtime, vmid, querySubId, queryRoleInstanceName |

### Disk & XDisk > Disk > 505 SCSI Disk Perf > 505 SCSI Disk Perf > Local SCSI Disk Perf (Average IO Latency) on Node
Path: `Disk & XDisk > Disk > 505 SCSI Disk Perf > 505 SCSI Disk Perf > Local SCSI Disk Perf (Average IO Latency) on Node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SCSI Disk Perf | TimeSeries | azcore.centralus | SharedWorkspace | starttime, endtime, nodeid |

### Disk & XDisk > Disk > Disk Windows Event > Disk Windows Event > Disk Event
Path: `Disk & XDisk > Disk > Disk Windows Event > Disk Windows Event > Disk Event`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Disk Event in Node Windows Event | Table | azcore.centralus | Fa | starttime, endtime, nodeid |

### Disk & XDisk > Disk > Disk Windows Event > Disk Windows Event > Disk Event Timeline
Path: `Disk & XDisk > Disk > Disk Windows Event > Disk Windows Event > Disk Event Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | BlobCache | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |

### Disk & XDisk > Disk > Storport Device
Path: `Disk & XDisk > Disk > Storport Device`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Storeport Events | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Disk & XDisk > Disk > Storport Device > Storport Event Timeline
Path: `Disk & XDisk > Disk > Storport Device > Storport Event Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Storport Event Timeline | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Disk & XDisk > Disk > VhdDisk > OsVhddiskEventTable
Path: `Disk & XDisk > Disk > VhdDisk > OsVhddiskEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query OsVhddiskEventTable | Table | Azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Disk & XDisk > Disk > VhdDisk > VhdDiskEtwEventTable
Path: `Disk & XDisk > Disk > VhdDisk > VhdDiskEtwEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query VhdDiskEtwEventTable | Table | Azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Deployment Limit
Path: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Deployment Limit`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Allocation Limit | TimeSeries | azcsupfollower | AzureCM | starttime, endtime, cluster |

### Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > New Deployment Allocatable State
Path: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > New Deployment Allocatable State`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Allocatable State | Timeline | azurecm | AzureCM | starttime, endtime, cluster |

### Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Node Count
Path: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Node Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Count | TimeSeries | azcsupfollower | AzureCM | starttime, endtime, cluster |

### Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Utilization Core
Path: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Utilization Core`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Util Core | TimeSeries | azcsupfollower | AzureCM | starttime, endtime, cluster |

### Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Utilization Memory
Path: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Utilization Memory`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Util Memory | TimeSeries | azcsupfollower | AzureCM | starttime, endtime, cluster |

### Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > Fabricator
Path: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > Fabricator`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Fabricator Instance | Timeline | azurecm | AzureCM | starttime, endtime, cluster |
| 2 | Fabricator Downtime | Timeline | AzureCM | AzureCM | starttime, endtime, cluster |

### Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > HumanInvestigate Node Count / Hour
Path: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > HumanInvestigate Node Count / Hour`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeStateHumanInvestigateCount | TimeSeries | azurecm | AzureCM | starttime, endtime, cluster |
| 2 | NodeStateReadyCount | TimeSeries | storageclient.eastus | Fc | starttime, endtime, cluster |

### Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > OutForRepair Node Count / Hour
Path: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > OutForRepair Node Count / Hour`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeStateOFRCount | TimeSeries | storageclient.eastus | Fc | starttime, endtime, cluster |

### Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > Ready Node Count
Path: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > Ready Node Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeStateReadyCount | TimeSeries | storageclient.eastus | Fc | starttime, endtime, cluster |

### Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > Unhealthy Node Count
Path: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > Unhealthy Node Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Unhealthy Node Count | TimeSeries | storageclient.eastus | Fc | starttime, endtime, cluster |

### Fabric / Tenant > Fabric / Compute Manager > Live Migration > HolmesGoalStateManagerEvent
Path: `Fabric / Tenant > Fabric / Compute Manager > Live Migration > HolmesGoalStateManagerEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Quyry HolmesGoalStateManagerEvent | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryContainerId |

### Fabric / Tenant > Fabric / Compute Manager > Live Migration > LiveMigrationSessionCompleteLog 
Path: `Fabric / Tenant > Fabric / Compute Manager > Live Migration > LiveMigrationSessionCompleteLog `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query LiveMigrationSessionCompleteLog | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryContainerId |

### Fabric / Tenant > Fabric / Compute Manager > Live Migration > LiveMigrationSessionStatusEventLog
Path: `Fabric / Tenant > Fabric / Compute Manager > Live Migration > LiveMigrationSessionStatusEventLog`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query LiveMigrationSessionStatusEventLog | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryContainerId |

### Fabric / Tenant > Fabric / Compute Manager > Node Management > Node Management > Node Management Events from TMMgmtNodeEventsEtwTable
Path: `Fabric / Tenant > Fabric / Compute Manager > Node Management > Node Management > Node Management Events from TMMgmtNodeEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtNodeEventsEtwTable | Table | azcsupfollower | azurecm | queryFrom, queryTo, queryNodeId, queryContainerId, queryCheckContainerOnly |

### Fabric / Tenant > Fabric / Compute Manager > Node Management > Node Management > TMMgmtNodeTraceEtwTable
Path: `Fabric / Tenant > Fabric / Compute Manager > Node Management > Node Management > TMMgmtNodeTraceEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtNodeTraceEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryNodeId |

### Fabric / Tenant > Fabric / Compute Manager > Scheduled Events
Path: `Fabric / Tenant > Fabric / Compute Manager > Scheduled Events`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant Scheduled Events | Timeline | azpe | azpe | queryFrom, queryTo, queryTenantName, queryInstanceName |
| 2 | Scheduled Events Enablement Status | Timeline | azpe | azpe | queryFrom, queryTo, queryTenantName |

### Fabric / Tenant > Fabric / Compute Manager > Scheduled Events > Events in TMMgmtTenantManagementJobInfoEtwTable
Path: `Fabric / Tenant > Fabric / Compute Manager > Scheduled Events > Events in TMMgmtTenantManagementJobInfoEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TMMgmtTenantManagementJobInfoEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### Fabric / Tenant > Fabric / Compute Manager > Scheduled Events > Scheduled Events in AzPEWorkflowEvent
Path: `Fabric / Tenant > Fabric / Compute Manager > Scheduled Events > Scheduled Events in AzPEWorkflowEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Tenant in AzPEWorkflowEvent | Table | azpe | azpe | queryFrom, queryTo, queryTenantName |

### Fabric / Tenant > Fabric / Compute Manager > Service Healing > AzSM Service Healing > AzSMServiceHealingResultEvents
Path: `Fabric / Tenant > Fabric / Compute Manager > Service Healing > AzSM Service Healing > AzSMServiceHealingResultEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AzSMServiceHealingResultEvents | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName |

### Fabric / Tenant > Fabric / Compute Manager > Service Healing > AzSM Service Healing > AzSMServiceHealingStepResultEvents
Path: `Fabric / Tenant > Fabric / Compute Manager > Service Healing > AzSM Service Healing > AzSMServiceHealingStepResultEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AzSMServiceHealingStepResultEvents | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName |

### Fabric / Tenant > Fabric / Compute Manager > Service Healing > AzSM Service Healing > AzSMServiceHealingTriggerEvents
Path: `Fabric / Tenant > Fabric / Compute Manager > Service Healing > AzSM Service Healing > AzSMServiceHealingTriggerEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AzSMServiceHealingTriggerEvents | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName |

### Fabric / Tenant > Fabric / Compute Manager > Service Healing > TM Service Healing > ServiceHealingTenantStatusEtwTable
Path: `Fabric / Tenant > Fabric / Compute Manager > Service Healing > TM Service Healing > ServiceHealingTenantStatusEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query ServiceHealingTenantStatusEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### Fabric / Tenant > Fabric / Compute Manager > Service Healing > TM Service Healing > ServiceHealingTriggerEtwTable
Path: `Fabric / Tenant > Fabric / Compute Manager > Service Healing > TM Service Healing > ServiceHealingTriggerEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query ServiceHealingTriggerEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### Fabric / Tenant > Fabric / Compute Manager > Tenant Management > Tenant Management > AzSMTenantEvents
Path: `Fabric / Tenant > Fabric / Compute Manager > Tenant Management > Tenant Management > AzSMTenantEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AzSMTenantEvents | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName |

### Fabric / Tenant > Fabric / Compute Manager > Tenant Management > Tenant Management > AzSMTenantStatemachineEvents
Path: `Fabric / Tenant > Fabric / Compute Manager > Tenant Management > Tenant Management > AzSMTenantStatemachineEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AzSMTenantStatemachineEvents | Table | accp.centralus | AZSM | queryFrom, queryTo, queryTenantName |

### Fabric / Tenant > Fabric / Compute Manager > Tenant Management > Tenant Management > Tenant Management Events from TMMgmtTenantEventsEtwTable
Path: `Fabric / Tenant > Fabric / Compute Manager > Tenant Management > Tenant Management > Tenant Management Events from TMMgmtTenantEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query TMMgmtTenantEventsEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryTenantName |

### General Tool Links
Path: `General Tool Links`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | JarvisDashTimeHelper | Single | azurecm | azurecm | queryFrom, queryTo |
| 2 | VmssIdHelper | Single | azurecm | azurecm | queryFrom, queryTo, queryContainerProperties |
| 3 | Unix Time Helper | Single | azurecm | AzureCM | queryFrom, queryTo |

### Hyper-V > Hyper-V > Hyper-V Event > Hyper-V Event > Hyper-V Event Timeline
Path: `Hyper-V > Hyper-V > Hyper-V Event > Hyper-V Event > Hyper-V Event Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Hyper-V Event Timeline | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |

### Hyper-V > Hyper-V > Hyper-V Event > Hyper-V Event > Hyper-V Events
Path: `Hyper-V > Hyper-V > Hyper-V Event > Hyper-V Event > Hyper-V Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Hyper-V Events | Table | azcore.centralus | Fa | starttime, endtime, nodeid, containerid |

### Hyper-V > Hyper-V > Hyper-V Worker > Worker > Hyper-V Worker Event
Path: `Hyper-V > Hyper-V > Hyper-V Worker > Worker > Hyper-V Worker Event`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMSS Table | Table | azcore.centralus | Fa | starttime, endtime, containerid, nodeid |

### Hyper-V > Hyper-V > Hyper-V Worker > Worker > Hyper-V Worker Timeline
Path: `Hyper-V > Hyper-V > Hyper-V Worker > Worker > Hyper-V Worker Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Hyper-V Worker Timeline | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid, containerid |

### Hyper-V > Hyper-V > HyperVAnalyticEvents
Path: `Hyper-V > Hyper-V > HyperVAnalyticEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query HyperVAnalyticEvents | Table | Azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Hyper-V > Hyper-V > HyperVHyperVAnalyticEventsStorageStackTable > HyperVStorageStackTable
Path: `Hyper-V > Hyper-V > HyperVHyperVAnalyticEventsStorageStackTable > HyperVStorageStackTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query HyperVStorageStackTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Hyper-V > Hyper-V > HyperVVmmsTable > HyperVVmmsTable
Path: `Hyper-V > Hyper-V > HyperVVmmsTable > HyperVVmmsTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query HyperVVmmsTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Network / TOR
Path: `Network / TOR`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TorDeviceInfo | Single | azphynet | azdhmds | queryFrom, queryTo, nodeid |
| 2 | Unix Time Helper | Single | azurecm | AzureCM | queryFrom, queryTo |
| 3 | vfpMDM | Single | azurehn | azurehn | queryCluster |

### Network > Network > Network Event Log > Network Event Log > Event Logs for Network Component
Path: `Network > Network > Network Event Log > Network Event Log > Event Logs for Network Component`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Windows Event Log for Networking | Table | azcore.centralus | Fa | starttime, endtime, nodeid |

### Network > Network > Network Event Log > Network Event Log > Timeline for Network Component
Path: `Network > Network > Network Event Log > Network Event Log > Timeline for Network Component`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Timeline for Windows Event Log related to Network Component | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |

### Network > Network > NM Programming > NM Programming > Interface Program State from InterfaceProgramEndFiveMinuteTable
Path: `Network > Network > NM Programming > NM Programming > Interface Program State from InterfaceProgramEndFiveMinuteTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query InterfaceProgramEndFiveMinuteTable | Table | aznwsdn | aznwmds | queryContainerId, queryNodeId, queryStart, queryEnd |

### Network > Network > NM Programming > NM Programming > NM Programming from DCMNMAgentProgrammingDurationEtwTable
Path: `Network > Network > NM Programming > NM Programming > NM Programming from DCMNMAgentProgrammingDurationEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query DCMNMAgentProgrammingDurationEtwTable | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryContainerId, queryNodeId |

### Network > Network > SoC > SoC BugChecks
Path: `Network > Network > SoC > SoC BugChecks`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query SoC Bugchecks | Table | azuredcm | AzureDCMDb | queryStart, queryEnd, queryContainerId, queryNodeId |

### Network > Network > SoC > SoC Crash Query
Path: `Network > Network > SoC > SoC Crash Query`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query SoC Crash | Table | azurehn | Azurehn | queryStart, queryEnd, queryNodeId |

### Network > Network > SoC > SoC Memory Usage
Path: `Network > Network > SoC > SoC Memory Usage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Soc Memory Usage | TimeSeries | azurehn | Azurehn | queryStart, queryEnd, queryContainerId, queryNodeId |

### Network > Network > SoC > SoC Process CPU Usage in MB
Path: `Network > Network > SoC > SoC Process CPU Usage in MB`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query SoC CPU | TimeSeries | azurehn | Azurehn | queryStart, queryEnd, queryContainerId, queryNodeId |
| 2 | Query Soc Memory Usage | TimeSeries | azurehn | Azurehn | queryStart, queryEnd, queryContainerId, queryNodeId |

### Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > BMC/SEL Hardware Event - RhwChassisSelItemEtwTable
Path: `Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > BMC/SEL Hardware Event - RhwChassisSelItemEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HardwareEvent | Table | azuredcm | AzureDCMDb | starttime, endtime, nodeid |

### Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > BMC/SEL Hardware Event - SparkleSELByNodeId
Path: `Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > BMC/SEL Hardware Event - SparkleSELByNodeId`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SparkleSELByNodeId | Table | sparkle.eastus | defaultdb | queryFrom, queryTo, queryNodeId |

### Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > DCM Hardware Resource Event - ResourceSnapshotHistoryV1
Path: `Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > DCM Hardware Resource Event - ResourceSnapshotHistoryV1`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Hardware Resource Event | Table | azuredcm | AzureDCMDb | starttime, endtime, nodeid |

### Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > DCM Health Timeline
Path: `Node (Hardware) > Node (Hardware) > DCM/SEL Health > DCM/SEL Health > DCM Health Timeline`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DCM Node State | Timeline | azuredcm | AzureDCMDb | starttime, endtime, nodeid |
| 2 | PilotFish State | Timeline | azuredcm | AzureDCMDb | starttime, endtime, nodeid |

### Node (Hardware) > Node (Hardware) > Hardware Event Log > Hardware Event Log > Hardware / Driver Event Log Timeline
Path: `Node (Hardware) > Node (Hardware) > Hardware Event Log > Hardware Event Log > Hardware / Driver Event Log Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Windows Event Log for Hardware | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Hardware) > Node (Hardware) > Hardware Event Log > Hardware Event Log > Hardware Events from WindowsEventTable
Path: `Node (Hardware) > Node (Hardware) > Hardware Event Log > Hardware Event Log > Hardware Events from WindowsEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Windows Event Log for Hardware | Table | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Hardware) > Node (Hardware) > Hardware Spec > CPU
Path: `Node (Hardware) > Node (Hardware) > Hardware Spec > CPU`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query CPU from dcmInventoryComponentCPUV2Direct | Table | AzureDCM | AzureDCMDb | queryFrom, queryTo, queryNodeId |

### Node (Hardware) > Node (Hardware) > Hardware Spec > HDD/SDD/NVME  from dcmInventoryComponentDiskHistory 
Path: `Node (Hardware) > Node (Hardware) > Hardware Spec > HDD/SDD/NVME  from dcmInventoryComponentDiskHistory `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query dcmInventoryComponentDiskHistory | Table | Azuredcm | AzureDCMDb | queryFrom, queryTo, queryNodeId |

### Node (Hardware) > Node (Hardware) > Hardware Spec > HDD/SDD/Virtual Disk/NVME Direct Drives from dcmInventoryComponentDiskUtilDirect 
Path: `Node (Hardware) > Node (Hardware) > Hardware Spec > HDD/SDD/Virtual Disk/NVME Direct Drives from dcmInventoryComponentDiskUtilDirect `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query dcmInventoryComponentDiskUtilDirect | Table | Azuredcm | AzureDCMDb | queryFrom, queryTo, queryNodeId |

### Node (Hardware) > Node (Hardware) > Hardware Spec > Memory / DIMM
Path: `Node (Hardware) > Node (Hardware) > Hardware Spec > Memory / DIMM`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query DIMM from dcmInventoryComponentDIMMDirect | Table | Azuredcm | AzureDCMDb | queryFrom, queryTo, queryNodeId |

### Node (Physical)
Path: `Node (Physical)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Hardware Properties | Single | azuredcm | AzureDCMDb | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Azure Watson > Azure Watson > Azure Watson Dump List
Path: `Node (Software) > Node (Software) > Azure Watson > Azure Watson > Azure Watson Dump List`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzureWatsonQuery | Table | azurewatsoncustomer | AzureWatsonCustomer | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Container List > Container List > Node Container CPU Perf
Path: `Node (Software) > Node (Software) > Container List > Container List > Node Container CPU Perf`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Container Performance | TimeSeries | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Container List > Container List > Node Container List
Path: `Node (Software) > Node (Software) > Container List > Container List > Node Container List`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Container List | Table | azcsupfollower | AzureCM | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Container List > Container List > Timeline - Container State > Timeline - Container OS State
Path: `Node (Software) > Node (Software) > Container List > Container List > Timeline - Container State > Timeline - Container OS State`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TImeline_ContainerOSState | Timeline | azcsupfollower | AzureCM | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Container List > Container List > Timeline - Container State > Timeline - Container State
Path: `Node (Software) > Node (Software) > Container List > Container List > Timeline - Container State > Timeline - Container State`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Container Timeline | Timeline | azcsupfollower | AzureCM | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Container List > Container List > Timeline - HyperV Heartbeat
Path: `Node (Software) > Node (Software) > Container List > Container List > Timeline - HyperV Heartbeat`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperV Heartbeat for Containers | Timeline | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Event Log > Event Log > Event Timeline
Path: `Node (Software) > Node (Software) > Event Log > Event Log > Event Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Storage | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Event Log > Event Log > Windows Event Table
Path: `Node (Software) > Node (Software) > Event Log > Event Log > Windows Event Table`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeWindowsEvent | Table | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Node Health > Node Health > Aggregation State from LogNodeSnapshot
Path: `Node (Software) > Node (Software) > Node Health > Node Health > Aggregation State from LogNodeSnapshot`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FilterNodeState | Filter | azcore.centralus | Fa | - |
| 2 | LogNodeSnapshot | Table | azcsupfollower | AzureCM | queryFrom, queryTo, nodeid, filterValue |

### Node (Software) > Node (Software) > Node Health > Node Health > Container Count on Node
Path: `Node (Software) > Node (Software) > Node Health > Node Health > Container Count on Node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ContainerConunt | TimeSeries | azcsupfollower | AzureCM | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Node Health > Node Health > Node State
Path: `Node (Software) > Node (Software) > Node Health > Node Health > Node State`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeStateQuery | Table | azcsupfollower | AzureCM | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Node Health > Node Health > Services on Node
Path: `Node (Software) > Node (Software) > Node Health > Node Health > Services on Node`  ·  Queries: 8

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

### Node (Software) > Node (Software) > Node Service > Node Service > General - Node Service > NS Events for this Container from NodeServiceEventEtwTable
Path: `Node (Software) > Node (Software) > Node Service > Node Service > General - Node Service > NS Events for this Container from NodeServiceEventEtwTable`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query NodeServiceEventEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerId, queryCheckThisContainer |
| 2 | Detector for NodeServiceEventEtwTable | IssueDetector | azcore.centralus | Fa | queryFrom, queryTo, queryContainerId, queryNodeId |

### Node (Software) > Node (Software) > Node Service > Node Service > General - Node Service > NS Operation Timeline
Path: `Node (Software) > Node (Software) > Node Service > Node Service > General - Node Service > NS Operation Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NSTimeline | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Node Service > Node Service > General - Node Service > NS Operations for this Container from NodeServiceOperationEtwTable
Path: `Node (Software) > Node (Software) > Node Service > Node Service > General - Node Service > NS Operations for this Container from NodeServiceOperationEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NSOperationQuery | Table | azcore.centralus | Fa | starttime, endtime, nodeid, containerid, queryCheckThisContainer |

### Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > File Downloading Status from AgentNfcHttpDownloadFileEtwTable 
Path: `Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > File Downloading Status from AgentNfcHttpDownloadFileEtwTable `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query AgentNfcHttpDownloadFileEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > NodeServiceBootstrapEtwTable
Path: `Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > NodeServiceBootstrapEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeServiceBootstrapEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > NodeServiceExitEtwTable
Path: `Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > NodeServiceExitEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query NodeServiceExitEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > NodeServiceWatchdogEtwTable
Path: `Node (Software) > Node (Software) > Node Service > Node Service > More Supporting Logs for Node Service > NodeServiceWatchdogEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query NodeServiceWatchdogEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Node Update > Node Update > General > CM Node Update - TMMgmtNodeEventsEtwTable
Path: `Node (Software) > Node (Software) > Node Update > Node Update > General > CM Node Update - TMMgmtNodeEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostPlugin Update from TMMgmtNodeEventsEtwTable | Table | azcsupfollower | AzureCM | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Node Update > Node Update > General > Node Update Event - Event Log
Path: `Node (Software) > Node (Software) > Node Update > Node Update > General > Node Update Event - Event Log`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Update Event | Table | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Node Update > Node Update > General > PF Service Update - ServiceVersionSwitch
Path: `Node (Software) > Node (Software) > Node Update > Node Update > General > PF Service Update - ServiceVersionSwitch`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PF Updates on ServiceVersionSwitch | Table | azcsupfollower | AzureCM | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Node Update > Node Update > General > Scheduled Event for HostUpdate - AzPEWorkflowEvent
Path: `Node (Software) > Node (Software) > Node Update > Node Update > General > Scheduled Event for HostUpdate - AzPEWorkflowEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Scheduled Events from AzPEWorkflowEvent | Table | azpe | azpe | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Node Update > Node Update > OSHP Details > OsUpdateManagerEvents 
Path: `Node (Software) > Node (Software) > Node Update > Node Update > OSHP Details > OsUpdateManagerEvents `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query OsUpdateManagerEvents | Table | azcsupfollower | AzureCM | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Other Agents / Logs > HostAgentEventsEtwTable > HostAgentEventsEtwTable
Path: `Node (Software) > Node (Software) > Other Agents / Logs > HostAgentEventsEtwTable > HostAgentEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query HostAgentEventsEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Other Agents / Logs > HostGAPlugin > HostGAPluginContextActivityLogs
Path: `Node (Software) > Node (Software) > Other Agents / Logs > HostGAPlugin > HostGAPluginContextActivityLogs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostGAPluginContextActivityLogs | Table | https://azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Other Agents / Logs > HostGAPlugin > HostGAPluginRestApiLogs
Path: `Node (Software) > Node (Software) > Other Agents / Logs > HostGAPlugin > HostGAPluginRestApiLogs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostGAPluginRestApiLogs | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Other Agents / Logs > Ifx Operation > IfxOperationV2v1EtwTable
Path: `Node (Software) > Node (Software) > Other Agents / Logs > Ifx Operation > IfxOperationV2v1EtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query IfxOperationV2v1EtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNode |

### Node (Software) > Node (Software) > Other Agents / Logs > IMDS > IMDS > IMDS HeartBeat - MetadataServerLogTable
Path: `Node (Software) > Node (Software) > Other Agents / Logs > IMDS > IMDS > IMDS HeartBeat - MetadataServerLogTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Heartbeat in MetadataServerLogTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Other Agents / Logs > IMDS > IMDS > IMDS Requests - MetadataServerLogTable
Path: `Node (Software) > Node (Software) > Other Agents / Logs > IMDS > IMDS > IMDS Requests - MetadataServerLogTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query MetadataServerLogTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerId, queryTargetContainerOnly |

### Node (Software) > Node (Software) > Other Agents / Logs > IMDS > IMDS > Query Error or Specific Request in MetadataServerLogTable
Path: `Node (Software) > Node (Software) > Other Agents / Logs > IMDS > IMDS > Query Error or Specific Request in MetadataServerLogTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Error in MetadataServerLogTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryFilterKeyword |

### Node (Software) > Node (Software) > Other Agents / Logs > OS Logger > OS Logger
Path: `Node (Software) > Node (Software) > Other Agents / Logs > OS Logger > OS Logger`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query OsLoggerTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Other Agents / Logs > Pool Memory (Kernel) > Pool Memory (Kernel) > Details of Pool Memory Usage
Path: `Node (Software) > Node (Software) > Other Agents / Logs > Pool Memory (Kernel) > Pool Memory (Kernel) > Details of Pool Memory Usage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Pool Memory Details | Table | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Other Agents / Logs > Pool Memory (Kernel) > Pool Memory (Kernel) > Non-Paged Pool Memory - Top 15
Path: `Node (Software) > Node (Software) > Other Agents / Logs > Pool Memory (Kernel) > Pool Memory (Kernel) > Non-Paged Pool Memory - Top 15`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Kernel Pool Memory Usage | TimeSeries | azcore.centralus | Fa | starttime, nodeid, endtime |

### Node (Software) > Node (Software) > Other Agents / Logs > Pool Memory (Kernel) > Pool Memory (Kernel) > Paged Pool Memory - Top 15
Path: `Node (Software) > Node (Software) > Other Agents / Logs > Pool Memory (Kernel) > Pool Memory (Kernel) > Paged Pool Memory - Top 15`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Paged Pool Memory | TimeSeries | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Other Agents / Logs > VM Service (VMAL) > VM Service (VMAL) > VM Service - Events
Path: `Node (Software) > Node (Software) > Other Agents / Logs > VM Service (VMAL) > VM Service (VMAL) > VM Service - Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMServiceEvents | Table | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Other Agents / Logs > VM Service (VMAL) > VM Service (VMAL) > VM Service - Operations
Path: `Node (Software) > Node (Software) > Other Agents / Logs > VM Service (VMAL) > VM Service (VMAL) > VM Service - Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMServiceContainerOperations | Table | azcore.centralus | Fa | starttime, endtime, nodeid |

### Node (Software) > Node (Software) > Other Agents / Logs > VM Service (VMAL) > VM Service (VMAL) > VmServiceVirtualDiskOperations
Path: `Node (Software) > Node (Software) > Other Agents / Logs > VM Service (VMAL) > VM Service (VMAL) > VmServiceVirtualDiskOperations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query VmServiceVirtualDiskOperations | Table | https://azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### Node (Software) > Node (Software) > Other Agents / Logs > Wireserver > Wireserver > Wireserver Heartbeat
Path: `Node (Software) > Node (Software) > Other Agents / Logs > Wireserver > Wireserver > Wireserver Heartbeat`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | wireserverheartbeat | Table | azcore.centralus | Fa | nodeid, starttime, endtime |

### Node (Software) > Node (Software) > Other Agents / Logs > Wireserver > Wireserver > Wireserver Request Log
Path: `Node (Software) > Node (Software) > Other Agents / Logs > Wireserver > Wireserver > Wireserver Request Log`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query WireserverHttpRequestLogEtwTable | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId, queryContainerd, queryQueryCheckContainerOnly |

### Overlake / SoC
Path: `Overlake / SoC`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OverlakeNodeMap | Single | azcore.centralus | OvlProd | queryFrom, queryTo, queryNodeId |

### Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Cluster Health
Path: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Cluster Health`  ·  Queries: 5

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Fabricator Instance | Timeline | azurecm | AzureCM | starttime, endtime, cluster |
| 2 | Fabricator Downtime | Timeline | AzureCM | AzureCM | starttime, endtime, cluster |
| 3 | Allocatable State | Timeline | azurecm | AzureCM | starttime, endtime, cluster |
| 4 | Cluster Planned Maintenance | Timeline | azurecm | AzureCM | queryFrom, queryTo, queryClusterName |
| 5 | Cluster Service Healing | Timeline | aplat.westcentralus | Aplat | queryFrom, queryTo, queryClusterName |

### Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health
Path: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container / Tenant Health`  ·  Queries: 22

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

### Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container Transition
Path: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container Transition`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ContainerStateTransition | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, queryVmId, queryContainerId |
| 2 | ContainerOSStateTransition | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, queryVmId, queryContainerId |

### Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container Transition > Extended Error Details (If Any)
Path: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Container Transition > Extended Error Details (If Any)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Extended Container Error Details | Table | azurecm | azurecm | qFrom, qTo, qContainer |

### Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > CRP Operation
Path: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > CRP Operation`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP Operation Timeline | Timeline | azcrp | crp_allprod | starttime, endtime, vmid, queryInstanceName, querySubId |

### Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health
Path: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Network Health`  ·  Queries: 17

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

### Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health
Path: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Health`  ·  Queries: 21

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

### Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Update
Path: `Start Page > Start Page > At-A-Glance Availability > At-A-Glance Health > Node Update`  ·  Queries: 5

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PF Update | Timeline | azurecm | AzureCM | queryFrom, queryTo, queryNodeId |
| 2 | Host Update | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |
| 3 | CM Node Update | Timeline | azurecm | AzureCM | queryFrom, queryTo, queryNodeId |
| 4 | AzPE Update | Timeline | azpe | azpe | queryFrom, queryTo, queryNodeId |
| 5 | FPGA Update | Timeline | azcore.centralus | Fa | starttime, endtime, nodeid |

### Start Page > Start Page > At-A-Glance Performance  > Container Performance Metrics (Node / Internal View)
Path: `Start Page > Start Page > At-A-Glance Performance  > Container Performance Metrics (Node / Internal View)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ContainerPerformance | TimeSeries | azcore.centralus | Fa | starttime, endtime, containerid |

### Start Page > Start Page > At-A-Glance Performance  > Container Performance Metrics (Shoebox Source / Customer View)
Path: `Start Page > Start Page > At-A-Glance Performance  > Container Performance Metrics (Shoebox Source / Customer View)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Performance Shoebox | TimeSeries | azcore.centralus | Fa | starttime, endtime, nodeid, containerid |

### Start Page > Start Page > VMA > VM Availability > VMA for this Subscription
Path: `Start Page > Start Page > VMA > VM Availability > VMA for this Subscription`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMA filter by Subscription | Table | vmainsight | vmadb | queryFrom, queryTo, queryContainerId |

### Start Page > Start Page > VMA > VM Availability > VMA on Node > VMA on Node > VMA Event on Node
Path: `Start Page > Start Page > VMA > VM Availability > VMA on Node > VMA on Node > VMA Event on Node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMAQuery | Table | vmainsight | vmadb | starttime, endtime, nodeid |

### Start Page > Start Page > VMA > VM Availability > VMA on Node > VMA on Node > VMA Timeline on Node
Path: `Start Page > Start Page > VMA > VM Availability > VMA on Node > VMA on Node > VMA Timeline on Node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Impacted VM | Timeline | vmainsight | vmadb | starttime, endtime, nodeid |

### Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > AIR Events
Path: `Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > AIR Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AIR-R & AIR-BP | Table | vmainsight | Air | starttime, endtime, vmid |

### Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > VMA / AIR Event Timeline
Path: `Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > VMA / AIR Event Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AIR & VMA Timeline | CoBeTimeline | vmainsight | Air | starttime, endtime, vmid |

### Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > VMA Event on VM ID
Path: `Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > VMA Event on VM ID`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMA Event on VM ID | Table | vmainsight | vmadb | starttime, endtime, vmid, queryContainerId |

### Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > VMA Timeline on VM ID
Path: `Start Page > Start Page > VMA > VM Availability > VMA on VM Id > VMA on VM Id > VMA Timeline on VM ID`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMA on VM ID | Timeline | vmainsight | vmadb | starttime, endtime, vmid |

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
