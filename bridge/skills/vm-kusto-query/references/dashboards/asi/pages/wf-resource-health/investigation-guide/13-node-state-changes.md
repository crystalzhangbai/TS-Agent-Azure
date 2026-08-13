# Node State Changes

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **Node State Changes** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### TMMgmtNodeStateChangedEtwTable DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Node State Changes`

```kusto
TMMgmtNodeStateChangedEtwTable 
| where  BladeID =~ query_NodeId
| where PreciseTimeStamp >= query_BeginTime
| where PreciseTimeStamp <= query_EndTime 
| project PreciseTimeStamp, BladeID, OldState, NewState
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---
