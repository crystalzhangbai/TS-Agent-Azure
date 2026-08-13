# ACC CVM — Confidential Virtual Machine: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:27:08.316Z.
> Total: 12 unique KQL queries across 7 panels (12 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 5

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Confidential Virtual Machine" | ResourceGet | azcrp | crp_allprod | globalFrom, globalTo, local_SubscriptionId, local_ResourceGroupName, local_ResourceName, local_VMId |
| 2 | CRP VM Events | Timeline | azcrp | crp_allprod | queryFrom, queryTo, querySubscriptionId, queryResourceGroup, queryResourceName, queryVmId |
| 3 | Container Events | Timeline | azcore.centralus | AzureCP | queryFrom, queryTo, queryVmId |
| 4 | VM Containers | Table | azcore.centralus | AzureCP | queryFrom, queryTo, queryVmId |
| 5 | Execution Graph | Table | executiongraph | eg | queryFrom, queryTo, queryVmId |

### Counters
Path: `Counters`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VM Performance Counters | TimeSeries | azcore.centralus | Fa | queryFrom, queryTo, queryVmId |

### CRP Event Logs
Path: `CRP Event Logs`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP VM Event Logs | Table | azcrp | crp_allprod | queryFrom, queryTo, querySubscriptionId, queryResourceGroup, queryResourceName |
| 2 | VMSS VM ApiQosEvent | Table | azcrp | crp_allprod | queryFrom, queryTo, SubscriptionId, ResourceGroupName, ResourceName |

### CRP VMSS VM Event Logs
Path: `CRP VMSS VM Event Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMSS VM ApiQosEvent | Table | azcrp | crp_allprod | queryFrom, queryTo, querySubscriptionId, queryResourceGroupName, queryResourceName |

### Disk Manager Events
Path: `Disk Manager Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Disk Manager Events | Table | disks | Disks | queryFrom, queryTo, queryCorrelationId |

### IGVM Agent Logs
Path: `IGVM Agent Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | IGVM Agent Logs | Table | https://azcore.centralus/ | acccvmtmgeneva | queryFrom, queryTo, queryContainers |

### Windows Event Logs
Path: `Windows Event Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Windows Event Table | Table | azcore.centralus | Fa | queryFrom, queryTo, queryContainers |
