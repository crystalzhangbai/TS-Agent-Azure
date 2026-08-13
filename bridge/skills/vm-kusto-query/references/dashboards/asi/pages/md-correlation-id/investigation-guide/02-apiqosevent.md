# ApiQosEvent

> Source: **Managed Disk - Correlation Id** dashboard, chapter **ApiQosEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ApiQosEvent

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `ApiQosEvent`

```kusto
let ext_start = queryTime-timespan(30m);
let ext_end = queryTime+timespan(30m);
ApiQosEvent
| where PreciseTimeStamp between(ext_start .. ext_end)
| where correlationId =~ queryCorrelationId
| project PreciseTimeStamp, operationName,operationId,resourceGroupName,resourceName,resultCode, durationInMilliseconds, e2EDurationInMilliseconds, 
    resultType, httpStatusCode, exceptionType, errorDetails, labels, requestEntity, userAgent
| order by PreciseTimeStamp desc
```

**Params:** `{queryTime}`, `{queryCorrelationId}`

---
