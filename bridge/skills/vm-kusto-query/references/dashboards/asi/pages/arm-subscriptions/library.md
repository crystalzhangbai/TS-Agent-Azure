# ARM — Subscriptions: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:29:22.207Z.
> Total: 8 unique KQL queries across 5 panels (8 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 4

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Subscriptions" | ResourceGet | customerdomrptwus3prod.westus3 | customerdomdata | local_SubscriptionId, globalFrom, globalTo |
| 2 | Subscription Requests | TimeSeries | armprodgbl.eastus | ARMProd | querySubscriptionId, queryFrom, queryTo |
| 3 | Subscription Requests by User Agent | TimeSeries | armprodgbl.eastus | ARMProd | queryFrom, queryTo, querySubscriptionId, queryOptionalRegion, queryOptionalFilter |
| 4 | Filter - Request Errors | Filter | ? | ? | - |

### Deployments > Subscription Deployments
Path: `Deployments > Subscription Deployments`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription Deployments | Table | armprodgbl.eastus | ARMProd | querySubscriptionId, qStart, qEnd |

### Resource Groups > Resource Groups
Path: `Resource Groups > Resource Groups`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription Resource Groups | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, qFrom, qTo |

### Resources > All Resources
Path: `Resources > All Resources`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription Resources | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId |

### VMs > VMs
Path: `VMs > VMs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription VMs | Table | azurecm | AzureCM | querySubscription, queryFrom, queryTo |
