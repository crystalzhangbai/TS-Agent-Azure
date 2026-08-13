# Host Resource Manager — NodeId: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:27:08.405Z.
> Total: 3 unique KQL queries across 1 panels (3 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "NodeId" | ResourceGet | wdgeventstore | KernelAgent | globalFrom, globalTo, local_NodeId |
| 2 | HRM snapshots | Timeline | wdgeventstore | KernelAgent | queryFrom, queryTo, nodeId |
| 3 | Entries for HRM snapshot | Table | wdgeventstore | KernelAgent | queryFrom, queryTo, nodeId, snapshotId |
