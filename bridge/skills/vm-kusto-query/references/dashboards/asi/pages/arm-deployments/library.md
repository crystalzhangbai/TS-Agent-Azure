# ARM — Deployments: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:23:52.577Z.
> Total: 4 unique KQL queries across 3 panels (5 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Deployments" | ResourceGet | armprodgbl.eastus | ARMProd | local_correlationId, local_deploymentName, local_endTime, local_resourceGroupName, local_startTime, local_subscriptionId, globalFrom, globalTo |

### Deployment Job Status
Path: `Deployment Job Status`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Job Status | Table | armprodgbl.eastus | ARMProd | queryFrom, queryTo, queryCorrelationId, qFilter |
| 2 | All or Errors | Filter | ? | ? | - |

### Operations > Deployment Operations
Path: `Operations > Deployment Operations`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Deployment Operations | Table | armprodgbl.eastus | ARMProd | querySubscriptionId, queryDeploymentName, queryCorrelationId, queryFuzzyStartTime, queryFuzzyEndTime, qFilter |
| 2 | All or Errors | Filter | ? | ? | - |
