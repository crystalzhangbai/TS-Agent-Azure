# Aztec — Clusters: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:20:33.064Z.
> Total: 15 unique KQL queries across 9 panels (15 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 7

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Clusters" | ResourceGet | azcsupfollower | AzureCM | globalFrom, globalTo, local_Tenant |
| 2 | Cluster Hosting Env | Table | azurecm | AzureCM | queryTenant |
| 3 | Cluster Setting Deletions | Timeline | azurecm | azurecm | queryCluster |
| 4 | Cluster Incarnations | Timeline | azurecm | AzureCM | queryTenant |
| 5 | LEGO DC Health Status | Timeline | silverstonepcs.eastus | silverstonepcsdb | queryRegion, queryCluster, queryFrom, queryTo |
| 6 | FC Downtime | Timeline | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName |
| 7 | FC Failover | Timeline | azcore.centralus | Fc | queryFrom, queryTo, queryTenantName |

### Allocation Activity > Allocation Activity
Path: `Allocation Activity > Allocation Activity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Stamp Allocation Activity  | Table | azcrp | crp_allprod | queryStamp, queryFrom, queryTo |

### Core Capacity > Cores
Path: `Core Capacity > Cores`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Cluster Cores | TimeSeries | azurecm | AzureCM | queryTenant |

### Gateway Service > GatewayServiceTraceEvent 
Path: `Gateway Service > GatewayServiceTraceEvent `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Check GatewayServiceTraceEvent by Cluster | Table | azcpplatform.westcentralus | azcpplatform | queryFrom, queryTo, queryClusterTenantName |

### LEGO EKG & Vitals > EKG & Vitals
Path: `LEGO EKG & Vitals > EKG & Vitals`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LEGO - EKG & Vitals | TimeSeries | silverstonepcs.eastus | silverstonepcsdb | queryRegion, queryCluster, queryFrom, queryTo |

### Node Capacity > Nodes
Path: `Node Capacity > Nodes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Cluster Nodes | TimeSeries | azurecm | AzureCM | queryTenant |

### Nodes > Nodes
Path: `Nodes > Nodes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Cluster Nodes | Table | azurecm | AzureCM | queryCluster |

### Tenants > Tenants
Path: `Tenants > Tenants`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Cluster Tenants | Table | azurecm | AzureCM | queryCluster, queryFrom, queryTo |

### Utilization % > Utilization %
Path: `Utilization % > Utilization %`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant Utilization Percent TimeSeries  | TimeSeries | AzureCM | AzureCM | queryFrom, queryTo, queryTenant |
