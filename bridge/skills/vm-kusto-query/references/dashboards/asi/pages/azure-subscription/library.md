# Azure Host — Azure Subscription: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T09:57:55.127Z.
> Total: 21 unique KQL queries across 21 panels (21 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Azure Subscription" | ResourceGet | datastudiostreaming | Shared | local_SubscriptionId, globalFrom, globalTo |

### Active Disks for the Subscription
Path: `Active Disks for the Subscription`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription Disks | Table | storageclient.eastus | Fa | startTime, endTime, subId, _storageAccountName |

### AIR-BP with RCA > Disk AIR-BP
Path: `AIR-BP with RCA > Disk AIR-BP`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription Disk AIR-BP | Table | Vmainsight | Air | queryFrom, queryTo, subId |

### Charts > Cache Policy - Active Disks
Path: `Charts > Cache Policy - Active Disks`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription Active Disks | CategoryChart | storageclient.eastus | Fa | startTime, endTime, subId |

### Charts > Disk IOPS - Active Regions
Path: `Charts > Disk IOPS - Active Regions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscriptions Surface Stats Region | TimeSeries | storageclient.eastus | Fa | startTime, endTime, subId |

### Charts > Stats by ResourceGroup
Path: `Charts > Stats by ResourceGroup`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Analyzer Subscription Disk Stats by ResourceGroup | Table | storageclient.eastus | Fa | queryFrom, queryTo, subscriptionId |

### Charts > Total IOPS/MBPS
Path: `Charts > Total IOPS/MBPS`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription Surface IO Stats | TimeSeries | storageclient.eastus | Fa | subId, startTime, endTime |

### Disk Limits Stats > Disk Limits Stats
Path: `Disk Limits Stats > Disk Limits Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription Disk Limits Stats | Table | storageclient.eastus | Fa | startTime, endTime, subId |

### DiskTier Stats > TotalDisks by Tier
Path: `DiskTier Stats > TotalDisks by Tier`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription Disk Stats by Tier | CategoryChart | storageclient.eastus | Fa | queryFrom, queryTo, subscriptionId |

### Info > Subscription Details
Path: `Info > Subscription Details`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SubscriptionDetails | Single | datastudiostreaming | Shared | queryFrom, queryTo, subId |

### List of VMs > List of VMs that were running during the selected time
Path: `List of VMs > List of VMs that were running during the selected time`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription VMs | Table | storageclient.eastus | Fc | startTime, endTime, subId |

### Stats > Total VMs
Path: `Stats > Total VMs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription VMs Timeline | TimeSeries | AzureCM | AzureCM | queryFrom, queryTo, subId |

### Stats > VM Sizes
Path: `Stats > VM Sizes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscriptions VMs by Type | CategoryChart | AzureCM | AzureCM | queryFrom, queryTo, subId |

### StorageAccounts > StorageAccount Summary
Path: `StorageAccounts > StorageAccount Summary`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription StorageAccounts | Table | azcore.centralus | Fa | startTime, endTime, subId |

### Summary by Histogram > Summary
Path: `Summary by Histogram > Summary`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription AIR-BP by Histogram | Table | rdosdata | rdosdatapath | queryFrom, queryTo, subId |

### Timeline Chart > AIR-BP (Reads, Writes, Flush)
Path: `Timeline Chart > AIR-BP (Reads, Writes, Flush)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription Disk AIR-BP Timeline | TimeSeries | storageclient.eastus | Fa | queryFrom, queryTo, subId |

### Usage Stats > IOPS Stats by DiskName
Path: `Usage Stats > IOPS Stats by DiskName`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Analyzer Subscription Disk Stats | Table | storageclient.eastus | Fa | queryFrom, queryTo, subscriptionId |

### Usage Stats > MBPS Stats by DiskName
Path: `Usage Stats > MBPS Stats by DiskName`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription Disk MBPS Stats | Table | storageclient.eastus | Fa | startTime, endTime, subId |

### VM Stats > VM Shoebox Counters Stats
Path: `VM Stats > VM Shoebox Counters Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription VM Shoebox Counter Stats | Table | storageclient.eastus | Fa | startTime, endTime, subId |

### VM Stats > VMs that are doing more than 95% (in the time period selected)
Path: `VM Stats > VMs that are doing more than 95% (in the time period selected)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription VM Shoebox Top VMs doing Max | Table | storageclient.eastus | Fa | startTime, endTime, subId |

### VMs Availability (AIR-R)
Path: `VMs Availability (AIR-R)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Azure Host Subscription AIR-R | Table | vmainsight | vmadb | queryFrom, queryTo, subId |
