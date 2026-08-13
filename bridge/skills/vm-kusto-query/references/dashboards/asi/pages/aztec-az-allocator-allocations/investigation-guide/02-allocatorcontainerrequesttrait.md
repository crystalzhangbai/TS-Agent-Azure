# AllocatorContainerRequestTrait 

> Source: **Aztec AzAllocatorAllocations Investigation Guide** dashboard, chapter **AllocatorContainerRequestTrait ** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query AllocatorContainerRequestTrait

_Widget purpose:_ AllocatorContainerRequestTrait 

Cluster: `AzureAllocator.westcentralus` · Database: `AzureAllocator` · Type: `Table`
Source panel: `AllocatorContainerRequestTrait `

```kusto
AllocatorContainerRequestTrait
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where  allocationId == queryAllocationId
| project PreciseTimeStamp, containerRequestId, name, value
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---
