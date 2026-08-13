# AIB INT Deployments

> Source: **Deployments** dashboard, chapter **AIB INT Deployments** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AIB Deployments

_Widget purpose:_ AIB INT Deployments

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `Table`
Source panel: `AIB INT Deployments`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Deployments').Deployments
    | where PreciseTimeStamp between(queryFrom .. queryTo)
    | where subscriptionId == subID
    | summarize arg_max(PreciseTimeStamp, *) by subscriptionId, resourceGroupName, deploymentName, ActivityId
    | extend startTime = todatetime(startTime), endTime = todatetime(endTime)
    | project 
        deploymentName, 
        resourceGroupName, 
        resourceGroupLocation, 
        resourceCount, 
        executionStatus, 
        startTime, 
        endTime, 
        durationInMilliseconds, 
        TaskName, 
        level = iif(TaskName == "DeploymentsFailed", "error", "info"),
        correlationId
)
| order by startTime desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subID}`

---
