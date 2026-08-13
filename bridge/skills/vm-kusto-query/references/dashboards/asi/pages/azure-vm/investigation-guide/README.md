# Azure Host - Azure VM — Investigation Guide

Chapter-keyed reference derived from the **Azure Host - Azure VM** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 1 queries
- [AIR-BP](02-air-bp.md) — 5 queries
- [ASAP NVMe](03-asap-nvme.md) — 1 queries
- [Container Availability Events (Fa)](04-container-availability-events-fa.md) — 1 queries
- [Container Tables](05-container-tables.md) — 7 queries
- [Events2](06-events2.md) — 1 queries
- [Guest Agent](07-guest-agent.md) — 4 queries
- [Guest Events](08-guest-events.md) — 1 queries
- [Guest Perf Counters](09-guest-perf-counters.md) — 1 queries
- [Host Events](10-host-events.md) — 1 queries
- [HyperVEvents](11-hypervevents.md) — 1 queries
- [IFX Table](12-ifx-table.md) — 1 queries
- [Insights](13-insights.md) — 10 queries
- [IO Stats](14-io-stats.md) — 6 queries
- [Overview & Timeline](15-overview-timeline.md) — 7 queries
- [Virtualization](16-virtualization.md) — 2 queries
- [VM Blobs](17-vm-blobs.md) — 2 queries
- [VM Counters — 5 Minute Counters](18a-vm-counters--5-minute-counters.md) — 1 queries
- [VM Counters — ASAP (OVL 2.0+)](18b-vm-counters--asap-ovl-2-0.md) — 35 queries
- [VM Counters (part 3/7)](18c-vm-counters--asap-vm-events.md) — 10 queries
- [VM Counters — Latency](18d-vm-counters--latency.md) — 49 queries
- [VM Counters — MPF Stats (v6 VMs Temp Disk) ](18e-vm-counters--mpf-stats-v6-vms-temp-disk.md) — 2 queries
- [VM Counters — Shoebox](18f-vm-counters--shoebox.md) — 26 queries
- [VM Counters (part 7/7)](18g-vm-counters--surface.md) — 23 queries
- [VM Details](19-vm-details.md) — 14 queries
- [VM Disk IO Latency Stats](20-vm-disk-io-latency-stats.md) — 5 queries
- [VM Downtime Events (VMA)](21-vm-downtime-events-vma.md) — 1 queries
- [VM Health](22-vm-health.md) — 10 queries

**Total queries: 228**

## Query index (by file)

### (top-level)

- Retrieve Resource "Azure VM" — see [01-top-level.md](01-top-level.md)

### AIR-BP

- Azure VM AirManagedEventsBrownouts — see [02-air-bp.md](02-air-bp.md)
- Azure Host VM AIRBP Disk — see [02-air-bp.md](02-air-bp.md)
- Azure Host VM Disk AIRBP Timeline — see [02-air-bp.md](02-air-bp.md)
- VM_XHealth_DiskBlackoutXStoreTriage — see [02-air-bp.md](02-air-bp.md)
- Azure VM AIRBP Managed Events — see [02-air-bp.md](02-air-bp.md)

### ASAP NVMe

- Azure VM ASAP NVMe TDPR Query — see [03-asap-nvme.md](03-asap-nvme.md)

### Container Availability Events (Fa)

- Azure Host VM Container Availability Impacting Events — see [04-container-availability-events-fa.md](04-container-availability-events-fa.md)

### Container Tables

- Gandalf Container Fault Query — see [05-container-tables.md](05-container-tables.md)
- Azure Host VM Container Health Snapshot — see [05-container-tables.md](05-container-tables.md)
- Gandalf Rogue Container Query — see [05-container-tables.md](05-container-tables.md)
- Azure Host VM ContainerSnapshot History — see [05-container-tables.md](05-container-tables.md)
- NodeService Events — see [05-container-tables.md](05-container-tables.md)
- RdAgent Container Traces — see [05-container-tables.md](05-container-tables.md)
- Gandalf Rogue Container Query — see [05-container-tables.md](05-container-tables.md)

### Events2

- Azure VM ASAP TDPR Query — see [06-events2.md](06-events2.md)

### Guest Agent

- Azure Host VM Guest Agent Events — see [07-guest-agent.md](07-guest-agent.md)
- Azure Host VM Guest Agent Generic Logs — see [07-guest-agent.md](07-guest-agent.md)
- Azure Host VM Guest Agent Perf Counters — see [07-guest-agent.md](07-guest-agent.md)
- GuestAgentPerformanceCounterEvents — see [07-guest-agent.md](07-guest-agent.md)

