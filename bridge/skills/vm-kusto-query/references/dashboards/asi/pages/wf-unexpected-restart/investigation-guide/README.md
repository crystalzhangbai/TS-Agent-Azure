# EEE RDOS — WF Unexpected Restart — Investigation Guide

Chapter-keyed reference derived from the **EEE RDOS — WF Unexpected Restart** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 15 queries
- [Container Investigation](02-container-investigation.md) — 13 queries
- [Emerging Issues (part 1/4)](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md) — 13 queries
- [Emerging Issues — High Flush latencies due to driver issue](03b-emerging-issues--high-flush-latencies-due-to-driver-issue.md) — 1 queries
- [Emerging Issues (part 3/4)](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md) — 31 queries
- [Emerging Issues (part 4/4)](03d-emerging-issues--vm-impacted-after-host-agent-update.md) — 9 queries
- [Hardware Investigation](04-hardware-investigation.md) — 16 queries
- [Live Migration](05-live-migration.md) — 19 queries
- [Node Investigation](06-node-investigation.md) — 53 queries
- [Planned Maintenance](07-planned-maintenance.md) — 13 queries
- [Service Healing](08-service-healing.md) — 12 queries
- [Update Investigation](09-update-investigation.md) — 13 queries

**Total queries: 208**

## Query index (by file)

### (top-level)

- VM stop check — see [01-top-level.md](01-top-level.md)
- VM shutdown check — see [01-top-level.md](01-top-level.md)
- VM guest OS shutdown — see [01-top-level.md](01-top-level.md)
- Sudden power loss logged — see [01-top-level.md](01-top-level.md)
- Power Supply input lost — see [01-top-level.md](01-top-level.md)
- VmStart_failed_Host_LowMem — see [01-top-level.md](01-top-level.md)
- Container Info_UnexpectedRestart DS — see [01-top-level.md](01-top-level.md)
- Retrieve Resource "VM" Unexpected Restart DS — see [01-top-level.md](01-top-level.md)
- vfpMDM — see [01-top-level.md](01-top-level.md)
- TimeCalcFrom — see [01-top-level.md](01-top-level.md)
- TimeCalcTo — see [01-top-level.md](01-top-level.md)
- Unix Time Helper — see [01-top-level.md](01-top-level.md)
- LM check — see [01-top-level.md](01-top-level.md)
- SOCNodeId — see [01-top-level.md](01-top-level.md)
- OverlakeNodeMap — see [01-top-level.md](01-top-level.md)

### Container Investigation

- CAD_UnexpectedRestart DS — see [02-container-investigation.md](02-container-investigation.md)
- LogContainerHealthSnapshot_UnexpectedRestart DS — see [02-container-investigation.md](02-container-investigation.md)
- LogContainerSnapshot_UnexpectedRestart DS — see [02-container-investigation.md](02-container-investigation.md)
- TMMgmtContainerTraceEtwTable DS — see [02-container-investigation.md](02-container-investigation.md)
- GuestAgentLogs DS — see [02-container-investigation.md](02-container-investigation.md)
- GuestOSDetails DS — see [02-container-investigation.md](02-container-investigation.md)
- TMMgmtSlaMeasurementEventEtwTable_UnexpectedRestart2 DS — see [02-container-investigation.md](02-container-investigation.md)
- TMMgmtTenantChangeProfilingEventEtwTable — see [02-container-investigation.md](02-container-investigation.md)
- TMMgmtTenantEventsEtwTable DS — see [02-container-investigation.md](02-container-investigation.md)
- GetVMRestartEvents DS — see [02-container-investigation.md](02-container-investigation.md)
- VMA5 DS — see [02-container-investigation.md](02-container-investigation.md)
- VmHealthRawStateEtwTable_UnexpectedRestart DS — see [02-container-investigation.md](02-container-investigation.md)
- VmServiceContainerOperations — see [02-container-investigation.md](02-container-investigation.md)

### Emerging Issues (part 1/4)

