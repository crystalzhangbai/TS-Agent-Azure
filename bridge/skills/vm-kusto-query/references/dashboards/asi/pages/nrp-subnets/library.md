# NRP — Subnets: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:53.899Z.
> Total: 12 unique KQL queries across 10 panels (12 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Subnets" | ResourceGet | argwus2nrpone.westus2 | AzureResourceGraph | local_subnetName, local_subscriptionId, local_resourceGroupName, local_virtualNetworkName |
| 2 | Subnet Features | FeatureList | argwus2nrpone.westus2 | AzureResourceGraph | queryVNetResourceId, querySubnetName, queryTimestampHint |
| 3 | Subnet Private Endpoints | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryFrom, queryTo, qSubnetName, qSubId, qRG, qVnetName |

### NSG
Path: `NSG`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Network Security Group | Single | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryResourceGroupName, queryNSGName |

### NSG > Current Rules > Current Rules > Security Rules
Path: `NSG > Current Rules > Current Rules > Security Rules`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NSG Security Rules | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryResourceGroupName, queryName, queryHintTime |

### NSG > NSG Updates
Path: `NSG > NSG Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NSG Updates | Timeline | nrp | mdsnrp | querySubscriptionId, queryResourceGroupName, queryNSGName, queryFrom, queryTo |

### NSG > Snapshots > Snapshots > NSG Snapshots (ARG)
Path: `NSG > Snapshots > Snapshots > NSG Snapshots (ARG)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Graph NSG Snapshots | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryName, queryResourceGroupName, querySubscriptionId, queryHintTime, queryFrom |

### Route Table
Path: `Route Table`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Route Table | Single | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryResourceGroupName, queryRouteTableName, queryOptionalHintTime |

### Route Table > Route Table Updates
Path: `Route Table > Route Table Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Route Table Changes | Timeline | nrp | mdsnrp | querySubscriptionId, queryResourceGroupName, queryRouteTableName, queryFrom, queryTo |

### Route Table > Route Updates > Route Updates > Route Updates
Path: `Route Table > Route Updates > Route Updates > Route Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tim Query Created for Andy | Table | nrp | mdsnrp | querySubscriptionId, queryResourceGroupName, queryRouteTableName, queryFrom, queryTo |

### Route Table > Routes > Routes > Routes
Path: `Route Table > Routes > Routes > Routes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Route Table Routes | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryResourceGroupName, queryRouteTableName, queryOptionalHintTime |

### Route Table > Snapshots > Route Table Snapshots (ARG)
Path: `Route Table > Snapshots > Route Table Snapshots (ARG)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NRP Route Table Snapshots | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryName, queryResourceGroupName, querySubscriptionId, queryHintTime |
