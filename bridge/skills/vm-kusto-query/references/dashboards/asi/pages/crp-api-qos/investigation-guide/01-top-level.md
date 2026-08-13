# (top-level)

> Source: **CRP API QoS Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "API QoS"

Cluster: `azcrp` · Database: `crp_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
let fuzzyStart = datetime_add("hour", -12, local_PreciseTimeStamp);
let fuzzyEnd = datetime_add("hour", 12, local_PreciseTimeStamp);
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent_nonGet
| where PreciseTimeStamp >= fuzzyStart and PreciseTimeStamp < fuzzyEnd
| where operationId == local_operationId
| extend opStartTime = floor(datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp), 1m)
| extend opEndTime = floor(PreciseTimeStamp, 1m) + 1m
| join kind=fullouter
(
cluster('azcrp.kusto.windows.net').database('crp_allprod').ComponentQoSEvent
| where PreciseTimeStamp >= fuzzyStart and PreciseTimeStamp < fuzzyEnd
| where activityId == local_operationId
) on $left.operationId==$right.activityId
| project PreciseTimeStamp=coalesce(PreciseTimeStamp1, PreciseTimeStamp), operationId=coalesce(operationId, activityId), opStartTime, opEndTime
| take 1
```

**Params:** `{local_PreciseTimeStamp}`, `{local_operationId}`, `{globalFrom}`, `{globalTo}`

---

### API QoS

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `CoBeTimeline`

```kusto
let startDatetime = datetime_add('hour', -12, timeStamp);
let endDatetime = datetime_add('hour', 12, timeStamp);
CRPAPIQoS(operationId, startDatetime, endDatetime)
// adding the following to try and make the timeline less noisy.
| where EventName !in (
    'Fabric:GetTenantInformation',
    'Fabric:GetRoleInstanceContainerProvisioningDetails'
)
```

**Params:** `{operationId}`, `{timeStamp}`

---
