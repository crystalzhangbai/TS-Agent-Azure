# Network Manager — NsmQosInfo Search: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:12:40.187Z.
> Total: 6 unique KQL queries across 1 panels (6 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 6

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "NsmQosInfo Search" | ResourceGet | azurecm | AzureCM | local_PreciseTimeStamp, local_TenantName |
| 2 | NsmQosOps | CoBeTimeline | azurecm | AzureCM | timestamp, queryTenantName |
| 3 | GetResourceGroup | Single | azcrp | crp_allprod | timestamp, queryTenantName |
| 4 | RNMRequest | Table | aznwsdn | aznwmds | timestamp, queryTenantName, queryRegion |
| 5 | RNM ResourceRelease | Table | aznwsdn | aznwmds | timestamp, queryRegion, queryTenantName |
| 6 | Frontend | Table | nrp | mdsnrp | timestamp, queryTenantName |