-  RH Sends Incorrect VM Availability state repeatedly — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- "EQ stuck" on EQn 0x4 DS — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- HyperVStorageStackAndBlobcacheInternal_EE — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- AKS_Linux_instances_are_reported_as_Windows — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- Attaching_Multiple_DataDisks_Over_Nvme_may_lead_to_VM_Restart — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- SoC_impacts_VM_accessibility — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- DppPluginOrPfDatapathServiceRequired — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- CreateContainer_failed_with_0xc3510153 — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- CreateContainer fails with 0x80070002 ERROR_FILE_NOT_FOUND — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- CRUDoperationFailuresDueTo"MissingStorageConfigurationsWillbe" — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- Dalds_v6_Windows_2025_datadisk_perf  — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- ASAP_completed_IOs — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)
- GPC_VMs_Fail_to_Start_IBManagerError_0x800704cd — see [03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md](03a-emerging-issues--resource-health-sends-incorrect-vm-availability-state-repeatedly.md)

### Emerging Issues — High Flush latencies due to driver issue

- HighFlushLatenciesDueToDriverIssue — see [03b-emerging-issues--high-flush-latencies-due-to-driver-issue.md](03b-emerging-issues--high-flush-latencies-due-to-driver-issue.md)

### Emerging Issues (part 3/4)

- HostNetworkIssue_FPGA_GFT_Unhealthy — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- stagingnodeimagesGen9 — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- LMFailed_FlexibleIODeviceRestoreFailure — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- LMSHduetoNVMeDeviceEndofLife — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- LMfailure_VFPRestoreFailure_Serialization_Issue_0x5aa_2 — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- LMfailure_VFPRestoreFailure_Serialization_Issue_0x5aa — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- VFPRestoreFailure_Deserialization_Issue_Port_0x51a — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- LM_failure_due_to_VFPRestoreFailure_NmAgentEventDelay — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- LocalNVMeDisksAreMissingInLv4series — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- IssueDetector_EI_AW_Check_0x20001_HYPERVISOR_ERROR — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- IssueDetector_EI_VMA_Check_Multiple_host_nodes_crashed_with_0x20 — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- NetAssist_LM — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- nodebugcheck_after_netdatapathupdate — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- NodeCrash_0xBC0000D6_BlobCache!BcReferenceTailPfnList — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- NV6_v5_VMs_Fail_to_Start_due_to_Low_Memory — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- NVMeControllerVMexperienceStornvmeResetOrBugcheck — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- NVMeVMhighdisklatency_dueto_CacheHintNoisyNeighbor — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- OSProvisioningTimedOut_DHCP_VNET_encryption_enabled — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- RH_Unavailable_Linux_6_2 — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- StagingNodeImages — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- Standard_ND96isr_H100_v5_HardwareFault_pCIfata — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- StopDestroy:STORVSP_VspDeviceCreate_ParserOverride_Avhdparser — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- Ultra_PremV2_DiskBlip_during_VDC_driver_update — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- VMAL_error_0x8000ffff — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- UnallocatableNode_XDiskleaks — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- UnallocatableNode_DestroyContainer_0x8abc0503 — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- bugcheck_0xd1_AV_Barbera!HbLldCompleteIrpOverlay — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- node_bugcheck_0xd1_AV_blobcache!BcPfnReferenceByCacheStorePfnA — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- EI_NetworkContainerAllocationIncarnation — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- v6VM_TPM_fails_start_due_to_Underhill_VM_initialization — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)
- VM_creation_failure_0xc3510224_VMAL_ASAPPF_NOT_RUNNING — see [03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md](03c-emerging-issues--hostnetworkissue-fpga-gft-unhealthy-on-overlake-nodes.md)

### Emerging Issues (part 4/4)

