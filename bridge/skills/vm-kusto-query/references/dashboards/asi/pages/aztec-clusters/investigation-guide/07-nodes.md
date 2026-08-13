# Nodes

> Source: **Aztec — Clusters** dashboard, chapter **Nodes** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Nodes

### Cluster Nodes

_Widget purpose:_ Nodes

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Nodes > Nodes`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where Tenant == queryCluster
| summarize LastSeen = arg_max(PreciseTimeStamp, *) by nodeId
| project LastSeen, nodeId, nodeState, nodeAvailabilityState, ipAddress, dedicatedNodeGroupName
```

**Params:** `{queryCluster}`

---
