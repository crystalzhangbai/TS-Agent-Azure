# (top-level)

> Source: **Aztec RelatedActivityId Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "RelatedActivityId"

Cluster: `AzureCM` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
let queryFrom = datetime_add("day", -1, local_startDate);
let queryTo = datetime_add("day", 1, local_startDate);
CommonWebOperationStart
| where PreciseTimeStamp between (queryFrom..queryTo)
| where RelatedActivityId =~ local_RelatedActivityId
| distinct AvailabilityZone,ClientType,CloudName,DataCenterName,Region,Tenant,local_RelatedActivityId,local_startDate,local_endDate
| limit 01
| extend RelatedActivityId=local_RelatedActivityId,startDate=local_startDate,endDate=local_endDate
| project AvailabilityZone,ClientType,CloudName,DataCenterName,Region,Tenant,RelatedActivityId
```

**Params:** `{local_RelatedActivityId}`, `{local_startDate}`, `{local_endDate}`

---

### RelatedActivityId CRP QoS Get

_Widget purpose:_ CRP

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`

```kusto
let queryFrom = datetime_add("day", -1, local_startDate);
let queryTo = datetime_add("day", 1, local_startDate);
ApiQosEvent
| where PreciseTimeStamp between (queryFrom..queryTo)
| where operationId =~ local_RelatedActivityId
| project operationId,correlationId,operationName,resourceGroupName,resourceName,e2EDurationInMilliseconds,httpStatusCode,resultCode,exceptionType,errorDetails
```

**Params:** `{local_startDate}`, `{local_RelatedActivityId}`

---