- LogContainerHealthSnapshot — see [03d-emerging-issues--vm-impacted-after-host-agent-update.md](03d-emerging-issues--vm-impacted-after-host-agent-update.md)
- TMMgmtNodeEventsEtwTable_UnexpectedRestart DS — see [03d-emerging-issues--vm-impacted-after-host-agent-update.md](03d-emerging-issues--vm-impacted-after-host-agent-update.md)
- VMA2 DS — see [03d-emerging-issues--vm-impacted-after-host-agent-update.md](03d-emerging-issues--vm-impacted-after-host-agent-update.md)
- HyperVStorageStackTable_all DS — see [03d-emerging-issues--vm-impacted-after-host-agent-update.md](03d-emerging-issues--vm-impacted-after-host-agent-update.md)
- HyperVStorageStackTable_vhdmp DS — see [03d-emerging-issues--vm-impacted-after-host-agent-update.md](03d-emerging-issues--vm-impacted-after-host-agent-update.md)
- HyperVStorageStackTable_writeError DS — see [03d-emerging-issues--vm-impacted-after-host-agent-update.md](03d-emerging-issues--vm-impacted-after-host-agent-update.md)
- VM reboot when trying to detach disks — see [03d-emerging-issues--vm-impacted-after-host-agent-update.md](03d-emerging-issues--vm-impacted-after-host-agent-update.md)
- CAD_StandardStorage DS — see [03d-emerging-issues--vm-impacted-after-host-agent-update.md](03d-emerging-issues--vm-impacted-after-host-agent-update.md)
- WindowsEvents_Internalrestart DS — see [03d-emerging-issues--vm-impacted-after-host-agent-update.md](03d-emerging-issues--vm-impacted-after-host-agent-update.md)

### Hardware Investigation

- FaultDescriptions — see [04-hardware-investigation.md](04-hardware-investigation.md)
- NumbHostsCluster — see [04-hardware-investigation.md](04-hardware-investigation.md)
- NumbHostsClusterNotProd — see [04-hardware-investigation.md](04-hardware-investigation.md)
- DCM HW Events DS — see [04-hardware-investigation.md](04-hardware-investigation.md)
- HW Repair Events DS — see [04-hardware-investigation.md](04-hardware-investigation.md)
- ResourceSnapshotHistoryV1_Unfiltered DS — see [04-hardware-investigation.md](04-hardware-investigation.md)
- BladeMemoryCorrectedFull — see [04-hardware-investigation.md](04-hardware-investigation.md)
- NVMEHWissues — see [04-hardware-investigation.md](04-hardware-investigation.md)
- NVMEDevRCA — see [04-hardware-investigation.md](04-hardware-investigation.md)
- NVMeHealthLog — see [04-hardware-investigation.md](04-hardware-investigation.md)
- RhwChassisSelItemEtwTable DS — see [04-hardware-investigation.md](04-hardware-investigation.md)
- SparkleSEL DS — see [04-hardware-investigation.md](04-hardware-investigation.md)
- SEL filtered DS — see [04-hardware-investigation.md](04-hardware-investigation.md)
- Whea DS — see [04-hardware-investigation.md](04-hardware-investigation.md)
- WindowsEventsFilteredHW DS — see [04-hardware-investigation.md](04-hardware-investigation.md)
- WindowsStorageEvents — see [04-hardware-investigation.md](04-hardware-investigation.md)

### Live Migration

- AirLiveMigrationEventsL30d — see [05-live-migration.md](05-live-migration.md)
- HolmesSubscriptionMetadataEvents — see [05-live-migration.md](05-live-migration.md)
- HolmesEvents — see [05-live-migration.md](05-live-migration.md)
- HolmesRHMNodeVacateStatusEvent — see [05-live-migration.md](05-live-migration.md)
- HolmesGoalStateManagerEvent — see [05-live-migration.md](05-live-migration.md)
- LiveMigrationSessionValidationCriticalEventLog-cl — see [05-live-migration.md](05-live-migration.md)
- LmFailures — see [05-live-migration.md](05-live-migration.md)
- LiveMigrationFailures — see [05-live-migration.md](05-live-migration.md)
- LiveMigrationEvents — see [05-live-migration.md](05-live-migration.md)
- LiveMigrationContainerDetailsEventLog DS — see [05-live-migration.md](05-live-migration.md)
- AirLiveMigrationEvents DS — see [05-live-migration.md](05-live-migration.md)
- LiveMigrationSessionCompleteLog DS — see [05-live-migration.md](05-live-migration.md)
- LiveMigrationSessionCreatedLog DS — see [05-live-migration.md](05-live-migration.md)
- LiveMigrationSessionCriticalLog DS — see [05-live-migration.md](05-live-migration.md)
- LiveMigrationSessionStatusEventLog DS — see [05-live-migration.md](05-live-migration.md)
- LiveMigrationSessionStatusEventLog_Error DS — see [05-live-migration.md](05-live-migration.md)
- LiveMigrationEventsOnSubscription — see [05-live-migration.md](05-live-migration.md)
- LMSupportCases — see [05-live-migration.md](05-live-migration.md)
- LmApplicableVms — see [05-live-migration.md](05-live-migration.md)

