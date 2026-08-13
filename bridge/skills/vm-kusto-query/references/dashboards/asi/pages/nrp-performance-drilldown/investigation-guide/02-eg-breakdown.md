# EG Breakdown

> Source: **NRP - Nrp Performance Drilldown** dashboard, chapter **EG Breakdown** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## NRP EG Exclusive Times

### NRP EG Percentile Times

_Widget purpose:_ NRP EG Exclusive Times

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `EG Breakdown > NRP EG Exclusive Times`

```kusto
let jobNameTimes = cluster('nrp').database('mdsnrp').QosEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == subscriptionId
| where Region == region
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| where BackgroundTaskQos == 0
| project OperationId, OperationName, ResourceName, ResourceGroup, SynchronousDurationInMilliseconds, AsynchronousDurationInMilliseconds, SourceAssemblyFileVersion, PreciseTimeStamp;
let operationToTrackMetadata = jobNameTimes
| distinct OperationId, OperationName, SourceAssemblyFileVersion;
let filteredIfx = NrpIfxOperationV3Event
| where env_time > startTime and env_time < endTime
| where Tenant == region
| where SubscriptionId == subscriptionId;
let syncRootFrame = filteredIfx
| where operationName endswith "Operation"
| parse env_cv with "##"parentGuid1"_"parentguid2"_"frameGuid
| extend childEnvPrefix = strcat("##", frameGuid)
| project parentOperationName=operationName, parentDuration=durationMs, childEnvPrefix, runningOperationId=OperationId;
let asyncRootFrame = filteredIfx
| where operationName endswith "Operation-Async"
| parse env_cv with "##"parentGuid1"_"parentguid2"_"frameGuid
| extend childEnvPrefix = strcat("##", frameGuid)
| project parentOperationName=operationName, parentDuration=durationMs, childEnvPrefix, runningOperationId=OperationId;
let asyncFrames = filteredIfx
| parse env_cv with prefix"_"*
| join kind=inner asyncRootFrame on $left.prefix == $right.childEnvPrefix
| project operationName, durationMs, childEnvPrefix, runningOperationId;
let syncFrames = filteredIfx
| parse env_cv with prefix"_"*
| join kind=inner syncRootFrame on $left.prefix == $right.childEnvPrefix
| where operationName != strcat(parentOperationName, "-Async")
| project operationName, durationMs, childEnvPrefix, runningOperationId;
let totalAsyncChildTime = asyncFrames
| summarize sum(durationMs) by childEnvPrefix;
let totalSyncChildTime = syncFrames
| summarize sum(durationMs) by childEnvPrefix;
let enhancedAsyncRootFrame = asyncRootFrame
| join kind=leftouter totalAsyncChildTime on childEnvPrefix
| extend effectiveDuration = parentDuration - iff(isnull(sum_durationMs), 0, sum_durationMs)
| project operationName=parentOperationName, effectiveDuration, runningOperationId;
let enhancedSyncRootFrame = syncRootFrame
| join kind=leftouter totalAsyncChildTime on childEnvPrefix
| extend effectiveDuration = parentDuration - iff(isnull(sum_durationMs), 0, sum_durationMs)
| project operationName=parentOperationName, effectiveDuration, runningOperationId;
let combinedFrames = asyncFrames
| union syncFrames
| project operationName, effectiveDuration=tolong(durationMs), runningOperationId
| union enhancedSyncRootFrame
| union enhancedAsyncRootFrame;
combinedFrames
| join kind=inner operationToTrackMetadata on $left.runningOperationId == $right.OperationId
| summarize count(), percentiles(durationMs=effectiveDuration, 50, 75, 99.9, 100) by operationName//, ResourceGroup=EffectiveResourceGroup
| order by percentile_durationMs_50
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `operationName endswith "Operation"` · `operationName endswith "Operation-Async"`

---
