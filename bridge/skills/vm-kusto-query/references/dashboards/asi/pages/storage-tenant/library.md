# Storage Tools — Storage Tenant: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:54:44.281Z.
> Total: 5 unique KQL queries across 4 panels (5 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Storage Tenant" | ResourceGet | xstore.westcentralus | xstore | local_Tenant, globalFrom, globalTo |

### Account Limits Overwrite
Path: `Account Limits Overwrite`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | List Account Limits Overwrite by Tenant | Table | https://xdeployment.westcentralus | Deployment | queryFrom, queryTo, tenant |

### Pages - Storage Tools
Path: `Pages - Storage Tools`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant Info by Account | Single | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |
| 2 | TrimStorageName | Single | xstore.westcentralus | xstore | local_StorageNameName |

### STG OS Deployment History
Path: `STG OS Deployment History`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant STGOS Deployment History | Table | xstore.westcentralus | xstore | queryFrom, queryTo, tenant |
