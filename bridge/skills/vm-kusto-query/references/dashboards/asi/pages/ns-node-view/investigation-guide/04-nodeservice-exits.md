# NodeService Exits

> Source: **NodeService - NodeService_NodeView** dashboard, chapter **NodeService Exits** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### NodeService Exits

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `NodeService Exits`

```kusto
NodeServiceExitEtwTable
| where PreciseTimeStamp between ((faultTime - 3h)..4h)
| where NodeId == queryNode
| project PreciseTimeStamp, ExitCode, Pid
```

**Params:** `{queryNode}`, `{faultTime}`

---
