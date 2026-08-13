# Azure Host — Azure VM: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:13:41.829Z.
> Total: 176 unique KQL queries across 160 panels (228 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Azure VM" | ResourceGet | AzureCM | AzureCM | globalFrom, globalTo, local_containerId, local_nodeId, local_virtualMachineUniqueId |

### AIR-BP >  Brownouts > AIR-BP Brownouts
Path: `AIR-BP >  Brownouts > AIR-BP Brownouts`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure VM AirManagedEventsBrownouts | Table | vmainsight | Air | startTime, endTime, queryNodeId, queryContainerId |

### AIR-BP > Disk > Disk > AIR-BP for Disks attached to the VM
Path: `AIR-BP > Disk > Disk > AIR-BP for Disks attached to the VM`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM AIRBP Disk | Table | Vmainsight | Air | startTime, endTime, containerId, nodeId |

### AIR-BP > Disk > Disk > Timeline of AIR-BP for Disks attached to the VM 
Path: `AIR-BP > Disk > Disk > Timeline of AIR-BP for Disks attached to the VM `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Disk AIRBP Timeline | TimeSeries | vmainsight | Air | startTime, endTime, nodeId, containerId |

### AIR-BP > DiskBlackoutXStoreTriage > DiskBlackoutXStoreTriage
Path: `AIR-BP > DiskBlackoutXStoreTriage > DiskBlackoutXStoreTriage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM_XHealth_DiskBlackoutXStoreTriage | Table | xlivesite | XHealthDiskTriage | startTime, endTime, nodeId, cluster, vmId, containerId |

### AIR-BP > Managed Events > AIR-BP Managed Events
Path: `AIR-BP > Managed Events > AIR-BP Managed Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure VM AIRBP Managed Events | Table | vmainsight | Air | startTime, endTime, queryNodeId, queryContainerId |

### ASAP NVMe
Path: `ASAP NVMe`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure VM ASAP NVMe TDPR Query | Table | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### Container Availability Events (Fa) > ContainerAvailabilityImpactingEtwTable
Path: `Container Availability Events (Fa) > ContainerAvailabilityImpactingEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Container Availability Impacting Events | Table | azcore.centralus | Fa | _startTime, _endTime, _vmId |

### Container Tables > Container Faults > ContainerFaults
Path: `Container Tables > Container Faults > ContainerFaults`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Gandalf Container Fault Query | Table | gandalfdeepad | gandalf_deepAD | _startTime, _endTime, _nodeId, _containerId |

### Container Tables > Container Health Snapshot > Container Health Snapshot > LogContainerHealthSnapshot
Path: `Container Tables > Container Health Snapshot > Container Health Snapshot > LogContainerHealthSnapshot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Container Health Snapshot | Table | AzureCM | AzureCM | startTime, endTime, vmId, cId |

### Container Tables > Container Snapshot History for VMId
Path: `Container Tables > Container Snapshot History for VMId`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Gandalf Rogue Container Query | MultiRow | https://gandalfdeepad | gandalf_deepad | _startTime, _endTime, _container_id, _node_id |

### Container Tables > Container Snapshot History for VMId > Container Snapshot History for VMId > LogContainerSnapshot
Path: `Container Tables > Container Snapshot History for VMId > Container Snapshot History for VMId > LogContainerSnapshot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM ContainerSnapshot History | Table | AzureCM | AzureCM | startTime, endTime, vmId, cId |

### Container Tables > NodeService Events > NodeServiceEventEtwTable
Path: `Container Tables > NodeService Events > NodeServiceEventEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeService Events | Table | azcore.centralus | Fa | startTime, endTime, containerId, nodeId |

### Container Tables > RdAgent Ifx Operations > IfxOperationV2v1EtwTable
Path: `Container Tables > RdAgent Ifx Operations > IfxOperationV2v1EtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RdAgent Container Traces | Table | https://azcore.centralus | Fa | queryFrom, queryTo, containerId, nodeId |

### Container Tables > Rogue Container > GetRogueContainerData
Path: `Container Tables > Rogue Container > GetRogueContainerData`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Gandalf Rogue Container Query | Table | https://gandalfdeepad | gandalf_deepad | _startTime, _endTime, _containerId, _nodeId |

### Events2 > Events2 (all events from ASAP, Hyper-V, Blobcache, WinEvents)
Path: `Events2 > Events2 (all events from ASAP, Hyper-V, Blobcache, WinEvents)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure VM ASAP TDPR Query | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### Guest Agent > Events > Events > Guest Agent Events
Path: `Guest Agent > Events > Events > Guest Agent Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Guest Agent Events | Table | azcore.centralus | Fa | startTime, endTime, containerId, qIncludeSummary |

### Guest Agent > Generic Logs > Generic Logs > Guest Agent Generic Logs
Path: `Guest Agent > Generic Logs > Generic Logs > Guest Agent Generic Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Guest Agent Generic Logs | Table | azcore.centralus | Fa | startTime, endTime, containerId |

### Guest Agent > Perf Counter > Perf Counter > Performance Counters
Path: `Guest Agent > Perf Counter > Perf Counter > Performance Counters`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Guest Agent Perf Counters | Table | azcore.centralus | Fa | startTime, endTime, containerId |

### Guest Agent > Perf Counter Chart > Performance Counter
Path: `Guest Agent > Perf Counter Chart > Performance Counter`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GuestAgentPerformanceCounterEvents | TimeSeries | azcore.centralus | Fa | startTime, endTime, containerId |

### Guest Events
Path: `Guest Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM SC Events | Table | storageclient.eastus | Sc | startTime, endTime, containerId |

### Guest Perf Counters > Guest Perf Counters (only for Host Storage Test Windows VMs)
Path: `Guest Perf Counters > Guest Perf Counters (only for Host Storage Test Windows VMs)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM HostStorage Guest Counters | TimeSeries | storageclient.eastus | Sc | queryFrom, queryTo, containerId |

### Host Events > Events for ContainerId (from Hyper-V/ASAP/Blobcache/Vhddisk)
Path: `Host Events > Events for ContainerId (from Hyper-V/ASAP/Blobcache/Vhddisk)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM TDPR HyperV Events | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### HyperVEvents > HyperVEventsV2
Path: `HyperVEvents > HyperVEventsV2`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVEventsV2 Guest Query | Table | azcore.centralus | SharedWorkspace | _startTime, _endTime, _nodeId, _containerId |

### IFX Table > IFX Table for the Container Operations
Path: `IFX Table > IFX Table for the Container Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure VM IFX Table | Table | azcore.centralus | Fa | queryFrom, queryTo, containerId, nodeId |

### Insights > Host Insights
Path: `Insights > Host Insights`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | node_insights_summary | Single | storageclient.eastus | sc | startTime, endTime, nodeId |

### Insights > Latency  Insights (Aquila)
Path: `Insights > Latency  Insights (Aquila)`  ·  Queries: 6

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get  Disk Properties for Aquila | Single | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, cluster, vmId |
| 2 | Get Tracker Guid | Single | storageclient.eastus | fa | queryFrom, queryTo |
| 3 | Progress Counter Query | MultiRow | storageclient.eastus | sc | queryFrom, queryTo |
| 4 | get_control_startTime | Single | storageclient.eastus | fa | queryFrom, queryTo |
| 5 | Call Latency API 4 | Single | storageclient.eastus | Sc | startTime, endTime, cluster, nodeId, containerId, blobPath, control_startTime, control_endTime, allBlobDetails, vmId, progress_guid |
| 6 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### Insights > Other > Azure Core RCA
Path: `Insights > Other > Azure Core RCA`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Azure Core RCA | Table | moseisley | Air | startTime, endTime, containerId |

### Insights > Other > VM Availability Impact Events
Path: `Insights > Other > VM Availability Impact Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM VmAvailability Events  | Table | vmainsight | Air | startTime, endTime, vmId |

### Insights > VM Insights
Path: `Insights > VM Insights`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container_Insights_Summary | Single | storageclient.eastus | sc | startTime, endTime, containerId, nodeId |

### IO Stats > IO Charts
Path: `IO Stats > IO Charts`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM TDPR IO timechart | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath |
| 2 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### IO Stats > IO Latency Stats during Provisioning
Path: `IO Stats > IO Latency Stats during Provisioning`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM TDPR IO Stats Provisioning | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### IO Stats > IO Stats during Prefetch
Path: `IO Stats > IO Stats during Prefetch`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM TDPR IO Stats Prefetch | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### IO Stats > IO Stats during Provisioning 
Path: `IO Stats > IO Stats during Provisioning `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM TDPR Surface Stats Provisioning | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### IO Stats > IO Stats during VmBoot
Path: `IO Stats > IO Stats during VmBoot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM TDPR IO Stats Boot | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### Overview & Timeline
Path: `Overview & Timeline`  ·  Queries: 5

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Prefetch | Timeline | egpublic.westus | eg | startTime, endTime, containerId |
| 2 | VmBoot | Timeline | egpublic.westus | eg | startTime, endTime, containerId |
| 3 | Provisioning | Timeline | egpublic.westus | eg | startTime, endTime, containerId |
| 4 | Xstore Server Read Latency | Timeline | egpublic.westus | eg | startTime, endTime, containerId |
| 5 | Azure Host VM TDPR Reads from Cache Latency | Timeline | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### Overview & Timeline > Execution Graph Data for the VM
Path: `Overview & Timeline > Execution Graph Data for the VM`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | EG for VM | Table | egpublic.westus | eg | startTime, endTime, containerId |

### Overview & Timeline > TDPR Insights for the VM (for the time selected)
Path: `Overview & Timeline > TDPR Insights for the VM (for the time selected)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TDPR Insights  | Table | storageclient.eastus | SharedWorkspace | startTime, endTime, containerId, nodeId |

### Virtualization > UnderhillEventTable
Path: `Virtualization > UnderhillEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM UnderhillEventTable | Table | azcore.centralus | Fa | startTime, endTime, nodeId, containerId |

### Virtualization > Virtualization Configuration
Path: `Virtualization > Virtualization Configuration`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Virtualization Configuration | Table | azcore.centralus | Fa | startTime, endTime, nodeId, containerId |

### VM Blobs > ABC Throttles
Path: `VM Blobs > ABC Throttles`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM ABCThrottles | Table | storageclient.eastus | Fa | nodeId, containerId, startTime, endTime, vmId |

### VM Blobs > Disks Attached to the VM
Path: `VM Blobs > Disks Attached to the VM`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Blobs | Table | storageclient.eastus | SharedWorkspace | _containerId, _startTime, _endTime, _nodeId, _cluster, _vmId |

### VM Counters > 5 Minute Counters > 5 Minute Counters > VM Counters
Path: `VM Counters > 5 Minute Counters > 5 Minute Counters > VM Counters`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM CPU Usage | TimeSeries | azcore.centralus | Fa | nodeId, containerId, startTime, endTime |

### VM Counters > ASAP (OVL 2.0+)
Path: `VM Counters > ASAP (OVL 2.0+)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GetASAPNSIndicesGlobalKQL | Single | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId |
| 2 | AsapContainerFOStatsAllDisks_GlobalKQL | Single | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId, _NsIndex |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > %FO of Total IO: Per VM, FO Disks only i.e UseSwpe = 0
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > %FO of Total IO: Per VM, FO Disks only i.e UseSwpe = 0`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapFOStats_FOPercentsQuery_asapPF | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, _containerId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Avg & Max New Min Latency floor delays PV2: (Unit is in terms of FPGA cycles, MaxDeltaCycles = NewMinLatencyFloor - CurrentMinLatencyFloor)
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Avg & Max New Min Latency floor delays PV2: (Unit is in terms of FPGA cycles, MaxDeltaCycles = NewMinLatencyFloor - CurrentMinLatencyFloor)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | MinLatencyFloorDelaysPV2VMQuery | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, _nodeId, _containerId, _NsIndex |
| 2 | GetNsIndicesForContainer | Filter | https://storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Counts of Exceptions Per VM:
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Counts of Exceptions Per VM:`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ExceptionsCountQuery_PerVM | CategoryChart | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, _containerId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > DD Backend Latency in Ms (Works for 6.91+ PF Versions Only)
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > DD Backend Latency in Ms (Works for 6.91+ PF Versions Only)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GetNsIndicesForContainer | Filter | https://storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |
| 2 | ASAP_DD_Backend_Latency_Query | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, nodeId, _containerId, _NsIndex |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > DD: Failover PO (eSWPE) Reads vs Write Percents
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > DD: Failover PO (eSWPE) Reads vs Write Percents`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FailoverPOPercentsDD | TimeSeries | https://storageclient.eastus | Fa | _startTime, _endTime, _NodeId, _containerId, _NsIndex |
| 2 | GetNsIndicesForContainer | Filter | https://storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > FO Exceptions Per VM 
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > FO Exceptions Per VM `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FOExceptions_PerVM | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, _containerId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > IOPS: FO vs PO (All Disks, includes boot disk)
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > IOPS: FO vs PO (All Disks, includes boot disk)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStats_asapPF_AllDisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId, _NsIndex |
| 2 | GetNsIndicesForContainer | Filter | https://storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > IOPS: FO vs PO (FO enabled Disks)
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > IOPS: FO vs PO (FO enabled Disks)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStats_asapPF_FODisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId, _NsIndex |
| 2 | GetNsIndicesForContainer | Filter | https://storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (All Disks, includes boot disk)
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (All Disks, includes boot disk)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStats_asapPF_AllDisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId, _NsIndex |
| 2 | GetNsIndicesForContainer | Filter | https://storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (FO enabled Disks)
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (FO enabled Disks)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStats_asapPF_FODisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId, _NsIndex |
| 2 | GetNsIndicesForContainer | Filter | https://storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > MBPS: FO vs PO (All Disks, includes boot disk)
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > MBPS: FO vs PO (All Disks, includes boot disk)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStats_asapPF_AllDisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId, _NsIndex |
| 2 | GetNsIndicesForContainer | Filter | https://storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > MBPS: FO vs PO (FO enabled Disks)
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > MBPS: FO vs PO (FO enabled Disks)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStats_asapPF_FODisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId, _NsIndex |
| 2 | GetNsIndicesForContainer | Filter | https://storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Spread of Disks and their %FO (UseSwpe =0)
Path: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Spread of Disks and their %FO (UseSwpe =0)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapFOStats_DisksSpreadFOPercent_asapPF | CategoryChart | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, _containerId |

### VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > %FO of Total IO: Per VM, FO Disks only i.e UseSwpe = 0
Path: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > %FO of Total IO: Per VM, FO Disks only i.e UseSwpe = 0`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStats_OsCounters_FOPercents | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId |

### VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > Disk Spread based on FO Percent KPI (FO Disks only, UseSwpe = 0)
Path: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > Disk Spread based on FO Percent KPI (FO Disks only, UseSwpe = 0)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DiskCounts_FOPercents_OSCountersV2 | CategoryChart | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId |

### VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > IOPS: FO vs PO (All Disks, includes boot disk)
Path: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > IOPS: FO vs PO (All Disks, includes boot disk)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStatsOsCounters | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, _containerId, _nodeId |

### VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > IOPS: FO vs PO (FO enabled Disks)
Path: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > IOPS: FO vs PO (FO enabled Disks)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStatsOsCountersUseSwpe0 | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, _nodeId, _containerId |

### VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > Latency: Average & Max in Ms (All Disks, includes boot disk)
Path: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > Latency: Average & Max in Ms (All Disks, includes boot disk)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStats_OsCounters_AllDisks_Latency | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId |

### VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > Latency: Average & Max in Ms (FO enabled Disks)
Path: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > Latency: Average & Max in Ms (FO enabled Disks)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStats_OsCounters_FODisks_Latency | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId |

### VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > List FO Disks Names used for FO Stats
Path: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > List FO Disks Names used for FO Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | List_AllDisks_OsCounters | Table | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, containerId |

### VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > MBPS, FO vs PO (All Disks, includes boot disk)
Path: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > MBPS, FO vs PO (All Disks, includes boot disk)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStatsOsCounters | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, _containerId, _nodeId |

### VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > MBPS, FO vs PO (FO enabled Disks)
Path: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > MBPS, FO vs PO (FO enabled Disks)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapContainerFOStatsOsCountersUseSwpe0 | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, _nodeId, _containerId |

### VM Counters > ASAP (OVL 2.0+) > IO Stats for Disks
Path: `VM Counters > ASAP (OVL 2.0+) > IO Stats for Disks`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM ASAP 2.0 IO Stats | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId, blobPath |

### VM Counters > ASAP VM Events > Timeline events for the VM from AsapPfEtwTraceLogEventViewExtended
Path: `VM Counters > ASAP VM Events > Timeline events for the VM from AsapPfEtwTraceLogEventViewExtended`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM ASAP VM AsapPfEtwTraceLogEventViewExtended2 | Table | storageclient.eastus | Fa | queryFrom, queryTo, containerID, nodeId |

### VM Counters > Burst > Burst > Disk Burst Counters (XIO Disks)
Path: `VM Counters > Burst > Burst > Disk Burst Counters (XIO Disks)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Disk Burst Counters | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath |
| 2 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### VM Counters > Burst > Burst > VM Burst Counters (Uncached)
Path: `VM Counters > Burst > Burst > VM Burst Counters (Uncached)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM Burst Counters | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Cache > Cache > VM Disk Cache Usage Size in GB (StorageClient)
Path: `VM Counters > Cache > Cache > VM Disk Cache Usage Size in GB (StorageClient)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM CacheUsagePct | TimeSeries | storageclient.eastus | SharedWorkspace | startTime, endTime, containerId, blobPath |

### VM Counters > Cache > Cache Tier Block Counts per WorkingSet (StorageClient)
Path: `VM Counters > Cache > Cache Tier Block Counts per WorkingSet (StorageClient)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Working Sets Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM Cache Tier Block Counts | TimeSeries | storageclient.eastus | SharedWorkspace | startTime, endTime, wsId, nodeId |

### VM Counters > Cache > VM Disk Cache Usage Size Per WorkingSet in GB (StorageClient)
Path: `VM Counters > Cache > VM Disk Cache Usage Size Per WorkingSet in GB (StorageClient)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Working Sets Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM CacheUsagePct Per WS | TimeSeries | storageclient.eastus | Fa | startTime, endTime, wsId, nodeId |

### VM Counters > Latency > Latency > HyperV > IO Latencies
Path: `VM Counters > Latency > Latency > HyperV > IO Latencies`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM HyperV Latency Query | Table | azcore.centralus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > Networking > Mellanox QoS Counters
Path: `VM Counters > Latency > Latency > Networking > Mellanox QoS Counters`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Mellanox QoS counters | TimeSeries | azcore.centralus | Fa | startTime, endTime, nodeId |

### VM Counters > Latency > Latency > Networking > RDMA Client Latency (in microseconds) from local to peers
Path: `VM Counters > Latency > Latency > Networking > RDMA Client Latency (in microseconds) from local to peers`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RDMA Client Latency from local to peers | TimeSeries | azurehn | Azurehn | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > Networking > RDMA Client Latency (in microseconds) from peers to local
Path: `VM Counters > Latency > Latency > Networking > RDMA Client Latency (in microseconds) from peers to local`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RDMA Client Latency from peers to local | TimeSeries | azurehn | Azurehn | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > Networking > RDMA Hardware Latency (in microseconds) from local to peers
Path: `VM Counters > Latency > Latency > Networking > RDMA Hardware Latency (in microseconds) from local to peers`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node RDMA Estats HW Latency Local to Peers | TimeSeries | netperf | NetPerfKustoDB | queryFrom, queryTo, nodeId |

### VM Counters > Latency > Latency > Networking > RDMA Hardware Latency (in microseconds) from peers to local
Path: `VM Counters > Latency > Latency > Networking > RDMA Hardware Latency (in microseconds) from peers to local`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host RDMA Estats Hardware Peers to local | TimeSeries | netperf | NetPerfKustoDB | queryFrom, queryTo, nodeId |

### VM Counters > Latency > Latency > StorageClient > IO Stats > IO Stats > IO Stats by TimeTaken (select the Histogram Layer)
Path: `VM Counters > Latency > Latency > StorageClient > IO Stats > IO Stats > IO Stats by TimeTaken (select the Histogram Layer)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM IO Stats Ex by HistogramType | TimeSeries | storageclient.eastus | Fa | blobPath, startTime, endTime, containerId, nodeId, histogramDesc |
| 3 | Azure Host VM Histogram Layers | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > IO Stats > IO Stats > Total IOs per Histogram Layer
Path: `VM Counters > Latency > Latency > StorageClient > IO Stats > IO Stats > Total IOs per Histogram Layer`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM Latency IO Stats per Histogram | TimeSeries | storageclient.eastus | Fa | blobPath, startTime, endTime, containerId, nodeId, ioSizeBucket |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Average in Milliseconds
Path: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Average in Milliseconds`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM UltraSSD Average Latency Per Blob | TimeSeries | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId, blobPath |

### VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q100 in milliseconds - Max Latency
Path: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q100 in milliseconds - Max Latency`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Latency Q100 | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath, ioSizeBucket |
| 2 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q50 in milliseconds
Path: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q50 in milliseconds`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM Surface Latency Stats Q50 | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath, ioSizeBucket |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q75 in milliseconds
Path: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q75 in milliseconds`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM Surface Latency Stats Q75 | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath, ioSizeBucket |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q95 in milliseconds
Path: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q95 in milliseconds`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM Latency Q95 | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath, ioSizeBucket |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q99 in milliseconds
Path: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q99 in milliseconds`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Latency Q99 | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath, ioSizeBucket |
| 2 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q100 in milliseconds
Path: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q100 in milliseconds`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Histogram Layers | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |
| 2 | Azure Host VM Per Histogram Q100 | TimeSeries | storageclient.eastus | Fa | histogramDesc, startTime, endTime, containerId, nodeId, ioSizeBucket |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q50 in milliseconds
Path: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q50 in milliseconds`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Histogram Layers | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |
| 2 | Azure Host VM Per Histogram Q50 | TimeSeries | storageclient.eastus | Fa | histogramDesc, startTime, endTime, containerId, nodeId, ioSizeBucket |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q75 in milliseconds
Path: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q75 in milliseconds`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Per Histogram Q75 | TimeSeries | storageclient.eastus | Fa | histogramDesc, startTime, endTime, containerId, nodeId, ioSizeBucket |
| 2 | Azure Host VM Histogram Layers | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q95 in milliseconds
Path: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q95 in milliseconds`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Histogram Layers | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |
| 2 | Azure Host VM Per Histogram Layer Q95 | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, histogramDesc, ioSizeBucket |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q99 in milliseconds
Path: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q99 in milliseconds`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Histogram Layers | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |
| 2 | Azure Host VM Per Histogram Layer Q99 | TimeSeries | storageclient.eastus | Fa | histogramDesc, startTime, endTime, containerId, nodeId, ioSizeBucket |
| 3 | Azure Host VM IO Block Sizes | Filter | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Latency > Latency > StorageServer (Xstore) > Average E2E Latency (in ms) Stats
Path: `VM Counters > Latency > Latency > StorageServer (Xstore) > Average E2E Latency (in ms) Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Xstore e2e Latency Top Summary | Table | azcore.centralus | Fa | queryFrom, queryTo, cluster, containerId, nodeId |

### VM Counters > Latency > Latency > StorageServer (Xstore) > Average E2E Latency (includes Server/Network/Client) (in ms)
Path: `VM Counters > Latency > Latency > StorageServer (Xstore) > Average E2E Latency (includes Server/Network/Client) (in ms)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Xstore Latency Stats | TimeSeries | azcore.centralus | Fa | queryFrom, queryTo, cluster, nodeId, containerId |

### VM Counters > Latency > Latency > StorageServer (Xstore) > Average Server Latency (in ms)
Path: `VM Counters > Latency > Latency > StorageServer (Xstore) > Average Server Latency (in ms)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Xstore Latency Stats | TimeSeries | azcore.centralus | Fa | queryFrom, queryTo, cluster, nodeId, containerId |

### VM Counters > Latency > Latency > StorageServer (Xstore) > Average Server Latency (in ms) Stats
Path: `VM Counters > Latency > Latency > StorageServer (Xstore) > Average Server Latency (in ms) Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Xstore Latency Top Summary | Table | azcore.centralus | Fa | queryFrom, queryTo, cluster, containerId, nodeId |

### VM Counters > Latency > Latency > StorageServer (Xstore) > Per-Blob Average Server Latency (in ms) 
Path: `VM Counters > Latency > Latency > StorageServer (Xstore) > Per-Blob Average Server Latency (in ms) `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Xstore Server Lat per Blob | TimeSeries | azcore.centralus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > MPF Stats (v6 VMs Temp Disk)  > MFND Controller Settings
Path: `VM Counters > MPF Stats (v6 VMs Temp Disk)  > MFND Controller Settings`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure VM MFND ControllerSettings | Table | azcore.centralus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Counters > MPF Stats (v6 VMs Temp Disk)  > MPF Telemetry
Path: `VM Counters > MPF Stats (v6 VMs Temp Disk)  > MPF Telemetry`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM MPF Stats | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Counters > Shoebox > Shoebox > Disk Bandwidth > Disk Bandwidth > Per Disk (LUN) Read MBytes/sec Average by minute
Path: `VM Counters > Shoebox > Shoebox > Disk Bandwidth > Disk Bandwidth > Per Disk (LUN) Read MBytes/sec Average by minute`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Read MBytes Sec | TimeSeries | azcore.centralus | Fa | startTime, endTime, shoeboxAccount, vmId |

### VM Counters > Shoebox > Shoebox > Disk Bandwidth > Disk Bandwidth > Per Disk (LUN) Write MBytes/sec Average by minute
Path: `VM Counters > Shoebox > Shoebox > Disk Bandwidth > Disk Bandwidth > Per Disk (LUN) Write MBytes/sec Average by minute`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Write Bytes Sec | TimeSeries | azcore.centralus | Fa | startTime, endTime, shoeboxAccount, vmId |

### VM Counters > Shoebox > Shoebox > Disk Bursting > Disk Bursting > Per Disk (LUN) Burst BPS Credits Percentage
Path: `VM Counters > Shoebox > Shoebox > Disk Bursting > Disk Bursting > Per Disk (LUN) Burst BPS Credits Percentage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Burst BPS Credit | TimeSeries | storageclient.eastus | SharedWorkspace | startTime, endTime, shoeboxAccount, vmId |

### VM Counters > Shoebox > Shoebox > Disk Bursting > Disk Bursting > Per Disk (LUN) Burst IO Credits Percentage
Path: `VM Counters > Shoebox > Shoebox > Disk Bursting > Disk Bursting > Per Disk (LUN) Burst IO Credits Percentage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Disk Bursting IO Credits | TimeSeries | storageclient.eastus | SharedWorkspace | startTime, endTime, shoeboxAccount, vmId |

### VM Counters > Shoebox > Shoebox > Disk Cache Hit > Disk Cache Hit > Per Disk (LUN) Cache Hit Percentage (per 5 mins)
Path: `VM Counters > Shoebox > Shoebox > Disk Cache Hit > Disk Cache Hit > Per Disk (LUN) Cache Hit Percentage (per 5 mins)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Cache Hit | TimeSeries | storageclient.eastus | SharedWorkspace | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > Disk IOPS > Disk IOPS > Per Disk (LUN) Read IOPS by minute
Path: `VM Counters > Shoebox > Shoebox > Disk IOPS > Disk IOPS > Per Disk (LUN) Read IOPS by minute`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Read IOPS | TimeSeries | azcore.centralus | Fa | startTime, endTime, shoeboxAccount, vmId |

### VM Counters > Shoebox > Shoebox > Disk IOPS > Disk IOPS > Per Disk (LUN) Write IOPS by minute
Path: `VM Counters > Shoebox > Shoebox > Disk IOPS > Disk IOPS > Per Disk (LUN) Write IOPS by minute`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Write IOPS | TimeSeries | azcore.centralus | Fa | startTime, endTime, shoeboxAccount, vmId |

### VM Counters > Shoebox > Shoebox > Disk Latency (Preview) > Disk Latency 
Path: `VM Counters > Shoebox > Shoebox > Disk Latency (Preview) > Disk Latency `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Disk Latency | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > Disk QD > Disk QD > Per Disk (LUN) Queue Depth Average by minute
Path: `VM Counters > Shoebox > Shoebox > Disk QD > Disk QD > Per Disk (LUN) Queue Depth Average by minute`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Queue Depth | TimeSeries | azcore.centralus | Fa | startTime, endTime, shoeboxAccount, vmId |

### VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Burst BPS Percentage Counters (Uncached)
Path: `VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Burst BPS Percentage Counters (Uncached)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DiskBurstBPSMetrics | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Burst IOPS Percentage Counters (Uncached)
Path: `VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Burst IOPS Percentage Counters (Uncached)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DiskBurstIOPSMetrics | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Percentage > Per Disk (LUN) Bandwidth Consumed Percentage by minute (Uncached)
Path: `VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Percentage > Per Disk (LUN) Bandwidth Consumed Percentage by minute (Uncached)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Disk Bandwidth Consumed Percentage | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Percentage > Per Disk (LUN) IOPS Consumed Percentage by minute (Uncached)
Path: `VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Percentage > Per Disk (LUN) IOPS Consumed Percentage by minute (Uncached)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Disk IOPS Consumed Percentage | TimeSeries | azcore.centralus | Fa | startTime, endTime, shoeboxAccount, vmId |

### VM Counters > Shoebox > Shoebox > Info > Shoebox Insights
Path: `VM Counters > Shoebox > Shoebox > Info > Shoebox Insights`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Insights | Table | storageclient.eastus | SharedWorkspace | startTime, endTime, nodeId, containerId |

### VM Counters > Shoebox > Shoebox > Networking > Networking > Inbound Flows
Path: `VM Counters > Shoebox > Shoebox > Networking > Networking > Inbound Flows`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Inbound Flows | TimeSeries | azcore.centralus | Fa | vmId, shoeboxAccount, startTime, endTime |

### VM Counters > Shoebox > Shoebox > Networking > Networking > Network In (Megabits per second)
Path: `VM Counters > Shoebox > Shoebox > Networking > Networking > Network In (Megabits per second)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Network InOut Bytes | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > Networking > Networking > Network Out (Megabits per second)
Path: `VM Counters > Shoebox > Shoebox > Networking > Networking > Network Out (Megabits per second)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Network InOut Bytes | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > Networking > Networking > Outbound Flows
Path: `VM Counters > Shoebox > Shoebox > Networking > Networking > Outbound Flows`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Outbound Flows | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > VM CPU > CPU Credits
Path: `VM Counters > Shoebox > Shoebox > VM CPU > CPU Credits`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox CPU Credits | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > VM CPU > CPU Percentage
Path: `VM Counters > Shoebox > Shoebox > VM CPU > CPU Percentage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Disk Consumed Percentage | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > VM Disk Limits > VM Percentage > VM Burst Percentage Counters
Path: `VM Counters > Shoebox > Shoebox > VM Disk Limits > VM Percentage > VM Burst Percentage Counters`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox VM Burst Consumed Percentage | TimeSeries | storageclient.eastus | SharedWorkspace | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > VM Disk Limits > VM Percentage > VM Shoebox Percentage Counters
Path: `VM Counters > Shoebox > Shoebox > VM Disk Limits > VM Percentage > VM Shoebox Percentage Counters`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Disk Consumed Percentage | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > VM IO Stats > VM IO Stats > VM Total IOPS (by minute avg)
Path: `VM Counters > Shoebox > Shoebox > VM IO Stats > VM IO Stats > VM Total IOPS (by minute avg)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox VM Disk IOPS | TimeSeries | azcore.centralus | Fa | startTime, endTime, shoeboxAccount, vmId, containerId, nodeId |

### VM Counters > Shoebox > Shoebox > VM IO Stats > VM IO Stats > VM Total MBytes/Sec (by minute avg)
Path: `VM Counters > Shoebox > Shoebox > VM IO Stats > VM IO Stats > VM Total MBytes/Sec (by minute avg)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox VM MBPS | TimeSeries | azcore.centralus | Fa | startTime, endTime, shoeboxAccount, vmId, containerId, nodeId |

### VM Counters > Shoebox > Shoebox > VM IO Stats > VM QD (Total QD cumulative of all disks attached to VM by minute)
Path: `VM Counters > Shoebox > Shoebox > VM IO Stats > VM QD (Total QD cumulative of all disks attached to VM by minute)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Total QD | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Shoebox > Shoebox > VM Memory > VM Memory > Available Memory Bytes
Path: `VM Counters > Shoebox > Shoebox > VM Memory > VM Memory > Available Memory Bytes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Shoebox Memory  | TimeSeries | azcore.centralus | Fa | startTime, endTime, vmId, shoeboxAccount |

### VM Counters > Surface > Surface > Surface Counter Stats (StorageClient)
Path: `VM Counters > Surface > Surface > Surface Counter Stats (StorageClient)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host StorageClient Surface Counter Stats | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath |
| 2 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### VM Counters > Throttling > Throttling > Throttle Stats (StorageClient) > Throttle Stats (StorageClient) > VM Throttle metrics (5 min average)
Path: `VM Counters > Throttling > Throttling > Throttle Stats (StorageClient) > Throttle Stats (StorageClient) > VM Throttle metrics (5 min average)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM Throttling Metrics Chart | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId, blobPath |
| 2 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### VM Counters > Throttling > Throttling > Throttle Stats (StorageClient) > Throttle Stats (StorageClient) > VM Throttle Stats
Path: `VM Counters > Throttling > Throttling > Throttle Stats (StorageClient) > Throttle Stats (StorageClient) > VM Throttle Stats`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Throttle Stats | Table | storageclient.eastus | SharedWorkspace | startTime, endTime, containerId, blobPath |
| 2 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### VM Counters > Vdc (UltraDisk Client) > AIR-BP Triage > RCA Categories
Path: `VM Counters > Vdc (UltraDisk Client) > AIR-BP Triage > RCA Categories`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VdcAIRBPQueryRCA | CategoryChart | storageclient.eastus | Analytics | startTime, endTime, nodeId, containerId |
| 2 | VdcAIRBPQueryRCACount | Table | storageclient.eastus | Analytics | startTime, endTime, nodeId, containerId |

### VM Counters > Vdc (UltraDisk Client) > AIR-BP Triage > VdcTriage Function output
Path: `VM Counters > Vdc (UltraDisk Client) > AIR-BP Triage > VdcTriage Function output`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VdcAIRBPQuery | Table | storageclient.eastus | Analytics | startTime, endTime, containerId, nodeId |

### VM Counters > Vdc (UltraDisk Client) > Blobcache Throttle Stats > Blobcache Throttle Stats
Path: `VM Counters > Vdc (UltraDisk Client) > Blobcache Throttle Stats > Blobcache Throttle Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VdcBlobcacheThrottleStats | TimeSeries | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### VM Counters > Vdc (UltraDisk Client) > Disk Info > Vdc Blob Properties (Ultra/Premium V2)
Path: `VM Counters > Vdc (UltraDisk Client) > Disk Info > Vdc Blob Properties (Ultra/Premium V2)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Analyzer VM Vdc Blob Properties | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > Vdc (UltraDisk Client) > Vdc Counters > Vdc Counters (Storage Client)
Path: `VM Counters > Vdc (UltraDisk Client) > Vdc Counters > Vdc Counters (Storage Client)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host Analyzer VM Vdc Counters | TimeSeries | storageclient.eastus | Fa | startTime, endTime, blobPath, containerId, nodeId |

### VM Counters > XDisk > XDisk > Debug Report > AIR-RDMA
Path: `VM Counters > XDisk > XDisk > Debug Report > AIR-RDMA`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM AIR-RDMA | Table | moseisley | Air | queryFrom, queryTo, containerId, nodeId |

### VM Counters > XDisk > XDisk > Debug Report > ETW Event 1: Failures
Path: `VM Counters > XDisk > XDisk > Debug Report > ETW Event 1: Failures`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Vhddisk Etw Evt1 Failures | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > XDisk > XDisk > Debug Report > Max/Min Response time at Vhddisk Layer (including retries)
Path: `VM Counters > XDisk > XDisk > Debug Report > Max/Min Response time at Vhddisk Layer (including retries)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Vhddisk MaxTime Summary | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, vmId |

### VM Counters > XDisk > XDisk > Debug Report > Xstore Role Crash data (hosting blobs of this VM)
Path: `VM Counters > XDisk > XDisk > Debug Report > Xstore Role Crash data (hosting blobs of this VM)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Xstore Role Crash | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId |

### VM Counters > XDisk > XDisk > Timeline of Vhddisk Events
Path: `VM Counters > XDisk > XDisk > Timeline of Vhddisk Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure VM Vhddisk Timeline Events | Single | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, vmId |

### VM Counters > XDisk > XDisk > Timeline of Vhddisk Events > Vhddisk Events for Disks attached to this VM
Path: `VM Counters > XDisk > XDisk > Timeline of Vhddisk Events > Vhddisk Events for Disks attached to this VM`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure VM Vhddisk Timeline Events Full | Table | storageclient.eastus | Fa | startTime, endTime, containerId, vmId, nodeId |

### VM Counters > XDisk > XDisk > Transport Percentage > Transport Percentage > IOPS percentage by Transport
Path: `VM Counters > XDisk > XDisk > Transport Percentage > Transport Percentage > IOPS percentage by Transport`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 2 | Azure Host VM XDisk Transport Percentage | TimeSeries | azcore.centralus | Fa | blobPath, startTime, endTime, containerId, nodeId |

### VM Counters > XDisk > XDisk > XDisk Counters > XDisk Counters > XDisk Counter Stats (StorageClient)
Path: `VM Counters > XDisk > XDisk > XDisk Counters > XDisk Counters > XDisk Counter Stats (StorageClient)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM XDisk Counter Stats | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath |
| 2 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### VM Details
Path: `VM Details`  ·  Queries: 9

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM VMA Query | Timeline | vmainsight | vmadb | startTime, endTime, containerIdStr, cloudEnv |
| 2 | Azure Host VM Health Timeline | Timeline | azcore.centralus | Fa | containerId, startTime, endTime |
| 3 | Azure Host VM Impactful Events | Timeline | vmainsight | Air | startTime, endTime, containerId |
| 4 | Azure Host VM CRP Actions | Timeline | Azcrp | crp_allprod | startTime, endTime, vmId |
| 5 | Azure Host VM DiskRP Actions | Timeline | disks | Disks | startTime, endTime, containerId, nodeId |
| 6 | Kyber Annotation Timeline | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, containerId |
| 7 | Azure Container Reuse Rejection | Timeline | AzureCM | AzureCM | startTime, endTime, containerId |
| 8 | Service Healing Trigger | Timeline | AzureCM | AzureCM | queryFrom, tenant, queryTo |
| 9 | Service Healing Tenant Status | Timeline | AzureCM | AzureCM | queryFrom, queryTo, tenantName |

### VM Details > {{VMName}} Details
Path: `VM Details > {{VMName}} Details`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM ArmId | Single | azcore.centralus | Fa | startTime, endTime, containerId |
| 2 | Azure Host VM HyperVVmConfigSnapshot | Single | azcore.centralus | Fa | startTime, endTime, containerId, nodeId |

### VM Details > Insights for Host Node where VM is running 
Path: `VM Details > Insights for Host Node where VM is running `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node StorageClient Insights | Table | storageclient.eastus | SharedWorkspace | nodeId, startTime, endTime, containerId |

### VM Details > Insights for the VM (for the time selected)
Path: `VM Details > Insights for the VM (for the time selected)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM StorageClient Insights | Table | storageclient.eastus | SharedWorkspace | containerId, startTime, endTime, nodeId |
| 2 | Azure Host VM Insights 3 | Table | storageclient.eastus | SharedWorkspace | startTime, endTime, nodeId, containerId |

### VM Disk IO Latency Stats > ASAP Latency Bucket Summary
Path: `VM Disk IO Latency Stats > ASAP Latency Bucket Summary`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM ASAP Latency Stats | Table | storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Disk IO Latency Stats > Hyper-V Layer Latency Bucket Summary
Path: `VM Disk IO Latency Stats > Hyper-V Layer Latency Bucket Summary`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Hyperv Disk Stats | Table | azcore.centralus | Fa | queryFrom, queryTo, containerId, nodeId |

### VM Disk IO Latency Stats > IO Latency Analysis
Path: `VM Disk IO Latency Stats > IO Latency Analysis`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzureHost VM Disk IO Latency Analysis | Table | storageclient.eastus | Fa | startTime, endTime, containerId |

### VM Disk IO Latency Stats > StorageClient IO Stats
Path: `VM Disk IO Latency Stats > StorageClient IO Stats`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM StorageClient IO Latency Stats | Table | storageclient.eastus | Fa | containerId, startTime, endTime, blobPath, nodeId, Cloud |
| 2 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |

### VM Downtime Events (VMA) > VM Availability Events
Path: `VM Downtime Events (VMA) > VM Availability Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM VMA Query v3 | Table | Vmainsight | vmadb | startTime, endTime, nodeId, containerId, vmId |

### VM Health > GHS Data > GHS Annotations [VmUniqueId]
Path: `VM Health > GHS Data > GHS Annotations [VmUniqueId]`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GHS Annotations | Table | https://genevahealtheventsprod | ResourceHealthAnnotations | queryFrom, queryTo, ShoeboxAccount, VmId |

### VM Health > GHS Data > GHS Health Transitions [VmUniqueId]
Path: `VM Health > GHS Data > GHS Health Transitions [VmUniqueId]`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GHS Health Transitions | Table | https://genevahealtheventsprod | ResourceHealthTransitions | queryFrom, queryTo, VmId, ShoeboxAccount |

### VM Health > Kyber Health Data > Kyber Health Timeline
Path: `VM Health > Kyber Health Data > Kyber Health Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Kyber Health Timeline | TimeSeries | aplat.westcentralus | APlat | queryFrom, queryTo, containerId |

### VM Health > Kyber Health Data > KyberAnnotationEvents
Path: `VM Health > Kyber Health Data > KyberAnnotationEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Kyber Metrics | Table | https://aplat.westcentralus | Aplat | queryFrom, queryTo, containerId |

### VM Health > Kyber Health Data > KyberContainerHealthMetricData
Path: `VM Health > Kyber Health Data > KyberContainerHealthMetricData`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Kyber Container Health Metrics | Table | https://aplat.westcentralus | APlat | queryFrom, queryTo, containerId |

### VM Health > RdAgent Annotations > AzPubSub Client Event(RdAgent Table)
Path: `VM Health > RdAgent Annotations > AzPubSub Client Event(RdAgent Table)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzPubSub RdAgent Events | Table | https://azcore.centralus | Fa | queryFrom, queryTo, nodeId, containerId |

### VM Health > RdAgent Annotations > RHCAnnotations Raw View
Path: `VM Health > RdAgent Annotations > RHCAnnotations Raw View`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RdAgent Container Annotations | Table | https://azcore.centralus | Fa | queryFrom, queryTo, containerId |

### VM Health > RdAgent Health Metrics > VM Health - All
Path: `VM Health > RdAgent Health Metrics > VM Health - All`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Health | Table | azcore.centralus | Fa | startTime, endTime, containerId |

### VM Health > RdAgent Health Metrics > VM Health - State Changes
Path: `VM Health > RdAgent Health Metrics > VM Health - State Changes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Health - State Changes | Table | azcore.centralus | Fa | startTime, endTime, containerId |

### VM Health > Scheduled Events > Scheduled Events
Path: `VM Health > Scheduled Events > Scheduled Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Scheduled Event Notifications | Table | azpe | azpe | startTime, endTime, roleInstanceName, tenantName |
