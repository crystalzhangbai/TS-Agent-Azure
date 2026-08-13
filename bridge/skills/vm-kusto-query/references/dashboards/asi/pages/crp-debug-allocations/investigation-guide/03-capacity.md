# Capacity

> Source: **CRP Debug Allocations Investigation Guide** dashboard, chapter **Capacity** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Request VM Size

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Single` · Widget: `Card`
Source panel: `Capacity`

```kusto
AllocatorContainerRequestTrait
| where allocationId == queryAllocationId
| where name == "OfferingName"
| top 1 by PreciseTimeStamp asc
| project value
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

**Signal filters seen in KQL:** `name == "OfferingName"`

---

## Capacity from AllocatorMonitoringLogAllocableVMCount

### Query AllocatorMonitoringLogAllocableVMCount

_Widget purpose:_ Capacity from AllocatorMonitoringLogAllocableVMCount

Cluster: `azureallocator.westcentralus` · Database: `azureallocator` · Type: `Table`
Source panel: `Capacity > Capacity from AllocatorMonitoringLogAllocableVMCount`

```kusto
AllocatorMonitoringLogAllocableVMCount
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where partitionType == "Cluster"
| where vmType =~ queryVMSize
| where Cluster =~ queryCluster
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, Cluster, priority, deploymentType, vmCount, Tenant = partitionName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVMSize}`, `{queryCluster}`

**Signal filters seen in KQL:** `partitionType == "Cluster"`

---
