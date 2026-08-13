# ARM Traces

> Source: **CRP Resource Move Investigation Guide** dashboard, chapter **ARM Traces** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ARM Traces

### ARM Trace

_Widget purpose:_ ARM Traces

Cluster: `armprod` · Database: `ARMProd` · Type: `Table`
Source panel: `ARM Traces > ARM Traces`

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').Traces
| where PreciseTimeStamp between (starttime .. endtime)
| where correlationId == correlationid
| project PreciseTimeStamp, Level, RoleInstance, ActivityId, subscriptionId, correlationId, operationName, message, exception, tenantId
| project PreciseTimeStamp, Level, operationName, message, exception
```

**Params:** `{starttime}`, `{endtime}`, `{correlationid}`

---
