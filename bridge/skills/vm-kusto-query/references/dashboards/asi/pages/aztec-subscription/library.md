# Aztec — Subscription: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T11:19:29.170Z.
> Total: 4 unique KQL queries across 4 panels (4 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Subscription" | ResourceGet | azurecm | AzureCM | local_endDate, local_startDate, local_subscriptionId |

### Availability Sets
Path: `Availability Sets`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription AvailabilitySet List | Table | AzureCM | AzureCM | local_subscriptionId, local_startDate, local_endDate |

### Related Activity Ids
Path: `Related Activity Ids`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription RelatedActivityId List | Table | AzureCM | AzureCM | local_subscriptionId, local_endDate, local_startDate |

### Role Instances / VMs
Path: `Role Instances / VMs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription RoleInstance List | Table | azurecm | AzureCM | local_subscriptionId, local_endDate, local_startDate |
