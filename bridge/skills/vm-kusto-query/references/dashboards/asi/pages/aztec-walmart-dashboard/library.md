# Aztec — Walmart Dashboard: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T11:19:29.141Z.
> Total: 3 unique KQL queries across 3 panels (3 widget refs).

## Page inputs (URL params)


## Panels

### Overview > Failure Trend
Path: `Overview > Failure Trend`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Exceptions | TimeSeries | azurecm | AzureCM | startTime, endTime, local_subscriptionId |

### Role Instance / VM > Role Instance / VM
Path: `Role Instance / VM > Role Instance / VM`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMSnapshot | Table | azurecm | AzureCM | startTime, endTime, local_subscriptionId |

### VMApiQosEvent > VMApiQOsEvent (Failures in selected time period)
Path: `VMApiQosEvent > VMApiQOsEvent (Failures in selected time period)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMApiQosEvent | Table | azurecm | AzureCM | startTime, endTime, local_subscriptionId |
