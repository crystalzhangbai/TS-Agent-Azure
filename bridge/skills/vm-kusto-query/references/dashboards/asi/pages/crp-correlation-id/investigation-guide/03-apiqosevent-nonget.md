# ApiQosEvent_nonGet

> Source: **CRP CorrelationId Investigation Guide** dashboard, chapter **ApiQosEvent_nonGet** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ApiQosEvent_nonGet

### CorrelationId - ApiQosEvent_nonGet

_Widget purpose:_ ApiQosEvent_nonGet

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `ApiQosEvent_nonGet > ApiQosEvent_nonGet`

```kusto
ApiQosEvent_nonGet
| where correlationId =~ local_correlationId
| extend startTime=PreciseTimeStamp-e2EDurationInMilliseconds*1ms
| project startTime,PreciseTimeStamp,operationName,operationId,resourceGroupName,resourceName,resultCode
| order by PreciseTimeStamp desc
```

**Params:** `{local_correlationId}`, `{local_endDate}`, `{local_startDate}`

---
