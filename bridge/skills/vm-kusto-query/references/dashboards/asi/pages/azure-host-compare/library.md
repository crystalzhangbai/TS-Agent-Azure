# Azure Host — Azure Host Compare: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T09:57:57.334Z.
> Total: 24 unique KQL queries across 39 panels (44 widget refs).

## Page inputs (URL params)


## Panels

### File Versions > FileVersions
Path: `File Versions > FileVersions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host FileVersion Compare | Table | storageclient.eastus | SharedWorkspace | queryFrom, queryTo, nodeId1, Time2From, Time2To, nodeId2 |

### File Versions > PF Services
Path: `File Versions > PF Services`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host PF Services Compare | Table | storageclient.eastus | AutopilotDeployment | queryFrom, queryTo, nodeId1, Time2From, Time2To, nodeId2 |

### Host Charts > Available Memory {{nodeId1}}
Path: `Host Charts > Available Memory {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Available Memory | TimeSeries | storageclient.eastus | Fa | nodeId, startTime, endTime |

### Host Charts > Available Memory {{nodeId2}}
Path: `Host Charts > Available Memory {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Available Memory | TimeSeries | storageclient.eastus | Fa | nodeId, startTime, endTime |

### Host Charts > Host CPU Node 1 ({{nodeId1}})
Path: `Host Charts > Host CPU Node 1 ({{nodeId1}})`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VP CPU | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Charts > Host CPU Node 2 ({{nodeId2}})
Path: `Host Charts > Host CPU Node 2 ({{nodeId2}})`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VP CPU | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Charts > Jitter Trend for {{nodeId1}}
Path: `Host Charts > Jitter Trend for {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CPU Jitter (High granularity) | TimeSeries | intmgmtshared.centralus | Fleet | nodeId, startTime, endTime |

### Host Charts > Jitter Trend for {{nodeId2}}
Path: `Host Charts > Jitter Trend for {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CPU Jitter (High granularity) | TimeSeries | intmgmtshared.centralus | Fleet | nodeId, startTime, endTime |

### Host Charts > Nonpaged Pool Bytes for {{nodeId1}}
Path: `Host Charts > Nonpaged Pool Bytes for {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node NPP Bytes | TimeSeries | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Charts > Nonpaged Pool Bytes for {{nodeId2}}
Path: `Host Charts > Nonpaged Pool Bytes for {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node NPP Bytes | TimeSeries | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Charts > Process Total Handle Count for {{nodeId1}}
Path: `Host Charts > Process Total Handle Count for {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Process Handle Count | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Charts > Process Total Handle Count for {{nodeId2}}
Path: `Host Charts > Process Total Handle Count for {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Process Handle Count | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Details > Node1 Details
Path: `Host Details > Node1 Details`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Azure Host Node" | ResourceGet | azurecm | AzureCM | local_nodeId, globalFrom, globalTo |
| 2 | Retrieve Node Hardware Details | Single | azuredcm | AzureDCMDb | queryFrom, queryTo, local_nodeId |
| 3 | Host OS Version | Single | wdgeventstore | HostOSDeploy | queryFrom, queryTo, local_nodeId |

### Host Details > Node2 Details
Path: `Host Details > Node2 Details`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Azure Host Node" | ResourceGet | azurecm | AzureCM | local_nodeId, globalFrom, globalTo |
| 2 | Retrieve Node Hardware Details | Single | azuredcm | AzureDCMDb | queryFrom, queryTo, local_nodeId |
| 3 | Host OS Version | Single | wdgeventstore | HostOSDeploy | queryFrom, queryTo, local_nodeId |

### Host Details > VMs running in {{nodeId1}}
Path: `Host Details > VMs running in {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Running VMs Query | Table | AzureCM | AzureCM | nodeIdStr, startTime, endTime |

### Host Details > VMs running in {{nodeId2}}
Path: `Host Details > VMs running in {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Running VMs Query | Table | AzureCM | AzureCM | nodeIdStr, startTime, endTime |

### Host Storage Charts > ASAP IO Stats for {{nodeId1}}
Path: `Host Storage Charts > ASAP IO Stats for {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node ASAP 2.0 IO Stats | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### Host Storage Charts > ASAP IO Stats for {{nodeId2}}
Path: `Host Storage Charts > ASAP IO Stats for {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node ASAP 2.0 IO Stats | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### Host Storage Charts > BlobCache/Vdc IO Stats for {{nodeId1}}
Path: `Host Storage Charts > BlobCache/Vdc IO Stats for {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Surface Stats for Node | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### Host Storage Charts > BlobCache/Vdc IO Stats for {{nodeId2}}
Path: `Host Storage Charts > BlobCache/Vdc IO Stats for {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Surface Stats for Node | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, nodeId |

### Host Storage Internal (test VMs only) > Hagrid Perf VMs > {{nodeId1}} VM's Max Latencies (in milliseconds)
Path: `Host Storage Internal (test VMs only) > Hagrid Perf VMs > {{nodeId1}} VM's Max Latencies (in milliseconds)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Test VMs Max Latencies | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, nodeIdStr |

### Host Storage Internal (test VMs only) > Hagrid Perf VMs > {{nodeId2}} VM's Max Latencies (in milliseconds)
Path: `Host Storage Internal (test VMs only) > Hagrid Perf VMs > {{nodeId2}} VM's Max Latencies (in milliseconds)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Test VMs Max Latencies | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, nodeIdStr |

### Host Tables > HighCPU Table > HighCPU Table for {{nodeId1}}
Path: `Host Tables > HighCPU Table > HighCPU Table for {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host HighCPUTable | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Tables > HighCPU Table > HighCPU Table for {{nodeId2}}
Path: `Host Tables > HighCPU Table > HighCPU Table for {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host HighCPUTable | Table | azcore.centralus | Fa | startTime, endTime, nodeId |

### Host Tables > Windows Event Table > Comparison > Windows Events Count
Path: `Host Tables > Windows Event Table > Comparison > Windows Events Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Compare Windows Event Comparison | Table | azcore.centralus | Fa | queryFrom, queryTo, nodeId1, Time2From, Time2To, nodeId2 |

### Host Tables > Windows Event Table > Events > Host Events {{nodeId1}}
Path: `Host Tables > Windows Event Table > Events > Host Events {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host WindowsEventTable | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### Host Tables > Windows Event Table > Events > Host Events {{nodeId2}}
Path: `Host Tables > Windows Event Table > Events > Host Events {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host WindowsEventTable | Table | azcore.centralus | Fa | nodeId, startTime, endTime |

### HostStorage CoPilot
Path: `HostStorage CoPilot`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | node_insights_summary | Single | storageclient.eastus | sc | startTime, endTime, nodeId |

### Registry Keys > Registry Keys in the Nodes (different is highlighted)
Path: `Registry Keys > Registry Keys in the Nodes (different is highlighted)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Node Compare Registry Keys | Table | storageclient.eastus | Fa | queryFrom, queryTo, nodeId1, Time2From, Time2To, nodeId2 |

### TDPR > {{nodeId1}} TDPR Stats
Path: `TDPR > {{nodeId1}} TDPR Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host TDPR | TimeSeries | azcore.centralus | Fa | queryFrom, queryTo, nodeId |

### TDPR > {{nodeId2}} TDPR Stats
Path: `TDPR > {{nodeId2}} TDPR Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host TDPR | TimeSeries | azcore.centralus | Fa | queryFrom, queryTo, nodeId |

### VM Charts > VM Available Memory {{nodeId1}}
Path: `VM Charts > VM Available Memory {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMs Memory Usage | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### VM Charts > VM Available Memory {{nodeId2}}
Path: `VM Charts > VM Available Memory {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMs Memory Usage | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### VM Charts > VM CPU {{nodeId1}}
Path: `VM Charts > VM CPU {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMs CPU Usage | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### VM Charts > VM CPU {{nodeId2}}
Path: `VM Charts > VM CPU {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VMs CPU Usage | TimeSeries | azcore.centralus | Fa | nodeId, startTime, endTime |

### VM Charts > VM Disk IOPS {{nodeId1}}
Path: `VM Charts > VM Disk IOPS {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host StorageClient VMs Disk IOPS | TimeSeries | storageclient.eastus | Fa | nodeIdStr, startTime, endTime |

### VM Charts > VM Disk IOPS {{nodeId2}}
Path: `VM Charts > VM Disk IOPS {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host StorageClient VMs Disk IOPS | TimeSeries | storageclient.eastus | Fa | nodeIdStr, startTime, endTime |

### VM Charts > VM Disk MBPS {{nodeId1}}
Path: `VM Charts > VM Disk MBPS {{nodeId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM StorageClient Disk MBPS | TimeSeries | storageclient.eastus | Fa | nodeIdStr, startTime, endTime |

### VM Charts > VM Disk MBPS {{nodeId2}}
Path: `VM Charts > VM Disk MBPS {{nodeId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM StorageClient Disk MBPS | TimeSeries | storageclient.eastus | Fa | nodeIdStr, startTime, endTime |
