# Server Failures

> Source: **Subscriptions with Failures** dashboard, chapter **Server Failures** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Subscriptions With Failures

_Widget purpose:_ Server Failures

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`
Source panel: `Server Failures`

```kusto
AsyncQoSEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where not(IsAIBSubscription(subscriptionID))
| where resultType == 2
| where iff(searchOperation != "", operationName == searchOperation, false)
| summarize Failures=count() by subscriptionID, operationName
| order by Failures desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{searchOperation}`

---
