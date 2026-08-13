# (top-level)

> Source: **ARM Activity Ids Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Activity Ids"

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `ResourceGet` · Widget: `Container`

```kusto
let startTime = datetime_add('hour', -1, local_timestamp);
let endTime = datetime_add('hour', 1, local_timestamp);
macro-expand isfuzzy=true ARMProdEG as X
(
    union 
        X.database('Requests').HttpIncomingRequests,
        X.database('Requests').HttpOutgoingRequests
    | where PreciseTimeStamp between(startTime..endTime)
    | where ActivityId == local_ActivityId
    | take 1
)
| extend fuzzyStartTime = startTime, fuzzyEndTime = endTime
```

**Params:** `{local_timestamp}`, `{local_ActivityId}`, `{globalFrom}`, `{globalTo}`

---

### Deployments for Activity Id

_Widget purpose:_ Deployment

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `Table`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Deployments').DeploymentOperations
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where isnotempty(queryActivityId) and ActivityId == queryActivityId
)
| distinct subscriptionId, resourceGroupName, deploymentName, todatetime(startTime), todatetime(endTime), correlationId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryActivityId}`

---
