# Aztec — Nodes: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T11:19:29.766Z.
> Total: 13 unique KQL queries across 6 panels (13 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 8

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Nodes" | ResourceGet | azurecm | AzureCM | local_nodeId, globalFrom, globalTo |
| 2 | Node Flags | FeatureList | azurecm | AzureCM | queryNodeId |
| 3 | Node Hosting Environment | Table | azurecm | azurecm | queryNodeId |
| 4 | Node State | Timeline | azurecm | AzureCM | queryNodeId |
| 5 | Node Availability State | Timeline | azurecm | AzureCM | queryNodeId |
| 6 | Node OS Image | Timeline | azurecm | AzureCM | queryNodeId |
| 7 | Node Disk Configuration | Timeline | azurecm | AzureCM | queryNodeId |
| 8 | Node VMA | Timeline | vmainsight | vmadb | queryNodeId |

### Containers > Containers > Container Time Series
Path: `Containers > Containers > Container Time Series`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node container counts | TimeSeries | azurecm | AzureCM | qFrom, qTo, qNodeId |

### Containers > Containers > Container Timeline
Path: `Containers > Containers > Container Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Host Node Container Timeline | Timeline | azcore.centralus | AzureCP | qFrom, qTo, qHostNode |

### Containers > Table View > Containers
Path: `Containers > Table View > Containers`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Containers | Table | azurecm | AzureCM | queryNodeId |

### Disk Health > Disk Health Status
Path: `Disk Health > Disk Health Status`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node Disk Health | TimeSeries | azcore.centralus | Fa | queryNodeId |

### High CPU > High CPU
Path: `High CPU > High CPU`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Node High CPU | TimeSeries | azcore.centralus | Fa | queryNodeId |
