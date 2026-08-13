# Node Events

> Source: **Unhealthy Node Analysis - Node Recovery Detail** dashboard, chapter **Node Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Events

### Node events

_Widget purpose:_ Events

Cluster: `hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `Node Events > Events`

```kusto
cluster('hawkeyekustocluster.centralus.kusto.windows.net').database('AzureCM').TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp between (st ..et ) and NodeId == nId
| where Message !contains "[FCPEStateSync] "
| project PreciseTimeStamp, Message
| sort by PreciseTimeStamp asc
```

**Params:** `{st}`, `{et}`, `{nId}`

---
