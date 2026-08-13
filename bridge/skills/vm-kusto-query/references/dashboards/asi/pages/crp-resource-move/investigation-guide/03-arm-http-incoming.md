# ARM HTTP Incoming

> Source: **CRP Resource Move Investigation Guide** dashboard, chapter **ARM HTTP Incoming** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ARM HTTP Incoming

### ARM HTTP Incoming

Cluster: `armprod` · Database: `ARMProd` · Type: `Table`
Source panel: `ARM HTTP Incoming > ARM HTTP Incoming`

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').HttpIncomingRequests
| where PreciseTimeStamp between ( starttime .. endtime)
| where correlationId == correlationid
| project PreciseTimeStamp, RoleInstance, Level, ActivityId, TaskName, subscriptionId, correlationId, operationName, 
  httpMethod, hostName, targetUri, httpStatusCode, errorCode, errorMessage, durationInMilliseconds, 
  contentLength, referer, userAgent, clientIpAddress, SourceNamespace, failureCause, clientApplicationId, clientRequestId,
  authorizationAction, authorizationSource, principalOid
```

**Params:** `{starttime}`, `{endtime}`, `{correlationid}`

---
