# Storage Tools — Billing Drilldown: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:54:47.530Z.
> Total: 5 unique KQL queries across 5 panels (6 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant Info by Account | Single | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |

### Account Billing Daily
Path: `Account Billing Daily`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | List Account Billing Daily | Table | xstore.westcentralus | xdataanalytics | queryFrom, queryTo, storageAccountName, meterId |

### Billable Transactions, Ingress & Egress
Path: `Billable Transactions, Ingress & Egress`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Account Billable Transactions | TimeSeries | xstore.westcentralus | xdataanalytics | queryFrom, queryTo, storageAccountName |

### Pages - Storage Tools
Path: `Pages - Storage Tools`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Tenant Info by Account | Single | xstore.westcentralus | xstore | queryFrom, queryTo, accountName |
| 2 | TrimStorageName | Single | xstore.westcentralus | xstore | local_StorageNameName |

### Sum of the total Transaction, Ingress & Egress
Path: `Sum of the total Transaction, Ingress & Egress`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Sum of total Transaction, Ingress & Egress | Table | xstore.westcentralus | xdataanalytics | queryFrom, queryTo, storageAccountName |
