# FrontEndQos

> Source: **AIB KPIs** dashboard, chapter **FrontEndQos** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AIB FrontEndQOS Failures

_Widget purpose:_ FrontEndQos

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`
Source panel: `FrontEndQos`

```kusto
// AIB FrontEndQos
FrontEndQoSEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
// | where not(IsAIBSubscription(subscriptionID))
| summarize
    callCount=todouble(count()),
    clientFailures=countif(resultType == 1),
    serverFailures=countif(resultType == 2),
    failures=countif(resultType != 0)
    by operationName
| extend successRate = round(((callCount - clientFailures - serverFailures) * 100 ) / (callCount - clientFailures), 3)
| project operationName, callCount, clientFailures, serverFailures, successRate
| order by successRate desc
| extend level = case(successRate == 100, "info", successRate > 99.5, "warning", successRate > 99, "error", "fatal")
```

**Params:** `{queryFrom}`, `{queryTo}`

---
