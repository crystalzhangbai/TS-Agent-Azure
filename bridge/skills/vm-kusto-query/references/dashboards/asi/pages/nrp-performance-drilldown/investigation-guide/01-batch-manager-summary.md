# Batch Manager Summary

> Source: **NRP - Nrp Performance Drilldown** dashboard, chapter **Batch Manager Summary** (7 queries across 7 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Batch Job Durations

### Batch Job Durations

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Batch Manager Summary > Batch Job Durations`

```kusto
cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == subscriptionId
| where Region == region
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| where EventCode == "TransactionJobExecutionFinished"
| where iff(QueueId startswith "ResourceLockingTransactionJob", Message endswith "ResourceLockingBatchQueue.", true)
| summarize count(), percentiles(toint(Duration), 50, 75, 95, 99.9) by JobName
| order by percentile_Duration_50
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `EventCode == "TransactionJobExecutionFinished"`

---

## Batch Queue Processing Percentiles

### Batch Manager Queue Processing Percentiles

_Widget purpose:_ Batch Queue Processing Percentiles

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Batch Manager Summary > Batch Queue Processing Percentiles`

```kusto
cluster('nrp').database('mdsnrp').FrontendOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == subscriptionId
| where Region == region
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance
| where Message startswith "Dequeue job id"
| parse Message with "Dequeue job id "id" of type "jobName" for execution in queue "queueId" duration in queue: "duration
| summarize count(), percentiles(toint(duration), 50, 75, 99, 99.9, 100) by queueId
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `Message startswith "Dequeue job id"`

---

## Batch Sizes

### Batch Sizes

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `CategoryChart`
Source panel: `Batch Manager Summary > Batch Sizes`

```kusto
let batchSizes = cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where TIMESTAMP between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subscriptionId
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance, QueueId
| where Message startswith "Complete dequeue chunk of"
| parse Message with "Complete dequeue chunk of "batchsize" jobs. Added "other" jobs to chunk id "JobChunkId;
let completedJobs = cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where TIMESTAMP between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subscriptionId
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance, QueueId, JobChunkId, JobId
| where EventCode == "TransactionJobExecutionFinished";
batchSizes
| join completedJobs on JobChunkId
| project batchsize, JobId, QueueId
| summarize percentiles(toint(batchsize), 50, 75, 90, 99.9) by QueueId
| project QueueId, percentile_batchsize_50, percentile_batchsize_75, percentile_batchsize_90, percentile_batchsize_99_9
| render barchart  by QueueId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subscriptionId}`

**Signal filters seen in KQL:** `Message startswith "Complete dequeue chunk of"` · `EventCode == "TransactionJobExecutionFinished"`

---

## Commit Duration

### Commit Duration

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Batch Manager Summary > Commit Duration`

```kusto
cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where TIMESTAMP between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId ==  subscriptionId
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance, QueueId
| parse Message with "Finished commit of job chunk "jobChunk" from queue "queueId" in "commitTime" ms"
| summarize percentiles(toint(commitTime), 50, 75, 95, 99) by queueId
| order by percentile_commitTime_50 desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subscriptionId}`

---

## Long Running Jobs

### Long Running Jobs

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Batch Manager Summary > Long Running Jobs`

```kusto
cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where TIMESTAMP between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subscription
| where Message contains "Long execution duration execution job id"
| parse Message with "Long execution duration execution job id: " LongRunningJobId ", duration: " ExecutionDuration
| extend jobDuration = toint(ExecutionDuration)
| project PreciseTimeStamp, JobId, JobName, Message, jobDuration
| summarize avg(jobDuration) by bin(PreciseTimeStamp, 1s), JobName, JobId
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subscription}`, `{region}`

**Signal filters seen in KQL:** `Message contains "Long execution duration execution job id"`

---

## Worst-Performing Non-Tenant Operations

### Worst Performing Non-Tenant Operations

_Widget purpose:_ Worst-Performing Non-Tenant Operations

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `CategoryChart`
Source panel: `Batch Manager Summary > Worst-Performing Non-Tenant Operations`

```kusto
cluster('nrp').database('mdsnrp').FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subscriptionId
| parse Message with "Dequeue job id "JobId" of type "jobName" for execution in queue "queueId" duration in queue: "duration
| project PreciseTimeStamp, duration, JobId, OperationId, OperationName, RoleInstance, Pid
| where OperationName !contains "tenant" and OperationName !contains "VirtualMachine" and OperationName !contains "ScaleSet"
| sort by toint(duration) desc 
| take 1000
| project OperationName, OperationId, toint(duration)
| render columnchart  by OperationName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subscriptionId}`, `{region}`

---

## Worst-Performing Tenant Operations

### Worst Performing Tenant Operations

_Widget purpose:_ Worst-Performing Tenant Operations

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `CategoryChart`
Source panel: `Batch Manager Summary > Worst-Performing Tenant Operations`

```kusto
cluster('nrp').database('mdsnrp').FrontendOperationEtwEvent
| where TIMESTAMP between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subscriptionId
| parse Message with "Dequeue job id "JobId" of type "jobName" for execution in queue "queueId" duration in queue: "duration
| project PreciseTimeStamp, duration, JobId, OperationId, OperationName, RoleInstance, Pid
| where OperationName contains "tenant" or OperationName contains "VirtualMachine" or OperationName contains "ScaleSet"
| sort by toint(duration) desc 
| take 1000
| project OperationName, OperationId, toint(duration)
| render columnchart  by OperationName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subscriptionId}`

**Signal filters seen in KQL:** `OperationName contains "tenant"`

---
