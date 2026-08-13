# (top-level)

> Source: **EEE CRP — VM Operation** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "VM Operation"

Cluster: `azcrp` · Database: `crp_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
//print correlationId = local_correlationId, operationId = local_operationId
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(globalFrom .. globalTo)
| where operationId == local_operationId
| where operationName !contains ".GET"
| where operationName !contains "FabricCallback"
| where operationName !contains "NrpCallback"
| where operationName !contains "AllocateDisks"
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
| project StartTime, EndTime = PreciseTimeStamp, operationId, correlationId, operationName, resourceGroupName, resourceName, 
  httpStatusCode, e2EDurationInMilliseconds, durationInMin, resultCode, errorDetails, requestEntity, subscriptionId, userAgent, 
  apiVersion, labels, region, RPTenant, clientPrincipalName, clientRequestId
| project correlationId, operationId, subscriptionId, resourceGroupName, resourceName
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_correlationId}`, `{local_operationId}`

---

### Preemption

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`

```kusto
union
(cluster('azcrp.kusto.windows.net').database('crp_allprod').ContextActivity
| where PreciseTimeStamp between (starttime .. endtime)
| where activityId == operationid
| where message contains "is requesting preemption." or message contains "Not preempting current execution as it was preempted too many times."
| parse message with "Activity " preemption_operationId " is requesting preemption. Current preemption count is " preemption_count "."
| order by PreciseTimeStamp asc
| extend preemption_status = case (message contains "is requesting preemption.", "Preempted", 
    message contains "Not preempting current execution as it was preempted too many times.", "Failed to preempt / Preempted too many times", "No Preemption")
| project PreciseTimeStamp, preemption_operationId, preemption_count, preemption_status),
(print PreciseTimeStamp = now(), preemption_operationId = "", preemption_count = 0, preemption_status = "Not Preempted")
| top 1 by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{operationid}`

**Signal filters seen in KQL:** `message contains "is requesting preemption."`

---

### CRP Operation Info

_Widget purpose:_ Operation Information

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(starttime .. endtime)
| where operationId == operationid
| where operationName !contains "GET"
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
```

**Params:** `{starttime}`, `{endtime}`, `{operationid}`

---
