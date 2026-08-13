# CRP — Resource Move: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:18:23.450Z.
> Total: 7 unique KQL queries across 6 panels (7 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Resource Move" | ResourceGet | armprodgbl.eastus | ARMProd | local_correlationId, globalFrom, globalTo |
| 2 | Move ARM Event | Single | armprod | ARMProd | starttime, endtime, correlationid |

### ARM Event > ARM Event
Path: `ARM Event > ARM Event`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARM Event | Table | armprod | ARMProd | starttime, endtime, correlationid |

### ARM Event > Latest Error Details
Path: `ARM Event > Latest Error Details`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Error Details | Single | armprod | ARMProd | starttime, endtime, correlationid |

### ARM HTTP Incoming > ARM HTTP Incoming
Path: `ARM HTTP Incoming > ARM HTTP Incoming`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARM HTTP Incoming | Table | armprod | ARMProd | starttime, endtime, correlationid |

### ARM HTTP Outgoing > ARM HTTP Outgoing
Path: `ARM HTTP Outgoing > ARM HTTP Outgoing`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARM HTTP Outgoing | Table | armprod | ARMProd | starttime, endtime, correlationid |

### ARM Traces > ARM Traces
Path: `ARM Traces > ARM Traces`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARM Trace | Table | armprod | ARMProd | starttime, endtime, correlationid |
