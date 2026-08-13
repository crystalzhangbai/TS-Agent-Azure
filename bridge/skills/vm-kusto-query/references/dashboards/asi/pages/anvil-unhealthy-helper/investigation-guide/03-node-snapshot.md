# Node snapshot

> Source: **Unhealthy Node Analysis - Unhealthy Helper** dashboard, chapter **Node snapshot** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### LogNodeSnapshot Query

_Widget purpose:_ Node snapshot

Cluster: `hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `Node snapshot`

```kusto
cluster('hawkeyekustocluster.centralus.kusto.windows.net').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp between (st ..et ) and nodeId == nId
| project PreciseTimeStamp, nodeState, nodeAvailabilityState, aliveContainerCount, containerCount, isNodeBugCheckIsolated, isIsolated, isOffline, isMaintenanceOs, faultInfo
| sort by PreciseTimeStamp asc
```

**Params:** `{st}`, `{et}`, `{nId}`

---
