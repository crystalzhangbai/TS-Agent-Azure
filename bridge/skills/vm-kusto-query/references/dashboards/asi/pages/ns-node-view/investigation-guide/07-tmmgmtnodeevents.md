# TMMgmtNodeEvents

> Source: **NodeService - NodeService_NodeView** dashboard, chapter **TMMgmtNodeEvents** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### TMMgmtNodeEventsTable

_Widget purpose:_ TMMgmtNodeEvents

Cluster: `https://hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `TMMgmtNodeEvents`

```kusto
TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp between ((faultTime - 3h)..(3h + 1min))
| where NodeId == queryNode
| project PreciseTimeStamp, Message, Pid
| top 500 by PreciseTimeStamp desc
| order by PreciseTimeStamp asc
```

**Params:** `{queryNode}`, `{faultTime}`

---
