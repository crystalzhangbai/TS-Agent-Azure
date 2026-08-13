# Allocations

> Source: **Aztec — Tenant** dashboard, chapter **Allocations** (8 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Allocations

### Query AllocatorAllocationResult

_Widget purpose:_ AllocatorAllocationResult

Cluster: `https://azureallocator.westcentralus.kusto.windows.net` · Database: `Azureallocator` · Type: `Table`
Source panel: `Allocations > Allocations > Allocator > Allocator > AllocatorAllocationResult`

```kusto
AllocatorAllocationResult
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where tenantName == queryTenantName
| extend level = case(
    isSucceeded == "False", "Error",
    "Info"
) 
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query AllocatorClusterSelectionResult

_Widget purpose:_ AllocatorClusterSelectionResult

Cluster: `azureallocator.westcentralus.kusto.windows.net` · Database: `AzureAllocator` · Type: `Table`
Source panel: `Allocations > Allocations > Allocator > Allocator > AllocatorClusterSelectionResult`

```kusto
let listAllocationId = cluster('azureallocator.westcentralus.kusto.windows.net').database('AzureAllocator').AllocatorAllocationResult
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| distinct allocationId; 
AllocatorClusterSelectionResult
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where allocationId in (listAllocationId)
| project PreciseTimeStamp, allocationId, allocationRetryNumber, containerRequestId, allocationFault, isSucceeded, candidateClustersCount, validClusterListId, selectedClusters, totalTime
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query AllocatorContainerResult

_Widget purpose:_ AllocatorContainerResult 

Cluster: `azureallocator.westcentralus.kusto.windows.net` · Database: `AzureAllocator` · Type: `Table`
Source panel: `Allocations > Allocations > Allocator > Allocator > AllocatorContainerResult `

```kusto
let listAllocationId = cluster('azureallocator.westcentralus.kusto.windows.net').database('AzureAllocator').AllocatorAllocationResult
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| distinct allocationId;
AllocatorContainerResult
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where  allocationId in (listAllocationId)
| project PreciseTimeStamp, Tenant, allocationId, containerRequestId, containerIndex, isSucceeded, resultType, containerId, fabricCluster, nodeId, totalTime, comment
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### AllocatorContainerReuseRejectionReason

Cluster: `azureallocator.westcentralus.kusto.windows.net` · Database: `AzureAllocator` · Type: `Table`
Source panel: `Allocations > Allocations > Allocator > Allocator > AllocatorContainerReuseRejectionReason`

```kusto
let listAllocationId = cluster('azureallocator.westcentralus.kusto.windows.net').database('AzureAllocator').AllocatorAllocationResult
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| distinct allocationId;
AllocatorContainerReuseRejectionReason
| where PreciseTimeStamp between (queryFrom..queryTo)
| where allocationId in (listAllocationId)
| project PreciseTimeStamp, allocationId, containerWorkflowStep, rejectedContainerId, ruleName, reason
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query AllocatorRejectedClusterInfo

_Widget purpose:_ AllocatorRejectedClusterInfo

Cluster: `https://azureallocator.westcentralus.kusto.windows.net` · Database: `AzureAllocator` · Type: `Table`
Source panel: `Allocations > Allocations > Allocator > Allocator > AllocatorRejectedClusterInfo`

```kusto
let listAllocationId = AllocatorAllocationResult
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| distinct allocationId; 
AllocatorRejectedClusterInfo
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where allocationId in (listAllocationId)
| project PreciseTimeStamp, allocationId, containerRequestId, rejectedClusterListId, reason
| join kind=inner (
    AllocatorClusterListToClusterMap
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | project allocationId, rejectedClusterListId = clusterListId, rejectedClusters = clusterNames)
    on rejectedClusterListId, allocationId
| project-away rejectedClusterListId1, allocationId1
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### AllocatorRejectedNodeInfo

Cluster: `azureallocator.westcentralus.kusto.windows.net` · Database: `AzureAllocator` · Type: `Table`
Source panel: `Allocations > Allocations > Allocator > Allocator > AllocatorRejectedNodeInfo`

```kusto
let listAllocationId = cluster("azureallocator.westcentralus.kusto.windows.net").database("AzureAllocator").AllocatorAllocationResult
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| distinct allocationId; 
cluster("azureallocator.westcentralus.kusto.windows.net").database("AzureAllocator").AllocatorRejectedNodeInfo
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where allocationId in (listAllocationId)
| project PreciseTimeStamp, allocationId, ruleName, reason, nodeCount, rejectedNodeListId
| join kind = leftouter (
    cluster("azureallocator.westcentralus.kusto.windows.net").database("AzureAllocator").AllocatorRejectedNodeList
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where allocationId in (listAllocationId)
    | project allocationId, rejectedNodeListId, nodeIds
) on allocationId, rejectedNodeListId
| project-away allocationId1, rejectedNodeListId1
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### AzAllocatorClientEvents

_Widget purpose:_ AzAllocatorClientEvents (AzSM)

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Allocations > Allocations > AzAllocatorClient > AzAllocatorClient > AzAllocatorClientEvents (AzSM)`

```kusto
AzAllocatorClientEvents
| where PreciseTimeStamp between(queryFrom..queryTo) and tenantName == queryTenantName
| extend level = case(
    status == "AllocationFailed", "error",
    "info"
)
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### Query ComputeAllocationActivity

_Widget purpose:_ CRP - ComputeAllocationActivity

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Allocations > Allocations > AzAllocatorClient > AzAllocatorClient > CRP - ComputeAllocationActivity`

```kusto
ComputeAllocationActivity
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| project PreciseTimeStamp, computeStamp, overallAllocationSuccess,activitySuccess, errorCode, errorMessage, resultDetails, activityName, activityId
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---
