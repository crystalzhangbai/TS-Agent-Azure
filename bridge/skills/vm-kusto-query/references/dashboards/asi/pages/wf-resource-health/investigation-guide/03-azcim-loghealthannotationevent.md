# AzCiM/LogHealthAnnotationEvent

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **AzCiM/LogHealthAnnotationEvent** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### LogContainerHealthSnapshot_RH_VMId_CM

_Widget purpose:_ AzCiM/LogHealthAnnotationEvent

Cluster: `Azurecm` · Database: `AzureCM` · Type: `Table` · Widget: `Tab`
Source panel: `AzCiM/LogHealthAnnotationEvent`

```kusto
union cluster('Azcim-centralus.centralus').database('AZCIM').AzTMHealthAnnotationEvent,LogHealthAnnotationEvent 
| where PreciseTimeStamp >= query_StartTime and PreciseTimeStamp <= query_EndTime
| where * contains query_VMId
| project-away TIMESTAMP, Role, Tid, SourceNamespace, SourceMoniker, NodeId, SourceVersion, CloudName, Region, DataCenterName, AvailabilityZone, RoleInstance 
| sort by PreciseTimeStamp asc
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_VMId}`

---

## Represents emitted annotations from Fabric for the Container Id shared

### LogHealthAnnotationEvent DS

_Widget purpose:_ Represents emitted annotations from Fabric for the Container Id shared

Cluster: `Azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `AzCiM/LogHealthAnnotationEvent > Represents emitted annotations from Fabric for the Container Id shared`

```kusto
union cluster('Azcim-centralus.centralus').database('AZCIM').AzTMHealthAnnotationEvent,LogHealthAnnotationEvent 
| where PreciseTimeStamp >= query_StartTime and PreciseTimeStamp <= query_EndTime and containerIdentifier == query_ContainerId  
| project-away TIMESTAMP, Role, Tid, SourceNamespace, SourceMoniker, NodeId, SourceVersion, CloudName, Region, DataCenterName, AvailabilityZone, RoleInstance | sort by PreciseTimeStamp asc
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_ContainerId}`

---
