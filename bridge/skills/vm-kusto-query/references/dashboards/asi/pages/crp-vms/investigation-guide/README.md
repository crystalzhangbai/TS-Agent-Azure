# CRP — VMs — Investigation Guide

Chapter-keyed reference derived from the **CRP — VMs** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 9 queries
- [Allocation Info (Goal Seek State)](02-allocation-info-goal-seek-state.md) — 3 queries
- [Container Transition](03-container-transition.md) — 3 queries
- [Containers](04-containers.md) — 1 queries
- [Counters](05-counters.md) — 1 queries
- [CRP Operations in ApiQosEvent](06-crp-operations-in-apiqosevent.md) — 2 queries
- [Disks from CRP BI](07-disks-from-crp-bi.md) — 1 queries
- [MeteredUsageEvent ](08-meteredusageevent.md) — 1 queries
- [Networking](09-networking.md) — 2 queries
- [ResourceHealthAzureActivityLogEvent](10-resourcehealthazureactivitylogevent.md) — 1 queries
- [Scheduled Events](11-scheduled-events.md) — 1 queries

**Total queries: 25**

## Query index (by file)

### (top-level)

- Retrieve Resource "VMs" — see [01-top-level.md](01-top-level.md)
- Get AzCoreSpoke — see [01-top-level.md](01-top-level.md)
- Query VM Placement History — see [01-top-level.md](01-top-level.md)
- CRP-SingleVM-NetworkProfile — see [01-top-level.md](01-top-level.md)
- VMAllocationInfo — see [01-top-level.md](01-top-level.md)
- Query VM Extension — see [01-top-level.md](01-top-level.md)
- Query VMs in AvailabilitySet — see [01-top-level.md](01-top-level.md)
- query Communications in AlbnTargets — see [01-top-level.md](01-top-level.md)
- Examine VM by ContainerId — see [01-top-level.md](01-top-level.md)

### Allocation Info (Goal Seek State)

- GoalState — see [02-allocation-info-goal-seek-state.md](02-allocation-info-goal-seek-state.md)
- Error from AllocationInfo — see [02-allocation-info-goal-seek-state.md](02-allocation-info-goal-seek-state.md)
- VMAllocationInfo Details — see [02-allocation-info-goal-seek-state.md](02-allocation-info-goal-seek-state.md)

### Container Transition

- ContainerStateTransition — see [03-container-transition.md](03-container-transition.md)
- ContainerOSStateTransition — see [03-container-transition.md](03-container-transition.md)
- Get Extended Container Error Details — see [03-container-transition.md](03-container-transition.md)

### Containers

- VM Fabric Containers — see [04-containers.md](04-containers.md)

### Counters

- VM Counters — see [05-counters.md](05-counters.md)

### CRP Operations in ApiQosEvent

- FilterOperations — see [06-crp-operations-in-apiqosevent.md](06-crp-operations-in-apiqosevent.md)
- Query VM Operations in ApiQosEvent — see [06-crp-operations-in-apiqosevent.md](06-crp-operations-in-apiqosevent.md)

### Disks from CRP BI

- Query VMManagedDisksAllocationInfo — see [07-disks-from-crp-bi.md](07-disks-from-crp-bi.md)

### MeteredUsageEvent 

- Query MeteredUsageEvent — see [08-meteredusageevent.md](08-meteredusageevent.md)

### Networking

- CRP-SingleVM-NetworkProfile — see [09-networking.md](09-networking.md)
- CRP-SingleVM-NetworkProfile-Expand — see [09-networking.md](09-networking.md)

### ResourceHealthAzureActivityLogEvent

- Query ResourceHealthAzureActivityLogEvent — see [10-resourcehealthazureactivitylogevent.md](10-resourcehealthazureactivitylogevent.md)

### Scheduled Events

- Query Scheduled Events in AzPEWorkflowEvent — see [11-scheduled-events.md](11-scheduled-events.md)
