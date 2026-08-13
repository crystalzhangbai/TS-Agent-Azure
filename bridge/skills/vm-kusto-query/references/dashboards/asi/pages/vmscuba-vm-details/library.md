# VM Scuba — VM Details: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:27:08.444Z.
> Total: 17 unique KQL queries across 15 panels (17 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-VMDetails | Single | moseisley | AzureCM | queryFrom, queryTo, RoleInstanceName |
| 2 | Get-TOR | Single | moseisley | AzureCM | queryFrom, queryTo, subscriptionId, roleInstanceName |
| 3 | Get-SessionId | Single | AzureCM | AzureCM | queryFrom, queryTo, containerId |

### Container Health status
Path: `Container Health status`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-ContainerHealthStatus | Table | azurecm | AzureCM | queryFrom, queryTo, containerId |

### Get HostOS Updates
Path: `Get HostOS Updates`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-HostOSUpdates | Table | AzureCM | AzureCM | queryFrom, queryTo, nodeId |

### Get Maintenance details 
Path: `Get Maintenance details `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-MaintenanceDetails | Table | Azdeployer | AzDeployerKusto | queryFrom, queryTo, subscriptionId, roleInstanceName, tenantName |

### Get Updates on Node
Path: `Get Updates on Node`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-NodeUpdates | Table | minekraft.westus | crawler5 | queryFrom, queryTo, nodeId |

### Live Migration Errors 
Path: `Live Migration Errors `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-LiveMigrationErrors | Table | azurecm | AzureCM | queryFrom, queryTo, sessionId |

### Live Migrations Events
Path: `Live Migrations Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-LiveMigrationsEvents | Table | azurecm | AzureCM | queryFrom, queryTo, sessionId |

### Node state change
Path: `Node state change`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-NodeStateChange | Table | AzureCM | AzureCM | queryFrom, queryTo, nodeId |

### Overlake Config
Path: `Overlake Config`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-Overlake Config | Table | gandalf | gandalf | queryFrom, queryTo, roleInstanceName |

### Resource Health
Path: `Resource Health`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-ResourceHealth | Table | icmbrain | AzureResourceHealth | queryFrom, queryTo, roleInstanceName, subscriptionId |

### TOR Health
Path: `TOR Health`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-TORHealth | Table | azphynet | azdhmds | queryFrom, queryTo |

### VM Config
Path: `VM Config`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-VMSummary | Table | azcrpbifollower | bi_allprod | queryFrom, queryTo, virtualMachineUniqueId |

### VM Insights for a given TIMESTAMP
Path: `VM Insights for a given TIMESTAMP`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-VMInsights | Table | rdosdata | rdosdatapath | queryFrom, queryTo, nodeId |

### VM Node to TOR Health
Path: `VM Node to TOR Health`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-VMNodetoTORHealth | Table | aznwsdn | aznwmds | queryFrom, queryTo, nodeId |

### VM Restart Events
Path: `VM Restart Events`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get-VMRestartEvents | Table | moseisley | Air | queryFrom, queryTo, virtualMachineUniqueId |
