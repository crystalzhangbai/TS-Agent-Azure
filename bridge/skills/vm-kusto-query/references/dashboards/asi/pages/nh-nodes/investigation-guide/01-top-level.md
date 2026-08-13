# (top-level)

> Source: **Node Heartbeat - Nodes** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Nodes"

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp > ago(2h)
| where nodeId == local_NodeId
| summarize arg_max(PreciseTimeStamp, State=nodeState, Availability=nodeAvailabilityState) by NodeId = nodeId
```

**Params:** `{local_NodeId}`

---
