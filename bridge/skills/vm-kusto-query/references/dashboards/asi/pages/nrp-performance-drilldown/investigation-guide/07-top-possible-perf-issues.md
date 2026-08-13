# Top Possible Perf Issues

> Source: **NRP - Nrp Performance Drilldown** dashboard, chapter **Top Possible Perf Issues** (4 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Highest Reading Operations

### Highest Read Size Operations

_Widget purpose:_ Highest Reading Operations

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Top Possible Perf Issues > Highest Reading Operations`

```kusto
let ['_startTime']=ago(1d);
let ['_endTime']=now();
let batchManagerTransactionStats = cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where Region == region
| where SubscriptionId == subscriptionId
| where EventCode == "DisposingKvsTransaction"
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| parse Message with "Transaction duration: "duration" ms; Reads: "readCount"/"readSize"; Adds: "addCount"/"addSize"; Updates: "updateCount"/"updateSize"; Deletes: "deleteCount"; Metadata: "Metadata"; SerializeDuration: "SerializeDuration"; DeserializeDuration: "DeserializeDuration"; TransactionCacheHit: "TransactionCacheHit"; TransactionCacheMiss: "TransactionCacheMiss"; GlobalCacheHit: "GlobalCacheHit"; GlobalCacheMiss: "GlobalCacheMiss"; " *
| extend transactionOwner = strcat("Batch Manager Queue ", QueueId)
| extend transactionInstance = JobChunkId
| project transactionOwner, transactionInstance, readCount, readSize, addCount, addSize, updateCount, updateSize, deleteCount, TransactionCacheHit, TransactionCacheMiss, GlobalCacheHit, GlobalCacheMiss, SourceAssemblyFileVersion, SubscriptionId, PreciseTimeStamp, Region, CorrelationRequestId;
let frontendTransactionStats = cluster('nrp').database('mdsnrp').FrontendOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where Region == region
| where SubscriptionId == subscriptionId
| where EventCode == "DisposingKvsTransaction"
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| parse Message with "Transaction duration: "duration" ms; Reads: "readCount"/"readSize"; Adds: "addCount"/"addSize"; Updates: "updateCount"/"updateSize"; Deletes: "deleteCount"; Metadata: "Metadata"; SerializeDuration: "SerializeDuration"; DeserializeDuration: "DeserializeDuration"; TransactionCacheHit: "TransactionCacheHit"; TransactionCacheMiss: "TransactionCacheMiss"; GlobalCacheHit: "GlobalCacheHit"; GlobalCacheMiss: "GlobalCacheMiss"; " *
| extend transactionOwner = strcat("FrontendOp ", OperationName)
| extend transactionInstance = OperationId
| project transactionOwner, transactionInstance, readCount, readSize, addCount, addSize, updateCount, updateSize, deleteCount, TransactionCacheHit, TransactionCacheMiss, GlobalCacheHit, GlobalCacheMiss, SourceAssemblyFileVersion, SubscriptionId, PreciseTimeStamp, Region, CorrelationRequestId;
let readOpTransactionStats = cluster('nrp').database('mdsnrp').FrontendReadOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where Region == region
| where SubscriptionId == subscriptionId
| where EventCode == "DisposingKvsTransaction"
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| parse Message with "Transaction duration: "duration" ms; Reads: "readCount"/"readSize"; Adds: "addCount"/"addSize"; Updates: "updateCount"/"updateSize"; Deletes: "deleteCount"; Metadata: "Metadata"; SerializeDuration: "SerializeDuration"; DeserializeDuration: "DeserializeDuration"; TransactionCacheHit: "TransactionCacheHit"; TransactionCacheMiss: "TransactionCacheMiss"; GlobalCacheHit: "GlobalCacheHit"; GlobalCacheMiss: "GlobalCacheMiss"; " *
| extend transactionOwner = strcat("ReadOp ", OperationName)
| extend transactionInstance = OperationId
| project transactionOwner, transactionInstance, readCount, readSize, addCount, addSize, updateCount, updateSize, deleteCount, TransactionCacheHit, TransactionCacheMiss, GlobalCacheHit, GlobalCacheMiss, SourceAssemblyFileVersion, SubscriptionId, PreciseTimeStamp, Region, CorrelationRequestId;
readOpTransactionStats
| union batchManagerTransactionStats
| union frontendTransactionStats
| summarize count(), ReadSize=sum(toint(readSize)), WriteSize=sum(toint(addSize))+sum(toint(updateSize)), sum(toint(TransactionCacheHit)), sum(toint(TransactionCacheMiss)), sum(toint(GlobalCacheHit)), sum(toint(GlobalCacheMiss)) by transactionOwner, OperationIdOrJobChunkId=transactionInstance, CorrelationRequestId, SubscriptionId
//| summarize count(), ReadSize=sum(sum_readSize), WriteSize=sum(sum_addSize)+sum(sum_updateSize), TransactionCacheHits=sum(sum_TransactionCacheHit), TransactionCacheMisses=sum(sum_TransactionCacheMiss), GlobalCacheHits=sum(sum_GlobalCacheHit), GlobalCacheMisses=sum(sum_GlobalCacheMiss) by transactionOwner, SubscriptionId
| order by ReadSize
| take 10
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `EventCode == "DisposingKvsTransaction"`

---

## Longest EG Frames

### Longest EG Frames

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Top Possible Perf Issues > Longest EG Frames`

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
| where Tenant == region;
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
| order by effectiveDuration
| project operationName, effectiveDuration, runningOperationId, runningOperationName=OperationName
| take 10
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `operationName endswith "Operation"` · `operationName endswith "Operation-Async"`

---

## Longest Subscription Locks

### Longest Sub Locks

_Widget purpose:_ Longest Subscription Locks

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Top Possible Perf Issues > Longest Subscription Locks`

```kusto
cluster('nrp').database('mdsnrp').FrontendOperationEtwEvent 
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where Region == region
| where SubscriptionId == subscriptionId
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| where EventCode == "LockReleased"
| parse Message with * "Operation "fullOpName" ("opId")"" released lock "lockResource" after "lockDuration" ms, refCount: "refcount
| where lockResource == SubscriptionId
| project PreciseTimeStamp, lockDuration, OperationName, OperationId, CorrelationRequestId, SubscriptionId
| order by toint(lockDuration)
| take 10
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `EventCode == "LockReleased"`

---

## Slowest Batch Jobs

### Slowest Batch Jobs

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Top Possible Perf Issues > Slowest Batch Jobs`

```kusto
cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == subscriptionId
| where Region == region
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| project PreciseTimeStamp, Message, JobChunkId, OperationId, OperationName, EventCode, Duration, SourceAssemblyFileVersion, JobName, CorrelationRequestId
| where EventCode == "TransactionJobExecutionFinished"
| order by Duration
| take 10
| project PreciseTimeStamp, Duration, JobName, OperationName, OperationId, CorrelationRequestId
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `EventCode == "TransactionJobExecutionFinished"`

---
