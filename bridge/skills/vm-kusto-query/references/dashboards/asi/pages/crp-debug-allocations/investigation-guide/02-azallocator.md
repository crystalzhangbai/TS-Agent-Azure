# AzAllocator

> Source: **CRP Debug Allocations Investigation Guide** dashboard, chapter **AzAllocator** (12 queries across 5 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Allocation Request Traits

### Get Allocation Request Trait

_Widget purpose:_ Allocation Request Traits

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Allocation Request Traits > Allocation Request Traits`

```kusto
union withsource=SourceTable AllocatorServiceRequestTrait, AllocatorContainerRequestTrait
| where allocationId == queryAllocationId
| project SourceTable, containerRequestId, name, value
| order by SourceTable, name
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

## Cluster Selection

### Query AllocatorActiveClusterSelectionRules

_Widget purpose:_ ActiveClusterSelectionRules 

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Cluster Selection > ActiveClusterSelectionRules `

```kusto
AllocatorActiveClusterSelectionRules
| where allocationId == queryAllocationId
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

### Cluster Select Results

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Cluster Selection > Cluster Select Results`

```kusto
AllocatorClusterSelectionResult
| where allocationId == queryAllocationId
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

### Get Rejected Clusters

_Widget purpose:_ Rejected Clusters from AllocatorRejectedClusterInfo

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Cluster Selection > Rejected Clusters from AllocatorRejectedClusterInfo`

```kusto
AllocatorRejectedClusterInfo
| where allocationId == queryAllocationId
| project PreciseTimeStamp, allocationId, containerRequestId, rejectedClusterListId, reason
| join kind=inner (
    AllocatorClusterListToClusterMap
    | project allocationId, rejectedClusterListId = clusterListId, rejectedClusters = clusterNames)
    on rejectedClusterListId, allocationId
| project-away rejectedClusterListId1, allocationId1
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

## Container Steps & Reuse

### Query AllocatorContainerReuseStep

_Widget purpose:_ AllocatorContainerReuseStep 

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Container Steps & Reuse > AllocatorContainerReuseStep `

```kusto
AllocatorContainerReuseStep
| where allocationId == queryAllocationId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

### Query Allocator Container Result

_Widget purpose:_ Container Results

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Container Steps & Reuse > Container Results`

```kusto
AllocatorContainerResult
| where allocationId == queryAllocationId
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

### Query AllocatorContainerReuseRejectionReason

_Widget purpose:_ Container Reuse Rejection Reason

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Container Steps & Reuse > Container Reuse Rejection Reason`

```kusto
AllocatorContainerReuseRejectionReason
| where allocationId == queryAllocationId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

## Limit Checks

### Query AllocatorClusterSelectionNodeLimitCheckInfo

_Widget purpose:_ AllocatorClusterSelectionNodeLimitCheckInfo

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Limit Checks > AllocatorClusterSelectionNodeLimitCheckInfo`

```kusto
AllocatorClusterSelectionNodeLimitCheckInfo
| where allocationId == queryAllocationId
| project PreciseTimeStamp, containerRequestId, clusterName, scope, isScaleUp, henCountToReserve, henReturnedByContainersToBeDeleted, adjustedHenCount, flightingNodeLimit, adjustedFlightingNodeCount, allocationRetryNumber, batchNumber, canUseReservedSlot, containerAllocationWorkflowStep
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

### Query AllocatorClusterSelectionUtilLimitCheckInfo

_Widget purpose:_ AllocatorClusterSelectionUtilLimitCheckInfo

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Limit Checks > AllocatorClusterSelectionUtilLimitCheckInfo`

```kusto
AllocatorClusterSelectionUtilLimitCheckInfo
| where allocationId == queryAllocationId
| project PreciseTimeStamp, Cluster, containerRequestId, clusterName, scope, isScaleUp, resourceName = resurceName, resourceReturnedByContainersToBeDeleted, resourceTotal,adjustedResourceUsed, allocationRetryNumber, batchNumber, canUseReservedSlot, containerAllocationWorkflowStep
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

### Query AllocatorVmLimitCheckInfo

_Widget purpose:_ VmLimitCheckInfo

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Single` · Widget: `Card`
Source panel: `AzAllocator > Limit Checks > VmLimitCheckInfo`

```kusto
AllocatorVmLimitCheckInfo
| where allocationId == queryAllocationId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

## Node Selection

### Get Rejected Node Lists

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Node Selection > Rejected Node Lists`

```kusto
AllocatorRejectedNodeInfo
| where allocationId == queryAllocationId
| project PreciseTimeStamp, allocationId, ruleName, reason, nodeCount, rejectedNodeListId
| join kind = leftouter (
    AllocatorRejectedNodeList
    | where allocationId == queryAllocationId
    | project allocationId, rejectedNodeListId, nodeIds
) on allocationId, rejectedNodeListId
| project-away allocationId1, rejectedNodeListId1
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---

### Get Rejected Nodes

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `AzAllocator > Node Selection > Rejected Nodes`

```kusto
AllocatorNodeRejectionReasons(queryAllocationId)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---
