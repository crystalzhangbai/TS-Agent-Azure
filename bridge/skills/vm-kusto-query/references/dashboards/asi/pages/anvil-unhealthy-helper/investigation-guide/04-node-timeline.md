# Node Timeline

> Source: **Unhealthy Node Analysis - Unhealthy Helper** dashboard, chapter **Node Timeline** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Node Snapshot timeline

_Widget purpose:_ Node Timeline

Cluster: `hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Node Timeline`

```kusto
cluster('hawkeyekustocluster.centralus.kusto.windows.net').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp between (st ..et ) and nodeId == nId
| summarize arg_max(PreciseTimeStamp, *), StartTime = min(PreciseTimeStamp) by nodeState, lastStateChangeTime
| project StartTime, EndTime = PreciseTimeStamp, Content = nodeState, ToolTip = tostring(bag_pack_columns(containerCount, faultInfo)), GroupBy = nodeAvailabilityState
```

**Params:** `{st}`, `{et}`, `{nId}`

---
