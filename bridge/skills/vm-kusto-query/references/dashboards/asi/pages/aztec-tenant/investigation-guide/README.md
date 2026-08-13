# Aztec — Tenant — Investigation Guide

Chapter-keyed reference derived from the **Aztec — Tenant** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 3 queries
- [Allocations](02-allocations.md) — 8 queries
- [ApiUnexpectedFailures IcMs](03-apiunexpectedfailures-icms.md) — 1 queries
- [At-A-Glance Health](04-at-a-glance-health.md) — 8 queries
- [AzPE](05-azpe.md) — 4 queries
- [AzSM](06-azsm.md) — 1 queries
- [AzSM Events & Traces](07-azsm-events-traces.md) — 8 queries
- [Cleanup](08-cleanup.md) — 5 queries
- [Containers](09-containers.md) — 6 queries
- [Jobs](10-jobs.md) — 2 queries
- [RNM & NSM Logs](11-rnm-nsm-logs.md) — 3 queries
- [Service Healing](12-service-healing.md) — 6 queries
- [Target Resource](13-target-resource.md) — 1 queries
- [Tenant  SLA & UD Walk](14-tenant-sla-ud-walk.md) — 5 queries
- [Tenant Logs](15-tenant-logs.md) — 4 queries
- [Tenant QoS](16-tenant-qos.md) — 9 queries
- [Tenant Settings](17-tenant-settings.md) — 2 queries
- [VIPs](18-vips.md) — 1 queries

**Total queries: 77**

## Query index (by file)

### (top-level)

- Retrieve Resource "Tenants" — see [01-top-level.md](01-top-level.md)
- Tenant Features — see [01-top-level.md](01-top-level.md)
- Tenant AzSM Features — see [01-top-level.md](01-top-level.md)

### Allocations

- Query AllocatorAllocationResult — see [02-allocations.md](02-allocations.md)
- Query AllocatorClusterSelectionResult — see [02-allocations.md](02-allocations.md)
- Query AllocatorContainerResult — see [02-allocations.md](02-allocations.md)
- AllocatorContainerReuseRejectionReason — see [02-allocations.md](02-allocations.md)
- Query AllocatorRejectedClusterInfo — see [02-allocations.md](02-allocations.md)
- AllocatorRejectedNodeInfo — see [02-allocations.md](02-allocations.md)
- AzAllocatorClientEvents — see [02-allocations.md](02-allocations.md)
- Query ComputeAllocationActivity — see [02-allocations.md](02-allocations.md)

### ApiUnexpectedFailures IcMs

- Query ApiUnexpectedFailures in IcMDataWarehouse — see [03-apiunexpectedfailures-icms.md](03-apiunexpectedfailures-icms.md)

### At-A-Glance Health

- Tenant Upgrade Rollouts — see [04-at-a-glance-health.md](04-at-a-glance-health.md)
- Tenant Container Health Faults — see [04-at-a-glance-health.md](04-at-a-glance-health.md)
- VMA — see [04-at-a-glance-health.md](04-at-a-glance-health.md)
- ICM Outages — see [04-at-a-glance-health.md](04-at-a-glance-health.md)
- FC Downtime — see [04-at-a-glance-health.md](04-at-a-glance-health.md)
- FC Failover — see [04-at-a-glance-health.md](04-at-a-glance-health.md)
- Tenant State — see [04-at-a-glance-health.md](04-at-a-glance-health.md)
- Explode LogContainerHealthSnapshot ExtendedDetails — see [04-at-a-glance-health.md](04-at-a-glance-health.md)

### AzPE

- AzPETenantSnapshot — see [05-azpe.md](05-azpe.md)
- Query AzPEWorkflowEvent — see [05-azpe.md](05-azpe.md)
- Query MREvents — see [05-azpe.md](05-azpe.md)
- AzPENotificationStepResultEvents — see [05-azpe.md](05-azpe.md)

### AzSM

- Get Tenant AzSM Application — see [06-azsm.md](06-azsm.md)

### AzSM Events & Traces

- Query AzSMExceptionsEvents — see [07-azsm-events-traces.md](07-azsm-events-traces.md)
- Query AzSMServiceTracesEvents — see [07-azsm-events-traces.md](07-azsm-events-traces.md)
- FilterMessages — see [07-azsm-events-traces.md](07-azsm-events-traces.md)
- Tenant AzSM State Machine Events — see [07-azsm-events-traces.md](07-azsm-events-traces.md)
- FilterMessages — see [07-azsm-events-traces.md](07-azsm-events-traces.md)
- Tenant AzSM State Machine Events timeline — see [07-azsm-events-traces.md](07-azsm-events-traces.md)
- Tenant AzSM Events — see [07-azsm-events-traces.md](07-azsm-events-traces.md)
- Query AzSMUpdateTenantEvents — see [07-azsm-events-traces.md](07-azsm-events-traces.md)

