# Resource Locking Summary

> Source: **NRP - Nrp Performance Drilldown** dashboard, chapter **Resource Locking Summary** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Resource Locks Acquired

### Resource Locks Acquired

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Resource Locking Summary > Resource Locks Acquired`

```kusto
let readLocks = cluster("nrp.kusto.windows.net").database("mdsnrp").BatchTransactionManagerEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == subscriptionId
| where Region == region
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance
| where Message startswith "Locking transaction with Id " and Message contains "aquired shared resource lock on"
| parse Message with "Locking transaction with Id "lockManagerId" running in job "jobId" aquired shared resource lock on "resourceIdWithNormalizedAppend
| parse resourceIdWithNormalizedAppend with resourceId" Stored under "normalizedTopLevelKey
| extend ResourceId = iff(resourceIdWithNormalizedAppend contains "Stored under", resourceId, resourceIdWithNormalizedAppend)
| parse ResourceId with "/subscriptions/"ResourceSubId"/resourceGroups/"ResourceRg"/providers/"ResourceProvider"/"ResourceType"/"ResourceName
| parse ResourceId with "/children//subscriptions/"NormResourceSubId"/resourceGroups/"NormResourceRg"/providers/"NormResourceProvider"/"NormResourceType"/"NormResourceName"/"NormChildCollection
| parse NormChildCollection with childCollection"/"childName
| parse NormChildCollection with referencingChildType"/"referencingChild"/"referenceCollection"@"referencedResource
| extend EffectiveResourceType = iff(ResourceType == "", strcat("/children/ ", NormResourceType, " ", iff(referenceCollection == "", childCollection, strcat("reference:", referencingChildType, "/", referenceCollection))), ResourceType)
| summarize count(), make_set(OperationName) by EffectiveResourceType, LockType="ReadLock";
let writeLocks = cluster("nrp.kusto.windows.net").database("mdsnrp").BatchTransactionManagerEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == subscriptionId
| where Region == region
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance
| where Message startswith "Locking transaction with Id " and Message contains "aquired resource lock on"
| parse Message with "Locking transaction with Id "lockManagerId" running in job "jobId" aquired resource lock on "resourceIdWithNormalizedAppend
| parse resourceIdWithNormalizedAppend with resourceId" Stored under "normalizedTopLevelKey
| extend ResourceId = iff(resourceIdWithNormalizedAppend contains "Stored under", resourceId, resourceIdWithNormalizedAppend)
| parse ResourceId with "/subscriptions/"ResourceSubId"/resourceGroups/"ResourceRg"/providers/"ResourceProvider"/"ResourceType"/"ResourceName
| parse ResourceId with "/children//subscriptions/"NormResourceSubId"/resourceGroups/"NormResourceRg"/providers/"NormResourceProvider"/"NormResourceType"/"NormResourceName"/"NormChildCollection
| parse NormChildCollection with childCollection"/"childName
| parse NormChildCollection with referencingChildType"/"referencingChild"/"referenceCollection"@"referencedResource
| extend EffectiveResourceType = iff(ResourceType == "", strcat("/children/ ", NormResourceType, " ", iff(referenceCollection == "", childCollection, strcat("reference:", referencingChildType, "/", referenceCollection))), ResourceType)
| summarize count(), make_set(OperationName) by EffectiveResourceType, LockType="WriteLockLock";
readLocks
| union writeLocks
```

**Params:** `{subscriptionId}`, `{region}`, `{operationId}`, `{correlationId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `Message startswith "Locking transaction with Id "`

---

## Resource Locks Acquisition Failures

### Resource Lock Acquisition Failures

_Widget purpose:_ Resource Locks Acquisition Failures

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Resource Locking Summary > Resource Locks Acquisition Failures`

```kusto
cluster('nrp').database('mdsnrp').FrontendOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == subscriptionId
| where Region == region
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance
| where EventCode == "ResourceLockingTransactionAquisitionFailure"
| parse Message with "Failed to aquire resource lock on "ResourceId" in job "JobId" with operation id "OperationIdOfLockFailure", going to restart job on lock aquisition."*
| parse ResourceId with "/subscriptions/"ResourceSubId"/resourceGroups/"ResourceRg"/providers/"ResourceProvider"/"ResourceType"/"ResourceName
| project PreciseTimeStamp, ResourceType, ResourceId, OperationId, OperationName, SourceAssemblyFileVersion
| summarize count() by ResourceType, ResourceId, OperationName
```

**Params:** `{subscriptionId}`, `{region}`, `{operationId}`, `{correlationId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `EventCode == "ResourceLockingTransactionAquisitionFailure"`

---
