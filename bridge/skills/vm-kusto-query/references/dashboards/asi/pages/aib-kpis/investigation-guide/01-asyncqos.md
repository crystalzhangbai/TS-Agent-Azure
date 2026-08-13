# AsyncQos

> Source: **AIB KPIs** dashboard, chapter **AsyncQos** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Improved AsyncQoS

_Widget purpose:_ AsyncQos

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`
Source panel: `AsyncQos`

```kusto
let KPiWithTriggers =
    AsyncQoSEvents
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    // | where not(IsAIBSubscription(subscriptionID))
    | summarize
        callCount=count(),
        clientFailures=countif(resultType == 1),
        serverFailures=countif(resultType == 2),
        failedSubs = dcountif(subscriptionID, resultType == 2)
        by operationName
    | extend
        successRate = round((callCount - clientFailures - serverFailures) * 100.0 / (callCount - clientFailures), 3),
        operationName
    | sort by successRate asc
    | project
        operationName,
        callCount,
        clientFailures,
        serverFailures,
        successRate,
        failedSubs;
let KPiWithoutTriggers =
    AsyncQoSEvents
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    // | where not(IsAIBSubscription(subscriptionID))
    | where operationName startswith "POST"
    | where subResourceName == ""
    | summarize
        callCount=count(),
        clientFailures=countif(resultType == 1),
        serverFailures=countif(resultType == 2),
        failedSubs = dcountif(subscriptionID, resultType == 2)
        by operationName
    | extend
        successRate = round((callCount - clientFailures - serverFailures) * 100.0 / (callCount - clientFailures), 3),
        operationName = "PostRunTemplateHandler.POST (without triggers)"
    | project
        operationName,
        callCount,
        clientFailures,
        serverFailures,
        successRate,
        failedSubs;
KPiWithTriggers
| union KPiWithoutTriggers
| order by successRate desc
| extend level = case(successRate == 100, "info", successRate > 99.5, "warning", successRate > 99, "error", "fatal")
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `operationName startswith "POST"`

---
