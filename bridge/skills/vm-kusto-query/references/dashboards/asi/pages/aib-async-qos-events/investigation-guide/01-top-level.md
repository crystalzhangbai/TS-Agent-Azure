# (top-level)

> Source: **AsyncQoSEvents by Operation** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AsyncQoSEvents Search by operationName

_Widget purpose:_ AsyncQoSEvents

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
AsyncQoSEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where operationName == Operation
| where Result == "" or result == Result
| where iff(resultTypeFilter != "", resultType == resultTypeFilter, true)
| project PreciseTimeStamp, correlationID, operationID, level, result, resultType, serviceBuild, errorDetails, subscriptionID
| where iff(subscription != "", subscriptionID == subscription, true)
| take 1000
```

**Params:** `{queryFrom}`, `{queryTo}`, `{Operation}`, `{Result}`, `{subscription}`, `{resultTypeFilter}`

---
