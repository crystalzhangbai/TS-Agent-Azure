# Exclusive Write Attribution

> Source: **NRP - Nrp Performance Drilldown** dashboard, chapter **Exclusive Write Attribution** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Exclusive Write Time Distribution

### ExclusiveWriteTimes

_Widget purpose:_ Exclusive Write Time Distribution

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Exclusive Write Attribution > Exclusive Write Time Distribution`

```kusto
let batchSizes = cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == subscriptionId
| where Region == region
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance, QueueId
| where Message startswith "Complete dequeue chunk of"
| parse Message with "Complete dequeue chunk of "batchsize" jobs. Added "other" jobs to chunk id "JobChunkId;
let completedJobs = cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == subscriptionId
| where Region == region
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance, QueueId, JobChunkId, JobId, Duration, JobName
| where EventCode == "TransactionJobExecutionFinished" and iff(QueueId contains "ResourceLockingTransactionJob", Message endswith "ResourceLockingBatchQueue.", true);
let subLockStats = cluster('nrp').database("mdsnrp").FrontendOperationEtwEvent 
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where Region == region
| where SubscriptionId == subscriptionId
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| where EventCode == "LockReleased"
| parse Message with * "Operation "fullOpName" ("opId")"" released lock "lockResource" after "lockDuration" ms, refCount: "refcount
| project lockResource, lockDuration, PreciseTimeStamp, OperationId, SubscriptionId, OperationName
| where lockResource == SubscriptionId
| project JobName = strcat("SubLoc_", OperationName), batchsize="1", Duration = tolong(lockDuration);
batchSizes
| join completedJobs on JobChunkId
| project batchsize, Duration, JobName
| union subLockStats
| summarize count(), sum(Duration), percentiles(Duration, 50, 75, 90, 99.9), percentiles(toint(batchsize), 50, 75, 90, 99.9) by JobName
| extend  PercentExclusiveUtilization=sum_Duration / ((endTime-startTime) / 1ms)
| project JobName, count_, sum_Duration, PercentExclusiveUtilization, percentile_Duration_50, percentile_Duration_75, percentile_Duration_90, percentile_Duration_99_9, percentile_batchsize_50, percentile_batchsize_75, percentile_batchsize_90, percentile_batchsize_99_9
| order by sum_Duration
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `Message startswith "Complete dequeue chunk of"` · `EventCode == "TransactionJobExecutionFinished"` · `EventCode == "LockReleased"`

---
