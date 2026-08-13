# Storage Tools — Control Plane Dashboard: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:54:41.134Z.
> Total: 5 unique KQL queries across 5 panels (6 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant Info by Account | Single | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |

### ARM Operations
Path: `ARM Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get account ARM requests | Table | https://armprodgbl.eastus/ | ARMProd | queryFrom, queryTo, accountName, subID, corrID, isNoGet |

### Pages - Storage Tools
Path: `Pages - Storage Tools`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant Info by Account | Single | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |
| 2 | TrimStorageName | Single | xstore.westcentralus | xstore | local_StorageNameName |

### SRP Operations
Path: `SRP Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | List SRP Operations  | Table | https://xstorepartners/ | SRP | queryFrom, queryTo, accountName, subID, corrID, isNoGet |

### SRP Throttling Detector
Path: `SRP Throttling Detector`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Detect SRP throttling Errors | IssueDetector | https://xstorepartners/ | SRP | queryFrom, queryTo, accountName |
