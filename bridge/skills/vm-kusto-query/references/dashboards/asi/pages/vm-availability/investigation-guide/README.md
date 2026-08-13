# EEE RDOS — VM Availability — Investigation Guide

Chapter-keyed reference derived from the **EEE RDOS — VM Availability** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

**How to use:**

1. Identify which dashboard chapter matches what you're investigating.
2. Open the matching section file from the list below.
3. Pick the query whose name / source panel / filter tips match your symptom.
4. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.
5. Execute via the **vm-kusto-query** skill (`kusto_runner.py`) or via the `replay.py` next to this folder (handles param aliases).

**Companion files (in parent folder):**

- `library.json` — canonical machine-readable source of all queries (panel-organized).
- `library.md`   — same content as flat human-readable index.
- `meta.json`    — pageId, totals, ASI URL.

## Files

- [(top-level)](01-top-level.md) — 3 queries
- [Automated Detector](02-automated-detector.md) — 59 queries
- [Container](03-container.md) — 25 queries
- [CRP / Operation](04-crp-operation.md) — 5 queries
- [Disk & XDisk](05-disk-xdisk.md) — 7 queries
- [Fabric / Tenant](06-fabric-tenant.md) — 29 queries
- [General Tool Links](07-general-tool-links.md) — 3 queries
- [Hyper-V](08-hyper-v.md) — 7 queries
- [Network / TOR](09-network-tor.md) — 3 queries
- [Network](10-network.md) — 9 queries
- [Node (Hardware)](11-node-hardware.md) — 11 queries
- [Node (Physical)](12-node-physical.md) — 1 queries
- [Node (Software)](13-node-software.md) — 49 queries
- [Overlake / SoC](14-overlake-soc.md) — 1 queries
- [Start Page](15-start-page.md) — 83 queries
- [Tenant / Container / Node](16-tenant-container-node.md) — 1 queries
- [VM](17-vm.md) — 4 queries

**Total queries: 300**

## Query index (by file)

### (top-level)

- Retrieve Resource "VM Availability" — see [01-top-level.md](01-top-level.md)
- OverlakeNodeMap — see [01-top-level.md](01-top-level.md)
- GetShoeboxAccount — see [01-top-level.md](01-top-level.md)

### Automated Detector

