# ACC — Confidential Virtual Machines: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:27:08.327Z.
> Total: 3 unique KQL queries across 1 panels (3 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Virtual Machines" | ResourceGet | azurecm | AzureCM | local_subscriptionId, local_virtualMachineUniqueId |
| 2 | VM Containers | Timeline | azurecm | AzureCM | queryVmId |
| 3 | VMA | Timeline | vmainsight | vmadb | queryVmOrContainerId, queryTenantName, global_startTime, global_endTime |
