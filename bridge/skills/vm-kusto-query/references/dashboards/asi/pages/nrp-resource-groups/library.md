# NRP — Resource Groups: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:53.692Z.
> Total: 9 unique KQL queries across 8 panels (9 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Resource Groups" | ResourceGet | argwus2nrpone.westus2 | AzureResourceGraph | local_subscriptionId, local_resourceGroupName |
| 2 | Sub or RG Route Tables | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryFrom, queryTo, querySubscriptionId, queryOptionalResourceGroupName |

### Firewalls
Path: `Firewalls`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription Firewalls | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryOptionalResourceGroupName, queryFrom, queryTo |

### Load Balancers
Path: `Load Balancers`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NRP Sub and RG Load Balancers | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryFrom, queryTo, queryOptionalResourceGroupName, querySubscriptionId |

### NSGs > Resource Group NSGs
Path: `NSGs > Resource Group NSGs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription NSGs | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryOptionalResourceGroupName, queryFrom, queryTo |

### Private Endpoints
Path: `Private Endpoints`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NRP Sub and RG Private Endpoints | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryFrom, queryTo, queryOptionalResourceGroupName, querySubscriptionId |

### Public IPs
Path: `Public IPs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NRP Public IPs by Sub and RG | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryFrom, queryTo, querySubscriptionId, queryOptionalResourceGroup |

### Subnets > Resource Group Subnets
Path: `Subnets > Resource Group Subnets`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription Subnets | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryOptionalResourceGroupName, queryFrom, queryTo |

### VNets > Resource Group VNets
Path: `VNets > Resource Group VNets`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Subscription VNets | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryOptionalResourceGroup, queryFrom, queryTo |