- IssueDetector_NetworkIssues — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_AzSMServiceHealing — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_TooManyUnhealthyNode — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_StopDestroy Fails with STORVSP_VspDeviceCreate* — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_SoC_Crash — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_RHSendsIncorrectVMAvailableStateRepeatedly — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_DppPluginOrPfDatapathServiceRequired — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_CreateContainer_fails_with_0x80070002_L-Series — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_CreateContainer_failed_with_0xc3510153 — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_VM reboot when trying to detach disks  — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_EQ stuck_on_EQn_0x4 — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_AirDiskBlip_BlobCache_Write_during_Congestion — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_NV6_v5_VMs_Fail_to_Start_due_to_Low_Memory — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_CRUD operationFailuresDueToContainerWorkflow* — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_Resource_Health_Unavailable_for_Linux_6.2Kernel — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_High_Flush_latencies_due_to_driver_issue — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_NetAssistMonitorTriggers_LM — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_TORFailures — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_TOR_DegradedUnhealthyEvents — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_SoC_Update — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_HostNetworkIssue_FPGA_GFT_Unhealthy_on_Overlake — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_LM_failure_VFPRestoreFailure_NmAgentEventDelay — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_Standard_ND96isr_H100_v5_HardwareFault_pCIfata — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_Attaching_Multiple_DataDisks_Over_Nvme_restart — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_OSProvisioningTimedOut_failure_DHCP_lease — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_AKS_Linux_instances_are_reported_as_Windows — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_Dalds_v6_Windows_2025_datadisk_perf — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_LM_VFPRestoreFailure_Deserialization_Issue_Port — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_NVME_HW_troubleshooting — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_node_bugcheck_0x50_netdatapath — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_StagingNodeImagesGen9 — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_Backplane_service_crash_on_SoC_impacts_VM — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_Node Crash_due_to_0xBC0000D6_BlobCache!BcRefere — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_GPC_VMs_Fail_to_Start_IBManagerError_0x800704c — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_Ultra_PremV2_DiskBlip_during_VDC_driver_update — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_v6VM_TPM_fails_start_due_to_Underhill_VM — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_node bugcheck_0xd1_AV_blobcache!BcPfnReferenc — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_Unable_to_create_VM_VMAL_error_0x8000ffff — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_TOR_Update — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_Node_Restart_Due_to_Planned_Maintenance — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_UnallocatableNode_DestroyContainer_0x8abc0503 — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_bugcheck_0xd1_AV_Barbera!HbLldCompleteIrpOve — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_Unallocatable_Node_due_to_XDisk_leaks — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_Local_NVMe_Disks_Are_Missing_In_Lv4_Series — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_LM_SH_due_to_NVMe_Device_End_of_Life — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_LMFailed_FlexibleIODeviceRestore — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_NetworkContainer_AllocationIncarnation — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_LMFailed_VFPSerializationIssue_0x5aa — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_NVMeVmHighDiskLatency_due_to_CacheHint — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_Sudden_Power_Loss_of_host_node — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_Booting_of_host_node_detected — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_HighHostCPU_temp_throttle — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_HighHostCPU_throttle — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_NVMe_Controller_VM_experience_stornvme_reset — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_VMA_bugcheck_0x20001_HYPERVISOR_ERROR — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_AW_bugcheck_0x20001_HYPERVISOR_ERROR — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_LMFailed_VFPSerializationIssue_0x5aa_2 — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_EI_VM_creation_failure_0xc3510224_VMAL_ASAPPF — see [02-automated-detector.md](02-automated-detector.md)
- IssueDetector_E17_Key_Vault_Encryption_Key_not_found — see [02-automated-detector.md](02-automated-detector.md)

### Container

- Anvil Event — see [03-container.md](03-container.md)
- Anvil Operation — see [03-container.md](03-container.md)
- Anvil Event Trigger — see [03-container.md](03-container.md)
- Azure Host VM Blobs — see [03-container.md](03-container.md)
- Query PaaS Container in  LogContainerSnapshot — see [03-container.md](03-container.md)
- Container Event — see [03-container.md](03-container.md)
- Query PaaS Container in LogContainerHealthSnapshot — see [03-container.md](03-container.md)
- FilterStates — see [03-container.md](03-container.md)
- Container Performance for Container Id — see [03-container.md](03-container.md)
- FilterStates — see [03-container.md](03-container.md)
- Query LogRoleInstanceSnapshot — see [03-container.md](03-container.md)
- Query PaaS Container in VmHealthRawStateEtwTable — see [03-container.md](03-container.md)
- FilterStates — see [03-container.md](03-container.md)
- GuestAgentAndExtensionTimeline — see [03-container.md](03-container.md)
- Guest OS Logs — see [03-container.md](03-container.md)
- GuestOSGenericLogs — see [03-container.md](03-container.md)
- Container Change History — see [03-container.md](03-container.md)
- FilterStates — see [03-container.md](03-container.md)
- LogContainerHealthSnapshot — see [03-container.md](03-container.md)
- FilterStates — see [03-container.md](03-container.md)
- HyperV states from VmHealthRawStateEtwTable — see [03-container.md](03-container.md)
- Query LogRoleInstanceSnapshot — see [03-container.md](03-container.md)
- Query FaComputeHourUsageEventCentralBondTable — see [03-container.md](03-container.md)
- Query LogHealthAnnotationEvent — see [03-container.md](03-container.md)
- Query RhcAnnotationReportsEtwTable — see [03-container.md](03-container.md)

### CRP / Operation

- CRP VM Snapshot — see [04-crp-operation.md](04-crp-operation.md)
- CRP Operations — see [04-crp-operation.md](04-crp-operation.md)
- filterCRP — see [04-crp-operation.md](04-crp-operation.md)
- CRP Operation Timeline — see [04-crp-operation.md](04-crp-operation.md)
- Fabric Callback to CRP — see [04-crp-operation.md](04-crp-operation.md)

