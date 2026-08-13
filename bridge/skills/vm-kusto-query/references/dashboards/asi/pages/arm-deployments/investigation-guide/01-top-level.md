# (top-level)

> Source: **ARM Deployments Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Deployments"

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `ResourceGet` · Widget: `Container`

```kusto
let fromTime = iif(isnotempty(local_startTime), datetime_add("hour", -2, local_startTime), globalFrom);
let toTime = iif(isnotempty(local_endTime), datetime_add("hour", 2, local_endTime), globalTo);
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Deployments').Deployments
    | where PreciseTimeStamp between(fromTime..toTime)
    | where isempty(local_correlationId) or correlationId =~ local_correlationId
    | where subscriptionId == local_subscriptionId and resourceGroupName == local_resourceGroupName and local_deploymentName == deploymentName
    | summarize 
        executionStatus = coalesce(take_anyif(executionStatus, executionStatus == 'Failed'), 'Succeeded'), 
        arg_max(PreciseTimeStamp, *) by subscriptionId, deploymentName
    | extend startTime = todatetime(startTime), endTime = todatetime(endTime)
    | extend fuzzyStartTime = datetime_add("hour", -2, startTime), fuzzyEndTime = datetime_add("hour", 2, endTime)
    | project-away TIMESTAMP, PreciseTimeStamp, Role, RoleInstance, Level, ProviderGuid, ProviderName, EventId, Pid, Tid, 
        SourceNamespace, SourceMoniker, SourceVersion, ['__AuthType__'], ['__AuthIdentity__']
)
| order by startTime desc
```

**Params:** `{local_correlationId}`, `{local_deploymentName}`, `{local_endTime}`, `{local_resourceGroupName}`, `{local_startTime}`, `{local_subscriptionId}`, `{globalFrom}`, `{globalTo}`

---
