# (top-level)

> Source: **Recovery Services Vaults - Private Endpoint** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ResourceIdforRSV

Cluster: `mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `Table`

```kusto
RegionalRPResourceAll
| where ResourceName =~ RSVName
| where SubscriptionId == RSVSubscriptionId
| where TIMESTAMP > StartTime and TIMESTAMP < EndTime
| where iff(isempty( RSVDeploymentName), true, DeploymentName== RSVDeploymentName)
| distinct tostring(ResourceId)
```

**Params:** `{RSVSubscriptionId}`, `{RSVName}`, `{RSVDeploymentName}`, `{StartTime}`, `{EndTime}`

---

### PEForResourceId

Cluster: `mabprod1.kusto.windows.net` · Database: `MABKustoProd1` · Type: `MultiRow` · Widget: `Table`

```kusto
RegionalRPResourceAll
| where ResourceName contains RSVName
| where TIMESTAMP > StartTime and TIMESTAMP < EndTime
| project TIMESTAMP, PrivateEndpointConnectionsBlobUri, tostring(ResourceId)
| where isempty(PrivateEndpointConnectionsBlobUri) == false and PrivateEndpointConnectionsBlobUri != "null" and PrivateEndpointConnectionsBlobUri != "[]"
| parse PrivateEndpointConnectionsBlobUri with *'/privateEndpoints/'PEName'"'*
| parse PrivateEndpointConnectionsBlobUri with *'groupIds":'GroupIds","*
| project TIMESTAMP, PEName, GroupIds, PrivateEndpointConnectionsBlobUri, tostring(ResourceId)
| summarize arg_min(TIMESTAMP, PEName, GroupIds) by PEName, GroupIds, tostring(ResourceId)
| project TIMESTAMP, PEName , GroupIds, tostring(ResourceId)
```

**Params:** `{RSVSubscriptionId}`, `{RSVDeploymentName}`, `{RSVName}`, `{StartTime}`, `{EndTime}`

---