### Disk & XDisk

- SCSI Disk Perf — see [05-disk-xdisk.md](05-disk-xdisk.md)
- Disk Event in Node Windows Event — see [05-disk-xdisk.md](05-disk-xdisk.md)
- BlobCache — see [05-disk-xdisk.md](05-disk-xdisk.md)
- Query Storeport Events — see [05-disk-xdisk.md](05-disk-xdisk.md)
- Query Storport Event Timeline — see [05-disk-xdisk.md](05-disk-xdisk.md)
- Query OsVhddiskEventTable — see [05-disk-xdisk.md](05-disk-xdisk.md)
- Query VhdDiskEtwEventTable — see [05-disk-xdisk.md](05-disk-xdisk.md)

### Fabric / Tenant

- Allocation Limit — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Allocatable State — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Node Count — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Util Core — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Util Memory — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Fabricator Instance — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Fabricator Downtime — see [06-fabric-tenant.md](06-fabric-tenant.md)
- NodeStateHumanInvestigateCount — see [06-fabric-tenant.md](06-fabric-tenant.md)
- NodeStateReadyCount — see [06-fabric-tenant.md](06-fabric-tenant.md)
- NodeStateOFRCount — see [06-fabric-tenant.md](06-fabric-tenant.md)
- NodeStateReadyCount — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Unhealthy Node Count — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Quyry HolmesGoalStateManagerEvent — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query LiveMigrationSessionCompleteLog — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query LiveMigrationSessionStatusEventLog — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query TMMgmtNodeEventsEtwTable — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query TMMgmtNodeTraceEtwTable — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Tenant Scheduled Events — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Scheduled Events Enablement Status — see [06-fabric-tenant.md](06-fabric-tenant.md)
- TMMgmtTenantManagementJobInfoEtwTable — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query Tenant in AzPEWorkflowEvent — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query AzSMServiceHealingResultEvents — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query AzSMServiceHealingStepResultEvents — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query AzSMServiceHealingTriggerEvents — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query ServiceHealingTenantStatusEtwTable — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query ServiceHealingTriggerEtwTable — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query AzSMTenantEvents — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query AzSMTenantStatemachineEvents — see [06-fabric-tenant.md](06-fabric-tenant.md)
- Query TMMgmtTenantEventsEtwTable — see [06-fabric-tenant.md](06-fabric-tenant.md)

### General Tool Links

- JarvisDashTimeHelper — see [07-general-tool-links.md](07-general-tool-links.md)
- VmssIdHelper — see [07-general-tool-links.md](07-general-tool-links.md)
- Unix Time Helper — see [07-general-tool-links.md](07-general-tool-links.md)

### Hyper-V

- Hyper-V Event Timeline — see [08-hyper-v.md](08-hyper-v.md)
- Hyper-V Events — see [08-hyper-v.md](08-hyper-v.md)
- VMSS Table — see [08-hyper-v.md](08-hyper-v.md)
- Hyper-V Worker Timeline — see [08-hyper-v.md](08-hyper-v.md)
- Query HyperVAnalyticEvents — see [08-hyper-v.md](08-hyper-v.md)
- Query HyperVStorageStackTable — see [08-hyper-v.md](08-hyper-v.md)
- Query HyperVVmmsTable — see [08-hyper-v.md](08-hyper-v.md)

### Network / TOR

- TorDeviceInfo — see [09-network-tor.md](09-network-tor.md)
- Unix Time Helper — see [09-network-tor.md](09-network-tor.md)
- vfpMDM — see [09-network-tor.md](09-network-tor.md)

### Network

- Windows Event Log for Networking — see [10-network.md](10-network.md)
- Timeline for Windows Event Log related to Network Component — see [10-network.md](10-network.md)
- Query InterfaceProgramEndFiveMinuteTable — see [10-network.md](10-network.md)
- Query DCMNMAgentProgrammingDurationEtwTable — see [10-network.md](10-network.md)
- Query SoC Bugchecks — see [10-network.md](10-network.md)
- Query SoC Crash — see [10-network.md](10-network.md)
- Query Soc Memory Usage — see [10-network.md](10-network.md)
- Query SoC CPU — see [10-network.md](10-network.md)
- Query Soc Memory Usage — see [10-network.md](10-network.md)

