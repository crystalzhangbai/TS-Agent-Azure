# KyberCoreServiceTrace

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **KyberCoreServiceTrace** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### KyberCoreServiceTrace

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `Aplat` · Type: `Table`
Source panel: `KyberCoreServiceTrace`

```kusto
KyberCoreServiceTrace
| where PreciseTimeStamp > queryFrom and PreciseTimeStamp < queryTo
| where Message contains query_ContainerId
| project PreciseTimeStamp, Message, ServiceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_ContainerId}`

---
