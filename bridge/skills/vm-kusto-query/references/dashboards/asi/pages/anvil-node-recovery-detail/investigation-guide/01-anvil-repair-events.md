# Anvil Repair Events

> Source: **Unhealthy Node Analysis - Node Recovery Detail** dashboard, chapter **Anvil Repair Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Anvil Repair events

_Widget purpose:_ Anvil Repair Events

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`
Source panel: `Anvil Repair Events`

```kusto
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (st ..et ) and ResourceDependencies contains nId
| project PreciseTimeStamp, TreeNodeKey, TreeActionName, Message, RequestIdentifier, Tenant
| where isnotempty(Message)
| sort by PreciseTimeStamp asc
```

**Params:** `{st}`, `{et}`, `{nId}`

---