### Guest Events

- Azure Host VM SC Events — see [08-guest-events.md](08-guest-events.md)

### Guest Perf Counters

- Azure Host VM HostStorage Guest Counters — see [09-guest-perf-counters.md](09-guest-perf-counters.md)

### Host Events

- Azure Host VM TDPR HyperV Events — see [10-host-events.md](10-host-events.md)

### HyperVEvents

- HyperVEventsV2 Guest Query — see [11-hypervevents.md](11-hypervevents.md)

### IFX Table

- Azure VM IFX Table — see [12-ifx-table.md](12-ifx-table.md)

### Insights

- node_insights_summary — see [13-insights.md](13-insights.md)
- Get  Disk Properties for Aquila — see [13-insights.md](13-insights.md)
- Get Tracker Guid — see [13-insights.md](13-insights.md)
- Progress Counter Query — see [13-insights.md](13-insights.md)
- get_control_startTime — see [13-insights.md](13-insights.md)
- Call Latency API 4 — see [13-insights.md](13-insights.md)
- Azure Host VM Active Blobs Filter — see [13-insights.md](13-insights.md)
- Azure Host VM Azure Core RCA — see [13-insights.md](13-insights.md)
- Azure Host VM VmAvailability Events  — see [13-insights.md](13-insights.md)
- Container_Insights_Summary — see [13-insights.md](13-insights.md)

### IO Stats

- Azure Host VM TDPR IO timechart — see [14-io-stats.md](14-io-stats.md)
- Azure Host VM Active Blobs Filter — see [14-io-stats.md](14-io-stats.md)
- Azure Host VM TDPR IO Stats Provisioning — see [14-io-stats.md](14-io-stats.md)
- Azure Host VM TDPR IO Stats Prefetch — see [14-io-stats.md](14-io-stats.md)
- Azure Host VM TDPR Surface Stats Provisioning — see [14-io-stats.md](14-io-stats.md)
- Azure Host VM TDPR IO Stats Boot — see [14-io-stats.md](14-io-stats.md)

### Overview & Timeline

- Prefetch — see [15-overview-timeline.md](15-overview-timeline.md)
- VmBoot — see [15-overview-timeline.md](15-overview-timeline.md)
- Provisioning — see [15-overview-timeline.md](15-overview-timeline.md)
- Xstore Server Read Latency — see [15-overview-timeline.md](15-overview-timeline.md)
- Azure Host VM TDPR Reads from Cache Latency — see [15-overview-timeline.md](15-overview-timeline.md)
- EG for VM — see [15-overview-timeline.md](15-overview-timeline.md)
- TDPR Insights  — see [15-overview-timeline.md](15-overview-timeline.md)

### Virtualization

- Azure Host VM UnderhillEventTable — see [16-virtualization.md](16-virtualization.md)
- Azure Host VM Virtualization Configuration — see [16-virtualization.md](16-virtualization.md)

### VM Blobs

- Azure Host VM ABCThrottles — see [17-vm-blobs.md](17-vm-blobs.md)
- Azure Host VM Blobs — see [17-vm-blobs.md](17-vm-blobs.md)

### VM Counters — 5 Minute Counters

- Azure Host VM CPU Usage — see [18a-vm-counters--5-minute-counters.md](18a-vm-counters--5-minute-counters.md)

### VM Counters — ASAP (OVL 2.0+)

- GetASAPNSIndicesGlobalKQL — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- AsapContainerFOStatsAllDisks_GlobalKQL — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapFOStats_FOPercentsQuery_asapPF — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- MinLatencyFloorDelaysPV2VMQuery — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- GetNsIndicesForContainer — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- ExceptionsCountQuery_PerVM — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- GetNsIndicesForContainer — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- ASAP_DD_Backend_Latency_Query — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- FailoverPOPercentsDD — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- GetNsIndicesForContainer — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- FOExceptions_PerVM — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStats_asapPF_AllDisks — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- GetNsIndicesForContainer — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStats_asapPF_FODisks — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- GetNsIndicesForContainer — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStats_asapPF_AllDisks — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- GetNsIndicesForContainer — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStats_asapPF_FODisks — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- GetNsIndicesForContainer — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStats_asapPF_AllDisks — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- GetNsIndicesForContainer — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStats_asapPF_FODisks — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- GetNsIndicesForContainer — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapFOStats_DisksSpreadFOPercent_asapPF — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStats_OsCounters_FOPercents — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- DiskCounts_FOPercents_OSCountersV2 — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStatsOsCounters — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStatsOsCountersUseSwpe0 — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStats_OsCounters_AllDisks_Latency — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStats_OsCounters_FODisks_Latency — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- List_AllDisks_OsCounters — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStatsOsCounters — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- asapContainerFOStatsOsCountersUseSwpe0 — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- Azure Host VM Active Blobs Filter — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)
- Azure Host VM ASAP 2.0 IO Stats — see [18b-vm-counters--asap-ovl-2-0.md](18b-vm-counters--asap-ovl-2-0.md)

