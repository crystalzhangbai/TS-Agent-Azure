# NodeService — Cumulus Tip Node Session: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:12:40.047Z.
> Total: 4 unique KQL queries across 2 panels (4 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Cumulus Tip Node Session" | ResourceGet | azcore.centralus | AutopilotDeployment | globalFrom, globalTo, local_tipNodeSessionId |
| 2 | Generate Node View Links | Single | ? | ? | row |
| 3 | ServiceManagerSysLog | Table | azcore.centralus | AutopilotDeployment | _tipNodeSessionId |

### GARSLog
Path: `GARSLog`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GARSLog | Table | azcore.centralus | AutopilotDeployment | _tipNodeSessionId |
