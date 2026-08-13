# EEE RDOS Start Hub — Investigation Guide

Symptom-keyed reference derived from the EEE RDOS Start Hub dashboard. Every KQL query backing the dashboard is included here, classified by investigation intent so an AI agent (or human) can route from a natural-language symptom directly to the queries that answer it.

**How to use:**

1. Identify what you are investigating (VM down? host hardware? network?).
2. Open the matching section file.
3. Pick the query whose name / source panel / filter tips match your symptom. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.
4. Execute via the vm-kusto-query skill (`kusto_runner.py`) or via `replay.py` next to this folder (the latter handles all 30+ param aliases automatically).

**Companion files (in parent folder):**

- `library.json` — canonical machine-readable source of all 172 queries (panel-organized).
- `library.md` — same content as flat human-readable index.
- `replay.py` — execution engine; resolves param aliases and runs queries.
- `link-inventory.md` — non-KQL links found on the page (other dashboards, aka.ms shortcuts).

## Sections

- [VM Availability & Lifecycle](01-vm-availability-and-lifecycle.md) — 9 queries
- [Container & Tenant State](02-container-and-tenant-state.md) — 15 queries
- [Host Node State & Faults](03-host-node-state-and-faults.md) — 23 queries
- [Host Hardware Faults](04-host-hardware-faults.md) — 8 queries
- [Network & TOR](05-network-and-tor.md) — 17 queries
- [Services on Node](06-services-on-node.md) — 8 queries
- [Node Update & Maintenance](07-node-update-and-maintenance.md) — 5 queries
- [Performance Metrics](08-performance-metrics.md) — 4 queries
- [Guest Agent & Extensions](09-guest-agent-and-extensions.md) — 3 queries
- [Helpers & Resource Lookups](11-helpers-and-lookups.md) — 21 queries
- [Detectors — Host Crash / Bugcheck](10a-detectors-host-crash-bugcheck.md) — 8 queries
- [Detectors — Live Migration / Service Healing](10b-detectors-live-migration.md) — 8 queries
- [Detectors — NVMe / Storage / Disk](10c-detectors-nvme-storage-disk.md) — 9 queries
- [Detectors — Network & TOR](10d-detectors-network-tor.md) — 7 queries
- [Detectors — SoC / Overlake / FPGA](10e-detectors-soc-overlake-fpga.md) — 2 queries
- [Detectors — VM Start / CreateContainer Failures](10f-detectors-vm-create-start-failures.md) — 10 queries
- [Detectors — Node Lifecycle / Unallocatable](10g-detectors-node-lifecycle.md) — 11 queries
- [Detectors — Host CPU / Memory / Power](10h-detectors-cpu-memory-power.md) — 2 queries
- [Detectors — Other / Uncategorized](10j-detectors-other.md) — 2 queries

**Total queries: 172**

## Query index (by section)

### VM Availability & Lifecycle

- `[Timeline]` **Hyper-V Heartbeat State** — see [01-vm-availability-and-lifecycle.md](01-vm-availability-and-lifecycle.md)
- `[Timeline]` **Hyper-V Power State** — see [01-vm-availability-and-lifecycle.md](01-vm-availability-and-lifecycle.md)
- `[Timeline]` **VMAvailabilityMetric** — see [01-vm-availability-and-lifecycle.md](01-vm-availability-and-lifecycle.md)
- `[Timeline]` **Container Live Migration** — see [01-vm-availability-and-lifecycle.md](01-vm-availability-and-lifecycle.md)
- `[Timeline]` **Service Healing(TM)** — see [01-vm-availability-and-lifecycle.md](01-vm-availability-and-lifecycle.md)
- `[Timeline]` **Service Healing(AzSM)** — see [01-vm-availability-and-lifecycle.md](01-vm-availability-and-lifecycle.md)
- `[Timeline]` **Planned Maintenance** — see [01-vm-availability-and-lifecycle.md](01-vm-availability-and-lifecycle.md)
- `[Timeline]` **VMA Event** — see [01-vm-availability-and-lifecycle.md](01-vm-availability-and-lifecycle.md)
- `[Timeline]` **AIR Events** — see [01-vm-availability-and-lifecycle.md](01-vm-availability-and-lifecycle.md)

### Container & Tenant State

