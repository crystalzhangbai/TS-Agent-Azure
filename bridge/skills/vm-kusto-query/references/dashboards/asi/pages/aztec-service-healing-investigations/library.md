# Aztec — ServiceHealingInvestigations: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T11:19:29.567Z.
> Total: 8 unique KQL queries across 4 panels (10 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 5

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Metedata Query from mycroft | Single | mycroft.westcentralus | Mycroft | queryFrom, queryTo, _sourceContainerIdToHeal |
| 2 | Mycroft container health summary | Single | azcore.centralus | AzureCP | queryFrom, queryTo, queryContainerId |
| 3 | Mycroft Node Health Summary | Single | azcore.centralus | AzureCP | queryFrom, queryTo, queryContainerId |
| 4 | Tenant Summary Query | Single | azurecm | AzureCM | queryFrom, queryTo, queryContainerId |
| 5 | FC Service Healing Trigger QUery | Table | azurecm | AzureCM | queryFrom, queryTo, _sourceContainerIdToHeal |

### AzSM Service Healing Step Result Events table
Path: `AzSM Service Healing Step Result Events table`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSM Service Healing Summary Query | Table | accp.centralus | AZSM | queryFrom, queryTo, _sourceContainerIdToHeal |

### AzSM Service Healing Summary
Path: `AzSM Service Healing Summary`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AzSM Service Healing Trigger and Result details | Single | accp.centralus | AZSM | queryFrom, queryTo, _sourceContainerIdToHeal |

### Tenant Service Healing Events Table
Path: `Tenant Service Healing Events Table`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Tenant Events Service Healing Trigger Events | Table | azurecm | AzureCM | queryFrom, queryTo, queryContainerId |
