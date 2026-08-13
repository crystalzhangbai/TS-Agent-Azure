# HttpOutgoingRequests

> Source: **Managed Disk - Correlation Id** dashboard, chapter **HttpOutgoingRequests** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### HttpOutgoingRequests

Cluster: `armprodeus.eastus` · Database: `Requests` · Type: `Table`
Source panel: `HttpOutgoingRequests`

```kusto
let ext_start = queryTime-timespan(30m);
let ext_end = queryTime+timespan(30m);
HttpOutgoingRequests
  | where PreciseTimeStamp between(ext_start .. ext_end)
  | where case(isnotempty(queryCorrelationId), correlationId =~ queryCorrelationId, false)
  | where httpStatusCode !in (-1, 0)
  | project PreciseTimeStamp, TaskName, operationName, httpMethod, httpStatusCode, durationInMilliseconds, targetUri, apiVersion, exceptionMessage
```

**Params:** `{queryTime}`, `{queryCorrelationId}`

---
