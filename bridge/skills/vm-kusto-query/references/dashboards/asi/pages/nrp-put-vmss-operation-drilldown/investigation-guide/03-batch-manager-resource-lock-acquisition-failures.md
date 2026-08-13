# Batch manager resource lock acquisition failures

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Batch manager resource lock acquisition failures** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### BatchManagerResourceLockingTransactionAquisitionFailurePerSub

_Widget purpose:_ Batch manager resource lock acquisition failures

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Batch manager resource lock acquisition failures`

```kusto
FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subId
| where EventCode == "ResourceLockingTransactionAquisitionFailure"
| parse Message with "Failed to aquire resource lock on " ResourceId " in job with JobId " FailingJobId ", JobName " FailingJobName ", and operation id " OperationIdOfLockFailure ", going to restart job on lock aquisition. Lock was last acquired by operation id " OwningOperationId ". Inner Exception " Exception " and owningJobName " owningJobName: string
| extend owningJobName = extract("^(.*?)(\\s|$)", 1, owningJobName)
| extend resourceType = extract(@"/providers/Microsoft\.(Network|Compute)/([^/]+)/", 2, ResourceId)
| extend resourceType = iff(isnull(resourceType), "subscriptions", resourceType)
| project PreciseTimeStamp,SubscriptionId, OperationId, CorrelationRequestId, OperationName, Message, FailingJobId, resourceType, FailingJobName, owningJobName
| summarize count() by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

**Signal filters seen in KQL:** `EventCode == "ResourceLockingTransactionAquisitionFailure"`

---
