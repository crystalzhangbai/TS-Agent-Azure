# AsyncQoSEvents

> Source: **Customer Drilldown** dashboard, chapter **AsyncQoSEvents** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AsyncQoSEvents Subscription Component Query

_Widget purpose:_ AsyncQoSEvents

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`
Source panel: `AsyncQoSEvents`

```kusto
// AIB AsyncQOS
AsyncQoSEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionID == subID
| summarize
    callCount=todouble(count()),
    clientFailures=countif(resultType == 1),
    serverFailures=countif(resultType == 2),
    failures=countif(resultType != 0),
    failedSubs=dcountif(subscriptionID, resultType != 0)
    by operationName
| extend successRate = round((callCount - failures) * 100 / callCount, 2)
| project operationName, callCount, clientFailures, serverFailures, successRate, failedSubs
| order by successRate desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subID}`

---