### Node Investigation

- Anvil DS — see [06-node-investigation.md](06-node-investigation.md)
- HAruns DS — see [06-node-investigation.md](06-node-investigation.md)
- WF_UR_AzureProfiler — see [06-node-investigation.md](06-node-investigation.md)
- AzureWatson DS — see [06-node-investigation.md](06-node-investigation.md)
- DiskFailureXStoreTriage DS — see [06-node-investigation.md](06-node-investigation.md)
- E17_for_container DS — see [06-node-investigation.md](06-node-investigation.md)
- Event17 DS — see [06-node-investigation.md](06-node-investigation.md)
- RDOSE17Triage — see [06-node-investigation.md](06-node-investigation.md)
- VDC_E17 — see [06-node-investigation.md](06-node-investigation.md)
- DiskEventsQuery — see [06-node-investigation.md](06-node-investigation.md)
- DiskLeaseOperations — see [06-node-investigation.md](06-node-investigation.md)
- FaultHandlingRecoveryEvent DS — see [06-node-investigation.md](06-node-investigation.md)
- WF_UR_Hawkeye — see [06-node-investigation.md](06-node-investigation.md)
- HostAgentEventsETW — see [06-node-investigation.md](06-node-investigation.md)
- HyperVAnalyticEvents DS — see [06-node-investigation.md](06-node-investigation.md)
- HyperVStorageStackTable DS — see [06-node-investigation.md](06-node-investigation.md)
- HyperVWorkerTable DS — see [06-node-investigation.md](06-node-investigation.md)
- Incidents DS — see [06-node-investigation.md](06-node-investigation.md)
- LogNodeSnapshot DS — see [06-node-investigation.md](06-node-investigation.md)
- OSCo — see [06-node-investigation.md](06-node-investigation.md)
- HawkeyeRCAEvents_lowmemory — see [06-node-investigation.md](06-node-investigation.md)
- kaconfig — see [06-node-investigation.md](06-node-investigation.md)
- OSConf — see [06-node-investigation.md](06-node-investigation.md)
- GetSnapshot — see [06-node-investigation.md](06-node-investigation.md)
- HostResourceManagerResourceSnapshotMetadata — see [06-node-investigation.md](06-node-investigation.md)
- KaHostSummary_lowmemory2 — see [06-node-investigation.md](06-node-investigation.md)
- KaHost — see [06-node-investigation.md](06-node-investigation.md)
- leakdetection — see [06-node-investigation.md](06-node-investigation.md)
- GetSnapshot — see [06-node-investigation.md](06-node-investigation.md)
- kaconfig — see [06-node-investigation.md](06-node-investigation.md)
- TMMgmtNodeEventsEtwTable_UnexpectedRestart2 DS — see [06-node-investigation.md](06-node-investigation.md)
- NodeFaultEvents DS — see [06-node-investigation.md](06-node-investigation.md)
- NodeServiceEventEtwTable DS — see [06-node-investigation.md](06-node-investigation.md)
- NodeServiceOperationEtwTable DS — see [06-node-investigation.md](06-node-investigation.md)
- TMMgmtNodeStateChangedEtwTable DS — see [06-node-investigation.md](06-node-investigation.md)
- TMMgmtNodeTraceEtwTable DS — see [06-node-investigation.md](06-node-investigation.md)
- DirectAccessEvent — see [06-node-investigation.md](06-node-investigation.md)
- HyperVEventsV2 — see [06-node-investigation.md](06-node-investigation.md)
- HyperVStorageStackErrors — see [06-node-investigation.md](06-node-investigation.md)
- HyperVStorageStackTable_NVME — see [06-node-investigation.md](06-node-investigation.md)
- HyperVStorageStackTable_filter_controller — see [06-node-investigation.md](06-node-investigation.md)
- WindowseEventsNVME — see [06-node-investigation.md](06-node-investigation.md)
- OsAnalyzer Host Node Analysis DS — see [06-node-investigation.md](06-node-investigation.md)
- OsLogger DS — see [06-node-investigation.md](06-node-investigation.md)
- HostAgentEventsEtwTable DS — see [06-node-investigation.md](06-node-investigation.md)
- Azure Host VMAL Container Operations DS — see [06-node-investigation.md](06-node-investigation.md)
- Azure Host VmServiceLeaseManagementOperation DS — see [06-node-investigation.md](06-node-investigation.md)
- Azure Host VMAL Disk Service Table DS — see [06-node-investigation.md](06-node-investigation.md)
- Azure Host VmServiceEventsEtwTable DS — see [06-node-investigation.md](06-node-investigation.md)
- Azure Host VMAL Service Init DS — see [06-node-investigation.md](06-node-investigation.md)
- TMMgmtSlaMeasurementEventEtwTable_UnexpectedRestart DS — see [06-node-investigation.md](06-node-investigation.md)
- VMA4 DS — see [06-node-investigation.md](06-node-investigation.md)
- WF_UR_WindowsEvents — see [06-node-investigation.md](06-node-investigation.md)

