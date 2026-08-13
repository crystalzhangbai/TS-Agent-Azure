# SOC Details

> Source: **Azure Host — Azure Host Node** dashboard, chapter **SOC Details** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## NDPA

### NetDatapathPerfCounters Query

_Widget purpose:_ NDPA

Cluster: `azurehn.kusto.windows.net` · Database: `Azurehn` · Type: `Table`
Source panel: `SOC Details > NDPA`

```kusto
NetDatapathPerfCounters 
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and Operation endswith "Version"
| summarize arg_max(LogTimestamp, CounterName, CounterValue) by ComponentName, Operation
| project LogTimestamp, ComponentName, Operation, CounterValue
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---
