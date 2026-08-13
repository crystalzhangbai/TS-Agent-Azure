# Low KPIs ( < 99 )

> Source: **AIB KPIs** dashboard, chapter **Low KPIs ( < 99 )** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Operation Warnings

_Widget purpose:_ Low KPIs ( < 99 )

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `MultiRow` · Widget: `ForEach`
Source panel: `Low KPIs ( < 99 )`

```kusto
// AIB Issue Detector
AsyncQoSEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| summarize
    callCount=todouble(count()),
    clientFailures=countif(resultType == 1),
    serverFailures=countif(resultType == 2),
    failures=countif(resultType != 0),
    // failedSubs=dcountif(subscriptionID, resultType != 0)
    failedSubs = dcountif(subscriptionID, resultType == 2)
    by operationName
| extend successRate = round(((callCount - clientFailures - serverFailures) * 100 ) / (callCount - clientFailures), 3)
| order by successRate asc  
| where successRate < 99
```

**Params:** `{queryFrom}`, `{queryTo}`

---