### Planned Maintenance

- Control Events for VM DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- Control History for VM DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- CustomerNotification1 DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- CustomerNotification2 DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- Events for VM DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- History for VM DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- PendingMaintenanceOperationDetails DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- MaintenancePhaseDetails DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- PendingMaintenanceOperationDetails DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- ScheduledEventsEnablementStatus DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- PendingMaintenanceOperationDetails DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- ScheduledMaintenanceInformational DS — see [07-planned-maintenance.md](07-planned-maintenance.md)
- TenanteEventsFilteredPM DS — see [07-planned-maintenance.md](07-planned-maintenance.md)

### Service Healing

- Service Healing Trigger Type — see [08-service-healing.md](08-service-healing.md)
- AzSMServiceHealingStepResultEvents — see [08-service-healing.md](08-service-healing.md)
- AzSMServiceHealingResultEvents_clmendes — see [08-service-healing.md](08-service-healing.md)
- AzSMServiceHealingStepResultEvents_clmendes — see [08-service-healing.md](08-service-healing.md)
- AzSMServiceHealingTriggerEvents_clmendes — see [08-service-healing.md](08-service-healing.md)
- AzSMTenantEvents_clmendes — see [08-service-healing.md](08-service-healing.md)
- AzSMTenantStatemachineEvents_clmendes — see [08-service-healing.md](08-service-healing.md)
- ServiceHealingTenantStatusEtwTable_clmendes — see [08-service-healing.md](08-service-healing.md)
- ServiceHealingTriggerEtwTable_clmendes — see [08-service-healing.md](08-service-healing.md)
- TMMgmtTenantManagementJobInfoEtwTable_clmendes — see [08-service-healing.md](08-service-healing.md)
- IssueDetector AzSMServiceHealing — see [08-service-healing.md](08-service-healing.md)
- IssueDetector FabricServiceHealing — see [08-service-healing.md](08-service-healing.md)

### Update Investigation

- AirHostNetworkingUpdateEvents DS — see [09-update-investigation.md](09-update-investigation.md)
- AirManagedEvents DS — see [09-update-investigation.md](09-update-investigation.md)
- AirManagedEventsBrownouts DS — see [09-update-investigation.md](09-update-investigation.md)
- CombinedQuery DS — see [09-update-investigation.md](09-update-investigation.md)
- HostPlugin Update - TMMgmtNodeEventsEtwTable DS — see [09-update-investigation.md](09-update-investigation.md)
- Node Update Event - Event Log DS — see [09-update-investigation.md](09-update-investigation.md)
- Azure Host Fast Restore Events DS — see [09-update-investigation.md](09-update-investigation.md)
- Azure Host OSHP Events DS — see [09-update-investigation.md](09-update-investigation.md)
- OSHP Update DS — see [09-update-investigation.md](09-update-investigation.md)
- ServiceVersionSwitch_UnexpectedRestart2 DS — see [09-update-investigation.md](09-update-investigation.md)
- Scheduled Event for HostUpdate - AzPEWorkflowEvent DS — see [09-update-investigation.md](09-update-investigation.md)
- SocUpdate — see [09-update-investigation.md](09-update-investigation.md)
- VMPhuEvents DS — see [09-update-investigation.md](09-update-investigation.md)
