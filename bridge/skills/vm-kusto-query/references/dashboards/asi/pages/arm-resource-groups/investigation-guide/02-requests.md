# Requests

> Source: **ARM Resource Groups Investigation Guide** dashboard, chapter **Requests** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Resource Group Requests

_Widget purpose:_ Requests

Cluster: `armprod` · Database: `armprod` · Type: `TimeSeries`
Source panel: `Requests`

```kusto
let rgToken = strcat("/", queryResourceGroupName, "/");
HttpIncomingRequests
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where subscriptionId == querySubscriptionId and targetUri has rgToken and TaskName != "HttpIncomingRequestStart"
| summarize Requests = count(), InternalServiceErrors = countif(httpStatusCode >= 500), Throttled = countif(httpStatusCode == 429) by bin(PreciseTimeStamp, 30m)
| order by PreciseTimeStamp asc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`

---
