# HttpIncomingRequests

> Source: **Managed Disk - Correlation Id** dashboard, chapter **HttpIncomingRequests** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### HttpIncomingRequests

Cluster: `armprodeus.eastus` · Database: `Requests` · Type: `Table`
Source panel: `HttpIncomingRequests`

```kusto
let ext_start = queryTime-timespan(30m);
let ext_end = queryTime+timespan(30m);
HttpIncomingRequests
  | where PreciseTimeStamp between(ext_start .. ext_end)
  //| where PreciseTimeStamp between(queryFrom..queryTo)
  | where case(isnotempty(queryCorrelationId), correlationId =~ queryCorrelationId, false)
  | where httpStatusCode !in (-1, 0)
  | project TIMESTAMP, ActivityId, subscriptionId, correlationId, principalOid, tenantId, operationName, targetUri, userAgent, clientRequestId, clientIpAddress, clientApplicationId, apiVersion, serviceRequestId, armServiceRequestId
```

**Params:** `{queryTime}`, `{queryCorrelationId}`

---
