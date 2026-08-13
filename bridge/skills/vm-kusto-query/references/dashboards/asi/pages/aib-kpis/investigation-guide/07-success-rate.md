# Success Rate

> Source: **AIB KPIs** dashboard, chapter **Success Rate** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Overall Success Rate

_Widget purpose:_ Success Rate

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `DataSummary`
Source panel: `Success Rate`

```kusto
// Overall Success Rate for Time Period
AsyncQoSEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
// | where not(IsAIBSubscription(subscriptionID))
| summarize
    callCount=todouble(count()),
    clientFailures=countif(resultType == 1),
    serverFailures=countif(resultType == 2),
    failedSubs=dcountif(subscriptionID, resultType != 0)
| extend successRate = round(((callCount - clientFailures - serverFailures) * 100 ) / (callCount - clientFailures), 2)
| extend Value = tostring(successRate)
// | project Value
| extend Health = case(successRate > 99, "Healthy", successRate > 98, "Neutral", successRate > 97, "Degraded", "Unhealthy")
// | extend Description = "Health over time period"
```

**Params:** `{queryFrom}`, `{queryTo}`

---
