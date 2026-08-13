# NRP — Virtual Networks: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:53.705Z.
> Total: 3 unique KQL queries across 3 panels (3 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Virtual Networks" | ResourceGet | argwus2nrpone.westus2 | AzureResourceGraph | local_name, local_resourceGroupName, local_subscriptionId, local_timestamp |

### Peerings > VNet Peerings
Path: `Peerings > VNet Peerings`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Virtual Network Peerings | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryId |

### Subnets > Subnets
Path: `Subnets > Subnets`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Virtual Network Subnets | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryVNetResourceId |
