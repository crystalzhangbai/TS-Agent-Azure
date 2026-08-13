# Network Manager — VIP Search: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:12:40.072Z.
> Total: 10 unique KQL queries across 1 panels (10 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 10

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "VIP Search" | ResourceGet | aznwsdn | nsmplus | local_PreciseTimeStamp, local_TenantName, local_publicIPAddress, local_Tenant |
| 2 | NsmQosOps | CoBeTimeline | azurecm | AzureCM | timestamp, queryTenantName |
| 3 | GetResourceGroup | Single | azcrp | crp_allprod | timestamp, queryTenantName |
| 4 | VIP State | Timeline | azurecm | AzureCM | queryPublicIpAddress, queryTenant, queryFrom, queryTo |
| 5 | RNMRequest | Table | aznwsdn | aznwmds | timestamp, queryTenantName, queryRegion |
| 6 | VipLifeCycle | Table | aznwsdn | aznwmds | timestamp, queryVip, queryRegion |
| 7 | VipOwnershipSnapshot | Table | aznwsdn | aznwmds | timestamp, queryVip, queryRegion |
| 8 | RNM ResourceRelease | Table | aznwsdn | aznwmds | timestamp, queryRegion, queryTenantName |
| 9 | Frontend | Table | nrp | mdsnrp | timestamp, queryTenantName |
| 10 | NsmPlusVipGS | Table | aznwsdn | nsmplus | timestamp, queryVip, queryRegion |
