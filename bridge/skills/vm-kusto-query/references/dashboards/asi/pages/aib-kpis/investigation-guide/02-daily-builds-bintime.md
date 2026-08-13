# Daily Builds - {{ binTime }}

> Source: **AIB KPIs** dashboard, chapter **Daily Builds - {{ binTime }}** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Daily Build Success Rate

_Widget purpose:_ Daily Builds - {{ binTime }}

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `TimeSeries`
Source panel: `Daily Builds - {{ binTime }}`

```kusto
AsyncQoSEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
// | where not(IsAIBSubscription(subscriptionID))
| where iff(build != "", serviceBuild == build, true)
| summarize
    callCount=todouble(count()),
    clientFailures=countif(resultType == 1),
    serverFailures=countif(resultType == 2),
    // failures=countif(resultType != 0),
    failedSubs=dcountif(subscriptionID, resultType != 0)
    by bin(PreciseTimeStamp, binTime)
| extend successRate = round(((callCount - clientFailures - serverFailures) * 100 ) / (callCount - clientFailures), 2)
| project PreciseTimeStamp, successRate, clientFailures, serverFailures
```

**Params:** `{queryFrom}`, `{queryTo}`, `{binTime}`, `{build}`

---
