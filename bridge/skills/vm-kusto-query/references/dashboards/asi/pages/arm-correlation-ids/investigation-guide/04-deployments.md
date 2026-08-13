# Deployments

> Source: **ARM Correlation Ids Investigation Guide** dashboard, chapter **Deployments** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Deployments by Correlation Id

_Widget purpose:_ Deployments

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `Table`
Source panel: `Deployments`

```kusto
let fuzzyStart = datetime_add("hour", -6, qFrom);
let fuzzyEnd = datetime_add("hour", 6, qTo);
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Deployments').Deployments
    | where TIMESTAMP between (fuzzyStart .. fuzzyEnd)
    | where correlationId == qCorrelationId
    | extend startTime = todatetime(startTime), endTime = todatetime(endTime)
    | extend duration = tostring(split(durationInMilliseconds * 1ms, '.')[0])
    | order by startTime asc 
    | project-away TIMESTAMP, PreciseTimeStamp, Role, RoleInstance, Level, ProviderGuid, ProviderName, EventId, Pid, Tid, 
        correlationId, SourceNamespace, SourceMoniker, SourceVersion, ['__AuthType__'], ['__AuthIdentity__']
    | extend level = case(
        executionStatus == 'Failed', 'error', 
        ''
    )
    | extend short_activity = substring(ActivityId, 0, 13)
    | project-reorder Deployment, startTime, endTime, duration, durationInMilliseconds, short_activity
    | extend formatted_start = format_datetime(startTime, 'yyyy-MM-dd [HH:mm:ss]')
    | extend formatted_end = format_datetime(endTime, 'yyyy-MM-dd [HH:mm:ss]')
)
```

**Params:** `{qFrom}`, `{qTo}`, `{qCorrelationId}`

---
