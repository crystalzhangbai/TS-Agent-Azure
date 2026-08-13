# NRP — Network Interfaces: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:53.718Z.
> Total: 6 unique KQL queries across 4 panels (6 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Network Interfaces" | ResourceGet | argwus2nrpone.westus2 | AzureResourceGraph | local_resourceGroupName, local_subscriptionId, local_name, local_timestamp |
| 2 | NIC IP Configurations | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryResourceGroupName, queryNICName, queryFrom, queryTo |
| 3 | Get Network Security Group | Single | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryResourceGroupName, queryNSGName |

### Current Rules > Current Rules > Security Rules
Path: `Current Rules > Current Rules > Security Rules`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NSG Security Rules | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryResourceGroupName, queryName, queryHintTime |

### NSG Updates
Path: `NSG Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NSG Updates | Timeline | nrp | mdsnrp | querySubscriptionId, queryResourceGroupName, queryNSGName, queryFrom, queryTo |

### Snapshots > Snapshots > NSG Snapshots (ARG)
Path: `Snapshots > Snapshots > NSG Snapshots (ARG)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Graph NSG Snapshots | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryName, queryResourceGroupName, querySubscriptionId, queryHintTime, queryFrom |
