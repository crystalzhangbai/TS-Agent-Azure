# ApiQosEvent

> Source: **CRP CorrelationId Investigation Guide** dashboard, chapter **ApiQosEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ApiQosEvent

### CorrelationId - ApiQosEvent

_Widget purpose:_ ApiQosEvent

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `ApiQosEvent > ApiQosEvent`

```kusto
ApiQosEvent
//| where PreciseTimeStamp between (local_startDate..local_endDate)
| where correlationId =~ local_correlationId
| project PreciseTimeStamp, operationName,operationId,resourceGroupName,resourceName,resultCode, durationInMilliseconds, e2EDurationInMilliseconds, 
    resultType, httpStatusCode, exceptionType, errorDetails, labels, requestEntity, userAgent
| order by PreciseTimeStamp desc
```

**Params:** `{local_correlationId}`, `{local_endDate}`, `{local_startDate}`

---
