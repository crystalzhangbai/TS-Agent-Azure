# Anvil Resource Events

> Source: **Unhealthy Node Analysis - Unhealthy Helper** dashboard, chapter **Anvil Resource Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Anvil Resource Events

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`
Source panel: `Anvil Resource Events`

```kusto
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceResourceEvents
| where PreciseTimeStamp between (st ..et ) and resourceId == nId
| project PreciseTimeStamp, message
| sort by PreciseTimeStamp asc
```

**Params:** `{st}`, `{et}`, `{nId}`

---
