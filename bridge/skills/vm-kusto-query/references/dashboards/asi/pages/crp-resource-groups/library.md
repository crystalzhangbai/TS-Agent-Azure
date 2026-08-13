# CRP — Resource Groups: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T10:18:20.626Z.
> Total: 3 unique KQL queries across 3 panels (3 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Resource Groups" | ResourceGet | azcrp | crp_allprod | local_subscriptionId, local_resourceGroupName |

### VMs > VMs
Path: `VMs > VMs`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Resource Group VMs | Table | azcrp | crp_allprod | local_subscriptionId, local_resourceGroup |

### VMSS > Scale Sets
Path: `VMSS > Scale Sets`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Resource Group Scale Sets | Table | azcrpbifollower | bi_allprod | querySubscriptionId, queryResourceGroup, queryFrom, queryTo |
