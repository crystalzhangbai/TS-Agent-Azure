# Subscription Lock Summary

> Source: **NRP - Nrp Performance Drilldown** dashboard, chapter **Subscription Lock Summary** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Subscription Lock Durations

### Subscription Lock Durations

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Subscription Lock Summary > Subscription Lock Durations`

```kusto
cluster('nrp').database('mdsnrp').FrontendOperationEtwEvent 
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where Region == region
| where SubscriptionId == subscriptionId
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| where EventCode == "LockReleased"
| parse Message with * "Operation "fullOpName" ("opId")"" released lock "lockResource" after "lockDuration" ms, refCount: "refcount
| project lockResource, lockDuration, PreciseTimeStamp, OperationId, SubscriptionId, OperationName
| where lockResource == SubscriptionId
| summarize count(), percentiles(toint(lockDuration), 50, 75, 99, 99.9,  100) by OperationName
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `EventCode == "LockReleased"`

---
