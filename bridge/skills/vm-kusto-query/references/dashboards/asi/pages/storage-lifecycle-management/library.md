# Storage Tools — Life Cycle Managment: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:54:41.451Z.
> Total: 9 unique KQL queries across 9 panels (10 widget refs).

## Page inputs (URL params)


## Panels

### Aggregated LCM Account Policy Execution Summary (Below number of Rows)
Path: `Aggregated LCM Account Policy Execution Summary (Below number of Rows)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Aggregate Account LCM run result | Table | xstore.westcentralus | xstore | queryFrom, queryTo, storageAccountName |

### LCM Account Policy Execution Stats
Path: `LCM Account Policy Execution Stats`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LCM Account Policy Execution Stats | Table | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |

### LCM Long Running Tasks
Path: `LCM Long Running Tasks`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | LCM Long Running Task Stats | Table | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |

### LCM Policy
Path: `LCM Policy`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get LCM policy definition | Table | https://xstore.westcentralus/ | xstore | queryFrom, queryTo, storageAccountName |

### LCM Scheduler Actions
Path: `LCM Scheduler Actions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Aggregate LCM Scheduler Actions | Table | xstore.westcentralus | xstore | queryFrom, queryTo, storageAccountName |

### LCM Task Execution Details 
Path: `LCM Task Execution Details `  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Aggregate LCM Tasks | Table | xstore.westcentralus | xstore | queryFrom, queryTo, storageAccountName |

### LCM Transactions Summary
Path: `LCM Transactions Summary`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get LCM Transactions | Table | xstore.westcentralus | xdataanalytics | queryFrom, queryTo, storageAccountName |

### Quick Links
Path: `Quick Links`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant Info by Account | Single | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |

### Quick Links > Pages - Storage Tools
Path: `Quick Links > Pages - Storage Tools`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant Info by Account | Single | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |
| 2 | TrimStorageName | Single | xstore.westcentralus | xstore | local_StorageNameName |
