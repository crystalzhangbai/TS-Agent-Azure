# CRP Debug Allocations Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **CRP Debug Allocations Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

**How to use:**

1. Identify which dashboard chapter matches what you're investigating.
2. Open the matching section file from the list below.
3. Pick the query whose name / source panel / filter tips match your symptom.
4. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.
5. Execute via the **vm-kusto-query** skill (`kusto_runner.py`) or via the `replay.py` next to this folder (handles param aliases).

**Companion files (in parent folder):**

- `library.json` — canonical machine-readable source of all queries (panel-organized).
- `library.md`   — same content as flat human-readable index.
- `meta.json`    — pageId, totals, ASI URL.

## Files

- [(top-level)](01-top-level.md) — 1 queries
- [AzAllocator](02-azallocator.md) — 12 queries
- [Capacity](03-capacity.md) — 2 queries
- [CRP](04-crp.md) — 5 queries

**Total queries: 20**

## Query index (by file)

### (top-level)

- Get Allocation from AllocatorAllocationResult — see [01-top-level.md](01-top-level.md)

### AzAllocator

- Get Allocation Request Trait — see [02-azallocator.md](02-azallocator.md)
- Query AllocatorActiveClusterSelectionRules — see [02-azallocator.md](02-azallocator.md)
- Cluster Select Results — see [02-azallocator.md](02-azallocator.md)
- Get Rejected Clusters — see [02-azallocator.md](02-azallocator.md)
- Query AllocatorContainerReuseStep — see [02-azallocator.md](02-azallocator.md)
- Query Allocator Container Result — see [02-azallocator.md](02-azallocator.md)
- Query AllocatorContainerReuseRejectionReason — see [02-azallocator.md](02-azallocator.md)
- Query AllocatorClusterSelectionNodeLimitCheckInfo — see [02-azallocator.md](02-azallocator.md)
- Query AllocatorClusterSelectionUtilLimitCheckInfo — see [02-azallocator.md](02-azallocator.md)
- Query AllocatorVmLimitCheckInfo — see [02-azallocator.md](02-azallocator.md)
- Get Rejected Node Lists — see [02-azallocator.md](02-azallocator.md)
- Get Rejected Nodes — see [02-azallocator.md](02-azallocator.md)

### Capacity

- Get Request VM Size — see [03-capacity.md](03-capacity.md)
- Query AllocatorMonitoringLogAllocableVMCount — see [03-capacity.md](03-capacity.md)

### CRP

- Query Operation from ApiQosEvent — see [04-crp.md](04-crp.md)
- CRP Allocation Request  — see [04-crp.md](04-crp.md)
- Query Allocations from AllocatorAllocationResult — see [04-crp.md](04-crp.md)
- Stamp Filtering in ComputeAllocationActivity — see [04-crp.md](04-crp.md)
- Query Allocation Activity — see [04-crp.md](04-crp.md)