- `[Timeline]` **Container State** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **Container OS State** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **Container Lifecycle** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **Container Fault** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **Node Service Error - Container** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **VMAL Ops** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **Hyper-V Events** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **Hyper-V StorageStack** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **Anvil Event - Container** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **Holmes Events** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **RH Annotation Report** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **ContainerStateTransition** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **ContainerOSStateTransition** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Table]` **Get Extended Container Error Details** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)
- `[Timeline]` **CRP Operation Timeline** — see [02-container-and-tenant-state.md](02-container-and-tenant-state.md)

### Host Node State & Faults

- `[Timeline]` **Fabricator Instance** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Fabricator Downtime** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Allocatable State** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Cluster Planned Maintenance** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Cluster Service Healing** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[TimeSeries]` **NodeStateHumanInvestigateCount** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[TimeSeries]` **NodeStateReadyCount** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **DCM Node State** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **DCM Node Fault** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Root Update Alloc Type** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Node State** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Node Availability** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Node Fault** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Node WillBe Channel Health Status** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Node WasChannel Health Status** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Node Service Error** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **VMAL Error** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Node Live Migration** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Anvil Event - Node** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[Timeline]` **Hyper-V State** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[TimeSeries]` **NodeStateOFRCount** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[TimeSeries]` **NodeStateReadyCount** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)
- `[TimeSeries]` **Unhealthy Node Count** — see [03-host-node-state-and-faults.md](03-host-node-state-and-faults.md)

### Host Hardware Faults

- `[Timeline]` **DCM SEL (Sparkle)** — see [04-host-hardware-faults.md](04-host-hardware-faults.md)
- `[Timeline]` **DCM SEL** — see [04-host-hardware-faults.md](04-host-hardware-faults.md)
- `[Timeline]` **Kernel/Driver Events** — see [04-host-hardware-faults.md](04-host-hardware-faults.md)
- `[Timeline]` **Remarkable Event - Disk** — see [04-host-hardware-faults.md](04-host-hardware-faults.md)
- `[Timeline]` **Remarkable Event - WHEA** — see [04-host-hardware-faults.md](04-host-hardware-faults.md)
- `[Timeline]` **Remarkable Event - Memory** — see [04-host-hardware-faults.md](04-host-hardware-faults.md)
- `[Timeline]` **Remarkable Event - HyperV** — see [04-host-hardware-faults.md](04-host-hardware-faults.md)
- `[Timeline]` **Azure Watson** — see [04-host-hardware-faults.md](04-host-hardware-faults.md)

### Network & TOR

- `[Timeline]` **ToR-Hosts PingMesh** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **Host-ToR PingMesh** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **ToR Health Event** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **ToR Update** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **ToR - Anvil Event** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **Wireserver Heartbeat** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **NMAgent Health** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **NMAgent Event** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **NM Programming** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **SoC OS Update** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **SoC Pilot Fish State** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **SoC PF Update** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **SoC Signal Event** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **SoC Azure Watson** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **SoC - Anvil Event** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **SoC VNetAgent Event** — see [05-network-and-tor.md](05-network-and-tor.md)
- `[Timeline]` **SoC Systemd Event** — see [05-network-and-tor.md](05-network-and-tor.md)

### Services on Node

- `[Timeline]` **Node WasChannel Health Status** — see [06-services-on-node.md](06-services-on-node.md)
- `[Timeline]` **Node WillBe Channel Health Status** — see [06-services-on-node.md](06-services-on-node.md)
- `[Timeline]` **PfAgent Status** — see [06-services-on-node.md](06-services-on-node.md)
- `[Timeline]` **PilotFish State** — see [06-services-on-node.md](06-services-on-node.md)
- `[Timeline]` **ApSvcMgr Status** — see [06-services-on-node.md](06-services-on-node.md)
- `[Timeline]` **ApLauncher Status** — see [06-services-on-node.md](06-services-on-node.md)
- `[Timeline]` **Node Service Status** — see [06-services-on-node.md](06-services-on-node.md)
- `[Timeline]` **WireService Status** — see [06-services-on-node.md](06-services-on-node.md)

### Node Update & Maintenance

- `[Timeline]` **PF Update** — see [07-node-update-and-maintenance.md](07-node-update-and-maintenance.md)
- `[Timeline]` **Host Update** — see [07-node-update-and-maintenance.md](07-node-update-and-maintenance.md)
- `[Timeline]` **CM Node Update** — see [07-node-update-and-maintenance.md](07-node-update-and-maintenance.md)
- `[Timeline]` **AzPE Update** — see [07-node-update-and-maintenance.md](07-node-update-and-maintenance.md)
- `[Timeline]` **FPGA Update** — see [07-node-update-and-maintenance.md](07-node-update-and-maintenance.md)

