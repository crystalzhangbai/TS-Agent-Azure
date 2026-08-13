# Outgoing Requests

> Source: **ARM Correlation Ids Investigation Guide** dashboard, chapter **Outgoing Requests** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Outgoing Requests

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `Table`
Source panel: `Outgoing Requests`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpOutgoingRequests
    | where TIMESTAMP between ((queryFrom - 12h) .. (queryTo + 12h))
    | where correlationId == queryCorrelationId and isnotempty(queryCorrelationId)
    | where operationName !in (
        "POST/SUBSCRIPTIONS/RESOURCEGROUPS/PROVIDERS/MICROSOFT.COMPUTE/VIRTUALMACHINESCALESETS/PROVIDERS/MICROSOFT.INSIGHTS/NOTIFY"
    )
    | where httpStatusCode > -1
    | extend duration = tostring(split(durationInMilliseconds * 1ms, '.')[0])
    | project-away TIMESTAMP, Role, RoleInstance, Level, ProviderGuid, ProviderName, EventId, Pid, Tid, 
        SourceNamespace, SourceMoniker, SourceVersion, ['__AuthType__'], ['__AuthIdentity__']
    | extend short_activity = substring(ActivityId, 0, 13)
    | extend level = case(
        httpStatusCode >= 500, 'error', 
        httpStatusCode >= 400, 'warning', 
        ''
    )
    | where not(qFilter == 'errors') or isnotempty(level)
)
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCorrelationId}`, `{qFilter}`

---

### All or Errors

_Widget purpose:_ Outgoing Requests

Cluster: `?` · Database: `?` · Type: `Filter` · Widget: `Table`
Source panel: `Outgoing Requests`

```kusto
[
    {Value: "all", Description: "All (default)"},
    {Value: "errors", Description:"Errors only"}
]
```

---