### VM Counters (part 3/7)

- Azure Host VM ASAP VM AsapPfEtwTraceLogEventViewExtended2 — see [18c-vm-counters--asap-vm-events.md](18c-vm-counters--asap-vm-events.md)
- Azure Host VM Disk Burst Counters — see [18c-vm-counters--asap-vm-events.md](18c-vm-counters--asap-vm-events.md)
- Azure Host VM Active Blobs Filter — see [18c-vm-counters--asap-vm-events.md](18c-vm-counters--asap-vm-events.md)
- VM Burst Counters — see [18c-vm-counters--asap-vm-events.md](18c-vm-counters--asap-vm-events.md)
- Azure Host VM Active Blobs Filter — see [18c-vm-counters--asap-vm-events.md](18c-vm-counters--asap-vm-events.md)
- Azure Host VM CacheUsagePct — see [18c-vm-counters--asap-vm-events.md](18c-vm-counters--asap-vm-events.md)
- Azure Host VM Active Working Sets Filter — see [18c-vm-counters--asap-vm-events.md](18c-vm-counters--asap-vm-events.md)
- Azure Host VM Cache Tier Block Counts — see [18c-vm-counters--asap-vm-events.md](18c-vm-counters--asap-vm-events.md)
- Azure Host VM Active Working Sets Filter — see [18c-vm-counters--asap-vm-events.md](18c-vm-counters--asap-vm-events.md)
- Azure Host VM CacheUsagePct Per WS — see [18c-vm-counters--asap-vm-events.md](18c-vm-counters--asap-vm-events.md)

### VM Counters — Latency

- Azure Host VM HyperV Latency Query — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host Node Mellanox QoS counters — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- RDMA Client Latency from local to peers — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- RDMA Client Latency from peers to local — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host Node RDMA Estats HW Latency Local to Peers — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host RDMA Estats Hardware Peers to local — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Active Blobs Filter — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Stats Ex by HistogramType — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Histogram Layers — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Active Blobs Filter — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Latency IO Stats per Histogram — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Active Blobs Filter — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM UltraSSD Average Latency Per Blob — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Latency Q100 — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Active Blobs Filter — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Active Blobs Filter — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Surface Latency Stats Q50 — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Active Blobs Filter — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Surface Latency Stats Q75 — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Active Blobs Filter — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Latency Q95 — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Latency Q99 — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Active Blobs Filter — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Histogram Layers — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Per Histogram Q100 — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Histogram Layers — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Per Histogram Q50 — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Per Histogram Q75 — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Histogram Layers — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Histogram Layers — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Per Histogram Layer Q95 — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Histogram Layers — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Per Histogram Layer Q99 — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM IO Block Sizes — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Xstore e2e Latency Top Summary — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Xstore Latency Stats — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Xstore Latency Stats — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Xstore Latency Top Summary — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)
- Azure Host VM Xstore Server Lat per Blob — see [18d-vm-counters--latency.md](18d-vm-counters--latency.md)

### VM Counters — MPF Stats (v6 VMs Temp Disk) 

- Azure VM MFND ControllerSettings — see [18e-vm-counters--mpf-stats-v6-vms-temp-disk.md](18e-vm-counters--mpf-stats-v6-vms-temp-disk.md)
- Azure Host VM MPF Stats — see [18e-vm-counters--mpf-stats-v6-vms-temp-disk.md](18e-vm-counters--mpf-stats-v6-vms-temp-disk.md)

### VM Counters — Shoebox

- Azure Host VM Shoebox Read MBytes Sec — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Write Bytes Sec — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Burst BPS Credit — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Disk Bursting IO Credits — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Cache Hit — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Read IOPS — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Write IOPS — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Disk Latency — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Queue Depth — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- DiskBurstBPSMetrics — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- DiskBurstIOPSMetrics — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Disk Bandwidth Consumed Percentage — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Disk IOPS Consumed Percentage — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Insights — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Inbound Flows — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Network InOut Bytes — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Network InOut Bytes — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Outbound Flows — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox CPU Credits — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Disk Consumed Percentage — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox VM Burst Consumed Percentage — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Disk Consumed Percentage — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox VM Disk IOPS — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox VM MBPS — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Total QD — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)
- Azure Host VM Shoebox Memory  — see [18f-vm-counters--shoebox.md](18f-vm-counters--shoebox.md)

