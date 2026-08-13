# RhcAnnotationReportsEtwTable

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **RhcAnnotationReportsEtwTable** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Represents emitted annotations from HostAgent

### RhcAnnotationReportsEtwTable DS

_Widget purpose:_ Represents emitted annotations from HostAgent

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `RhcAnnotationReportsEtwTable > Represents emitted annotations from HostAgent`

```kusto
RhcAnnotationReportsEtwTable
| where VmId == query_VmId
| where PreciseTimeStamp >= query_StartTime and PreciseTimeStamp <= query_EndTime
| project PreciseTimeStamp, Annotation, VmId, ContainerId, NodeId
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_VmId}`

---
