# Allocation Activity

> Source: **Aztec RelatedActivityId Investigation Guide** dashboard, chapter **Allocation Activity** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Compute Allocation Activity

### Compute Allocation Activity - ActivityId

_Widget purpose:_ Compute Allocation Activity

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Allocation Activity > Compute Allocation Activity`

```kusto
let queryFrom = datetime_add("day", -1, queryOperationTime);
let queryTo = datetime_add("day", 1, queryOperationTime);
ComputeAllocationActivity
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where activityId == queryActivityId
| extend Message = resultDetails
| project PreciseTimeStamp, overallAllocationSuccess, activitySuccess, activityName, computeStamp, errorCode, 
    Message, activityId, subscriptionId, tenantName, extraInfo, errorType
| order by PreciseTimeStamp desc
```

**Params:** `{queryActivityId}`, `{queryOperationTime}`

---
