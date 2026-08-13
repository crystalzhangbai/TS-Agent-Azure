# Batch Sizes

> Source: **NRP - Latency and Performance Investigation Dashboard** dashboard, chapter **Batch Sizes** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Batch Sizes

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Batch Sizes`

```kusto
let batchSizes = cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where TIMESTAMP between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subscription
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance, QueueId
| where Message startswith "Complete dequeue chunk of"
| parse Message with "Complete dequeue chunk of "batchsize" jobs. Added "other" jobs to chunk id "JobChunkId;
let completedJobs = cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where TIMESTAMP between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subscription
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance, QueueId, JobChunkId, JobId
| where EventCode == "TransactionJobExecutionFinished";
batchSizes
| join completedJobs on JobChunkId
| project batchsize, JobId, QueueId
| summarize percentiles(toint(batchsize), 50, 75, 90, 99.9) by QueueId
| project QueueId, percentile_batchsize_50, percentile_batchsize_75, percentile_batchsize_90, percentile_batchsize_99_9
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subscription}`

**Signal filters seen in KQL:** `Message startswith "Complete dequeue chunk of"` · `EventCode == "TransactionJobExecutionFinished"`

---
