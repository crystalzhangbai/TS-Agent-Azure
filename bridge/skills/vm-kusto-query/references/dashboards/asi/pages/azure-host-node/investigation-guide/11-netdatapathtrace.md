# NetDatapathTrace

> Source: **Azure Host — Azure Host Node** dashboard, chapter **NetDatapathTrace** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### NetDatapathTrace Query

Cluster: `azurehn.kusto.windows.net` · Database: `Azurehn` · Type: `Table`
Source panel: `NetDatapathTrace`

```kusto
NetDatapathTrace
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId
| project LogTimestamp, LogLevel, Message
| sort by LogTimestamp
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---
