# (top-level)

> Source: **CRP Debug Allocations Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Allocation from AllocatorAllocationResult

_Widget purpose:_ Debug Allocations {{allocationId}}

Cluster: `azureallocator.westcentralus` · Database: `AzureAllocator` · Type: `Single` · Widget: `Container`

```kusto
AllocatorAllocationResult
| where allocationId == queryAllocationId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAllocationId}`

---
