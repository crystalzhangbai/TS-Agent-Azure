# Deployment Job Status

> Source: **ARM Deployments Investigation Guide** dashboard, chapter **Deployment Job Status** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Job Status

_Widget purpose:_ Deployment Job Status

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `Table`
Source panel: `Deployment Job Status`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Jobs').JobStatus
    | where TIMESTAMP between (queryFrom..queryTo)
    | where correlationId == queryCorrelationId and isnotempty(queryCorrelationId)
    | where jobType contains "Deployment" // we need 'contains' here
    | extend duration = tostring(split(jobDurationMs * 1ms, '.')[0])
    | project PreciseTimeStamp, Deployment, ActivityId, jobType, jobPartition, jobId, resourceId, operationName, jobStatus, duration, message, 
        resourceProvider, resourceType, resourceName, jobCompletionStatus, jobFailureCause, jobFailureDetails
    | extend level = case(
        jobStatus =~ 'Failed', 'error', 
        ''
    )
    | where not(qFilter == 'errors') or isnotempty(level)
    | extend formatted_ts = format_datetime(PreciseTimeStamp, 'yyyy-MM-dd [HH:mm:ss]')
    | extend short_activity = substring(ActivityId, 0, 13)
)
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCorrelationId}`, `{qFilter}`

**Signal filters seen in KQL:** `jobType contains "Deployment"`

---

### All or Errors

_Widget purpose:_ Deployment Job Status

Cluster: `?` · Database: `?` · Type: `Filter` · Widget: `Table`
Source panel: `Deployment Job Status`

```kusto
[
    {Value: "all", Description: "All (default)"},
    {Value: "errors", Description:"Errors only"}
]
```

---
