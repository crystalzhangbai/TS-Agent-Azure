# Node Snapshot Table

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **Node Snapshot Table** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### LogNodeSnapshot

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Node Snapshot Table`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp >= query_BeginTime and nodeId == query_NodeId
| project PreciseTimeStamp,nodeId,nodeState,nodeAvailabilityState,containerCount,diskConfiguration,faultInfo,rootUpdateAllocationType,cmNodeChannelAggregatedHealthStatus,isIsolated
```

**Params:** `{query_BeginTime}`, `{query_NodeId}`

---
