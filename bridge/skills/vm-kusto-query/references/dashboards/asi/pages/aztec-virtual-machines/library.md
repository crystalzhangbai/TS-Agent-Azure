# Aztec — Virtual Machines: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T11:19:32.190Z.
> Total: 7 unique KQL queries across 2 panels (7 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 6

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Virtual Machines" | ResourceGet | azurecm | AzureCM | local_virtualMachineUniqueId |
| 2 | MDM Shoebox Region | Single | AzureCM | AzureCM | queryVmRegion |
| 3 | VM Containers | Timeline | azcore.centralus | AzureCP | qVmId, qFrom, qTo |
| 4 | Container VMA | Timeline | azcore.centralus | AzureCP | qFrom, qTo, qVM |
| 5 | Air VMA | Timeline | vmainsight | Air | queryVmId |
| 6 | VM Hosts | Timeline | azcore.centralus | AzureCP | qFrom, qTo, qVmId |

### Containers > Containers
Path: `Containers > Containers`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Virtual Machine Containers Table | Table | azurecm | AzureCM | queryVmId |