### Node (Hardware)

- HardwareEvent — see [11-node-hardware.md](11-node-hardware.md)
- SparkleSELByNodeId — see [11-node-hardware.md](11-node-hardware.md)
- Hardware Resource Event — see [11-node-hardware.md](11-node-hardware.md)
- DCM Node State — see [11-node-hardware.md](11-node-hardware.md)
- PilotFish State — see [11-node-hardware.md](11-node-hardware.md)
- Windows Event Log for Hardware — see [11-node-hardware.md](11-node-hardware.md)
- Windows Event Log for Hardware — see [11-node-hardware.md](11-node-hardware.md)
- Query CPU from dcmInventoryComponentCPUV2Direct — see [11-node-hardware.md](11-node-hardware.md)
- Query dcmInventoryComponentDiskHistory — see [11-node-hardware.md](11-node-hardware.md)
- Query dcmInventoryComponentDiskUtilDirect — see [11-node-hardware.md](11-node-hardware.md)
- Query DIMM from dcmInventoryComponentDIMMDirect — see [11-node-hardware.md](11-node-hardware.md)

### Node (Physical)

- Node Hardware Properties — see [12-node-physical.md](12-node-physical.md)

### Node (Software)

- AzureWatsonQuery — see [13-node-software.md](13-node-software.md)
- Node Container Performance — see [13-node-software.md](13-node-software.md)
- Node Container List — see [13-node-software.md](13-node-software.md)
- TImeline_ContainerOSState — see [13-node-software.md](13-node-software.md)
- Node Container Timeline — see [13-node-software.md](13-node-software.md)
- HyperV Heartbeat for Containers — see [13-node-software.md](13-node-software.md)
- Storage — see [13-node-software.md](13-node-software.md)
- NodeWindowsEvent — see [13-node-software.md](13-node-software.md)
- FilterNodeState — see [13-node-software.md](13-node-software.md)
- LogNodeSnapshot — see [13-node-software.md](13-node-software.md)
- ContainerConunt — see [13-node-software.md](13-node-software.md)
- NodeStateQuery — see [13-node-software.md](13-node-software.md)
- Node WasChannel Health Status — see [13-node-software.md](13-node-software.md)
- Node WillBe Channel Health Status — see [13-node-software.md](13-node-software.md)
- PfAgent Status — see [13-node-software.md](13-node-software.md)
- PilotFish State — see [13-node-software.md](13-node-software.md)
- ApSvcMgr Status — see [13-node-software.md](13-node-software.md)
- ApLauncher Status — see [13-node-software.md](13-node-software.md)
- Node Service Status — see [13-node-software.md](13-node-software.md)
- WireService Status — see [13-node-software.md](13-node-software.md)
- Query NodeServiceEventEtwTable — see [13-node-software.md](13-node-software.md)
- Detector for NodeServiceEventEtwTable — see [13-node-software.md](13-node-software.md)
- NSTimeline — see [13-node-software.md](13-node-software.md)
- NSOperationQuery — see [13-node-software.md](13-node-software.md)
- Query AgentNfcHttpDownloadFileEtwTable — see [13-node-software.md](13-node-software.md)
- NodeServiceBootstrapEtwTable — see [13-node-software.md](13-node-software.md)
- Query NodeServiceExitEtwTable — see [13-node-software.md](13-node-software.md)
- Query NodeServiceWatchdogEtwTable — see [13-node-software.md](13-node-software.md)
- HostPlugin Update from TMMgmtNodeEventsEtwTable — see [13-node-software.md](13-node-software.md)
- Node Update Event — see [13-node-software.md](13-node-software.md)
- PF Updates on ServiceVersionSwitch — see [13-node-software.md](13-node-software.md)
- Scheduled Events from AzPEWorkflowEvent — see [13-node-software.md](13-node-software.md)
- Query OsUpdateManagerEvents — see [13-node-software.md](13-node-software.md)
- Query HostAgentEventsEtwTable — see [13-node-software.md](13-node-software.md)
- HostGAPluginContextActivityLogs — see [13-node-software.md](13-node-software.md)
- HostGAPluginRestApiLogs — see [13-node-software.md](13-node-software.md)
- Query IfxOperationV2v1EtwTable — see [13-node-software.md](13-node-software.md)
- Query Heartbeat in MetadataServerLogTable — see [13-node-software.md](13-node-software.md)
- Query MetadataServerLogTable — see [13-node-software.md](13-node-software.md)
- Query Error in MetadataServerLogTable — see [13-node-software.md](13-node-software.md)
- Query OsLoggerTable — see [13-node-software.md](13-node-software.md)
- Pool Memory Details — see [13-node-software.md](13-node-software.md)
- Kernel Pool Memory Usage — see [13-node-software.md](13-node-software.md)
- Paged Pool Memory — see [13-node-software.md](13-node-software.md)
- VMServiceEvents — see [13-node-software.md](13-node-software.md)
- VMServiceContainerOperations — see [13-node-software.md](13-node-software.md)
- Query VmServiceVirtualDiskOperations — see [13-node-software.md](13-node-software.md)
- wireserverheartbeat — see [13-node-software.md](13-node-software.md)
- Query WireserverHttpRequestLogEtwTable — see [13-node-software.md](13-node-software.md)

