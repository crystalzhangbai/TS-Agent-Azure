# Success Rate by Request Type - {{binTime}}

> Source: **AIB KPIs** dashboard, chapter **Success Rate by Request Type - {{binTime}}** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Daily Build Success by Operation Type

_Widget purpose:_ Success Rate by Request Type - {{binTime}}

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `TimeSeries`
Source panel: `Success Rate by Request Type - {{binTime}}`

```kusto
AsyncQoSEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
// | where not(IsAIBSubscription(subscriptionID))
| extend requestType = extract("([A-Z]+)$", 1, operationName)
| summarize
    callCount=todouble(count()),
    clientFailures=countif(resultType == 1),
    serverFailures=countif(resultType == 2),
    failedSubs=dcountif(subscriptionID, resultType != 0)
    by bin(PreciseTimeStamp, binTime), requestType
| extend successRate = round(((callCount - clientFailures - serverFailures) * 100 ) / (callCount - clientFailures), 2)
| summarize
    POST_successRate = maxif(successRate, requestType == "POST"),
    PUT_successRate = maxif(successRate, requestType == "PUT"),
    DELETE_successRate = maxif(successRate, requestType == "DELETE"),
    clientFailures = sum(clientFailures),
    serverFailures = sum(serverFailures)
    by PreciseTimeStamp
| project PreciseTimeStamp, POST_successRate, PUT_successRate, DELETE_successRate, clientFailures, serverFailures
```

**Params:** `{queryFrom}`, `{queryTo}`, `{binTime}`

---
