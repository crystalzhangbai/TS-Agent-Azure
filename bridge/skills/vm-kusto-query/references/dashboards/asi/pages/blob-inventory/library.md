# Storage Tools — Blob Inventory: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:54:48.679Z.
> Total: 6 unique KQL queries across 6 panels (7 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant Info by Account | Single | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |

### Account Rules Status & SLO
Path: `Account Rules Status & SLO`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Account Inventory Rules & SLO | Table | xstore.westcentralus | xstore | queryFrom, queryTo, storageAccountName, runID |

### Pages - Storage Tools
Path: `Pages - Storage Tools`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant Info by Account | Single | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |
| 2 | TrimStorageName | Single | xstore.westcentralus | xstore | local_StorageNameName |

### Recent Run
Path: `Recent Run`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Blob Inventory Task Run | Table | xstore.westcentralus | xstore | queryFrom, queryTo, storageAccountName, policyRunId |

### Rule Definition
Path: `Rule Definition`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Blob Inventory Rule Definition | Table | xstore.westcentralus | xstore | queryFrom, queryTo, storageAccountName, policyRunId |

### Scheduler Logs
Path: `Scheduler Logs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Blob Inventory Scheduler Logs | Table | https://xstore.westcentralus/ | xstore | queryFrom, queryTo, storageAccountName, runID |
