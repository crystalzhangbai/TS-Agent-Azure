# ARM — CoBe AzControlPlaneRegionInsights: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:23:48.064Z.
> Total: 19 unique KQL queries across 2 panels (19 widget refs).

## Page inputs (URL params)


## Panels

### Outage
Path: `Outage`  ·  Queries: 14

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AAD Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 2 | ARM Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 3 | AzPolicy Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 4 | CosmosDB Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 5 | Virtual Machines Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 6 | Network Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 7 | AKS Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 8 | Storage Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 9 | SQL Database Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 10 | App Services Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 11 | Container Instances Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 12 | PostgreSQL Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 13 | LogicApps Outages | Timeline | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |
| 14 | Region Outages | Table | https://icmcluster | IcMDataWarehouse | region, startTime, endTime |

### Release
Path: `Release`  ·  Queries: 5

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | CRP Release | Timeline | aegisfollower.centralus | gandalf_tdpr | region, startTime, endTime |
| 2 | NRP Release | Timeline | aegisfollower.centralus | gandalf_tdpr | region, startTime, endTime |
| 3 | AKS Release | Timeline | https://aegisfollower.centralus | gandalf_tdpr | startTime, endTime, region |
| 4 | ARM Release | Timeline | gandalfcontrolplane | arm_analytics | region, startTime, endTime |
| 5 | Release | Table | gandalfcontrolplane | arm_analytics | region, startTime, endTime |
