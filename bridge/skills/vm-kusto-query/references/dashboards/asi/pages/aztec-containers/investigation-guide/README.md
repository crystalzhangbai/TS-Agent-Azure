# Aztec Containers Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Aztec Containers Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 10 queries
- [Change Profiling Events](02-change-profiling-events.md) — 1 queries
- [Container Isolation & Role Instance Cleanup](03-container-isolation-role-instance-cleanup.md) — 2 queries
- [Container State](04-container-state.md) — 3 queries
- [Counters](05-counters.md) — 1 queries
- [Eviction](06-eviction.md) — 1 queries
- [Fault Handling Container Recovery Event](07-fault-handling-container-recovery-event.md) — 1 queries
- [Guest Agent Events](08-guest-agent-events.md) — 1 queries
- [Guest Agent Generic Logs](09-guest-agent-generic-logs.md) — 1 queries
- [Networking](10-networking.md) — 2 queries
- [Reuse Rejection Reason](11-reuse-rejection-reason.md) — 1 queries
- [Service Healing](12-service-healing.md) — 3 queries
- [Sla Measurement Event](13-sla-measurement-event.md) — 1 queries
- [TMMgmtContainerTraceEtwTable](14-tmmgmtcontainertraceetwtable.md) — 1 queries
- [TMMgmtLeaseManagerEtwTable](15-tmmgmtleasemanageretwtable.md) — 1 queries

**Total queries: 30**

## Query index (by file)

### (top-level)

- Retrieve Resource "Containers" — see [01-top-level.md](01-top-level.md)
- Lookup AzCompute Shoebox Account — see [01-top-level.md](01-top-level.md)
- Lookup AzNw Region Code — see [01-top-level.md](01-top-level.md)
- VM Context — see [01-top-level.md](01-top-level.md)
- Node TOR Info — see [01-top-level.md](01-top-level.md)
- VM Impacting Events — see [01-top-level.md](01-top-level.md)
- VMA — see [01-top-level.md](01-top-level.md)
- Air Managed Events — see [01-top-level.md](01-top-level.md)
- Query DCMNMAgentProgrammingDurationEtwTable — see [01-top-level.md](01-top-level.md)
- Container DNS Queries — see [01-top-level.md](01-top-level.md)

### Change Profiling Events

- Change Profiling Events — see [02-change-profiling-events.md](02-change-profiling-events.md)

### Container Isolation & Role Instance Cleanup

- Query TMMgmtContainerIsolationStatusEtwTable — see [03-container-isolation-role-instance-cleanup.md](03-container-isolation-role-instance-cleanup.md)
- Container Role Instance Cleanup Events — see [03-container-isolation-role-instance-cleanup.md](03-container-isolation-role-instance-cleanup.md)

### Container State

- AggregateState — see [04-container-state.md](04-container-state.md)
- Query LogContainerHealthSnapshot by ContainerId — see [04-container-state.md](04-container-state.md)
- Query LogRoleInstanceSnapshot — see [04-container-state.md](04-container-state.md)

### Counters

- Container Counters — see [05-counters.md](05-counters.md)

### Eviction

- Query LowPriorityVmPreemptionEvent — see [06-eviction.md](06-eviction.md)

### Fault Handling Container Recovery Event

- Fault Handling Container Recovery Event — see [07-fault-handling-container-recovery-event.md](07-fault-handling-container-recovery-event.md)

### Guest Agent Events

- Container Guest Agent Extension Events — see [08-guest-agent-events.md](08-guest-agent-events.md)

### Guest Agent Generic Logs

- Container Guest Agent Generic Logs — see [09-guest-agent-generic-logs.md](09-guest-agent-generic-logs.md)

### Networking

- Get Container Info — see [10-networking.md](10-networking.md)
- Container NMAgent — see [10-networking.md](10-networking.md)

### Reuse Rejection Reason

- Container Reuse Rejection Reason — see [11-reuse-rejection-reason.md](11-reuse-rejection-reason.md)

### Service Healing

- Container Service Healing Not Triggered Reasons — see [12-service-healing.md](12-service-healing.md)
- Service Healing Result Events — see [12-service-healing.md](12-service-healing.md)
- Service Healing - TriggeredFaultReason — see [12-service-healing.md](12-service-healing.md)

### Sla Measurement Event

- Sla Measurement Event — see [13-sla-measurement-event.md](13-sla-measurement-event.md)

### TMMgmtContainerTraceEtwTable

- Query TMMgmtContainerTraceEtwTable — see [14-tmmgmtcontainertraceetwtable.md](14-tmmgmtcontainertraceetwtable.md)

### TMMgmtLeaseManagerEtwTable

- Query TMMgmtLeaseManagerEtwTable — see [15-tmmgmtleasemanageretwtable.md](15-tmmgmtleasemanageretwtable.md)
