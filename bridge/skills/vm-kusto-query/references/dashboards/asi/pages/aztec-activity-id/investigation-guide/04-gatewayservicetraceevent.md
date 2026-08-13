# GatewayServiceTraceEvent

> Source: **Aztec ActivityId Investigation Guide** dashboard, chapter **GatewayServiceTraceEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## GatewayServiceTraceEvent

### ActivityId GatewayServiceTraceEvent

_Widget purpose:_ GatewayServiceTraceEvent

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `GatewayServiceTraceEvent > GatewayServiceTraceEvent`

```kusto
GatewayServiceTraceEvent
| where PreciseTimeStamp between ((local_startDate - 6h) .. (local_endDate + 6h))
| where ActivityId =~ local_ActivityId
| project PreciseTimeStamp,level,message
| order by PreciseTimeStamp desc
```

**Params:** `{local_ActivityId}`, `{local_endDate}`, `{local_startDate}`

---
