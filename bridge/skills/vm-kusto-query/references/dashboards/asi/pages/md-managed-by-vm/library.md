# Managed Disk — Managed by VM: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:27:08.035Z.
> Total: 2 unique KQL queries across 2 panels (2 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Managed by VM" | ResourceGet | AzureCM | AzureCM | local_cluster, local_containerid, local_nodeid, local_Region, local_roleInstanceName, local_subscriptionId, local_tenantname, local_vmid, globalFrom, globalTo |

### Disks from CRP BI
Path: `Disks from CRP BI`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | VMManagedDisksAllocationInfo | Table | Azcrpbifollower | bi_allprod | queryFrom, queryTo, queryVMId |