### Performance Metrics

- `[TimeSeries]` **EEERDOSHostMemoryPerformance** — see [08-performance-metrics.md](08-performance-metrics.md)
- `[TimeSeries]` **HostCPUPerformance** — see [08-performance-metrics.md](08-performance-metrics.md)
- `[TimeSeries]` **ContainerPerformance** — see [08-performance-metrics.md](08-performance-metrics.md)
- `[TimeSeries]` **Container Performance Shoebox** — see [08-performance-metrics.md](08-performance-metrics.md)

### Guest Agent & Extensions

- `[Timeline]` **Tenant Scheduled Events** — see [09-guest-agent-and-extensions.md](09-guest-agent-and-extensions.md)
- `[Timeline]` **ICM Report** — see [09-guest-agent-and-extensions.md](09-guest-agent-and-extensions.md)
- `[Timeline]` **GuestAgentAndExtensionTimeline** — see [09-guest-agent-and-extensions.md](09-guest-agent-and-extensions.md)

### Helpers & Resource Lookups

- `[ResourceGet]` **Retrieve Resource "Start Hub"** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **OverlakeNodeMap** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **GetShoeboxAccount** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **AIPromptGenerator** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **JarvisDashTimeHelper** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **VmssIdHelper** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **Unix Time Helper** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **TorDeviceInfo** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **Unix Time Helper** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **vfpMDM** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **Node Hardware Properties** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **OverlakeNodeMap** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[FeatureList]` **Container Features** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **PageInputHelper** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **GetARMResourceId** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **GetShoeboxAccount** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **VmssIdHelper** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Table]` **Azure Host VM Blobs** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[TimeSeries]` **Compute Hour Usage Table** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **ContainerPolicyQuery** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)
- `[Single]` **CRP VM Snapshot** — see [11-helpers-and-lookups.md](11-helpers-and-lookups.md)

### Detectors — Host Crash / Bugcheck

- `[IssueDetector]` **IssueDetector_SoC_Crash** — see [10a-detectors-host-crash-bugcheck.md](10a-detectors-host-crash-bugcheck.md)
- `[IssueDetector]` **IssueDetector_EI_node_bugcheck_0x50_netdatapath** — see [10a-detectors-host-crash-bugcheck.md](10a-detectors-host-crash-bugcheck.md)
- `[IssueDetector]` **IssueDetector_EI_Node Crash_due_to_0xBC0000D6_BlobCache!BcRefere** — see [10a-detectors-host-crash-bugcheck.md](10a-detectors-host-crash-bugcheck.md)
- `[IssueDetector]` **IssueDetector_EI_node bugcheck_0xd1_AV_blobcache!BcPfnReferenc** — see [10a-detectors-host-crash-bugcheck.md](10a-detectors-host-crash-bugcheck.md)
- `[IssueDetector]` **IssueDetector_EI_bugcheck_0xd1_AV_Barbera!HbLldCompleteIrpOve** — see [10a-detectors-host-crash-bugcheck.md](10a-detectors-host-crash-bugcheck.md)
- `[IssueDetector]` **IssueDetector_Sudden_Power_Loss_of_host_node** — see [10a-detectors-host-crash-bugcheck.md](10a-detectors-host-crash-bugcheck.md)
- `[IssueDetector]` **IssueDetector_EI_VMA_bugcheck_0x20001_HYPERVISOR_ERROR** — see [10a-detectors-host-crash-bugcheck.md](10a-detectors-host-crash-bugcheck.md)
- `[IssueDetector]` **IssueDetector_EI_AW_bugcheck_0x20001_HYPERVISOR_ERROR** — see [10a-detectors-host-crash-bugcheck.md](10a-detectors-host-crash-bugcheck.md)

### Detectors — Live Migration / Service Healing

- `[IssueDetector]` **IssueDetector_AzSMServiceHealing** — see [10b-detectors-live-migration.md](10b-detectors-live-migration.md)
- `[IssueDetector]` **IssueDetector_EI_NetAssistMonitorTriggers_LM** — see [10b-detectors-live-migration.md](10b-detectors-live-migration.md)
- `[IssueDetector]` **IssueDetector_EI_LM_failure_VFPRestoreFailure_NmAgentEventDelay** — see [10b-detectors-live-migration.md](10b-detectors-live-migration.md)
- `[IssueDetector]` **IssueDetector_EI_LM_VFPRestoreFailure_Deserialization_Issue_Port** — see [10b-detectors-live-migration.md](10b-detectors-live-migration.md)
- `[IssueDetector]` **IssueDetector_EI_LM_SH_due_to_NVMe_Device_End_of_Life** — see [10b-detectors-live-migration.md](10b-detectors-live-migration.md)
- `[IssueDetector]` **IssueDetector_EI_LMFailed_FlexibleIODeviceRestore** — see [10b-detectors-live-migration.md](10b-detectors-live-migration.md)
- `[IssueDetector]` **IssueDetector_EI_LMFailed_VFPSerializationIssue_0x5aa** — see [10b-detectors-live-migration.md](10b-detectors-live-migration.md)
- `[IssueDetector]` **IssueDetector_EI_LMFailed_VFPSerializationIssue_0x5aa_2** — see [10b-detectors-live-migration.md](10b-detectors-live-migration.md)

### Detectors — NVMe / Storage / Disk

- `[IssueDetector]` **IssueDetector_EI_AirDiskBlip_BlobCache_Write_during_Congestion** — see [10c-detectors-nvme-storage-disk.md](10c-detectors-nvme-storage-disk.md)
- `[IssueDetector]` **IssueDetector_EI_High_Flush_latencies_due_to_driver_issue** — see [10c-detectors-nvme-storage-disk.md](10c-detectors-nvme-storage-disk.md)
- `[IssueDetector]` **IssueDetector_EI_Attaching_Multiple_DataDisks_Over_Nvme_restart** — see [10c-detectors-nvme-storage-disk.md](10c-detectors-nvme-storage-disk.md)
- `[IssueDetector]` **IssueDetector_EI_Dalds_v6_Windows_2025_datadisk_perf** — see [10c-detectors-nvme-storage-disk.md](10c-detectors-nvme-storage-disk.md)
- `[IssueDetector]` **IssueDetector_NVME_HW_troubleshooting** — see [10c-detectors-nvme-storage-disk.md](10c-detectors-nvme-storage-disk.md)
- `[IssueDetector]` **IssueDetector_EI_Ultra_PremV2_DiskBlip_during_VDC_driver_update** — see [10c-detectors-nvme-storage-disk.md](10c-detectors-nvme-storage-disk.md)
- `[IssueDetector]` **IssueDetector_EI_Local_NVMe_Disks_Are_Missing_In_Lv4_Series** — see [10c-detectors-nvme-storage-disk.md](10c-detectors-nvme-storage-disk.md)
- `[IssueDetector]` **IssueDetector_EI_NVMeVmHighDiskLatency_due_to_CacheHint** — see [10c-detectors-nvme-storage-disk.md](10c-detectors-nvme-storage-disk.md)
- `[IssueDetector]` **IssueDetector_EI_NVMe_Controller_VM_experience_stornvme_reset** — see [10c-detectors-nvme-storage-disk.md](10c-detectors-nvme-storage-disk.md)

### Detectors — Network & TOR

- `[IssueDetector]` **IssueDetector_NetworkIssues** — see [10d-detectors-network-tor.md](10d-detectors-network-tor.md)
- `[IssueDetector]` **IssueDetector_EI_StopDestroy Fails with STORVSP_VspDeviceCreate*** — see [10d-detectors-network-tor.md](10d-detectors-network-tor.md)
- `[IssueDetector]` **IssueDetector_TORFailures** — see [10d-detectors-network-tor.md](10d-detectors-network-tor.md)
- `[IssueDetector]` **IssueDetector_TOR_DegradedUnhealthyEvents** — see [10d-detectors-network-tor.md](10d-detectors-network-tor.md)
- `[IssueDetector]` **IssueDetector_EI_HostNetworkIssue_FPGA_GFT_Unhealthy_on_Overlake** — see [10d-detectors-network-tor.md](10d-detectors-network-tor.md)
- `[IssueDetector]` **IssueDetector_TOR_Update** — see [10d-detectors-network-tor.md](10d-detectors-network-tor.md)
- `[IssueDetector]` **IssueDetector_EI_NetworkContainer_AllocationIncarnation** — see [10d-detectors-network-tor.md](10d-detectors-network-tor.md)

### Detectors — SoC / Overlake / FPGA

- `[IssueDetector]` **IssueDetector_SoC_Update** — see [10e-detectors-soc-overlake-fpga.md](10e-detectors-soc-overlake-fpga.md)
- `[IssueDetector]` **IssueDetector_EI_Backplane_service_crash_on_SoC_impacts_VM** — see [10e-detectors-soc-overlake-fpga.md](10e-detectors-soc-overlake-fpga.md)

### Detectors — VM Start / CreateContainer Failures

- `[IssueDetector]` **IssueDetector_EI_CreateContainer_fails_with_0x80070002_L-Series** — see [10f-detectors-vm-create-start-failures.md](10f-detectors-vm-create-start-failures.md)
- `[IssueDetector]` **IssueDetector_EI_CreateContainer_failed_with_0xc3510153** — see [10f-detectors-vm-create-start-failures.md](10f-detectors-vm-create-start-failures.md)
- `[IssueDetector]` **IssueDetector_EI_VM reboot when trying to detach disks ** — see [10f-detectors-vm-create-start-failures.md](10f-detectors-vm-create-start-failures.md)
- `[IssueDetector]` **IssueDetector_EI_NV6_v5_VMs_Fail_to_Start_due_to_Low_Memory** — see [10f-detectors-vm-create-start-failures.md](10f-detectors-vm-create-start-failures.md)
- `[IssueDetector]` **IssueDetector_EI_OSProvisioningTimedOut_failure_DHCP_lease** — see [10f-detectors-vm-create-start-failures.md](10f-detectors-vm-create-start-failures.md)
- `[IssueDetector]` **IssueDetector_EI_GPC_VMs_Fail_to_Start_IBManagerError_0x800704c** — see [10f-detectors-vm-create-start-failures.md](10f-detectors-vm-create-start-failures.md)
- `[IssueDetector]` **IssueDetector_EI_v6VM_TPM_fails_start_due_to_Underhill_VM** — see [10f-detectors-vm-create-start-failures.md](10f-detectors-vm-create-start-failures.md)
- `[IssueDetector]` **IssueDetector_EI_Unable_to_create_VM_VMAL_error_0x8000ffff** — see [10f-detectors-vm-create-start-failures.md](10f-detectors-vm-create-start-failures.md)
- `[IssueDetector]` **IssueDetector_EI_VM_creation_failure_0xc3510224_VMAL_ASAPPF** — see [10f-detectors-vm-create-start-failures.md](10f-detectors-vm-create-start-failures.md)
- `[IssueDetector]` **IssueDetector_E17_Key_Vault_Encryption_Key_not_found** — see [10f-detectors-vm-create-start-failures.md](10f-detectors-vm-create-start-failures.md)

### Detectors — Node Lifecycle / Unallocatable

- `[IssueDetector]` **IssueDetector_TooManyUnhealthyNode** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)
- `[IssueDetector]` **IssueDetector_EI_RHSendsIncorrectVMAvailableStateRepeatedly** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)
- `[IssueDetector]` **IssueDetector_EI_DppPluginOrPfDatapathServiceRequired** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)
- `[IssueDetector]` **IssueDetector_EI_CRUD operationFailuresDueToContainerWorkflow*** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)
- `[IssueDetector]` **IssueDetector_EI_Resource_Health_Unavailable_for_Linux_6.2Kernel** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)
- `[IssueDetector]` **IssueDetector_EI_AKS_Linux_instances_are_reported_as_Windows** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)
- `[IssueDetector]` **IssueDetector_EI_StagingNodeImagesGen9** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)
- `[IssueDetector]` **IssueDetector_Node_Restart_Due_to_Planned_Maintenance** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)
- `[IssueDetector]` **IssueDetector_EI_UnallocatableNode_DestroyContainer_0x8abc0503** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)
- `[IssueDetector]` **IssueDetector_EI_Unallocatable_Node_due_to_XDisk_leaks** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)
- `[IssueDetector]` **IssueDetector_Booting_of_host_node_detected** — see [10g-detectors-node-lifecycle.md](10g-detectors-node-lifecycle.md)

### Detectors — Host CPU / Memory / Power

- `[IssueDetector]` **IssueDetector_HighHostCPU_temp_throttle** — see [10h-detectors-cpu-memory-power.md](10h-detectors-cpu-memory-power.md)
- `[IssueDetector]` **IssueDetector_HighHostCPU_throttle** — see [10h-detectors-cpu-memory-power.md](10h-detectors-cpu-memory-power.md)

### Detectors — Other / Uncategorized

- `[IssueDetector]` **IssueDetector_EI_EQ stuck_on_EQn_0x4** — see [10j-detectors-other.md](10j-detectors-other.md)
- `[IssueDetector]` **IssueDetector_EI_Standard_ND96isr_H100_v5_HardwareFault_pCIfata** — see [10j-detectors-other.md](10j-detectors-other.md)
