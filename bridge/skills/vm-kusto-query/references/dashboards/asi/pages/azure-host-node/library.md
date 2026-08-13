# Azure Host — Azure Host Node: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:13:37.794Z.
> Total: 256 unique KQL queries across 234 panels (276 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Azure Host Node" | ResourceGet | azurecm | AzureCM | local_nodeId, globalFrom, globalTo |
| 2 | ExtendedFaultTable | Table | azcore.centralus | Fa | queryFrom, queryTo, nodeid |

### AIR-BP > Brownouts > Brownouts > AIR-BP Brownouts
Path: `AIR-BP > Brownouts > Brownouts > AIR-BP Brownouts`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host AirManagedEventsBrownouts | Table | vmainsight | Air | startTime, endTime, nodeId |

### AIR-BP > DiskBlackoutXStoreTriage > DiskBlackoutXStoreTriage
Path: `AIR-BP > DiskBlackoutXStoreTriage > DiskBlackoutXStoreTriage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | XHealth_DiskBlackoutXStoreTriage | Table | Xlivesite | XHealthDiskTriage | query_StartTime, query_EndTime, query_NodeId |

### AIR-BP > Disks > Disks > AIR-BP for Disks
Path: `AIR-BP > Disks > Disks > AIR-BP for Disks`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host AIRBP | Table | vmainsight | Air | nodeId, startTime, endTime |

### AIR-BP > Managed Events > Managed Events > AIR-BP Managed Events
Path: `AIR-BP > Managed Events > Managed Events > AIR-BP Managed Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host AIRBP Managed Events | Table | vmainsight | Air | startTime, endTime, nodeId |

### AIR-J > AIR-J Trend > AIR-J Trend > Jitter Trend (1h granularity, 90d retention)
Path: `AIR-J > AIR-J Trend > AIR-J Trend > Jitter Trend (1h granularity, 90d retention)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CPU Jitter comparison with baseline | TimeSeries | intmgmtshared.centralus | Public | nodeId, startTime, endTime |

### AIR-J > AIR-J Trend > AIR-J Trend > Jitter Trend (5sec granularity, 7d retention)
Path: `AIR-J > AIR-J Trend > AIR-J Trend > Jitter Trend (5sec granularity, 7d retention)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CPU Jitter (High granularity) | TimeSeries | intmgmtshared.centralus | Fleet | nodeId, startTime, endTime |

### AIR-J > Utilization & Incidents > Utilization & Incidents > AIR-J incidents
Path: `AIR-J > Utilization & Incidents > Utilization & Incidents > AIR-J incidents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AIR-J Incidents | Table | intmgmtshared.centralus | Public | nodeId, startTime, endTime |

### AIR-J > Utilization & Incidents > Utilization & Incidents > Node Utilization
Path: `AIR-J > Utilization & Incidents > Utilization & Incidents > Node Utilization`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Utilization Landscape | TimeSeries | intmgmtshared.centralus | Public | nodeId, startTime, endTime |

### Direct Drive Performance Tables > Agent Start Operation Performance DD (P50, 90, 99)
Path: `Direct Drive Performance Tables > Agent Start Operation Performance DD (P50, 90, 99)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Agent Start Operations Details Direct Drive (P50, 90, 99) | Table | azcore.centralus | Fa | queryFrom, queryTo |

### Direct Drive Performance Tables > Container Workflow Details DD (P50, 90, 99)
Path: `Direct Drive Performance Tables > Container Workflow Details DD (P50, 90, 99)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Workflow Details Direct Drive (P50, 90, 99) | Table | azurecm | AzureCM | queryFrom, queryTo |

### Direct Drive Performance Tables > IfxOperationV2 Performance DD (P50, 90, 99)
Path: `Direct Drive Performance Tables > IfxOperationV2 Performance DD (P50, 90, 99)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | IfxOperationV2 Performance Details Direct Drive (P50, 90, 99) | Table | azcore.centralus | Fa | queryFrom, queryTo |

### Direct Drive Performance Tables > Node Workflow Details DD (P50, 90, 99)
Path: `Direct Drive Performance Tables > Node Workflow Details DD (P50, 90, 99)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeWorkflow Details Direct Drive (P50, 90, 99) | Table | azurecm | AzureCM | queryFrom, queryTo |

### Fabric Tables > Anvil Events > Anvil Events > Anvil Events
Path: `Fabric Tables > Anvil Events > Anvil Events > Anvil Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Anvil ForgeEvents | Table | azcore.centralus | AzureCP | startTime, endTime, nodeId |

### Fabric Tables > Container Health Snapshot > Container Health Snapshot > LogContainerHealthSnapshot
Path: `Fabric Tables > Container Health Snapshot > Container Health Snapshot > LogContainerHealthSnapshot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ContainerHealth Snapshot | Table | storageclient.eastus | Fc | startTime, endTime, nodeIdStr |

### Fabric Tables > Fabric Fault Handler Recovery > Fabric Fault Handler Recovery > FaultHandlingRecoveryEventEtwTable
Path: `Fabric Tables > Fabric Fault Handler Recovery > Fabric Fault Handler Recovery > FaultHandlingRecoveryEventEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Fabric FaultHandler Recovery | Table | AzureCM | AzureCM | nodeId, startTime, endTime |

### Fabric Tables > Fabric Node Events > Fabric Node Events > TMMgmtNodeEventsEtwTable
Path: `Fabric Tables > Fabric Node Events > Fabric Node Events > TMMgmtNodeEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Fabric Node Events | Table | storageclient.eastus | Fc | nodeId, startTime, endTime |

### Fabric Tables > Fabric Node Faults > Fabric Node Faults > TMMgmtNodeFaultEtwTable
Path: `Fabric Tables > Fabric Node Faults > Fabric Node Faults > TMMgmtNodeFaultEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Fabric Node Faults | Table | storageclient.eastus | Fc | nodeId, startTime, endTime |

### Fabric Tables > Hawkeye Events > Hawkeye Events
Path: `Fabric Tables > Hawkeye Events > Hawkeye Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Hawkeye Events | Table | hawkeyedataexplorer.westus2 | HawkeyeLogs | queryFrom, queryTo, nodeId |

### Fabric Tables > Node State Changes
Path: `Fabric Tables > Node State Changes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LogNodeSnapshot | Table | azurecm.centralus | AzureCM | startTime, endTime, NodeID |

### Fabric Tables > Node State Changes > Node State Changes > TMMgmtNodeStateChangedEtwTable
Path: `Fabric Tables > Node State Changes > Node State Changes > TMMgmtNodeStateChangedEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Fabric Node State Changes | Table | storageclient.eastus | Fc | nodeId, startTime, endTime |

### Fabric Tables > Rogue Containers > GetRogueContainerData
Path: `Fabric Tables > Rogue Containers > GetRogueContainerData`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Gandalf Rogue Containers Query | Table | https://gandalfdeepad | gandalf_deepad | _startTime, _endTime, _nodeId |

### Fabric Tables > SLAMeasurementTable > SLAMeasurementTable > TMMgmtSlaMeasurementEventEtwTable
Path: `Fabric Tables > SLAMeasurementTable > SLAMeasurementTable > TMMgmtSlaMeasurementEventEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Fabric SLAMeasurementTable | Table | AzureCM | AzureCM | startTime, endTime, nodeId |

### Host Charts > ASAP > Node ASAP IO Stats
Path: `Host Charts > ASAP > Node ASAP IO Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM ASAP 2.0 IO Stats | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId, blobPath |

### Host Charts > Host Memory > HostResourceManager High Level Memory Usage (by MaxCommitUsageBytesTotal)
Path: `Host Charts > Host Memory > HostResourceManager High Level Memory Usage (by MaxCommitUsageBytesTotal)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostResourceManager High Level Memory Usage Breakdown | TimeSeries | azcore.centralus | KernelAgent | startTime, endTime, nodeId |

### Host Charts > Host Memory > HostResourceManager Top Pool Tags (by MaxCommitUsageBytesTotal)
Path: `Host Charts > Host Memory > HostResourceManager Top Pool Tags (by MaxCommitUsageBytesTotal)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostResourceManager Top Pool Tags | TimeSeries | azcore.centralus | KernelAgent | startTime, endTime, nodeId |

### Host Charts > Host Memory > HostResourceManager Top Processes (by MaxCommitUsageBytesTotal)
Path: `Host Charts > Host Memory > HostResourceManager Top Processes (by MaxCommitUsageBytesTotal)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostResourceManager Top Processes | TimeSeries | azcore.centralus | KernelAgent | startTime, endTime, nodeId |

### Host Charts > Host Memory > Hypervisor Metadata Memory Partition MBytes
Path: `Host Charts > Host Memory > Hypervisor Metadata Memory Partition MBytes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Hypervisor Metadata Memory Partition | TimeSeries | azcore.centralus | KernelAgent | startTime, endTime, nodeId |

### Host Charts > Host Memory > System Partition MBytes (Host OS)
Path: `Host Charts > Host Memory > System Partition MBytes (Host OS)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Host System Partition Memory | TimeSeries | azcore.centralus | KernelAgent | startTime, endTime, nodeId |

### Host Charts > Host Memory > VM Memory Partition MBytes (including IO Space and metadata)
Path: `Host Charts > Host Memory > VM Memory Partition MBytes (including IO Space and metadata)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM Memory Partition All Pages | TimeSeries | azcore.centralus | KernelAgent | startTime, endTime, nodeId |

### Host Charts > Host Memory > VM Memory Partition MBytes (IO Space only)
Path: `Host Charts > Host Memory > VM Memory Partition MBytes (IO Space only)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM Memory Partition IO Space Pages | TimeSeries | azcore.centralus | KernelAgent | startTime, endTime, nodeId |

### Host Charts > Host System > System > C Drive Free Space %
Path: `Host Charts > Host System > System > C Drive Free Space %`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Drive Free Space | TimeSeries | azcore.centralus | Fa | driveLetter, nodeId, startTime, endTime |

### Host Charts > Host System > System > D Drive Free Space %
Path: `Host Charts > Host System > System > D Drive Free Space %`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Drive Free Space | TimeSeries | azcore.centralus | Fa | driveLetter, nodeId, startTime, endTime |

### Host Charts > Host System > System > Host Available Memory (MBytes)
Path: `Host Charts > Host System > System > Host Available Memory (MBytes)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Available Memory | TimeSeries | storageclient.eastus | Fa | nodeId, startTime, endTime |

### Host Charts > Host System > System > Host CPU (5 seconds)
Path: `Host Charts > Host System > System > Host CPU (5 seconds)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host CPU 5 seconds | TimeSeries | intmgmtshared.centralus | Fleet | startTime, endTime, nodeId |

### Host Charts > Host System > System > Host CPU Usage Graph (1 min avg)
Path: `Host Charts > Host System > System > Host CPU Usage Graph (1 min avg)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VP CPU | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Charts > Host System > System > Host Nonpaged Pool Bytes
Path: `Host Charts > Host System > System > Host Nonpaged Pool Bytes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node NPP Bytes | TimeSeries | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Charts > Host System > System > Host Process Total Handle Count
Path: `Host Charts > Host System > System > Host Process Total Handle Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Process Handle Count | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Charts > Local Disks > Local Disks > Local Disk Avg Latencies (microseconds)
Path: `Host Charts > Local Disks > Local Disks > Local Disk Avg Latencies (microseconds)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostStorage Avg IO Latency | TimeSeries | azcore.centralus | SharedWorkspace | nodeId, startTime, endTime |

### Host Charts > Local Disks > Local Disks > Local Disk Health Status
Path: `Host Charts > Local Disks > Local Disks > Local Disk Health Status`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Disk Status | TimeSeries | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Charts > Local Disks > Local Disks > Local Disk High Latency IO Count
Path: `Host Charts > Local Disks > Local Disks > Local Disk High Latency IO Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostStorage High Latency IO Counts | TimeSeries | azcore.centralus | SharedWorkspace | nodeId, startTime, endTime |

### Host Charts > Local Disks > Local Disks > Local Disk Max Latencies (microseconds)
Path: `Host Charts > Local Disks > Local Disks > Local Disk Max Latencies (microseconds)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostStorage Max IO Latency | TimeSeries | azcore.centralus | SharedWorkspace | startTime, endTime, nodeId |

### Host Charts > Local Disks > Local Disks > StorPort IO Telemetry (per hour)
Path: `Host Charts > Local Disks > Local Disks > StorPort IO Telemetry (per hour)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host StorPort IO Telemetry Stats | TimeSeries | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Charts > MPF > Node MPF IO Stats 
Path: `Host Charts > MPF > Node MPF IO Stats `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM MPF Stats | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId |

### Host Charts > Networking > Networking > Port Count by Process
Path: `Host Charts > Networking > Networking > Port Count by Process`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Networking PortQuotaRundown | TimeSeries | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Charts > Networking > Networking > TCPIP Connection Counters
Path: `Host Charts > Networking > Networking > TCPIP Connection Counters`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TCPIP Connection Counters | TimeSeries | wdgeventstore | HostOSCoreNet | nodeId, startTime, endTime |

### Host Charts > Networking > Networking > TCPIP Performance Counters
Path: `Host Charts > Networking > Networking > TCPIP Performance Counters`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | TCPIP Performance Counters | TimeSeries | wdgeventstore | HostOSCoreNet | nodeId, startTime, endTime |

### Host Charts > VMs CPU > VMs CPU > VM CPU Percentage
Path: `Host Charts > VMs CPU > VMs CPU > VM CPU Percentage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMs CPU Usage | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Charts > VMs Disk IO Stats > VMs Disk IO Stats > VM Disk IOPS (StorageClient)
Path: `Host Charts > VMs Disk IO Stats > VMs Disk IO Stats > VM Disk IOPS (StorageClient)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host StorageClient VMs Disk IOPS | TimeSeries | storageclient.eastus | Fa | nodeIdStr, startTime, endTime |

### Host Charts > VMs Disk IO Stats > VMs Disk IO Stats > VM Disk MBPS (StorageClient)
Path: `Host Charts > VMs Disk IO Stats > VMs Disk IO Stats > VM Disk MBPS (StorageClient)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM StorageClient Disk MBPS | TimeSeries | storageclient.eastus | Fa | nodeIdStr, startTime, endTime |

### Host Charts > VMs Memory > VMs Memory > Average Memory Pressure on VMs
Path: `Host Charts > VMs Memory > VMs Memory > Average Memory Pressure on VMs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMs Memory Usage | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Details
Path: `Host Details`  ·  Queries: 15

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node VMA Query | Timeline | Vmakpi | vmadb | nodeId, startTime, endTime |
| 2 | Azure Host Node State (Fabric) | Timeline | AzureCM | AzureCM | nodeId, startTime, endTime |
| 3 | Azure Host TOR Pingmesh | Timeline | azphynet | azdhmds | startTime, endTime, nodeId |
| 4 | Azure Host Node Power State Timeline | Timeline | storageclient.eastus | Fc | startTime, endTime, nodeId |
| 5 | Azure Host Vhddisk Events Query | Timeline | azcore.centralus | Fa | nodeId, startTime, endTime |
| 6 | Azure Host PF Service Updates | Timeline | AzureCM | AzureCM | startTime, endTime, nodeId |
| 7 | Azure Host Fabric Node Fault | Timeline | storageclient.eastus | Fc | nodeId, startTime, endTime |
| 8 | Azure Host XStore E17 AutoTriage | Timeline | azcore.centralus | XHealth | startTime, endTime, nodeId |
| 9 | Azure Host OSHostPlugin Events | Timeline | azcore.centralus | Fa | startTime, endTime, nodeId |
| 10 | Azure Host Impactful Events | Timeline | vmainsight | Air | startTime, endTime, nodeId |
| 11 | Azure Host Node Updates | Timeline | storageclient.eastus | Fc | startTime, endTime, nodeId |
| 12 | Azure Host Node TIP sessions | Timeline | AzureCM | AzureCM | queryFrom, queryTo, _nodeId |
| 13 | Azure Host Node Events | Timeline | azcore.centralus | Fa | queryFrom, queryTo, nodeId |
| 14 | Azure Fault Recovery Events | Timeline | azurecm | AzureCM | startTime, endTime, nodeId |
| 15 | Azure Node HealthSignal (Fabric) | Timeline | azurecm.centralus | AzureCM | startTime, endTime, NodeID |

### Host Details > {{nodeId}} Properties
Path: `Host Details > {{nodeId}} Properties`  ·  Queries: 4

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Host OS Version | Single | wdgeventstore | HostOSDeploy | queryFrom, queryTo, local_nodeId |
| 2 | Retrieve Node Hardware Details | Single | azuredcm | AzureDCMDb | queryFrom, queryTo, local_nodeId |
| 3 | Cluster Overlake Version (HostOS) | Single | storageclient.eastus | Fc | _nodeId |
| 4 | GetTimeinDeviceDrillFormat | Single | storageclient.eastus | fa | queryFrom, queryTo |

### Host Details > File Versions
Path: `Host Details > File Versions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host FileVersions Query | Table | storageclient.eastus | SharedWorkspace | startTime, endTime, nodeId |

### Host Details > Insights
Path: `Host Details > Insights`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node StorageClient Insights | Table | storageclient.eastus | SharedWorkspace | nodeId, startTime, endTime, containerId |

### Host Details > PF Services
Path: `Host Details > PF Services`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host PF Services Versions | Table | AzureCM | AzureCM | nodeId, startTime, endTime |

### Host Tables > ASC HA Runs > ASC HA Runs > HostAnalyzer Runs from ASC for Host {{nodeId}}
Path: `Host Tables > ASC HA Runs > ASC HA Runs > HostAnalyzer Runs from ASC for Host {{nodeId}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASC HA Runs | Table | Azds | adsmds | nodeId, startTime, endTime |

### Host Tables > Azure Profiler > Azure Profiler > Hottest Callstacks
Path: `Host Tables > Azure Profiler > Azure Profiler > Hottest Callstacks`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Profiler Traces with Hottest Callstacks | Table | azureprofilerfollower.westus2 | azureprofiler | startTime, endTime, nodeId |

### Host Tables > Azure Profiler > Azure Profiler > Hottest Functions > Azure Profiler Traces with Hot Functions
Path: `Host Tables > Azure Profiler > Azure Profiler > Hottest Functions > Azure Profiler Traces with Hot Functions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Profiler | Table | https://azureprofilerfollower.westus2 | azureprofiler | startTime, endTime, nodeId |

### Host Tables > Azure Watson > Azure Watson > Azure Watson Dumps for {{nodeId}}
Path: `Host Tables > Azure Watson > Azure Watson > Azure Watson Dumps for {{nodeId}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Watson Dumps | Table | Azurewatsoncustomer | AzureWatsonCustomer | startTime, endTime, nodeId |

### Host Tables > Hardware > Hardware > SEL Logs > SEL Logs > SEL Logs
Path: `Host Tables > Hardware > Hardware > SEL Logs > SEL Logs > SEL Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host SEL Logs | Table | sparkle.eastus | defaultdb | startTime, endTime, nodeId |

### Host Tables > HealthStore > HealthStore Regressed Signals which stopped the deployment
Path: `Host Tables > HealthStore > HealthStore Regressed Signals which stopped the deployment`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node HealthStore Regressed Signals | Table | storageclient.eastus | sharedworkspace | queryFrom, queryTo, nodeId |

### Host Tables > HealthStore > HealthStore Underthreshold Signals
Path: `Host Tables > HealthStore > HealthStore Underthreshold Signals`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node HealthStore UnderThreshold Signals | Table | storageclient.eastus | sharedworkspace | queryFrom, queryTo, nodeId |

### Host Tables > Host Disk Storage > Disk Storage > Disk Inventory > Disk Inventory > HostStorage DCM Inventory
Path: `Host Tables > Host Disk Storage > Disk Storage > Disk Inventory > Disk Inventory > HostStorage DCM Inventory`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostStorage DCM Inventory | Table | Azuredcm | AzureDCMDb | nodeId |

### Host Tables > Host Disk Storage > Disk Storage > Disk IO Errors > Disk IO Errors
Path: `Host Tables > Host Disk Storage > Disk Storage > Disk IO Errors > Disk IO Errors`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostStorage Disk IO Errors - WindowsStorageEvents | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Tables > Host Disk Storage > Disk Storage > Disk IO Timeouts > Disk IO Timeouts > Disk IO Timeouts - WindowsStorageEvents
Path: `Host Tables > Host Disk Storage > Disk Storage > Disk IO Timeouts > Disk IO Timeouts > Disk IO Timeouts - WindowsStorageEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HostStorage Disk IO Timeouts - WindowsStorageEvents | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Tables > Host Networking > Host Networking > NDIS DMA Allocations > NDIS DMA Allocations > NDIS DMA Allocations
Path: `Host Tables > Host Networking > Host Networking > NDIS DMA Allocations > NDIS DMA Allocations > NDIS DMA Allocations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NDIS DMA Allocation Summary | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Tables > Host Networking > Host Networking > Network Port Quota > Network Port Quota > Port Quota
Path: `Host Tables > Host Networking > Host Networking > Network Port Quota > Network Port Quota > Port Quota`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Network Port Quota | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Tables > IcMs for Host > IcMs for Host > IcMs for {{nodeId}}
Path: `Host Tables > IcMs for Host > IcMs for Host > IcMs for {{nodeId}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host IcMs | Table | icmcluster | IcmDataWarehouse | nodeId, startTime, endTime |

### Host Tables > LiveMigration > LiveMigration Events
Path: `Host Tables > LiveMigration > LiveMigration Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node LiveMigration Completions | Table | AzureCM | AzureCM | queryFrom, queryTo, nodeIdStr |

### Host Tables > OSHP > OSHP > OSHP FastSave > OSHP FastSave > Fast Restore Events
Path: `Host Tables > OSHP > OSHP > OSHP FastSave > OSHP FastSave > Fast Restore Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Fast Restore Events | Table | AzureCM | AzureCM | startTime, endTime, nodeId |

### Host Tables > OSHP > OSHP > OSHP FastSave > OSHP FastSave > Fast Save Events
Path: `Host Tables > OSHP > OSHP > OSHP FastSave > OSHP FastSave > Fast Save Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host FastSave Events | Table | AzureCM | AzureCM | startTime, endTime, nodeId |

### Host Tables > OSHP > OSHP > OSHP Timeline Events > OSHP Timeline Events
Path: `Host Tables > OSHP > OSHP > OSHP Timeline Events > OSHP Timeline Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host OSHP Events | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Tables > OSHP > OSHP > OSHP Update Logs > OSHP Update Logs > OSHP Update Logs (PF)
Path: `Host Tables > OSHP > OSHP > OSHP Update Logs > OSHP Update Logs > OSHP Update Logs (PF)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host OSHP Update Logs | Table | AzureCM | AzureCM | startTime, endTime, nodeId |

### Host Tables > OSHP > OSHP > OSHP Update Logs > OSHP Update Logs > OSHP Update Logs (plugin)
Path: `Host Tables > OSHP > OSHP > OSHP Update Logs > OSHP Update Logs > OSHP Update Logs (plugin)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host OSHP Plugin Update | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Tables > OSHP > OSHP > VM-PHU Compute Blackout
Path: `Host Tables > OSHP > OSHP > VM-PHU Compute Blackout`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM-PHU Node Compute Blackout Query | Table | baseplatform.westus | vmphu | startTime, endTime, nodeId |

### Host Tables > OsLoggerTable > OsLoggerTable
Path: `Host Tables > OsLoggerTable > OsLoggerTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host OsLoggerTable | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Tables > System > System > Disk Space > Disk Space > Folders using large Disk Space (usage in MB)
Path: `Host Tables > System > System > Disk Space > Disk Space > Folders using large Disk Space (usage in MB)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Disk Space Table | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### Host Tables > System > System > Events > Events > WindowsEventTable
Path: `Host Tables > System > System > Events > Events > WindowsEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host WindowsEventTable | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Tables > System > System > HighCPU Table > HighCPU Table > VPs running hot chart view (30 second averages per VP)
Path: `Host Tables > System > System > HighCPU Table > HighCPU Table > VPs running hot chart view (30 second averages per VP)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host HighCPUTable Chart View | TimeSeries | storageclient.eastus | Fa | startTime, endTime, nodeId |

### Host Tables > System > System > HighCPU Table > HighCPU Table > VPs running hot tabular view (30 second averages per VP)
Path: `Host Tables > System > System > HighCPU Table > HighCPU Table > VPs running hot tabular view (30 second averages per VP)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host HighCPUTable | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Tables > System > System > Poolmon > Poolmon > OsPoolmonTable (pushed by OsAnalyzer from poolmon output)
Path: `Host Tables > System > System > Poolmon > Poolmon > OsPoolmonTable (pushed by OsAnalyzer from poolmon output)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Poolmon Data for Azure Host Node | Table | storageclient.eastus | Fa | nodeId, startTime, endTime |

### Host Tables > System > System > Settings > Settings > OsConfigTable (pushed by OsAnalyzer)
Path: `Host Tables > System > System > Settings > Settings > OsConfigTable (pushed by OsAnalyzer)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host OsConfigTable | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### Host Tables > Updates > Updates > PF Service Updates
Path: `Host Tables > Updates > Updates > PF Service Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host PF Updates Table | Table | AzureCM | AzureCM | nodeId, startTime, endTime |

### Host Tables > Updates > Updates > Root HE Component Updates
Path: `Host Tables > Updates > Updates > Root HE Component Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host RootHE Updates | Table | AzureCM | AzureCM | startTime, endTime, nodeId |

### Hyper-V Tables > Analytic > Analytic > HyperVAnalyticEvents
Path: `Hyper-V Tables > Analytic > Analytic > HyperVAnalyticEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host HyperV Analytic | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### Hyper-V Tables > HyperVEvents > HyperVEventsV2
Path: `Hyper-V Tables > HyperVEvents > HyperVEventsV2`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | HyperVEventsV2 Host Query | Table | azcore.centralus | SharedWorkspace | _startTime, _endTime, _nodeId |

### Hyper-V Tables > IO Latencies > Hyper-V IO Latencies seen (10+ second IOs)
Path: `Hyper-V Tables > IO Latencies > Hyper-V IO Latencies seen (10+ second IOs)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM HyperV Latency Query | Table | azcore.centralus | Fa | startTime, endTime, containerId, nodeId |

### Hyper-V Tables > Storage Stack > Storage Stack > HyperVStorageStackTable > HyperVStorageStackTable > HyperVStorageStackTable
Path: `Hyper-V Tables > Storage Stack > Storage Stack > HyperVStorageStackTable > HyperVStorageStackTable > HyperVStorageStackTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host HyperV Storage | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Hyper-V Tables > Storage Stack > Storage Stack > Incomplete IO Operations > Incomplete IO Operations
Path: `Hyper-V Tables > Storage Stack > Storage Stack > Incomplete IO Operations > Incomplete IO Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host HyperVStorageStack Incomplete IO Operations | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Hyper-V Tables > Storage Stack > Storage Stack > IO Operations Summary > IO Operations Summary
Path: `Hyper-V Tables > Storage Stack > Storage Stack > IO Operations Summary > IO Operations Summary`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host HyperVStorageStack IO Operations Summary | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Hyper-V Tables > Virtualization > UnderhillEventTable
Path: `Hyper-V Tables > Virtualization > UnderhillEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node UnderhillEventTable | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Hyper-V Tables > Virtualization > Virtualization Configuration
Path: `Hyper-V Tables > Virtualization > Virtualization Configuration`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Virtualization Configuration | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Hyper-V Tables > Worker > Worker > HyperVWorkerTable
Path: `Hyper-V Tables > Worker > Worker > HyperVWorkerTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Hyper-V Worker | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### Insights > Host Insights Summary
Path: `Insights > Host Insights Summary`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | node_insights_summary | Single | storageclient.eastus | sc | startTime, endTime, nodeId |

### Insights > Other > Azure Core RCA
Path: `Insights > Other > Azure Core RCA`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Azure Core RCA | Table | moseisley | Air | nodeId, startTime, endTime |

### NetDatapathTrace
Path: `NetDatapathTrace`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NetDatapathTrace Query | Table | azurehn | Azurehn | startTime, endTime, nodeId |

### RdAgent Tables > VMAL Container Operations > VMAL Container Operations > VmServiceContainerOperations
Path: `RdAgent Tables > VMAL Container Operations > VMAL Container Operations > VmServiceContainerOperations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMAL Container Operations | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### RdAgent Tables > VMAL Disk Lease Operations > VMAL Disk Lease Operations
Path: `RdAgent Tables > VMAL Disk Lease Operations > VMAL Disk Lease Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VmServiceLeaseManagementOperation | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### RdAgent Tables > VMAL Disk Operations > VMAL Disk Operations > VmServiceVirtualDiskOperations
Path: `RdAgent Tables > VMAL Disk Operations > VMAL Disk Operations > VmServiceVirtualDiskOperations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMAL Disk Service Table | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### RdAgent Tables > VMAL Service Events > VMAL Service Events > VmServiceEventsEtwTable
Path: `RdAgent Tables > VMAL Service Events > VMAL Service Events > VmServiceEventsEtwTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VmServiceEventsEtwTable | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### RdAgent Tables > VMAL Service Init > VMAL Service Init > VmServiceInitialization
Path: `RdAgent Tables > VMAL Service Init > VMAL Service Init > VmServiceInitialization`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMAL Service Init | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### ServiceHealth > Service Health Table
Path: `ServiceHealth > Service Health Table`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node SoC Service Health | Table | azcore.centralus | OvlProd | startTime, endTime, nodeId |

### SOC Details > NDPA
Path: `SOC Details > NDPA`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NetDatapathPerfCounters Query | Table | azurehn | Azurehn | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASAP and ASFO features
Path: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASAP and ASFO features`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASFO Features Values | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASAP Components Versions from Events
Path: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASAP Components Versions from Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASFO Components Versions | Table | storageclient.eastus | Fa | _startTime, _endTime, _nodeId |

### StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASFO Node Details
Path: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASFO Node Details`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASFO Features | FeatureList | storageclient.eastus | Fa | startTime, endTime, nodeId |
| 2 | Azure Host Node Info ASAP | Single | storageclient.eastus | Fa | _nodeId, _startTime, _endTime |

### StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASFO PO <-> FO transitions
Path: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASFO PO <-> FO transitions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ASFO_PO_FO_Transitions | Table | storageclient.eastus | Fa | _startTime, _endTime, _nodeId |

### StorageClient Tables > ASAP > ASAP > ASFO Host Details > Mapping for ASAP VF ID to Container ID
Path: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > Mapping for ASAP VF ID to Container ID`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AsapMapVfIdToContainerIdOvl2Node | Table | storageclient.eastus | Fa | _startTime, _endTime, _nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Details
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Details`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASAP Full Offload PF and UMED details | Table | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Details > ASAP events count by provider and event Id (every 5 min)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Details > ASAP events count by provider and event Id (every 5 min)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASFO Node Events Stats Table | Table | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > ASFO Exceptions Total Counts
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > ASFO Exceptions Total Counts`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FullOffloadExceptionsQuery | CategoryChart | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Avg & Max New Min Latency floor delays PV2: (PS: Unit is in terms of FPGA cycles, MaxDeltaCycles = NewMinLatencyFloor - CurrentMinLatencyFloor)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Avg & Max New Min Latency floor delays PV2: (PS: Unit is in terms of FPGA cycles, MaxDeltaCycles = NewMinLatencyFloor - CurrentMinLatencyFloor)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | MinLatencyFloorDelayPv2Query | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > IOPS: FO vs PO (All Disks, includes boot disk)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > IOPS: FO vs PO (All Disks, includes boot disk)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_asapPf_AllDisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > IOPS: FO vs PO (FO enabled Disks)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > IOPS: FO vs PO (FO enabled Disks)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_asapPf_UseSwpe0 | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (All Disks, includes boot disk)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (All Disks, includes boot disk)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_asapPf_AllDisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (FO enabled Disks)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (FO enabled Disks)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_asapPf_UseSwpe0 | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > MBPS: FO vs PO (All Disks, includes boot disk)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > MBPS: FO vs PO (All Disks, includes boot disk)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_asapPf_AllDisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > MBPS: FO vs PO (FO enabled Disks)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > MBPS: FO vs PO (FO enabled Disks)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_asapPf_UseSwpe0 | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Spread of 'AsapQpHealthCheckFailed' Event (Only in PF Version 6.70.2.32+)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Spread of 'AsapQpHealthCheckFailed' Event (Only in PF Version 6.70.2.32+)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AsapQpHealthCheckFailed_Spread | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Spread of ASFO FO Exceptions
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Spread of ASFO FO Exceptions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Full Offload Exceptions | TimeSeries | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO Average & Max Latencies, (Milliseconds), All disks
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO Average & Max Latencies, (Milliseconds), All disks`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_OsCounters_AllDisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO Average & Max Latencies, (Milliseconds), FO disks i.e UseSwpe = 0
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO Average & Max Latencies, (Milliseconds), FO disks i.e UseSwpe = 0`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_OsCounters_UseSwpe0 | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: IOPS All disks (includes bootdisk)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: IOPS All disks (includes bootdisk)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_OsCounters_AllDisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: IOPS, FO disks i.e UseSwpe = 0
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: IOPS, FO disks i.e UseSwpe = 0`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_OsCounters_UseSwpe0 | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: MBPS All disks (includes bootdisk)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: MBPS All disks (includes bootdisk)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_OsCounters_AllDisks | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: MBPS, FO disks i.e UseSwpe = 0
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: MBPS, FO disks i.e UseSwpe = 0`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | asapNodeFOStats_OsCounters_UseSwpe0 | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > ASFO Exceptions
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > ASFO Exceptions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Full Offload Exceptions | TimeSeries | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > FO% KPI : [ %FO = Ratio of FullOffload IO to Total IO]
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > FO% KPI : [ %FO = Ratio of FullOffload IO to Total IO]`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FOPercent_NodeQuery | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (IOPS KPIs, All data disks)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (IOPS KPIs, All data disks)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FullOffloadStats_AllDisksQuery | TimeSeries | https://storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (IOPS KPIs, FO data disks i.e UseSwpe = 0)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (IOPS KPIs, FO data disks i.e UseSwpe = 0)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Fulloffload Statistics | TimeSeries | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (throughput KPIs, All data disks)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (throughput KPIs, All data disks)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FullOffloadStats_AllDisksQuery | TimeSeries | https://storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (throughput KPIs, FO data disks)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (throughput KPIs, FO data disks)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Fulloffload Statistics | TimeSeries | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload Exceptions Counts
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload Exceptions Counts`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FullOffloadExceptionsQuery | CategoryChart | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > Total FO VMs running and their Average FO% (Source = OSCounters, asapPF does not currently have ConrtainerID in its payload)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Total FO VMs running and their Average FO% (Source = OSCounters, asapPF does not currently have ConrtainerID in its payload)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMCountsPerFOPercent | CategoryChart | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Full Offload Stats > VM outliers list: where %FO was < 80% (OSDiagVer >= 0.58)
Path: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > VM outliers list: where %FO was < 80% (OSDiagVer >= 0.58)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OutlierContainersListQuery | Table | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId, fobucket |
| 2 | FoBucketFilterQuery | Filter | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Heartbeats for PF and KMS
Path: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Heartbeats for PF and KMS`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Asap Heartbeats | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view
Path: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`  ·  Queries: 11

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node ASAP VMA Query | Timeline | Vmakpi | vmadb | startTime, endTime, nodeId |
| 2 | Azure Host Node Events | Timeline | azcore.centralus | Fa | queryFrom, queryTo, nodeId |
| 3 | Azure Host Node State (Fabric) | Timeline | AzureCM | AzureCM | nodeId, startTime, endTime |
| 4 | Azure Host XStore E17 AutoTriage | Timeline | azcore.centralus | XHealth | startTime, endTime, nodeId |
| 5 | Azure Host Node Updates | Timeline | storageclient.eastus | Fc | startTime, endTime, nodeId |
| 6 | Azure Host PF Service Updates | Timeline | AzureCM | AzureCM | startTime, endTime, nodeId |
| 7 | Azure Host OSHostPlugin Events | Timeline | azcore.centralus | Fa | startTime, endTime, nodeId |
| 8 | ASAP UMED CE Events Timeline | Timeline | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |
| 9 | ASAP KMS CE Events Timeline | Timeline | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |
| 10 | ASAP PF CE Events Timeline | Timeline | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |
| 11 | Azure Host Node TIP sessions | Timeline | AzureCM | AzureCM | queryFrom, queryTo, _nodeId |

### StorageClient Tables > ASAP > ASAP > Heartbeats > Controller Resets and IO Loss events Query
Path: `StorageClient Tables > ASAP > ASAP > Heartbeats > Controller Resets and IO Loss events Query`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ControllerResetsAndIoLossQuery | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Heartbeats > Critical Errors Query 
Path: `StorageClient Tables > ASAP > ASAP > Heartbeats > Critical Errors Query `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CriticalErrorsQuery  | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Heartbeats > Vf Stuck and Extreme Prejudice Events Count
Path: `StorageClient Tables > ASAP > ASAP > Heartbeats > Vf Stuck and Extreme Prejudice Events Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VfStuckExtrPrejudiceQuery | TimeSeries | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Insights > Insights > ASAP Insights for the OVL 1.1 Node (for the time selected)
Path: `StorageClient Tables > ASAP > ASAP > Insights > Insights > ASAP Insights for the OVL 1.1 Node (for the time selected)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node ASAP Insights For Node | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Insights > Insights > ASAP Insights OVL 2 Node (for selected time range)
Path: `StorageClient Tables > ASAP > ASAP > Insights > Insights > ASAP Insights OVL 2 Node (for selected time range)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AsapInsightsOVL2Query | Table | https://storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > MANA Version > MANA Versions
Path: `StorageClient Tables > ASAP > ASAP > MANA Version > MANA Versions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ManaVersion | Table | Azcore.centralus | Fa | startTime, endTime, nodeid |

### StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > All Tables > All Tables > Non-Informational Only
Path: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > All Tables > All Tables > Non-Informational Only`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASAP All Tables Union | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > DataLogger
Path: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > DataLogger`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node ASAP FPGA DataLogger | Table | xaccel | xaccel | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > Debug Registers Dump (Overlake 1.1) > HW Critical Errors from ASAP FPGA debug registers dump
Path: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > Debug Registers Dump (Overlake 1.1) > HW Critical Errors from ASAP FPGA debug registers dump`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ASAP ASAP PF HWCE and Debug Registers Dump | Table | xaccel.centralus | XAccel | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > HW CE from DR (Overlake 1.1)
Path: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > HW CE from DR (Overlake 1.1)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Edit Query Azure Host ASAP Debug Registers HW CE | Table | xaccel | XAccel | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > KMS ETW > KMS ETW > AsapKmsEtwEventTable
Path: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > KMS ETW > KMS ETW > AsapKmsEtwEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASAP KMS Table | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > Node Story > Node story based on ASAP, Hyper-V and NDPA events
Path: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > Node Story > Node story based on ASAP, Hyper-V and NDPA events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node ASAP Node Story | Table | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > NVME ETW > NVME ETW > AsapNvmeEtwEventTable
Path: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > NVME ETW > NVME ETW > AsapNvmeEtwEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASAP ETW Table | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > PF ETW > PF ETW > AsapPfEtwEventTable
Path: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > PF ETW > PF ETW > AsapPfEtwEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host PF ETW Table | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > Shell HW FPGA > Shell HW FPGA Telemetry
Path: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > Shell HW FPGA > Shell HW FPGA Telemetry`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASAP FPGA HW Shell Telemetry | Table | azcore.centralus | Fa | queryFrom, queryTo, queryNodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Critical and Error Events > ASAP Components Versions from Events
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Critical and Error Events > ASAP Components Versions from Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASFO Critical and Error Events | Table | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > S0C0 - S3Cx (Overlake 2) > Debug Registers for clients S0C0 to S3Cx
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > S0C0 - S3Cx (Overlake 2) > Debug Registers for clients S0C0 to S3Cx`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ASAP Hardware Debug Registers Output S0C0 to S3CX | Table | xaccel.centralus | XAccel | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > S4C0 - S7Cx (Overlake 2) > Debug Registers for clients S4C0 to S7Cx
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > S4C0 - S7Cx (Overlake 2) > Debug Registers for clients S4C0 to S7Cx`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ASAP Hardware Debug Registers Output S4C0 to S7CX | Table | xaccel.centralus | XAccel | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > S8C0 - SBCx (Overlake 2) > Debug Registers for clients S8C0 to SBCx
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > S8C0 - SBCx (Overlake 2) > Debug Registers for clients S8C0 to SBCx`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ASAP Hardware Debug Registers Output S8C0 to SBCX | Table | xaccel.centralus | XAccel | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > SCC0 - SFCx (Overlake 2) > Debug Registers for clients SCC0 to SFCx
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > SCC0 - SFCx (Overlake 2) > Debug Registers for clients SCC0 to SFCx`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ASAP Hardware Debug Registers Output SCC0 to SFCX | Table | xaccel.centralus | XAccel | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Full Offload Investigations
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Full Offload Investigations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASAP Full Offload PF Investigations | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > HW CE from DR (Overlake 2)
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > HW CE from DR (Overlake 2)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASAP Debug Registers HW CE Overlake 2 | Table | xaccel.centralus | XAccel | queryFrom, queryTo, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Insights > ASAP Insights for Overlake 2 node
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Insights > ASAP Insights for Overlake 2 node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node ASAP Insights for Overlake 2 Node | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > KMS Trace Logging
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > KMS Trace Logging`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASAP KMS Trace Logging | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > NVME (UMED) Trace Logging
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > NVME (UMED) Trace Logging`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host ASAP NVME Trace Logging | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > PF Trace Logging
Path: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > PF Trace Logging`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host PF Trace Logging | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > ASAP > ASAP > Servicing
Path: `StorageClient Tables > ASAP > ASAP > Servicing`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Show_Cobe_Condition_OSHP  | Single | https://storageclient.eastus | Fa | _NodeId, _EndTime, _StartTime |
| 2 | MaxVM_ComputeBlackout1_ADPA | Single | https://storageclient.eastus | Fa | _NodeId, _EndTime, _StartTime |
| 3 | MaxVM_ComputeBlackout2_ADPA | Single | https://storageclient.eastus | Fa | _NodeId, _EndTime, _StartTime |

### StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Service_V2
Path: `StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Service_V2`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Display_ContainerIds_Query | Table | https://storageclient.eastus | Fa | _NodeId, _EndTime, _StartTime |
| 2 | Check_ShowCobe_Condition_ADPA_MultiVm | MultiRow | https://storageclient.eastus | Fa | _NodeId, _StartTime, _EndTime, _ContainerId |
| 3 | AdpaServiceQueryPerContainer | CoBeTimeline | https://storageclient.eastus | Fa | _NodeId, _EndTime, _ContainerId, _StartTime |

### StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Summary > OVL 1.1 Node Events (ADPA servicing) (Scroll down for OVL2+)
Path: `StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Summary > OVL 1.1 Node Events (ADPA servicing) (Scroll down for OVL2+)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ADPA_BlackoutBrownout_Test | Timeline | https://storageclient.eastus | Fa | _NodeId, _EndTime, _StartTime |

### StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Summary > OVL 2+ Node Events  (ADPA servicing)
Path: `StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Summary > OVL 2+ Node Events  (ADPA servicing)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AdpaServicingEventsAllVMsOVL2 | CoBeTimeline | https://storageclient.eastus | Fa | _startTime, _endTime, _NodeId |

### StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Service_V2
Path: `StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Service_V2`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DisplayContainersQuery | Table | https://storageclient.eastus | Fa | _NodeId, _EndTime, _StartTime |
| 2 | OshpServiceQueryPerContainer | CoBeTimeline | https://storageclient.eastus | Fa | _NodeId, _EndTime, _StartTime, _ContainerId |

### StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Summary > OVL 1.1 Node Events (OSHP servicing) (Scroll down for OVL2+)
Path: `StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Summary > OVL 1.1 Node Events (OSHP servicing) (Scroll down for OVL2+)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OSHP_MaxVM_ScenarioQuery | Timeline | https://storageclient.eastus | Fa | _NodeId, _EndTime, _StartTime |

### StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Summary > OVL 2+ Node Events (OSHP servicing)
Path: `StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Summary > OVL 2+ Node Events (OSHP servicing)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OshpServicingEventsAllVMsOVL2 | CoBeTimeline | https://storageclient.eastus | Fa | _startTime, _endTime, _NodeId |

### StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Summary > OVL2+ Node Events (OSHP Servicing) View 2:
Path: `StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Summary > OVL2+ Node Events (OSHP Servicing) View 2:`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OshpServicingEventsAllVMsOVL2V2 | Timeline | https://storageclient.eastus | Fa | _startTime, _endTime, _NodeId |

### StorageClient Tables > Barbera > Barbera > Barbera Events > Barbera Events > OsBarberaEventTable
Path: `StorageClient Tables > Barbera > Barbera > Barbera Events > Barbera Events > OsBarberaEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Barbera Events Query | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Barbera > Barbera > Barbera Ring Creation Failures > Barbera Ring Creation Failures (StorageClient)
Path: `StorageClient Tables > Barbera > Barbera > Barbera Ring Creation Failures > Barbera Ring Creation Failures (StorageClient)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Barbera Ring Creation Failures Query | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Barbera > Barbera > Barbera Ring Usage Stats > Ring Statistics
Path: `StorageClient Tables > Barbera > Barbera > Barbera Ring Usage Stats > Ring Statistics`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Barbera Active Owb Index Filter | Filter | azcore.centralus | Fa | startTime, endTime, nodeId |
| 2 | Azure Host Barbera Usage Ring Stats Query | TimeSeries | azcore.centralus | Fa | startTime, endTime, nodeId, owbIndexArray |

### StorageClient Tables > Barbera > Barbera > BarberaConfigData > BarberaConfigData > Barbera Config Details
Path: `StorageClient Tables > Barbera > Barbera > BarberaConfigData > BarberaConfigData > Barbera Config Details`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | BarberaConfigDetails | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Barbera > Barbera > BarberaConfigData > BarberaConfigData > Latest Buddy Summary
Path: `StorageClient Tables > Barbera > Barbera > BarberaConfigData > BarberaConfigData > Latest Buddy Summary`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | BarberaConfigSummary | Single | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > Barbera > Barbera > BarberaSvcEvent > BarberaSvcEvent > OsBarberaEventTable
Path: `StorageClient Tables > Barbera > Barbera > BarberaSvcEvent > BarberaSvcEvent > OsBarberaEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host BarberaSvcEvent Query | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Barbera > Barbera > BarberaSvcRingEvent > BarberaSvcRingEvent > BarberaSvcRingEvent
Path: `StorageClient Tables > Barbera > Barbera > BarberaSvcRingEvent > BarberaSvcRingEvent > BarberaSvcRingEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host BarberaSvcRingEvent Query | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Barbera > Barbera > BarberaSvcTopologyEvent > BarberaSvcTopologyEvent > BarberaSvcTopologyEvent
Path: `StorageClient Tables > Barbera > Barbera > BarberaSvcTopologyEvent > BarberaSvcTopologyEvent > BarberaSvcTopologyEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host BarberaSvcTopologyEvent Query | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > BlobCache > BlobCache > Blobcache Config
Path: `StorageClient Tables > BlobCache > BlobCache > Blobcache Config`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host BlobCache Config Table | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > BlobCache > BlobCache > Blobcache Events > Blobcache Events > OsBlobCacheEventTable
Path: `StorageClient Tables > BlobCache > BlobCache > Blobcache Events > Blobcache Events > OsBlobCacheEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host BlobCache Event Table | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > BlobCache > BlobCache > BlobCache Internal Counters > Blobcache Global Internal Counters (StorageClient)
Path: `StorageClient Tables > BlobCache > BlobCache > BlobCache Internal Counters > Blobcache Global Internal Counters (StorageClient)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Blobcache InternalCounters Query | TimeSeries | storageclient.eastus | Fa | startTime, endTime, nodeId, Cloud |

### StorageClient Tables > BlobCache > BlobCache > CacheStore Stats > CacheStore Config
Path: `StorageClient Tables > BlobCache > BlobCache > CacheStore Stats > CacheStore Config`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host CacheStore Configuration | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > BlobCache > BlobCache > CacheStore Stats > CacheStore Stats
Path: `StorageClient Tables > BlobCache > BlobCache > CacheStore Stats > CacheStore Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Blobcache CacheStore Stats TL | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > BlobCache > BlobCache > Throttle Config > Blobcache Throttle mismatch Surfaces
Path: `StorageClient Tables > BlobCache > BlobCache > Throttle Config > Blobcache Throttle mismatch Surfaces`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Blobcache Throttle missing  | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > DAL > DAL Table > Storage Tracing Event Table
Path: `StorageClient Tables > DAL > DAL Table > Storage Tracing Event Table`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node DAL Logs2 | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > DAL > DirectAccessEvent
Path: `StorageClient Tables > DAL > DirectAccessEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node DirectAccessEvent | Table | azcore.centralus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > DAL > IFX Table > IFX Table with DAL/VMAL Logs
Path: `StorageClient Tables > DAL > IFX Table > IFX Table with DAL/VMAL Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host DAL Logs | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > DAL > OsLoggerTable (filtered for DAL) > OsLoggerTable (filtered for DAL)
Path: `StorageClient Tables > DAL > OsLoggerTable (filtered for DAL) > OsLoggerTable (filtered for DAL)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node DAL OsLoggerTable | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Driver Logs > Driver Logs > StorageClient Driver Logs (Barbera, BlobCache, HandleProxy)
Path: `StorageClient Tables > Driver Logs > Driver Logs > StorageClient Driver Logs (Barbera, BlobCache, HandleProxy)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host StorageClient Driver Logs | Table | storageclient.eastus | Fa | nodeId, startTime, endTime |

### StorageClient Tables > EDrive > EDrive Manager Event > EDrvMgrEventTable
Path: `StorageClient Tables > EDrive > EDrive Manager Event > EDrvMgrEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node EDrive Manager EvtTable | Table | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > EDrive > EDrive Manager Operations > EdrvMgrOperationsTable
Path: `StorageClient Tables > EDrive > EDrive Manager Operations > EdrvMgrOperationsTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node EDrive Operations | Table | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > EDrive > EDrive Manager Table > EDrvMgrTable
Path: `StorageClient Tables > EDrive > EDrive Manager Table > EDrvMgrTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node EDrive Manager Table | Table | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > EDrive > Encryption Event > XdiskEncEvent
Path: `StorageClient Tables > EDrive > Encryption Event > XdiskEncEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node EDrive Encryption Events | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Event 17 Analysis > Event 17 Analysis > OsAnalyzerTable > OsAnalyzerTable > OsAnalyzer Host Node Analysis
Path: `StorageClient Tables > Event 17 Analysis > Event 17 Analysis > OsAnalyzerTable > OsAnalyzerTable > OsAnalyzer Host Node Analysis`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host OsAnalyzerTable | Table | storageclient.eastus | SharedWorkspace | nodeId, startTime, endTime, cluster |

### StorageClient Tables > Event 17 Analysis > Event 17 Analysis > XStore Analysis > XStore Analysis > XStore AutoTriage Analysis
Path: `StorageClient Tables > Event 17 Analysis > Event 17 Analysis > XStore Analysis > XStore Analysis > XStore AutoTriage Analysis`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host XStore AutoTriage | Table | azcore.centralus | XHealth | startTime, endTime, nodeId |

### StorageClient Tables > MFND > Driver Events > PnP Events > WindowsEventTable
Path: `StorageClient Tables > MFND > Driver Events > PnP Events > WindowsEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PnP Events | Table | azcore.centralus | Fa | _startTime, _endTime, _nodeId |

### StorageClient Tables > MFND > Driver Events > StorPort Events > WindowsStorageEvents
Path: `StorageClient Tables > MFND > Driver Events > StorPort Events > WindowsStorageEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | StorPort Events | Table | azcore.centralus | Fa | _startTime, _endTime, _nodeId |

### StorageClient Tables > MFND > MFND Events > Direct Access MFND Event > DirectAccessEvent
Path: `StorageClient Tables > MFND > MFND Events > Direct Access MFND Event > DirectAccessEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | DirectAccessEvent MFND Query | Table | azcore.centralus | Fa | _startTime, _endTime, _nodeId |

### StorageClient Tables > MFND > MFND Events > Storage Tracing MFND Event > StorageTracingEventTable
Path: `StorageClient Tables > MFND > MFND Events > Storage Tracing MFND Event > StorageTracingEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Storage Tracing MFND Event Query | Table | azcore.centralus | Fa | _startTime, _endTime, _nodeId |

### StorageClient Tables > StorSnap > StorSnap > StorSnap Events
Path: `StorageClient Tables > StorSnap > StorSnap > StorSnap Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | StorSnap Event Query | Table | azcore.centralus | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > Updates > DPHP Update Logs > Brownout > StorageClientVmBrownout for All VMs
Path: `StorageClient Tables > Updates > DPHP Update Logs > Brownout > StorageClientVmBrownout for All VMs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Storage Client VM Brownout for all VMs | Table | storageclient.eastus | Sc | _startTime, _endTime, _nodeId |

### StorageClient Tables > Updates > DPHP Update Logs > DPP Update Graph > DPP Executions
Path: `StorageClient Tables > Updates > DPHP Update Logs > DPP Update Graph > DPP Executions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ListOfExecutions | Table | storageclient.eastus | SharedWorkspace | queryFrom, queryTo, Node_Id |

### StorageClient Tables > Updates > DPHP Update Logs > DPP Update Graph > DPP Executions > DPP Update Graph
Path: `StorageClient Tables > Updates > DPHP Update Logs > DPP Update Graph > DPP Executions > DPP Update Graph`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Update_Node_Logs | CoBeTimeline | rdosdata | rdosdatapath | queryFrom, queryTo, Execution_Id, DphpStartTime, DphpEndTime, Node_Id |
| 2 | XIO_Condition_Query | Single | storageclient.eastus | Fa | queryFrom, queryTo, Execution_ID |

### StorageClient Tables > Updates > DPHP Update Logs > DPP Verbose Logs > StorageClient Drivers Update Logs
Path: `StorageClient Tables > Updates > DPHP Update Logs > DPP Verbose Logs > StorageClient Drivers Update Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host DPHP Update Events | Table | storageclient.eastus | SharedWorkspace | nodeId, startTime, endTime |

### StorageClient Tables > Updates > DPHP Update Logs > PF Services Update Logs > OsAnalyzerLogTable
Path: `StorageClient Tables > Updates > DPHP Update Logs > PF Services Update Logs > OsAnalyzerLogTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node OsAnalyzerLogTable | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > User Mode Processes > Host Storage Team's Usermode Processes
Path: `StorageClient Tables > User Mode Processes > Host Storage Team's Usermode Processes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Storage Client User Mode Processes Usage Stats | TimeSeries | storageclient.eastus | AutopilotDeployment | queryFrom, queryTo, nodeId |

### StorageClient Tables > Vdc (UltraDisk Client) > Vdc > Disk Pacing Events
Path: `StorageClient Tables > Vdc (UltraDisk Client) > Vdc > Disk Pacing Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VDC_Diskpacing_Events | Table | https://azcore.centralus/ | Fa | queryFrom, queryTo, nodeId |

### StorageClient Tables > Vdc (UltraDisk Client) > Vdc > StorageAgent (updates) > StorageAgent > StorageAgent ETW Table
Path: `StorageClient Tables > Vdc (UltraDisk Client) > Vdc > StorageAgent (updates) > StorageAgent > StorageAgent ETW Table`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host StorageAgent ETW Table | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Vdc (UltraDisk Client) > Vdc > StorageAgent Update Graph > Storage Agent Executions
Path: `StorageClient Tables > Vdc (UltraDisk Client) > Vdc > StorageAgent Update Graph > Storage Agent Executions`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SAListOfExecutions | Table | storageclient.eastus | Fa | queryFrom, queryTo, node_Id |
| 2 | SA_Node_Update_Logs | CoBeTimeline | storageclient.eastus | Fa | queryFrom, queryTo, node_Id, execution_Id |

### StorageClient Tables > Vdc (UltraDisk Client) > Vdc > VdcEtwEvents > VdcEtwEvents > Vdc (UltraDisk Client) ETW Events
Path: `StorageClient Tables > Vdc (UltraDisk Client) > Vdc > VdcEtwEvents > VdcEtwEvents > Vdc (UltraDisk Client) ETW Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Vdc Etw Events | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### StorageClient Tables > Vhddisk > Vhddisk > Debug > Max/Min Response time at Vhddisk Layer (including retries)
Path: `StorageClient Tables > Vhddisk > Vhddisk > Debug > Max/Min Response time at Vhddisk Layer (including retries)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Vhddisk MaxTime Summary | Table | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, vmId |

### StorageClient Tables > Vhddisk > Vhddisk > ETW > ETW > Vhddisk ETW Events
Path: `StorageClient Tables > Vhddisk > Vhddisk > ETW > ETW > Vhddisk ETW Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Vhddisk ETW Events | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Vhddisk > Vhddisk > Events > Events > Vhddisk Events
Path: `StorageClient Tables > Vhddisk > Vhddisk > Events > Events > Vhddisk Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Vhddisk Events | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Vhddisk > Vhddisk > IO Transport Stats > IO percentage by Transport
Path: `StorageClient Tables > Vhddisk > Vhddisk > IO Transport Stats > IO percentage by Transport`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Transport Percentage Query | TimeSeries | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Vhddisk > Vhddisk > OsVhddiskEventTable
Path: `StorageClient Tables > Vhddisk > Vhddisk > OsVhddiskEventTable`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | OsVhddiskEventTable | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > Vhddisk > Vhddisk > Vhdum > Vhdum > Vhdum Events (user-mode calls)
Path: `StorageClient Tables > Vhddisk > Vhddisk > Vhdum > Vhdum > Vhdum Events (user-mode calls)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node vhdum logs | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > VM Disks > Disks attached to VMs running in this node
Path: `StorageClient Tables > VM Disks > Disks attached to VMs running in this node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node VM Disks | Table | storageclient.eastus | fa | startTime, endTime, nodeId, cluster |

### StorageClient Tables > XDiskSvc > XDiskSvc > XDiskEncEvent > XDiskEncEvent > XdiskEncEvent
Path: `StorageClient Tables > XDiskSvc > XDiskSvc > XDiskEncEvent > XDiskEncEvent > XdiskEncEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host XdiskEncEvent | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### StorageClient Tables > XDiskSvc > XDiskSvc > XDiskSvcEvent > XDiskSvcEvent > XdiskSvcEvent
Path: `StorageClient Tables > XDiskSvc > XDiskSvc > XDiskSvcEvent > XDiskSvcEvent > XdiskSvcEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host XDiskSvcEvent Query | Table | storageclient.eastus | Fa | startTime, endTime, nodeId |

### SystemD > SystemD Journal Logs
Path: `SystemD > SystemD Journal Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node SoC SystemD Logs | Table | azcore.centralus | OvlProd | startTime, endTime, nodeId |

### TDPR > Deployment EG > Deployment EG > IaasVmOperations
Path: `TDPR > Deployment EG > Deployment EG > IaasVmOperations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host EG Telemetry  | Table | egpublic.westus | eg | startTime, endTime, nodeId |

### TDPR > Host Storage IFX > IFX Tables
Path: `TDPR > Host Storage IFX > IFX Tables`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure VM IFX Table | Table | azcore.centralus | Fa | queryFrom, queryTo, containerId, nodeId |

### Timeline of Startup Table
Path: `Timeline of Startup Table`  ·  Queries: 5

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Health | Timeline | azurecm | AzureCM | queryFrom, queryTo, nodeid |
| 2 | NodeWorkflow Timeline | Timeline | azurecm | AzureCM | queryFrom, queryTo, nodeid |
| 3 | Agent Start Operations Details | Timeline | azcore.centralus | Fa | queryFrom, queryTo, nodeid |
| 4 | Container Workflow Details | Timeline | azurecm | AzureCM | queryFrom, queryTo, nodeid |
| 5 | IFxOperationV2 Table | Timeline | azcore.centralus | Fa | queryFrom, queryTo, nodeid |

### Updates > SoC Updates
Path: `Updates > SoC Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node SoC Updates | Table | azcore.centralus | OvlProd | startTime, endTime, nodeId |

### VM Details > VM IO Limits > VM's IO Throttle Limits (Cached) configured
Path: `VM Details > VM IO Limits > VM's IO Throttle Limits (Cached) configured`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node VM Cached Throttle Settings | Table | storageclient.eastus | Fa | startTime, endTime, nodeIdStr, cluster |

### VM Details > VM IO Limits > VM's IO Throttle Limits (Uncached) configured
Path: `VM Details > VM IO Limits > VM's IO Throttle Limits (Uncached) configured`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node VM Throttle Settings | Table | storageclient.eastus | Fa | startTime, endTime, nodeIdStr, cluster |

### VM Details > VMs > VM Running in the Host Node
Path: `VM Details > VMs > VM Running in the Host Node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Running VMs Query | Table | Storageclient.eastus | AzureCP | _nodeId, _startTime, _endTime |

### VMA (AIR-R) > VMA events for {{nodeId}}
Path: `VMA (AIR-R) > VMA events for {{nodeId}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMA | Table | vmainsight | vmadb | nodeId, startTime, endTime |

### XStore Performance Tables > Agent Start Operation Performance (P50, 90, 99)
Path: `XStore Performance Tables > Agent Start Operation Performance (P50, 90, 99)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Agent Start Operations Performance (P50, 90, 99) | Table | azcore.centralus | Fa | queryFrom, queryTo |

### XStore Performance Tables > Container Workflow Details (P50, 90, 99)
Path: `XStore Performance Tables > Container Workflow Details (P50, 90, 99)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Workflow Details (P50, 90, 99) | Table | https://azurecm/ | AzureCM | queryFrom, queryTo |

### XStore Performance Tables > IfxOperationV2 Performance (P50, 90, 99)
Path: `XStore Performance Tables > IfxOperationV2 Performance (P50, 90, 99)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | IfxOperationV2 Performance (P50, 90, 99) | Table | azcore.centralus | Fa | queryFrom, queryTo |

### XStore Performance Tables > Node Workflow Details (P50, 90, 99)
Path: `XStore Performance Tables > Node Workflow Details (P50, 90, 99)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NodeWorkflow P50, P90, P99 | Table | https://azurecm/ | AzureCM | queryFrom, queryTo |