### Cleanup

- Tenant AzSM Cleanup Events — see [08-cleanup.md](08-cleanup.md)
- Query FRIC from RnmOperationEvents — see [08-cleanup.md](08-cleanup.md)
- Query LogRoleInstanceCleanupEvent by TenantName — see [08-cleanup.md](08-cleanup.md)
- Rnm Operation Events — see [08-cleanup.md](08-cleanup.md)
- Tenant Cleanup Events — see [08-cleanup.md](08-cleanup.md)

### Containers

- AggregateState — see [09-containers.md](09-containers.md)
- Query LogContainerHealthSnapshot — see [09-containers.md](09-containers.md)
- Container Health — see [09-containers.md](09-containers.md)
- Tenant Containers — see [09-containers.md](09-containers.md)
- Tenant Instance Count — see [09-containers.md](09-containers.md)
- RoleState for PaaS Containers — see [09-containers.md](09-containers.md)

### Jobs

- Query TMMgmtMRJobSnapshotEtwTable — see [10-jobs.md](10-jobs.md)
- Tenant Job Info — see [10-jobs.md](10-jobs.md)

### RNM & NSM Logs

- Query DeleteResourceEvent — see [11-rnm-nsm-logs.md](11-rnm-nsm-logs.md)
- Query ResourceReleaseEvent — see [11-rnm-nsm-logs.md](11-rnm-nsm-logs.md)
- Query ServiceExecutionEvent — see [11-rnm-nsm-logs.md](11-rnm-nsm-logs.md)

### Service Healing

- AzSMServiceHealingStepResultEvents — see [12-service-healing.md](12-service-healing.md)
- AzSMServiceHealingResultEvents — see [12-service-healing.md](12-service-healing.md)
- AzSMServiceHealingStepResultEvents — see [12-service-healing.md](12-service-healing.md)
- AzSMServiceHealingTriggerEvents — see [12-service-healing.md](12-service-healing.md)
- Query ServiceHealingTenantStatusEtwTable — see [12-service-healing.md](12-service-healing.md)
- Query ServiceHealingTriggerEtwTable — see [12-service-healing.md](12-service-healing.md)

### Target Resource

- Locate Resource by Tenant Name — see [13-target-resource.md](13-target-resource.md)

### Tenant  SLA & UD Walk

- Tenant Change Profiling Events — see [14-tenant-sla-ud-walk.md](14-tenant-sla-ud-walk.md)
- Qury TMMgmtSlaMeasurementEventEtwTable — see [14-tenant-sla-ud-walk.md](14-tenant-sla-ud-walk.md)
- Query TMMgmtHighLatencyUDWalkEtwTable — see [14-tenant-sla-ud-walk.md](14-tenant-sla-ud-walk.md)
- Query TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable — see [14-tenant-sla-ud-walk.md](14-tenant-sla-ud-walk.md)
- Query TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable — see [14-tenant-sla-ud-walk.md](14-tenant-sla-ud-walk.md)

### Tenant Logs

- Query all TMMgmtNodeEventsEtwTable in the one tenant — see [15-tenant-logs.md](15-tenant-logs.md)
- TenantAuditEvents — see [15-tenant-logs.md](15-tenant-logs.md)
- Query TMMgmtTenantEventsEtwTable — see [15-tenant-logs.md](15-tenant-logs.md)
- Tenant Logs — see [15-tenant-logs.md](15-tenant-logs.md)

### Tenant QoS

- Query TMClusterFabricAuditEtwTable — see [16-tenant-qos.md](16-tenant-qos.md)
- FilterGetOperations — see [16-tenant-qos.md](16-tenant-qos.md)
- Query ComponentQoSEvent — see [16-tenant-qos.md](16-tenant-qos.md)
- FilterGetOperations — see [16-tenant-qos.md](16-tenant-qos.md)
- Query Operations in CommonWebOperationEnd — see [16-tenant-qos.md](16-tenant-qos.md)
- FilterGetOperations — see [16-tenant-qos.md](16-tenant-qos.md)
- Query GatewayRequestCompleted — see [16-tenant-qos.md](16-tenant-qos.md)
- Query GatewayServiceTraceEvent — see [16-tenant-qos.md](16-tenant-qos.md)
- FilterMessages — see [16-tenant-qos.md](16-tenant-qos.md)

### Tenant Settings

- Query AzPETenantSettingsSnapshot — see [17-tenant-settings.md](17-tenant-settings.md)
- Query LogTenantOverridableSettingsSnapshot — see [17-tenant-settings.md](17-tenant-settings.md)

### VIPs

- Tenant VIPs — see [18-vips.md](18-vips.md)
