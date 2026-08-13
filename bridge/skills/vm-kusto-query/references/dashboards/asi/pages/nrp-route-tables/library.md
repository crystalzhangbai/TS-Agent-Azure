# NRP — Route Tables: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:53.682Z.
> Total: 6 unique KQL queries across 5 panels (6 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Route Tables" | ResourceGet | nrp | binrp | local_name, local_resourceGroupName, local_subscriptionId, local_timestamp |
| 2 | Route Table | Single | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryResourceGroupName, queryRouteTableName, queryOptionalHintTime |

### Route Table Updates
Path: `Route Table Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Route Table Changes | Timeline | nrp | mdsnrp | querySubscriptionId, queryResourceGroupName, queryRouteTableName, queryFrom, queryTo |

### Route Updates > Route Updates > Route Updates
Path: `Route Updates > Route Updates > Route Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tim Query Created for Andy | Table | nrp | mdsnrp | querySubscriptionId, queryResourceGroupName, queryRouteTableName, queryFrom, queryTo |

### Routes > Routes > Routes
Path: `Routes > Routes > Routes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Route Table Routes | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryResourceGroupName, queryRouteTableName, queryOptionalHintTime |

### Snapshots > Route Table Snapshots (ARG)
Path: `Snapshots > Route Table Snapshots (ARG)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NRP Route Table Snapshots | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryName, queryResourceGroupName, querySubscriptionId, queryHintTime |
