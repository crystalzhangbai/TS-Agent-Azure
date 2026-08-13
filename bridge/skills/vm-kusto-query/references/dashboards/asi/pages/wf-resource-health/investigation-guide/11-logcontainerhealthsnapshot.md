# LogContainerHealthSnapshot

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **LogContainerHealthSnapshot** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### LogContainerHealthSnapshot_RH_VMId_CM

_Widget purpose:_ LogContainerHealthSnapshot

Cluster: `Azurecm` · Database: `AzureCM` · Type: `Table` · Widget: `Tab`
Source panel: `LogContainerHealthSnapshot`

```kusto
union cluster('Azcim-centralus.centralus').database('AZCIM').AzTMHealthAnnotationEvent,LogHealthAnnotationEvent 
| where PreciseTimeStamp >= query_StartTime and PreciseTimeStamp <= query_EndTime
| where * contains query_VMId
| project-away TIMESTAMP, Role, Tid, SourceNamespace, SourceMoniker, NodeId, SourceVersion, CloudName, Region, DataCenterName, AvailabilityZone, RoleInstance 
| sort by PreciseTimeStamp asc
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_VMId}`

---

### LogContainerHealthSnapshot_ResourceHealth DS

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `LogContainerHealthSnapshot`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp > query_StartTime
| where PreciseTimeStamp < query_EndTime
| where containerId == query_ContainerId
| project PreciseTimeStamp,  roleInstanceName ,  Tenant, containerId , nodeId,  containerState, actualOperationalState, containerLifecycleState, vmExpectedHealthState, faultInfo, containerIsolationState, containerOsState   
| order by PreciseTimeStamp asc
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_ContainerId}`

---
