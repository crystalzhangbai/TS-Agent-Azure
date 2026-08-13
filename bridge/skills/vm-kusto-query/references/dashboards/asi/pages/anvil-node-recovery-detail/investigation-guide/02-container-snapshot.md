# Container Snapshot

> Source: **Unhealthy Node Analysis - Node Recovery Detail** dashboard, chapter **Container Snapshot** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Container Snapshot

Cluster: `hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `Container Snapshot`

```kusto
cluster('hawkeyekustocluster.centralus.kusto.windows.net').database('AzureCM').LogContainerHealthSnapshot
| where PreciseTimeStamp between (st ..et ) and nodeId == nId
| summarize arg_max(PreciseTimeStamp, *) by containerId
| project PreciseTimeStamp, Tenant, containerId, nodeId, tenantName, roleInstanceName, virtualMachineUniqueId, containerState, containerOsState, containerLifecycleState, containerIsolationState, actualOperationalState
| join kind=inner (cluster('hawkeyekustocluster.centralus.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (st ..et ) and nodeId == nId
| summarize arg_max(PreciseTimeStamp, *) by containerId
| project containerId, nodeId, subscriptionId, priority, containerType) on containerId, nodeId
| project PreciseTimeStamp, containerId, nodeId, roleInstanceName, subscriptionId, priority, containerType, containerState, containerOsState, containerLifecycleState, containerIsolationState, actualOperationalState
```

**Params:** `{st}`, `{et}`, `{nId}`

---
