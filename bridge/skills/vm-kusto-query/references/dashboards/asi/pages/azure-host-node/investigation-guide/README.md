# Azure Host — Azure Host Node — Investigation Guide

Chapter-keyed reference derived from the **Azure Host — Azure Host Node** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 2 queries
- [AIR-BP](02-air-bp.md) — 4 queries
- [AIR-J](03-air-j.md) — 4 queries
- [Direct Drive Performance Tables](04-direct-drive-performance-tables.md) — 4 queries
- [Fabric Tables](05-fabric-tables.md) — 10 queries
- [Host Charts](06-host-charts.md) — 28 queries
- [Host Details](07-host-details.md) — 22 queries
- [Host Tables](08-host-tables.md) — 29 queries
- [Hyper-V Tables](09-hyper-v-tables.md) — 9 queries
- [Insights](10-insights.md) — 2 queries
- [NetDatapathTrace](11-netdatapathtrace.md) — 1 queries
- [RdAgent Tables](12-rdagent-tables.md) — 5 queries
- [ServiceHealth](13-servicehealth.md) — 1 queries
- [SOC Details](14-soc-details.md) — 1 queries
- [StorageClient Tables — ASAP](15a-storageclient-tables--asap.md) — 85 queries
- [StorageClient Tables (part 2/3)](15b-storageclient-tables--barbera.md) — 31 queries
- [StorageClient Tables (part 3/3)](15c-storageclient-tables--updates.md) — 21 queries
- [SystemD](16-systemd.md) — 1 queries
- [TDPR](17-tdpr.md) — 2 queries
- [Timeline of Startup Table](18-timeline-of-startup-table.md) — 5 queries
- [Updates](19-updates.md) — 1 queries
- [VM Details](20-vm-details.md) — 3 queries
- [VMA (AIR-R)](21-vma-air-r.md) — 1 queries
- [XStore Performance Tables](22-xstore-performance-tables.md) — 4 queries

**Total queries: 276**

## Query index (by file)

### (top-level)

- Retrieve Resource "Azure Host Node" — see [01-top-level.md](01-top-level.md)
- ExtendedFaultTable — see [01-top-level.md](01-top-level.md)

### AIR-BP

- Azure Host AirManagedEventsBrownouts — see [02-air-bp.md](02-air-bp.md)
- XHealth_DiskBlackoutXStoreTriage — see [02-air-bp.md](02-air-bp.md)
- Azure Host AIRBP — see [02-air-bp.md](02-air-bp.md)
- Azure Host AIRBP Managed Events — see [02-air-bp.md](02-air-bp.md)

### AIR-J

- CPU Jitter comparison with baseline — see [03-air-j.md](03-air-j.md)
- CPU Jitter (High granularity) — see [03-air-j.md](03-air-j.md)
- AIR-J Incidents — see [03-air-j.md](03-air-j.md)
- Node Utilization Landscape — see [03-air-j.md](03-air-j.md)

### Direct Drive Performance Tables

- Agent Start Operations Details Direct Drive (P50, 90, 99) — see [04-direct-drive-performance-tables.md](04-direct-drive-performance-tables.md)
- Container Workflow Details Direct Drive (P50, 90, 99) — see [04-direct-drive-performance-tables.md](04-direct-drive-performance-tables.md)
- IfxOperationV2 Performance Details Direct Drive (P50, 90, 99) — see [04-direct-drive-performance-tables.md](04-direct-drive-performance-tables.md)
- NodeWorkflow Details Direct Drive (P50, 90, 99) — see [04-direct-drive-performance-tables.md](04-direct-drive-performance-tables.md)

### Fabric Tables

- Azure Host Anvil ForgeEvents — see [05-fabric-tables.md](05-fabric-tables.md)
- Azure Host ContainerHealth Snapshot — see [05-fabric-tables.md](05-fabric-tables.md)
- Azure Host Fabric FaultHandler Recovery — see [05-fabric-tables.md](05-fabric-tables.md)
- Azure Host Fabric Node Events — see [05-fabric-tables.md](05-fabric-tables.md)
- Azure Host Fabric Node Faults — see [05-fabric-tables.md](05-fabric-tables.md)
- Azure Host Hawkeye Events — see [05-fabric-tables.md](05-fabric-tables.md)
- LogNodeSnapshot — see [05-fabric-tables.md](05-fabric-tables.md)
- Azure Host Fabric Node State Changes — see [05-fabric-tables.md](05-fabric-tables.md)
- Gandalf Rogue Containers Query — see [05-fabric-tables.md](05-fabric-tables.md)
- Azure Host Fabric SLAMeasurementTable — see [05-fabric-tables.md](05-fabric-tables.md)

