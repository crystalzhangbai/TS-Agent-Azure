# Azure Host — Azure VM Compare: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T09:57:55.687Z.
> Total: 17 unique KQL queries across 19 panels (26 widget refs).

## Page inputs (URL params)


## Panels

### HostStorage CoPilot > Summary for {{containerId1}}
Path: `HostStorage CoPilot > Summary for {{containerId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container_Insights_Summary | Single | storageclient.eastus | sc | startTime, endTime, containerId, nodeId |

### HostStorage CoPilot > Summary for {{containerId2}}
Path: `HostStorage CoPilot > Summary for {{containerId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container_Insights_Summary | Single | storageclient.eastus | sc | startTime, endTime, containerId, nodeId |

### HostStorage VM Charts > ASAP IO Stats for {{containerId1}}
Path: `HostStorage VM Charts > ASAP IO Stats for {{containerId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM ASAP 2.0 IO Stats | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId, blobPath |

### HostStorage VM Charts > ASAP IO Stats for {{containerId2}}
Path: `HostStorage VM Charts > ASAP IO Stats for {{containerId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM ASAP 2.0 IO Stats | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, containerId, nodeId, blobPath |

### HostStorage VM Charts > Blobcache/vdc IO stats for {{containerId1}}
Path: `HostStorage VM Charts > Blobcache/vdc IO stats for {{containerId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host StorageClient Surface Counter Stats | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath |

### HostStorage VM Charts > Blobcache/vdc IO stats for {{containerId2}}
Path: `HostStorage VM Charts > Blobcache/vdc IO stats for {{containerId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host StorageClient Surface Counter Stats | TimeSeries | storageclient.eastus | Fa | startTime, endTime, containerId, nodeId, blobPath |

### HostStorage VM Charts > VM Disk Cache Usage Size in GB for {{containerId1}}
Path: `HostStorage VM Charts > VM Disk Cache Usage Size in GB for {{containerId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM CacheUsagePct | TimeSeries | storageclient.eastus | SharedWorkspace | startTime, endTime, containerId, blobPath |

### HostStorage VM Charts > VM Disk Cache Usage Size in GB for {{containerId2}}
Path: `HostStorage VM Charts > VM Disk Cache Usage Size in GB for {{containerId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM CacheUsagePct | TimeSeries | storageclient.eastus | SharedWorkspace | startTime, endTime, containerId, blobPath |

### Metrics Comparison
Path: `Metrics Comparison`  ·  Queries: 7

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | get_control_startTime | Single | storageclient.eastus | fa | queryFrom, queryTo |
| 2 | Retrieve Resource "Azure VM" | ResourceGet | AzureCM | AzureCM | globalFrom, globalTo, local_containerId, local_nodeId, local_virtualMachineUniqueId |
| 3 | Get Vm Details For Container 2 | Single | storageclient.eastus | Fc | startTime, endTime, containerIdentifier |
| 4 | Azure Host VM Active Blobs Filter | Filter | storageclient.eastus | Fa | startTime, endTime, nodeId, containerId |
| 5 | Azure Host VM Active Blobs Filter For Container 2 | Filter | storageclient.eastus | fa | startTime, endTime, nodeId, containerId |
| 6 | HeatMap_Type_Filter | Filter | azcore.centralus | fa | queryFrom, queryTo |
| 7 | Flip Baseline Container | Filter | storageclient.eastus | fa | queryFrom, queryTo |

### Metrics Comparison >  
Path: `Metrics Comparison >  `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Time Difference in Page Time Range | Single | storageclient.eastus | fa | queryFrom, queryTo |

### Metrics Comparison > {{Description}} {{Value}}
Path: `Metrics Comparison > {{Description}} {{Value}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Build_HeatMap | Heatmap | azcore.centralus | fa | startTime1, endTime1, cluster1, containerId1, nodeId1, blobPath1, startTime2, endTime2, cluster2, containerId2, nodeId2, blobPath2, heatMapType, filterVerbosity, baseline |

### TDPR > Comparing the IFX Functions
Path: `TDPR > Comparing the IFX Functions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM Compare IFX Tables | Table | azcore.centralus | Fa | queryFrom, queryTo, containerId1, queryParam3, queryParam4, containerId2 |

### VM Charts > Guest CPU Counters (30 seconds)
Path: `VM Charts > Guest CPU Counters (30 seconds)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure VM MetricsPerContainer | TimeSeries | intmgmtshared.centralus | Fleet | queryFrom, queryTo, containerId |

### VM Charts > VM 5 Min Counters for {{containerId1}}
Path: `VM Charts > VM 5 Min Counters for {{containerId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM CPU Usage | TimeSeries | azcore.centralus | Fa | nodeId, containerId, startTime, endTime |

### VM Charts > VM 5 Min Counters for {{containerId2}}
Path: `VM Charts > VM 5 Min Counters for {{containerId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM CPU Usage | TimeSeries | azcore.centralus | Fa | nodeId, containerId, startTime, endTime |

### VM Details > Container1 Details
Path: `VM Details > Container1 Details`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Azure VM" | ResourceGet | AzureCM | AzureCM | globalFrom, globalTo, local_containerId, local_nodeId, local_virtualMachineUniqueId |

### VM Details > Container2 Details
Path: `VM Details > Container2 Details`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Azure VM" | ResourceGet | AzureCM | AzureCM | globalFrom, globalTo, local_containerId, local_nodeId, local_virtualMachineUniqueId |

### VM IO Histogram Stats > HostStorage IO Stats Summary for {{containerId1}}
Path: `VM IO Histogram Stats > HostStorage IO Stats Summary for {{containerId1}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM StorageClient IO Latency Stats | Table | storageclient.eastus | Fa | containerId, startTime, endTime, blobPath, nodeId, Cloud |

### VM IO Histogram Stats > HostStorage IO Stats Summary for {{containerId2}}
Path: `VM IO Histogram Stats > HostStorage IO Stats Summary for {{containerId2}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host VM StorageClient IO Latency Stats | Table | storageclient.eastus | Fa | containerId, startTime, endTime, blobPath, nodeId, Cloud |
