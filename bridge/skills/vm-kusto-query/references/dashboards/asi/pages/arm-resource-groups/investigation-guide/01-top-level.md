# (top-level)

> Source: **ARM Resource Groups Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Resource Group Deployments

Cluster: `armprod` · Database: `armprod` · Type: `Table`

```kusto
Deployments
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where subscriptionId == querySubscriptionId and resourceGroupName =~ queryResourceGroupName
| summarize arg_max(PreciseTimeStamp, *) by subscriptionId, resourceGroupName, deploymentName
| extend startTime = todatetime(startTime), endTime = todatetime(endTime)
| project deploymentName, resourceGroupName, resourceGroupLocation, resourceCount, executionStatus, startTime, endTime, durationInMilliseconds
| order by startTime desc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`

---