### Host Charts

- Azure Host VM ASAP 2.0 IO Stats — see [06-host-charts.md](06-host-charts.md)
- HostResourceManager High Level Memory Usage Breakdown — see [06-host-charts.md](06-host-charts.md)
- HostResourceManager Top Pool Tags — see [06-host-charts.md](06-host-charts.md)
- HostResourceManager Top Processes — see [06-host-charts.md](06-host-charts.md)
- Hypervisor Metadata Memory Partition — see [06-host-charts.md](06-host-charts.md)
- Host System Partition Memory — see [06-host-charts.md](06-host-charts.md)
- VM Memory Partition All Pages — see [06-host-charts.md](06-host-charts.md)
- VM Memory Partition IO Space Pages — see [06-host-charts.md](06-host-charts.md)
- Azure Host Drive Free Space — see [06-host-charts.md](06-host-charts.md)
- Azure Host Drive Free Space — see [06-host-charts.md](06-host-charts.md)
- Azure Host Node Available Memory — see [06-host-charts.md](06-host-charts.md)
- Azure Host CPU 5 seconds — see [06-host-charts.md](06-host-charts.md)
- Azure Host VP CPU — see [06-host-charts.md](06-host-charts.md)
- Azure Host Node NPP Bytes — see [06-host-charts.md](06-host-charts.md)
- Azure Host Node Process Handle Count — see [06-host-charts.md](06-host-charts.md)
- HostStorage Avg IO Latency — see [06-host-charts.md](06-host-charts.md)
- Azure Host Disk Status — see [06-host-charts.md](06-host-charts.md)
- HostStorage High Latency IO Counts — see [06-host-charts.md](06-host-charts.md)
- HostStorage Max IO Latency — see [06-host-charts.md](06-host-charts.md)
- Azure Host StorPort IO Telemetry Stats — see [06-host-charts.md](06-host-charts.md)
- Azure Host VM MPF Stats — see [06-host-charts.md](06-host-charts.md)
- Azure Host Networking PortQuotaRundown — see [06-host-charts.md](06-host-charts.md)
- TCPIP Connection Counters — see [06-host-charts.md](06-host-charts.md)
- TCPIP Performance Counters — see [06-host-charts.md](06-host-charts.md)
- Azure Host VMs CPU Usage — see [06-host-charts.md](06-host-charts.md)
- Azure Host StorageClient VMs Disk IOPS — see [06-host-charts.md](06-host-charts.md)
- Azure Host VM StorageClient Disk MBPS — see [06-host-charts.md](06-host-charts.md)
- Azure Host VMs Memory Usage — see [06-host-charts.md](06-host-charts.md)

### Host Details

- Azure Host Node VMA Query — see [07-host-details.md](07-host-details.md)
- Azure Host Node State (Fabric) — see [07-host-details.md](07-host-details.md)
- Azure Host TOR Pingmesh — see [07-host-details.md](07-host-details.md)
- Azure Host Node Power State Timeline — see [07-host-details.md](07-host-details.md)
- Azure Host Vhddisk Events Query — see [07-host-details.md](07-host-details.md)
- Azure Host PF Service Updates — see [07-host-details.md](07-host-details.md)
- Azure Host Fabric Node Fault — see [07-host-details.md](07-host-details.md)
- Azure Host XStore E17 AutoTriage — see [07-host-details.md](07-host-details.md)
- Azure Host OSHostPlugin Events — see [07-host-details.md](07-host-details.md)
- Azure Host Impactful Events — see [07-host-details.md](07-host-details.md)
- Azure Host Node Updates — see [07-host-details.md](07-host-details.md)
- Azure Host Node TIP sessions — see [07-host-details.md](07-host-details.md)
- Azure Host Node Events — see [07-host-details.md](07-host-details.md)
- Azure Fault Recovery Events — see [07-host-details.md](07-host-details.md)
- Azure Node HealthSignal (Fabric) — see [07-host-details.md](07-host-details.md)
- Host OS Version — see [07-host-details.md](07-host-details.md)
- Retrieve Node Hardware Details — see [07-host-details.md](07-host-details.md)
- Cluster Overlake Version (HostOS) — see [07-host-details.md](07-host-details.md)
- GetTimeinDeviceDrillFormat — see [07-host-details.md](07-host-details.md)
- Azure Host FileVersions Query — see [07-host-details.md](07-host-details.md)
- Azure Host Node StorageClient Insights — see [07-host-details.md](07-host-details.md)
- Azure Host PF Services Versions — see [07-host-details.md](07-host-details.md)