### Overlake / SoC

- OverlakeNodeMap — see [14-overlake-soc.md](14-overlake-soc.md)

### Start Page

- Fabricator Instance — see [15-start-page.md](15-start-page.md)
- Fabricator Downtime — see [15-start-page.md](15-start-page.md)
- Allocatable State — see [15-start-page.md](15-start-page.md)
- Cluster Planned Maintenance — see [15-start-page.md](15-start-page.md)
- Cluster Service Healing — see [15-start-page.md](15-start-page.md)
- Container State — see [15-start-page.md](15-start-page.md)
- Container OS State — see [15-start-page.md](15-start-page.md)
- Hyper-V Heartbeat State — see [15-start-page.md](15-start-page.md)
- Hyper-V Power State — see [15-start-page.md](15-start-page.md)
- VMAvailabilityMetric — see [15-start-page.md](15-start-page.md)
- Container Lifecycle — see [15-start-page.md](15-start-page.md)
- Container Fault — see [15-start-page.md](15-start-page.md)
- Node Service Error - Container — see [15-start-page.md](15-start-page.md)
- VMAL Ops — see [15-start-page.md](15-start-page.md)
- Hyper-V Events — see [15-start-page.md](15-start-page.md)
- Hyper-V StorageStack — see [15-start-page.md](15-start-page.md)
- Tenant Scheduled Events — see [15-start-page.md](15-start-page.md)
- Anvil Event - Container — see [15-start-page.md](15-start-page.md)
- Container Live Migration — see [15-start-page.md](15-start-page.md)
- Service Healing(TM) — see [15-start-page.md](15-start-page.md)
- Service Healing(AzSM) — see [15-start-page.md](15-start-page.md)
- Planned Maintenance — see [15-start-page.md](15-start-page.md)
- Holmes Events — see [15-start-page.md](15-start-page.md)
- RH Annotation Report — see [15-start-page.md](15-start-page.md)
- VMA Event — see [15-start-page.md](15-start-page.md)
- AIR Events — see [15-start-page.md](15-start-page.md)
- ICM Report — see [15-start-page.md](15-start-page.md)
- ContainerStateTransition — see [15-start-page.md](15-start-page.md)
- ContainerOSStateTransition — see [15-start-page.md](15-start-page.md)
- Get Extended Container Error Details — see [15-start-page.md](15-start-page.md)
- CRP Operation Timeline — see [15-start-page.md](15-start-page.md)
- ToR-Hosts PingMesh — see [15-start-page.md](15-start-page.md)
- Host-ToR PingMesh — see [15-start-page.md](15-start-page.md)
- ToR Health Event — see [15-start-page.md](15-start-page.md)
- ToR Update — see [15-start-page.md](15-start-page.md)
- ToR - Anvil Event — see [15-start-page.md](15-start-page.md)
- Wireserver Heartbeat — see [15-start-page.md](15-start-page.md)
- NMAgent Health — see [15-start-page.md](15-start-page.md)
- NMAgent Event — see [15-start-page.md](15-start-page.md)
- NM Programming — see [15-start-page.md](15-start-page.md)
- SoC OS Update — see [15-start-page.md](15-start-page.md)
- SoC Pilot Fish State — see [15-start-page.md](15-start-page.md)
- SoC PF Update — see [15-start-page.md](15-start-page.md)
- SoC Signal Event — see [15-start-page.md](15-start-page.md)
- SoC Azure Watson — see [15-start-page.md](15-start-page.md)
- SoC - Anvil Event — see [15-start-page.md](15-start-page.md)
- SoC VNetAgent Event — see [15-start-page.md](15-start-page.md)
- SoC Systemd Event — see [15-start-page.md](15-start-page.md)
- DCM Node State — see [15-start-page.md](15-start-page.md)
- DCM Node Fault — see [15-start-page.md](15-start-page.md)
- DCM SEL (Sparkle) — see [15-start-page.md](15-start-page.md)
- DCM SEL — see [15-start-page.md](15-start-page.md)
- Root Update Alloc Type — see [15-start-page.md](15-start-page.md)
- Node State — see [15-start-page.md](15-start-page.md)
- Node Availability — see [15-start-page.md](15-start-page.md)
- Node Fault — see [15-start-page.md](15-start-page.md)
- Node WillBe Channel Health Status — see [15-start-page.md](15-start-page.md)
- Node WasChannel Health Status — see [15-start-page.md](15-start-page.md)
- Node Service Error — see [15-start-page.md](15-start-page.md)
- VMAL Error — see [15-start-page.md](15-start-page.md)
- Node Live Migration — see [15-start-page.md](15-start-page.md)
- Anvil Event - Node — see [15-start-page.md](15-start-page.md)
- Kernel/Driver Events — see [15-start-page.md](15-start-page.md)
- Remarkable Event - Disk — see [15-start-page.md](15-start-page.md)
- Remarkable Event - WHEA — see [15-start-page.md](15-start-page.md)
- Remarkable Event - Memory — see [15-start-page.md](15-start-page.md)
- Remarkable Event - HyperV — see [15-start-page.md](15-start-page.md)
- Azure Watson — see [15-start-page.md](15-start-page.md)
- Hyper-V State — see [15-start-page.md](15-start-page.md)
- PF Update — see [15-start-page.md](15-start-page.md)
- Host Update — see [15-start-page.md](15-start-page.md)
- CM Node Update — see [15-start-page.md](15-start-page.md)
- AzPE Update — see [15-start-page.md](15-start-page.md)
- FPGA Update — see [15-start-page.md](15-start-page.md)
- ContainerPerformance — see [15-start-page.md](15-start-page.md)
- Container Performance Shoebox — see [15-start-page.md](15-start-page.md)
- VMA filter by Subscription — see [15-start-page.md](15-start-page.md)
- VMAQuery — see [15-start-page.md](15-start-page.md)
- Impacted VM — see [15-start-page.md](15-start-page.md)
- AIR-R & AIR-BP — see [15-start-page.md](15-start-page.md)
- AIR & VMA Timeline — see [15-start-page.md](15-start-page.md)
- VMA Event on VM ID — see [15-start-page.md](15-start-page.md)
- VMA on VM ID — see [15-start-page.md](15-start-page.md)

### Tenant / Container / Node

- Container Features — see [16-tenant-container-node.md](16-tenant-container-node.md)

### VM

- PageInputHelper — see [17-vm.md](17-vm.md)
- GetARMResourceId — see [17-vm.md](17-vm.md)
- GetShoeboxAccount — see [17-vm.md](17-vm.md)
- VmssIdHelper — see [17-vm.md](17-vm.md)
