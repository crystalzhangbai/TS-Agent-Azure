# NodeServiceEvents

> Source: **NodeService - NodeService_Peregrine** dashboard, chapter **NodeServiceEvents** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### NodeServiceEventsEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `NodeServiceEvents`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp between (queryFrom..queryTo)
| where ScopeIdentifier == containerId
| project PreciseTimeStamp, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
