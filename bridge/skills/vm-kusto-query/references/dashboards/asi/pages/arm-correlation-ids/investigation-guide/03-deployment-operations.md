# Deployment Operations

> Source: **ARM Correlation Ids Investigation Guide** dashboard, chapter **Deployment Operations** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Deployment Operations

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `Table`
Source panel: `Deployment Operations`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Deployments').DeploymentOperations
    | where PreciseTimeStamp between ((queryFuzzyStartTime - 12h) .. (queryFuzzyEndTime + 12h))
    | where correlationId == queryCorrelationId and (isempty(queryDeploymentName) or deploymentName == queryDeploymentName)
    | where subscriptionId == querySubscriptionId 
    | extend startTime = todatetime(startTime), endTime = todatetime(endTime)
    | extend level = iif(executionStatus != "Succeeded", "Error", "")
    | where not(qFilter == 'errors') or isnotempty(level)
    | extend duration = tostring(split(durationInMilliseconds * 1ms, '.')[0])
    | project-away TIMESTAMP, PreciseTimeStamp, Role, RoleInstance, Level, ProviderGuid, ProviderName, EventId, Pid, Tid, 
        correlationId, SourceNamespace, SourceMoniker, SourceVersion, ['__AuthType__'], ['__AuthIdentity__']
    | order by startTime asc
    | extend formatted_start = format_datetime(startTime, 'yyyy-MM-dd [HH:mm:ss]')
    | extend formatted_end = format_datetime(endTime, 'yyyy-MM-dd [HH:mm:ss]')
    | extend short_activity = substring(ActivityId, 0, 13)
    | extend statusMessage = parse_json(statusMessage)
    | extend error_code = tostring(statusMessage.error.code)
    | extend error_message = tostring(statusMessage.error.message)
)
```

**Params:** `{querySubscriptionId}`, `{queryDeploymentName}`, `{queryCorrelationId}`, `{queryFuzzyStartTime}`, `{queryFuzzyEndTime}`, `{qFilter}`

---

### All or Errors

_Widget purpose:_ Deployment Operations

Cluster: `?` · Database: `?` · Type: `Filter` · Widget: `Table`
Source panel: `Deployment Operations`

```kusto
[
    {Value: "all", Description: "All (default)"},
    {Value: "errors", Description:"Errors only"}
]
```

---
