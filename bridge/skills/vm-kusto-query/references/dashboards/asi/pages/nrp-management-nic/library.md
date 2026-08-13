# NRP — Management Nic: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:53.943Z.
> Total: 19 unique KQL queries across 12 panels (19 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 8

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | F5 Enic Error Summary | Table | https://nrp | mdsnrp | queryFrom, queryTo |
| 2 | NIC - Notifications fetched | TimeSeries | https://nrp/ | mdsnrp | startTime, endTime, tenantName |
| 3 | NIC- Notifications started being processed | TimeSeries | https://nrp/ | mdsnrp | startTime, endTime, tenantName |
| 4 | NIC- Notifications Processed | TimeSeries | https://nrp/ | mdsnrp | startTime, endTime, tenantName |
| 5 | NIC- Create or Update | TimeSeries | https://nrp/ | mdsnrp | startTime, endTime, tenantName |
| 6 | NIC - Delete | TimeSeries | https://nrp/ | mdsnrp | startTime, endTime, tenantName |
| 7 |  NIC- Resource not exist but entry not deleted2 | Table | https://nrp/ | mdsnrp | startTime, endTime, tenantName |
| 8 | invalidEnic | Table | https://nrp/ | mdsnrp | startTime, endTime, tenantName |

### Elastic Nic Request > Elastic Nic Usage
Path: `Elastic Nic Request > Elastic Nic Usage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Enic Change Distibution | TimeSeries | https://nrp | mdsnrp | region, startTime, endTime |

### Elastic Nic Request > Parent Nic Usage
Path: `Elastic Nic Request > Parent Nic Usage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Parent Nic Usage | TimeSeries | https://nrp | mdsnrp | region, startTime, endTime |

### Elastic Nic Request > VMSS Enic Request
Path: `Elastic Nic Request > VMSS Enic Request`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMSS Enic Hourly Summarize | TimeSeries | https://nrp | mdsnrp | startTime, endTime |

### Enic Usage > Enic Usage Customer Based
Path: `Enic Usage > Enic Usage Customer Based`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Enic Usage per Customer | TimeSeries | https://nrp | mdsnrp | startTime, endTime |

### Enic Usage > Enic Usage Region Based
Path: `Enic Usage > Enic Usage Region Based`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Enic Usage | TimeSeries | https://nrp | mdsnrp | startTime, endTime |

### Enic Usage > Monthly Active Enic
Path: `Enic Usage > Monthly Active Enic`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Monthly Active Enic | TimeSeries | https://nrp | mdsnrp | - |

### Enic Usage > Pnic Usage
Path: `Enic Usage > Pnic Usage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Pnic Usage | TimeSeries | https://nrp | mdsnrp | startTime, endTime |

### F5 Network > Enic Usage
Path: `F5 Network > Enic Usage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | F5 Enic Usage | TimeSeries | https://nrp | mdsnrp | queryFrom, queryTo |

### Operation Errors Summary > Elastic Nic Create/Update Error Summarize
Path: `Operation Errors Summary > Elastic Nic Create/Update Error Summarize`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ElasticNic Query | Table | https://nrp | mdsnrp | startTime, endTime |

### Operation Errors Summary > Parent Nic Create/Update Error Summarize
Path: `Operation Errors Summary > Parent Nic Create/Update Error Summarize`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Parent Nic | Table | https://nrp | mdsnrp | startTime, endTime |

### Operation Errors Summary > VMSS with Mgmt Nic Config
Path: `Operation Errors Summary > VMSS with Mgmt Nic Config`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMSS with Mgmt Nic | Table | https://nrp | mdsnrp | startTime, endTime |
