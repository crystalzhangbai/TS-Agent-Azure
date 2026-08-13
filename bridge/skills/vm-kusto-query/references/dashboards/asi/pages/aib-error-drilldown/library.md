# Azure VM Image Builder — Error Drilldown: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:12:12.702Z.
> Total: 4 unique KQL queries across 3 panels (4 widget refs).

## Page inputs (URL params)


## Panels

### ARM > Incoming Requests
Path: `ARM > Incoming Requests`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Incoming Requests | Table | armprodgbl.eastus | ARMProd | queryFrom, queryTo, queryCorrelationId, qFilter |
| 2 | All or Errors | Filter | ? | ? | - |

### AsyncContextActivity > AsyncContextActivity
Path: `AsyncContextActivity > AsyncContextActivity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AsyncContextActivity | Table | azcrp | vmimagebuilder | queryFrom, queryTo, local_correlationID |

### AsyncQoSEvents > AsyncQoSEvents
Path: `AsyncQoSEvents > AsyncQoSEvents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AsyncQoSEvents by correlationID | Table | azcrp | vmimagebuilder | local_correlationID |
