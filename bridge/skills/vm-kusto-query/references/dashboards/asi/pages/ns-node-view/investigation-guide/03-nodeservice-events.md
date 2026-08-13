# NodeService Events

> Source: **NodeService - NodeService_NodeView** dashboard, chapter **NodeService Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### NodeService Events

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `NodeService Events`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp between ((faultTime - 45m)..1h)
| where NodeId == queryNode
| project TIMESTAMP, Message, Pid
| order by TIMESTAMP asc
```

**Params:** `{queryNode}`, `{faultTime}`

---
