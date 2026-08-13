# Related Activity Ids

> Source: **Aztec Subscription Investigation Guide** dashboard, chapter **Related Activity Ids** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Subscription RelatedActivityId List

_Widget purpose:_ Related Activity Ids

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Related Activity Ids`

```kusto
let operationIds=cluster('azcrp').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between (local_startDate..local_endDate)
| where subscriptionId =~ local_subscriptionId
| distinct operationId;
let RelatedActivityIds=CommonWebOperationStart
| where PreciseTimeStamp between (local_startDate..local_endDate)
| where RelatedActivityId in (operationIds)
| distinct RelatedActivityId;
cluster('azcrp').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between (local_startDate..local_endDate)
| where operationId in (RelatedActivityIds)
| project PreciseTimeStamp,RelatedActivityId=operationId,operationName,resourceGroupName,resourceName,resultCode,exceptionType
```

**Params:** `{local_subscriptionId}`, `{local_endDate}`, `{local_startDate}`

---