### Host Tables

- Azure Host ASC HA Runs — see [08-host-tables.md](08-host-tables.md)
- Azure Profiler Traces with Hottest Callstacks — see [08-host-tables.md](08-host-tables.md)
- Azure Host Profiler — see [08-host-tables.md](08-host-tables.md)
- Azure Host Watson Dumps — see [08-host-tables.md](08-host-tables.md)
- Azure Host SEL Logs — see [08-host-tables.md](08-host-tables.md)
- Azure Host Node HealthStore Regressed Signals — see [08-host-tables.md](08-host-tables.md)
- Azure Host Node HealthStore UnderThreshold Signals — see [08-host-tables.md](08-host-tables.md)
- HostStorage DCM Inventory — see [08-host-tables.md](08-host-tables.md)
- HostStorage Disk IO Errors - WindowsStorageEvents — see [08-host-tables.md](08-host-tables.md)
- HostStorage Disk IO Timeouts - WindowsStorageEvents — see [08-host-tables.md](08-host-tables.md)
- NDIS DMA Allocation Summary — see [08-host-tables.md](08-host-tables.md)
- Azure Host Network Port Quota — see [08-host-tables.md](08-host-tables.md)
- Azure Host IcMs — see [08-host-tables.md](08-host-tables.md)
- Azure Host Node LiveMigration Completions — see [08-host-tables.md](08-host-tables.md)
- Azure Host Fast Restore Events — see [08-host-tables.md](08-host-tables.md)
- Azure Host FastSave Events — see [08-host-tables.md](08-host-tables.md)
- Azure Host OSHP Events — see [08-host-tables.md](08-host-tables.md)
- Azure Host OSHP Update Logs — see [08-host-tables.md](08-host-tables.md)
- Azure Host OSHP Plugin Update — see [08-host-tables.md](08-host-tables.md)
- VM-PHU Node Compute Blackout Query — see [08-host-tables.md](08-host-tables.md)
- Azure Host OsLoggerTable — see [08-host-tables.md](08-host-tables.md)
- Azure Host Disk Space Table — see [08-host-tables.md](08-host-tables.md)
- Azure Host WindowsEventTable — see [08-host-tables.md](08-host-tables.md)
- Azure Host HighCPUTable Chart View — see [08-host-tables.md](08-host-tables.md)
- Azure Host HighCPUTable — see [08-host-tables.md](08-host-tables.md)
- Poolmon Data for Azure Host Node — see [08-host-tables.md](08-host-tables.md)
- Azure Host OsConfigTable — see [08-host-tables.md](08-host-tables.md)
- Azure Host PF Updates Table — see [08-host-tables.md](08-host-tables.md)
- Azure Host RootHE Updates — see [08-host-tables.md](08-host-tables.md)

### Hyper-V Tables

- Azure Host HyperV Analytic — see [09-hyper-v-tables.md](09-hyper-v-tables.md)
- HyperVEventsV2 Host Query — see [09-hyper-v-tables.md](09-hyper-v-tables.md)
- Azure Host VM HyperV Latency Query — see [09-hyper-v-tables.md](09-hyper-v-tables.md)
- Azure Host HyperV Storage — see [09-hyper-v-tables.md](09-hyper-v-tables.md)
- Azure Host HyperVStorageStack Incomplete IO Operations — see [09-hyper-v-tables.md](09-hyper-v-tables.md)
- Azure Host HyperVStorageStack IO Operations Summary — see [09-hyper-v-tables.md](09-hyper-v-tables.md)
- Azure Host Node UnderhillEventTable — see [09-hyper-v-tables.md](09-hyper-v-tables.md)
- Azure Host Node Virtualization Configuration — see [09-hyper-v-tables.md](09-hyper-v-tables.md)
- Azure Host Hyper-V Worker — see [09-hyper-v-tables.md](09-hyper-v-tables.md)

### Insights