### VM Counters (part 7/7)

- Azure Host StorageClient Surface Counter Stats — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM Active Blobs Filter — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- VM Throttling Metrics Chart — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM Active Blobs Filter — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM Throttle Stats — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM Active Blobs Filter — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- VdcAIRBPQueryRCA — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- VdcAIRBPQueryRCACount — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- VdcAIRBPQuery — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- VdcBlobcacheThrottleStats — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host Analyzer VM Vdc Blob Properties — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM Active Blobs Filter — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host Analyzer VM Vdc Counters — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM AIR-RDMA — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM Vhddisk Etw Evt1 Failures — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM Vhddisk MaxTime Summary — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM Xstore Role Crash — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure VM Vhddisk Timeline Events — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure VM Vhddisk Timeline Events Full — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM Active Blobs Filter — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM XDisk Transport Percentage — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM XDisk Counter Stats — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)
- Azure Host VM Active Blobs Filter — see [18g-vm-counters--surface.md](18g-vm-counters--surface.md)

### VM Details

- Azure Host VM VMA Query — see [19-vm-details.md](19-vm-details.md)
- Azure Host VM Health Timeline — see [19-vm-details.md](19-vm-details.md)
- Azure Host VM Impactful Events — see [19-vm-details.md](19-vm-details.md)
- Azure Host VM CRP Actions — see [19-vm-details.md](19-vm-details.md)
- Azure Host VM DiskRP Actions — see [19-vm-details.md](19-vm-details.md)
- Kyber Annotation Timeline — see [19-vm-details.md](19-vm-details.md)
- Azure Container Reuse Rejection — see [19-vm-details.md](19-vm-details.md)
- Service Healing Trigger — see [19-vm-details.md](19-vm-details.md)
- Service Healing Tenant Status — see [19-vm-details.md](19-vm-details.md)
- Azure Host VM ArmId — see [19-vm-details.md](19-vm-details.md)
- Azure Host VM HyperVVmConfigSnapshot — see [19-vm-details.md](19-vm-details.md)
- Azure Host Node StorageClient Insights — see [19-vm-details.md](19-vm-details.md)
- Azure Host VM StorageClient Insights — see [19-vm-details.md](19-vm-details.md)
- Azure Host VM Insights 3 — see [19-vm-details.md](19-vm-details.md)

### VM Disk IO Latency Stats

- Azure Host VM ASAP Latency Stats — see [20-vm-disk-io-latency-stats.md](20-vm-disk-io-latency-stats.md)
- Azure Host VM Hyperv Disk Stats — see [20-vm-disk-io-latency-stats.md](20-vm-disk-io-latency-stats.md)
- AzureHost VM Disk IO Latency Analysis — see [20-vm-disk-io-latency-stats.md](20-vm-disk-io-latency-stats.md)
- Azure Host VM StorageClient IO Latency Stats — see [20-vm-disk-io-latency-stats.md](20-vm-disk-io-latency-stats.md)
- Azure Host VM Active Blobs Filter — see [20-vm-disk-io-latency-stats.md](20-vm-disk-io-latency-stats.md)

### VM Downtime Events (VMA)

- Azure Host VM VMA Query v3 — see [21-vm-downtime-events-vma.md](21-vm-downtime-events-vma.md)

### VM Health

- GHS Annotations — see [22-vm-health.md](22-vm-health.md)
- GHS Health Transitions — see [22-vm-health.md](22-vm-health.md)
- Kyber Health Timeline — see [22-vm-health.md](22-vm-health.md)
- Kyber Metrics — see [22-vm-health.md](22-vm-health.md)
- Kyber Container Health Metrics — see [22-vm-health.md](22-vm-health.md)
- AzPubSub RdAgent Events — see [22-vm-health.md](22-vm-health.md)
- RdAgent Container Annotations — see [22-vm-health.md](22-vm-health.md)
- Azure Host VM Health — see [22-vm-health.md](22-vm-health.md)
- Azure Host VM Health - State Changes — see [22-vm-health.md](22-vm-health.md)
- Azure Host VM Scheduled Event Notifications — see [22-vm-health.md](22-vm-health.md)
