# NRP — Firewall: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:53.676Z.
> Total: 9 unique KQL queries across 9 panels (9 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Firewall" | ResourceGet | argwus2nrpone.westus2 | AzureResourceGraph | local_resourceGroupName, local_subscriptionId, local_name, local_timestamp |

### Application Rules
Path: `Application Rules`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Firewall - ApplicationRuleCollections | Table | argwus2nrpone.westus2 | AzureResourceGraph | local_resourceGroupName, local_subscriptionId, local_name, local_timestamp |

### Application Rules > Rules
Path: `Application Rules > Rules`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Firewall - ApplicationRuleCollections - Rules | Table | argwus2nrpone.westus2 | AzureResourceGraph | local_resourceGroupName, local_subscriptionId, local_name, local_timestamp, rule_collection_id |

### Firewall Snapshots
Path: `Firewall Snapshots`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Az firewall snapshots | Table | argwus2nrpone.westus2 | AzureResourceGraph | qFrom, qTo, qName, qRG, qSub |

### FW Operations
Path: `FW Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AZ Firewall Operation Timline | Timeline | nrp | mdsnrp | qFrom, qTo, qName, qSub, qRG |

### NAT Rules
Path: `NAT Rules`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Firewall - NatRuleCollections | Table | argwus2nrpone.westus2 | AzureResourceGraph | local_resourceGroupName, local_subscriptionId, local_name, local_timestamp |

### NAT Rules > Rules
Path: `NAT Rules > Rules`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Firewall - NatRuleCollections - Rules | Table | argwus2nrpone.westus2 | AzureResourceGraph | local_resourceGroupName, local_subscriptionId, local_name, local_timestamp, rule_collection_id |

### Rule Collections
Path: `Rule Collections`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Firewall - Network Rule Collections | Table | argwus2nrpone.westus2 | AzureResourceGraph | local_resourceGroupName, local_subscriptionId, local_name, local_timestamp |

### Rule Collections > Rules
Path: `Rule Collections > Rules`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Firewall - NetworkRuleCollections - Rules | Table | argwus2nrpone.westus2 | AzureResourceGraph | local_resourceGroupName, local_subscriptionId, local_name, local_timestamp, rule_collection_id |
