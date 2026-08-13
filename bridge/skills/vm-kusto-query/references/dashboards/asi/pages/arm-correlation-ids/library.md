# ARM — Correlation Ids: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:23:58.118Z.
> Total: 9 unique KQL queries across 8 panels (11 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Correlation Ids" | ResourceGet | armprodgbl.eastus | ARMProd | local_timestamp, local_correlationId, globalFrom, globalTo |

### CoBe Timeline
Path: `CoBe Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARMCorrelationId | CoBeTimeline | armprodgbl.eastus | ARMProd | correlationId, PreciseTimeStamp |

### Deployment Operations
Path: `Deployment Operations`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Deployment Operations | Table | armprodgbl.eastus | ARMProd | querySubscriptionId, queryDeploymentName, queryCorrelationId, queryFuzzyStartTime, queryFuzzyEndTime, qFilter |
| 2 | All or Errors | Filter | ? | ? | - |

### Deployments
Path: `Deployments`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Deployments by Correlation Id | Table | armprodgbl.eastus | ARMProd | qFrom, qTo, qCorrelationId |

### Execution Graph
Path: `Execution Graph`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Lookup up EG | Single | https://egpublic.westus | eg | queryCorrelationOrOperationId |

### Incoming Requests
Path: `Incoming Requests`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Incoming Requests | Table | armprodgbl.eastus | ARMProd | queryFrom, queryTo, queryCorrelationId, qFilter |
| 2 | All or Errors | Filter | ? | ? | - |

### Outgoing Requests
Path: `Outgoing Requests`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Outgoing Requests | Table | armprodgbl.eastus | ARMProd | queryFrom, queryTo, queryCorrelationId, qFilter |
| 2 | All or Errors | Filter | ? | ? | - |

### Preflight Operations
Path: `Preflight Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Correlation ID - Preflight Ops | Table | armprodgbl.eastus | ARMProd | queryFrom, queryTo, queryCorrelationId |
