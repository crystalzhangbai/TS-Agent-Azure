# (top-level)

> Source: **NRP - Batch Manager & NRP Performance Drill Down** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Top 10 Lock Contention Sources

_Widget purpose:_ Top 10 Sources Of Lock Contention

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `MultiRow` · Widget: `Card`

```kusto
cluster('nrp').database('mdsnrp').FrontendOperationEtwEvent
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where Region == region
| where EventCode == "ResourceLockingTransactionAquisitionFailure"
| parse Message with "Failed to aquire resource lock on " ResourceId " in job with JobId " FailingJobId ", JobName " FailingJobName ", and operation id " OperationIdOfLockFailure ", going to restart job on lock aquisition. Lock was last acquired by operation id " OwningOperationId ". Inner Exception " Exception " and owningJobName " owningJobName: string
| extend owningJobName = extract("^(.*?)(\\s|$)", 1, owningJobName)
| extend resourceType = extract(@"/providers/Microsoft\.(Network|Compute)/([^/]+)/", 2, ResourceId)
| extend resourceType = iff(isnull(resourceType), "subscriptions", resourceType)
| where resourceType != "privateIpAllocatorHeads"
| summarize dcount(FailingJobId) by FailingJobName, owningJobName,resourceType
| order by dcount_FailingJobId desc 
| take 10
```

**Params:** `{startTime}`, `{endTime}`, `{region}`

**Signal filters seen in KQL:** `EventCode == "ResourceLockingTransactionAquisitionFailure"` · `resourceType != "privateIpAllocatorHeads"`

---
