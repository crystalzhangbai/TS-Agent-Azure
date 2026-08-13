# Container Health Snapshots

> Source: **Container** dashboard, chapter **Container Health Snapshots** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Container Health Snapshot

_Widget purpose:_ Container Health Snapshots

Cluster: `mycroft.westcentralus.kusto.windows.net` · Database: `Mycroft` · Type: `Table`
Source panel: `Container Health Snapshots`

```kusto
MycroftContainerHealthSnapshot
| where ContainerId == queryContainerId
| top 1000 by TIMESTAMP desc
| project-reorder TIMESTAMP, RoleInstanceName, OsState, IsolationState, LifecycleState, ActualOperationalState, 
    FaultInfo, LifecycleStateChangeTime, ContainerId, NodeId, Tenant
| project-away TIMESTAMP, Pid, Tid, ActivityId, Version, SourceNamespace, SourceMoniker, SourceVersion, 
    __AuthType__, __AuthIdentity__
| extend NodeIdTrunc = strcat(substring(NodeId, 0, 8), '...')
| extend ContainerIdTrunc = strcat(substring(ContainerId, 0, 8), '...')
```

**Params:** `{queryContainerId}`

---
