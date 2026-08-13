# Storage Tools — Storage Account: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:54:44.276Z.
> Total: 12 unique KQL queries across 9 panels (12 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Storage Account" | ResourceGet | azcore.centralus | Xstore | local_StorageAccountName, globalFrom, globalTo |

### Account Limits & Usage (99% Percentile)
Path: `Account Limits & Usage (99% Percentile)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Account Limit | Table | azcore.centralus | Xstore | queryFrom, queryTo, accountName |

### Account Usage Metrics (Beta)
Path: `Account Usage Metrics (Beta)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Usage Metrics | TimeSeries | azcore.centralus | Xstore | queryFrom, queryTo, accountName, usageType, tenant |

### ASI Pages > Pages - Storage Tools
Path: `ASI Pages > Pages - Storage Tools`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant Info by Account | Single | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |
| 2 | TrimStorageName | Single | xstore.westcentralus | xstore | local_StorageNameName |

### DGrep Links > DGrep Links
Path: `DGrep Links > DGrep Links`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant RSRP name | Single | xstore.westcentralus | xstore | queryFrom, queryTo, tenant |
| 2 | Storage_Regions | Single | azcore.centralus | Xstore | location_withoutSpace |

### MDM Dashboards > MDM Dashboards
Path: `MDM Dashboards > MDM Dashboards`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Account Tenant Info | Single | xstore.westcentralus | xstore | queryFrom, queryTo, tenant |
| 2 | UnixTimeFormat_Converter | Single | azcore.centralus | Xstore | queryFrom, queryTo |

### Regional Account Distribution
Path: `Regional Account Distribution`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Regional Accounts Distribution | Table | https://xdeployment.westcentralus | Deployment | queryFrom, queryTo, accountName |

### Transactions by Request Type
Path: `Transactions by Request Type`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Storage Account Transactions By RequestType | CategoryChart | xstore.westcentralus | xdataanalytics | queryFrom, queryTo, accountName |

### User Guide
Path: `User Guide`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get_ServiceID | Single | azcore.centralus | Xstore | queryFrom, queryTo, queryServiceId |