- node_insights_summary — see [10-insights.md](10-insights.md)
- Azure Host Azure Core RCA — see [10-insights.md](10-insights.md)

### NetDatapathTrace

- NetDatapathTrace Query — see [11-netdatapathtrace.md](11-netdatapathtrace.md)

### RdAgent Tables

- Azure Host VMAL Container Operations — see [12-rdagent-tables.md](12-rdagent-tables.md)
- Azure Host VmServiceLeaseManagementOperation — see [12-rdagent-tables.md](12-rdagent-tables.md)
- Azure Host VMAL Disk Service Table — see [12-rdagent-tables.md](12-rdagent-tables.md)
- Azure Host VmServiceEventsEtwTable — see [12-rdagent-tables.md](12-rdagent-tables.md)
- Azure Host VMAL Service Init — see [12-rdagent-tables.md](12-rdagent-tables.md)

### ServiceHealth

- Azure Host Node SoC Service Health — see [13-servicehealth.md](13-servicehealth.md)

### SOC Details

- NetDatapathPerfCounters Query — see [14-soc-details.md](14-soc-details.md)

### StorageClient Tables — ASAP

- Azure Host ASFO Features Values — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASFO Components Versions — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASFO Features — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Node Info ASAP — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ASFO_PO_FO_Transitions — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- AsapMapVfIdToContainerIdOvl2Node — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASAP Full Offload PF and UMED details — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASFO Node Events Stats Table — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- FullOffloadExceptionsQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- MinLatencyFloorDelayPv2Query — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_asapPf_AllDisks — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_asapPf_UseSwpe0 — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_asapPf_AllDisks — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_asapPf_UseSwpe0 — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_asapPf_AllDisks — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_asapPf_UseSwpe0 — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- AsapQpHealthCheckFailed_Spread — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Full Offload Exceptions — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_OsCounters_AllDisks — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_OsCounters_UseSwpe0 — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_OsCounters_AllDisks — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_OsCounters_UseSwpe0 — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_OsCounters_AllDisks — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- asapNodeFOStats_OsCounters_UseSwpe0 — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Full Offload Exceptions — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- FOPercent_NodeQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- FullOffloadStats_AllDisksQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Fulloffload Statistics — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- FullOffloadStats_AllDisksQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Fulloffload Statistics — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- FullOffloadExceptionsQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- VMCountsPerFOPercent — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- OutlierContainersListQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- FoBucketFilterQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Asap Heartbeats — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Node ASAP VMA Query — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Node Events — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Node State (Fabric) — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host XStore E17 AutoTriage — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Node Updates — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host PF Service Updates — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host OSHostPlugin Events — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ASAP UMED CE Events Timeline — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ASAP KMS CE Events Timeline — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ASAP PF CE Events Timeline — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Node TIP sessions — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ControllerResetsAndIoLossQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- CriticalErrorsQuery  — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- VfStuckExtrPrejudiceQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Node ASAP Insights For Node — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- AsapInsightsOVL2Query — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ManaVersion — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASAP All Tables Union — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Node ASAP FPGA DataLogger — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ASAP ASAP PF HWCE and Debug Registers Dump — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Edit Query Azure Host ASAP Debug Registers HW CE — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASAP KMS Table — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Node ASAP Node Story — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASAP ETW Table — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host PF ETW Table — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASAP FPGA HW Shell Telemetry — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASFO Critical and Error Events — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ASAP Hardware Debug Registers Output S0C0 to S3CX — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ASAP Hardware Debug Registers Output S4C0 to S7CX — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ASAP Hardware Debug Registers Output S8C0 to SBCX — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ASAP Hardware Debug Registers Output SCC0 to SFCX — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASAP Full Offload PF Investigations — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASAP Debug Registers HW CE Overlake 2 — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host Node ASAP Insights for Overlake 2 Node — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASAP KMS Trace Logging — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host ASAP NVME Trace Logging — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Azure Host PF Trace Logging — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Show_Cobe_Condition_OSHP  — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- MaxVM_ComputeBlackout1_ADPA — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- MaxVM_ComputeBlackout2_ADPA — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Display_ContainerIds_Query — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- Check_ShowCobe_Condition_ADPA_MultiVm — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- AdpaServiceQueryPerContainer — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- ADPA_BlackoutBrownout_Test — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- AdpaServicingEventsAllVMsOVL2 — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- DisplayContainersQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- OshpServiceQueryPerContainer — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- OSHP_MaxVM_ScenarioQuery — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- OshpServicingEventsAllVMsOVL2 — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)
- OshpServicingEventsAllVMsOVL2V2 — see [15a-storageclient-tables--asap.md](15a-storageclient-tables--asap.md)

