# CRP — Subscriptions: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:18:19.594Z.
> Total: 16 unique KQL queries across 14 panels (16 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Subscriptions" | ResourceGet | azcrpbifollower | bi_allprod | local_subscriptionId |
| 2 | Query Sub from CommonDims | Single | customerdomrptwus3prod.westus3 | customerdomdata | queryFrom, queryTo, querySubId |
| 3 | Subscription Availability Zones | Table | azcrpbifollower | bi_allprod | querySubscriptionId |

### ASC Tab - Use the same queries from ASC > Current Maintenance-Control Status by Subscription
Path: `ASC Tab - Use the same queries from ASC > Current Maintenance-Control Status by Subscription`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Current Maintenance-Control Status by Subscription | Table | Azdeployer | AzDeployerKusto | queryFrom, queryTo, querySub |

### ASC Tab - Use the same queries from ASC > Maintenance-Control Status History by Subscription
Path: `ASC Tab - Use the same queries from ASC > Maintenance-Control Status History by Subscription`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Maintenance-Control Status History by Subscription | Table | Azdeployer | AzDeployerKusto | queryFrom, queryTo, querySub |

### ASC Tab - Use the same queries from ASC > Planned Maintenance History by Subscription
Path: `ASC Tab - Use the same queries from ASC > Planned Maintenance History by Subscription`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Planned Maintenance History by Subscription | Table | Azdeployer | AzDeployerKusto | queryFrom, queryTo, querySub |

### ASC Tab - Use the same queries from ASC > Planned Maintenance Notifications/Emails
Path: `ASC Tab - Use the same queries from ASC > Planned Maintenance Notifications/Emails`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GetCommunicationsForSupport | Table | icmcluster | ACM.Publisher | queryFrom, queryTo, querySub, queryCloud |

### ASC Tab - Use the same queries from ASC > Planned Maintenance Phase Details
Path: `ASC Tab - Use the same queries from ASC > Planned Maintenance Phase Details`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Planned Maintenance Phase Details by Subscription | Table | azcsupfollower | AzureCM | queryFrom, queryTo, querySubId |

### ASC Tab - Use the same queries from ASC > Planned Maintenance Status Summary
Path: `ASC Tab - Use the same queries from ASC > Planned Maintenance Status Summary`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Query Planned Maintenance Status Summary by Subscription | Table | Azdeployer | AzDeployerKusto | queryFrom, queryTo, querySubId |

### ASC Tab - Use the same queries from ASC > Test
Path: `ASC Tab - Use the same queries from ASC > Test`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Service Healing due to Planned Maintenance by Sub | Table | azcsupfollower | AzureCM | queryFrom, queryTo, querySub |

### CSS Tab - Customized queries for CSS > Planned Maintenance Communications/Emails
Path: `CSS Tab - Customized queries for CSS > Planned Maintenance Communications/Emails`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GetPlannedMaintenanceCommunicationsForSupport | Table | Icmcluster | ACM.Backend | queryFrom, queryTo, querySub |

### CSS Tab - Customized queries for CSS > Planned Maintenance Status
Path: `CSS Tab - Customized queries for CSS > Planned Maintenance Status`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Current Maintenance Status By Subscription | Table | azcsupfollower | AzureCM | queryFrom, queryTo, querySub |

### Resource Groups > Resource Groups
Path: `Resource Groups > Resource Groups`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Resource Groups | Table | azcrp | crp_allprod | querySubscriptionId |

### Scale Sets / VMSS
Path: `Scale Sets / VMSS`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Resource Group Scale Sets | Table | azcrpbifollower | bi_allprod | querySubscriptionId, queryResourceGroup, queryFrom, queryTo |

### Throttling
Path: `Throttling`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription Throttling | TimeSeries | azcrp | crp_allprod | querySubscriptionId |

### VMs > VMs
Path: `VMs > VMs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription VMs | Table | azcrpbifollower | bi_allprod | querySubscriptionId, queryResourceGroupName, queryFrom, queryTo |
