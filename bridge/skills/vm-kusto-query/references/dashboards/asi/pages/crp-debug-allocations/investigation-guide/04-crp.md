# CRP

> Source: **CRP Debug Allocations Investigation Guide** dashboard, chapter **CRP** (5 queries across 5 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query Operation from ApiQosEvent

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`
Source panel: `CRP`

```kusto
ApiQosEvent
//| where PreciseTimeStamp between(queryFrom .. queryTo)
| where operationId == queryOperationId
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend endTime = PreciseTimeStamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOperationId}`

---

## Allocation

### CRP Allocation Request 

_Widget purpose:_ Allocation

Cluster: `azcrp` · Database: `crp_allprod` · Type: `MultiRow` · Widget: `Card`
Source panel: `CRP > Allocation`

```kusto
ComputeAllocationActivity
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where activityId == queryOperationId
| where activityName in ("AllocateStarted", "StampOrdering", "OverallComputeAllocation")
| summarize arg_max(PreciseTimeStamp, activitySuccess, resultDetails, extraInfo) by activityName 
| extend value = case(activityName == "AllocateStarted", parse_json(extraInfo), resultDetails)
| extend name = case (activityName == "AllocateStarted", "Allocation Request", 
    activityName == "StampOrdering", "Stamp Ordering Result", 
    activityName == "OverallComputeAllocation", "Allocation Result", 
    "")
| where isnotempty(name)    
| where isnotempty(name)    
| project name, value
| evaluate pivot(name, take_any(value))
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOperationId}`

---

## Allocations from this Operation

### Query Allocations from AllocatorAllocationResult

_Widget purpose:_ Allocations from this Operation

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `CRP > Allocations from this Operation`

```kusto
AllocatorAllocationResult
| where activityId == "e4fe13ce-e85d-4a4e-9ade-1bca96c51cb5"
| project PreciseTimeStamp, Cluster, allocationId, allocationRequestType, tenantName, isSucceeded, containersRequested, containersAllocated, containersToSuspend, totalTime, allocationFault
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryActivityId}`

**Signal filters seen in KQL:** `activityId == "e4fe13ce-e85d-4a4e-9ade-1bca96c51cb5"`

---

## Cluster Filtering in ComputeAllocationActivity

### Stamp Filtering in ComputeAllocationActivity

_Widget purpose:_ Cluster Filtering in ComputeAllocationActivity

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `CRP > Cluster Filtering in ComputeAllocationActivity > Cluster Filtering in ComputeAllocationActivity`

```kusto
ComputeAllocationActivity
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where activityId == queryOperationId
| order by PreciseTimeStamp asc
| where isnotempty( computeStamp) and isnotempty(errorCode)
| where activitySuccess == bool(False)
| summarize cluster_list = make_set(computeStamp) by errorCode
| extend number_of_cluster =  array_length(cluster_list)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOperationId}`

---

## Details Logs

### Query Allocation Activity

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `CRP > Details Logs`

```kusto
ComputeAllocationActivity
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where activityId == queryActivityId
| extend Message = resultDetails
| project PreciseTimeStamp, overallAllocationSuccess, activitySuccess, activityName, computeStamp, errorCode, 
    Message, activityId, subscriptionId, tenantName, extraInfo
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryActivityId}`

---