### StorageClient Tables (part 2/3)

- Azure Host Barbera Events Query — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Barbera Ring Creation Failures Query — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Barbera Active Owb Index Filter — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Barbera Usage Ring Stats Query — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- BarberaConfigDetails — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- BarberaConfigSummary — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host BarberaSvcEvent Query — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host BarberaSvcRingEvent Query — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host BarberaSvcTopologyEvent Query — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host BlobCache Config Table — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host BlobCache Event Table — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Blobcache InternalCounters Query — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host CacheStore Configuration — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Node Blobcache CacheStore Stats TL — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Node Blobcache Throttle missing  — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Node DAL Logs2 — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Node DirectAccessEvent — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host DAL Logs — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Node DAL OsLoggerTable — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host StorageClient Driver Logs — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Node EDrive Manager EvtTable — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Node EDrive Operations — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Node EDrive Manager Table — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host Node EDrive Encryption Events — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host OsAnalyzerTable — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Azure Host XStore AutoTriage — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- PnP Events — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- StorPort Events — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- DirectAccessEvent MFND Query — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- Storage Tracing MFND Event Query — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)
- StorSnap Event Query — see [15b-storageclient-tables--barbera.md](15b-storageclient-tables--barbera.md)

### StorageClient Tables (part 3/3)

- Storage Client VM Brownout for all VMs — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- ListOfExecutions — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Update_Node_Logs — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- XIO_Condition_Query — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host DPHP Update Events — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host Node OsAnalyzerLogTable — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host Storage Client User Mode Processes Usage Stats — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- VDC_Diskpacing_Events — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host StorageAgent ETW Table — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- SAListOfExecutions — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- SA_Node_Update_Logs — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host Vdc Etw Events — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host VM Vhddisk MaxTime Summary — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host Vhddisk ETW Events — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host Vhddisk Events — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Node Transport Percentage Query — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- OsVhddiskEventTable — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host Node vhdum logs — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host Node VM Disks — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host XdiskEncEvent — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)
- Azure Host XDiskSvcEvent Query — see [15c-storageclient-tables--updates.md](15c-storageclient-tables--updates.md)

### SystemD

- Azure Host Node SoC SystemD Logs — see [16-systemd.md](16-systemd.md)

### TDPR

- Azure Host EG Telemetry  — see [17-tdpr.md](17-tdpr.md)
- Azure VM IFX Table — see [17-tdpr.md](17-tdpr.md)

### Timeline of Startup Table

- Node Health — see [18-timeline-of-startup-table.md](18-timeline-of-startup-table.md)
- NodeWorkflow Timeline — see [18-timeline-of-startup-table.md](18-timeline-of-startup-table.md)
- Agent Start Operations Details — see [18-timeline-of-startup-table.md](18-timeline-of-startup-table.md)
- Container Workflow Details — see [18-timeline-of-startup-table.md](18-timeline-of-startup-table.md)
- IFxOperationV2 Table — see [18-timeline-of-startup-table.md](18-timeline-of-startup-table.md)

### Updates

- Azure Host Node SoC Updates — see [19-updates.md](19-updates.md)

### VM Details

- Azure Host Node VM Cached Throttle Settings — see [20-vm-details.md](20-vm-details.md)
- Azure Host Node VM Throttle Settings — see [20-vm-details.md](20-vm-details.md)
- Azure Host Running VMs Query — see [20-vm-details.md](20-vm-details.md)

### VMA (AIR-R)

- Azure Host VMA — see [21-vma-air-r.md](21-vma-air-r.md)

### XStore Performance Tables

- Agent Start Operations Performance (P50, 90, 99) — see [22-xstore-performance-tables.md](22-xstore-performance-tables.md)
- Container Workflow Details (P50, 90, 99) — see [22-xstore-performance-tables.md](22-xstore-performance-tables.md)
- IfxOperationV2 Performance (P50, 90, 99) — see [22-xstore-performance-tables.md](22-xstore-performance-tables.md)
- NodeWorkflow P50, P90, P99 — see [22-xstore-performance-tables.md](22-xstore-performance-tables.md)
