# NRP — Load Balancer: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:53.885Z.
> Total: 10 unique KQL queries across 9 panels (10 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Load Balancer" | ResourceGet | argwus2nrpone.westus2 | AzureResourceGraph | local_name, local_resourceGroup, local_subscriptionId, local_timestamp |
| 2 | Load Balancer Operation Timeline | Timeline | nrp | mdsnrp | queryFrom, queryTo, querySubscriptionId, queryResourceGroupName, queryResourceName |

### Backend Address Pools > Backend Address Pools
Path: `Backend Address Pools > Backend Address Pools`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SLB - Backend Address Pools | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySub, queryGroup, queryName, queryTime |

### Frontend IP Configs > Front End IP Configurations
Path: `Frontend IP Configs > Front End IP Configurations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SLB - Front End IP Configurations | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySub, queryGroup, queryName, queryTime |

### Inbound Nat Pools > Inbound NAT Pools
Path: `Inbound Nat Pools > Inbound NAT Pools`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SLB - Inbound NAT Pools | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySub, queryGroup, queryName, queryTime |

### Inbound Nat Rules > Inbound NAT Rules
Path: `Inbound Nat Rules > Inbound NAT Rules`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SLB - Inbound Nat Rules | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySub, queryGroup, queryName, queryTime |

### Load Balancer Snapshots
Path: `Load Balancer Snapshots`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Load Balancer Snapshots | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySubscriptionId, queryId, queryFrom, queryTo |

### Load Balancing Rules > Load Balancing Rules
Path: `Load Balancing Rules > Load Balancing Rules`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SLB - Load Balancing Rules | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySub, queryGroup, queryName, queryTime |

### Outbound Rules > Outbound Rules
Path: `Outbound Rules > Outbound Rules`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SLB - Outbound Rules | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySub, queryGroup, queryName, queryTime |

### Probes > Probes
Path: `Probes > Probes`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | SLB - Probes | Table | argwus2nrpone.westus2 | AzureResourceGraph | querySub, queryGroup, queryName, queryTime |
