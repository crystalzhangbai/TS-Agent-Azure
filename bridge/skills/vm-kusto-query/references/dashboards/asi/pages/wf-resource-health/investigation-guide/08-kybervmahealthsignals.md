# KyberVMAHealthSignals

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **KyberVMAHealthSignals** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### KyberVMAHealthSignals

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`
Source panel: `KyberVMAHealthSignals`

```kusto
KyberVMAHealthSignals
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ContainerId == containerId
| project PreciseTimeStamp, ArmId, IcHeartbeat, PowerState, HyperVHandshake, VscState, EventType, isDegraded, hasMigrated
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
