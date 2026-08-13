# Incoming Requests

> Source: **ARM Correlation Ids Investigation Guide** dashboard, chapter **Incoming Requests** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Incoming Requests

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `Table`
Source panel: `Incoming Requests`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpIncomingRequests
    | where TIMESTAMP between ((queryFrom - 12h) .. (queryTo + 12h))
    | where correlationId == queryCorrelationId and isnotempty(queryCorrelationId)
    | where httpStatusCode > -1
    | extend duration = tostring(split(durationInMilliseconds * 1ms, '.')[0])
    | project-reorder TIMESTAMP, ActivityId, correlationId, authorizationAction, operationName, httpStatusCode, targetUri, duration, RoleLocation, Role
    | extend short_activity = substring(ActivityId, 0, 13)
    | extend level = case(
        httpStatusCode >= 500, 'error', 
        httpStatusCode >= 400, 'warning', 
        ''
    )
    | where not(qFilter == 'errors') or isnotempty(level)
)
| order by TIMESTAMP asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCorrelationId}`, `{qFilter}`

---

### All or Errors

_Widget purpose:_ Incoming Requests

Cluster: `?` · Database: `?` · Type: `Filter` · Widget: `Table`
Source panel: `Incoming Requests`

```kusto
[
    {Value: "all", Description: "All (default)"},
    {Value: "errors", Description:"Errors only"}
]
```

---
