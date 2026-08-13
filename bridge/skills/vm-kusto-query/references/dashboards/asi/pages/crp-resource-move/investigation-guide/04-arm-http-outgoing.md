# ARM HTTP Outgoing

> Source: **CRP Resource Move Investigation Guide** dashboard, chapter **ARM HTTP Outgoing** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ARM HTTP Outgoing

### ARM HTTP Outgoing

Cluster: `armprod` · Database: `ARMProd` · Type: `Table`
Source panel: `ARM HTTP Outgoing > ARM HTTP Outgoing`

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').HttpOutgoingRequests
| where PreciseTimeStamp between (starttime .. endtime)
| where correlationId == correlationid
// | where TaskName <> "HttpOutgoingRequestStart"
| project PreciseTimeStamp, RoleInstance, Level, ActivityId, TaskName, subscriptionId, correlationId, operationName, 
  httpMethod, hostName, targetUri, httpStatusCode, exceptionMessage, errorCode, errorMessage, durationInMilliseconds, 
  contentLength, referer, SourceNamespace, clientRequestId, principalOid
```

**Params:** `{starttime}`, `{endtime}`, `{correlationid}`

**Signal filters seen in KQL:** `TaskName <> "HttpOutgoingRequestStart"`

---
