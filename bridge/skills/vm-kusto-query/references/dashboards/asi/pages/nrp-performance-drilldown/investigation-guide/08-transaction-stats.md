# Transaction Stats

> Source: **NRP - Nrp Performance Drilldown** dashboard, chapter **Transaction Stats** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Resource Type Read Count

### Resource Type Read Count

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Transaction Stats > Resource Type Read Count`

```kusto
let batchManagerTransactionStats = cluster("nrp.kusto.windows.net").database("mdsnrp").BatchTransactionManagerEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where Region == region
| where SubscriptionId == subscriptionId
| where EventCode == "DisposingKvsTransaction"
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| parse Message with *"ResourceTypeBasedReadCount:"resourceReadCount
| extend SplitResources = split(resourceReadCount, ";")
| project PreciseTimeStamp, OperationId, SplitResources, OperationName, SourceAssemblyFileVersion, SubscriptionId, Region
| mv-expand SplitResources
| where SplitResources contains ":"
| extend readParts = split(SplitResources, ":")
| extend resourceType = readParts[0]
| extend readCount = toint(readParts[1])
| extend transactionOwner = strcat("Batch Manager Queue ", OperationName)
| extend transactionInstance = OperationId
| project transactionOwner, transactionInstance, resourceType, readCount, SourceAssemblyFileVersion, SubscriptionId, PreciseTimeStamp, Region;
let frontendTransactionStats = cluster("nrp.kusto.windows.net").database("mdsnrp").FrontendOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where Region == region
| where SubscriptionId == subscriptionId
| where EventCode == "DisposingKvsTransaction"
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| parse Message with *"ResourceTypeBasedReadCount:"resourceReadCount
| extend SplitResources = split(resourceReadCount, ";")
| project PreciseTimeStamp, OperationId, SplitResources, OperationName, SourceAssemblyFileVersion, SubscriptionId, Region
| mv-expand SplitResources
| where SplitResources contains ":"
| extend readParts = split(SplitResources, ":")
| extend resourceType = readParts[0]
| extend readCount = toint(readParts[1])
| extend transactionOwner = strcat("FrontendOp ", OperationName)
| extend transactionInstance = OperationId
| project transactionOwner, transactionInstance, resourceType, readCount, SourceAssemblyFileVersion, SubscriptionId, PreciseTimeStamp, Region;
let readOpTransactionStats = cluster("nrp.kusto.windows.net").database("mdsnrp").FrontendReadOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where Region == region
| where SubscriptionId == subscriptionId
| where EventCode == "DisposingKvsTransaction"
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| parse Message with *"ResourceTypeBasedReadCount:"resourceReadCount
| extend SplitResources = split(resourceReadCount, ";")
| project PreciseTimeStamp, OperationId, SplitResources, OperationName, SourceAssemblyFileVersion, SubscriptionId, Region
| mv-expand SplitResources
| where SplitResources contains ":"
| extend readParts = split(SplitResources, ":")
| extend resourceType = readParts[0]
| extend readCount = toint(readParts[1])
| extend transactionOwner = strcat("ReadOp ", OperationName)
| extend transactionInstance = OperationId
| project transactionOwner, transactionInstance, resourceType, readCount, SourceAssemblyFileVersion, SubscriptionId, PreciseTimeStamp, Region;
readOpTransactionStats
| union batchManagerTransactionStats
| union frontendTransactionStats
| summarize sum(readCount) by tostring(resourceType), transactionOwner
```

**Params:** `{subscriptionId}`, `{region}`, `{operationId}`, `{correlationId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `EventCode == "DisposingKvsTransaction"` · `SplitResources contains ":"`

---

## Transaction Stats

### Transaction Stats

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Transaction Stats > Transaction Stats`

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
| project transactionOwner, transactionInstance, readCount, readSize, addCount, addSize, updateCount, updateSize, deleteCount, TransactionCacheHit, TransactionCacheMiss, GlobalCacheHit, GlobalCacheMiss, SourceAssemblyFileVersion, SubscriptionId, PreciseTimeStamp, Region;
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
| project transactionOwner, transactionInstance, readCount, readSize, addCount, addSize, updateCount, updateSize, deleteCount, TransactionCacheHit, TransactionCacheMiss, GlobalCacheHit, GlobalCacheMiss, SourceAssemblyFileVersion, SubscriptionId, PreciseTimeStamp, Region;
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
| project transactionOwner, transactionInstance, readCount, readSize, addCount, addSize, updateCount, updateSize, deleteCount, TransactionCacheHit, TransactionCacheMiss, GlobalCacheHit, GlobalCacheMiss, SourceAssemblyFileVersion, SubscriptionId, PreciseTimeStamp, Region;
readOpTransactionStats
| union batchManagerTransactionStats
| union frontendTransactionStats
| summarize count(), sum(toint(readSize)), sum(toint(addSize)), sum(toint(updateSize)), sum(toint(TransactionCacheHit)), sum(toint(TransactionCacheMiss)), sum(toint(GlobalCacheHit)), sum(toint(GlobalCacheMiss)) by transactionOwner, transactionInstance, SubscriptionId
| summarize count(), ReadSize=sum(sum_readSize), WriteSize=sum(sum_addSize)+sum(sum_updateSize), TransactionCacheHits=sum(sum_TransactionCacheHit), TransactionCacheMisses=sum(sum_TransactionCacheMiss), GlobalCacheHits=sum(sum_GlobalCacheHit), GlobalCacheMisses=sum(sum_GlobalCacheMiss) by transactionOwner, SubscriptionId
| order by ReadSize
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `EventCode == "DisposingKvsTransaction"`

---
