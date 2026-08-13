# (top-level)

> Source: **ARM Correlation Ids Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Correlation Ids"

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `ResourceGet` · Widget: `Container`

```kusto
let fuzzyStart = datetime_add("hour", -12, local_timestamp);
let fuzzyEnd = datetime_add("hour", 12, local_timestamp);
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpIncomingRequests
    | where PreciseTimeStamp between(fuzzyStart..fuzzyEnd)
    | where correlationId == local_correlationId
    | where TaskName != 'HttpIncomingRequestStart'
)
| summarize 
    first_op = min(PreciseTimeStamp),
    last_op = max(PreciseTimeStamp),
    arg_min(PreciseTimeStamp, *)
    by correlationId
| project-away PreciseTimeStamp, TIMESTAMP, Deployment, Role, RoleInstance, Level, ProviderGuid, 
    ProviderName, EventId, Pid, Tid, SourceNamespace, SourceMoniker, SourceVersion, referer, activityVector,
    locale, altSecId, ['__AuthType__'], ['__AuthIdentity__']
| project-reorder first_op, last_op, correlationId
| extend duration = datetime_diff('minute', last_op, first_op)
| extend cobe_start = first_op - 2h
| extend cobe_end = last_op + 2h
```

**Params:** `{local_timestamp}`, `{local_correlationId}`, `{globalFrom}`, `{globalTo}`

**Signal filters seen in KQL:** `TaskName != "HttpIncomingRequestStart"`

---
