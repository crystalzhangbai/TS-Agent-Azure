# CMWorkerNodeServiceChannel failures

> Source: **NodeService - NodeService_NodeView** dashboard, chapter **CMWorkerNodeServiceChannel failures** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### CMWorkerNodeServiceChannel failures

Cluster: `https://hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `CMWorkerNodeServiceChannel failures`

```kusto
CMWorkerNodeServiceChannelFailure
| where NodeId == queryNode  and PreciseTimeStamp between ((faultTime - 3h)..4h)
| project PreciseTimeStamp, Message
```

**Params:** `{queryNode}`, `{faultTime}`

---
