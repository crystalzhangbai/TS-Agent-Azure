# EEE RDOS — WF Resource Health — Investigation Guide

Chapter-keyed reference derived from the **EEE RDOS — WF Resource Health** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [ActivityLogForProdDiagnosticPipeline](02-activitylogforproddiagnosticpipeline.md) — 2 queries
- [AzCiM/LogHealthAnnotationEvent](03-azcim-loghealthannotationevent.md) — 2 queries
- [KyberAnnotationEvent](04-kyberannotationevent.md) — 1 queries
- [KyberAnnotationEvent by VmId](05-kyberannotationevent-by-vmid.md) — 1 queries
- [KyberCoreServiceTrace](06-kybercoreservicetrace.md) — 1 queries
- [KyberGHSAnnotationEmissionEvent](07-kyberghsannotationemissionevent.md) — 1 queries
- [KyberVMAHealthSignals](08-kybervmahealthsignals.md) — 1 queries
- [KyberVmAvailabilityMetricEmission](09-kybervmavailabilitymetricemission.md) — 1 queries
- [KyberVmAvailabilityMetricEmission by VmId](10-kybervmavailabilitymetricemission-by-vmid.md) — 1 queries
- [LogContainerHealthSnapshot](11-logcontainerhealthsnapshot.md) — 2 queries
- [Node Snapshot Table](12-node-snapshot-table.md) — 1 queries
- [Node State Changes](13-node-state-changes.md) — 1 queries
- [RdAgentAzPubSubEtwTable](14-rdagentazpubsubetwtable.md) — 1 queries
- [Resource Health Unavailable for Linux 6.2 Kernel](15-resource-health-unavailable-for-linux-6-2-kernel.md) — 1 queries
- [ResourceHealthAnnotationEvent](16-resourcehealthannotationevent.md) — 1 queries
- [ResourceHealthAzureActivityLogEvent](17-resourcehealthazureactivitylogevent.md) — 1 queries
- [ResourceHealthStatusTransitionEvent](18-resourcehealthstatustransitionevent.md) — 1 queries
- [RhcAnnotationReportsEtwTable](19-rhcannotationreportsetwtable.md) — 1 queries
- [RhcWatchdogReportsErrorEtwTable](20-rhcwatchdogreportserroretwtable.md) — 1 queries
- [RoleInstanceDownTimeEvents](21-roleinstancedowntimeevents.md) — 1 queries
- [Scheduled Event Notifications](22-scheduled-event-notifications.md) — 1 queries
- [Tenant Management Events](23-tenant-management-events.md) — 1 queries
- [VM placement thru time on host node(s)](24-vm-placement-thru-time-on-host-node-s.md) — 1 queries
- [VMA](25-vma.md) — 1 queries
- [VmHealthRawStateEtwTable](26-vmhealthrawstateetwtable.md) — 1 queries
- [Windows Events for VM](27-windows-events-for-vm.md) — 1 queries

**Total queries: 32**

## Query index (by file)

### (top-level)

- Retrieve Resource "Azure VM" ResourceHealth DS — see [01-top-level.md](01-top-level.md)
- LogContainerHealthSnapshot_RH_VMId_CM — see [01-top-level.md](01-top-level.md)
- VmShoeboxCounterTable DS — see [01-top-level.md](01-top-level.md)

### ActivityLogForProdDiagnosticPipeline

- ResourceHealthAzureActivityLogEvent_UnexpectedRestart DS — see [02-activitylogforproddiagnosticpipeline.md](02-activitylogforproddiagnosticpipeline.md)
- VmShoeboxCounterTable DS — see [02-activitylogforproddiagnosticpipeline.md](02-activitylogforproddiagnosticpipeline.md)

### AzCiM/LogHealthAnnotationEvent

- LogContainerHealthSnapshot_RH_VMId_CM — see [03-azcim-loghealthannotationevent.md](03-azcim-loghealthannotationevent.md)
- LogHealthAnnotationEvent DS — see [03-azcim-loghealthannotationevent.md](03-azcim-loghealthannotationevent.md)

### KyberAnnotationEvent

- KyberAnnotationEvent — see [04-kyberannotationevent.md](04-kyberannotationevent.md)

### KyberAnnotationEvent by VmId

- kyberannotationbyvmid — see [05-kyberannotationevent-by-vmid.md](05-kyberannotationevent-by-vmid.md)

### KyberCoreServiceTrace

- KyberCoreServiceTrace — see [06-kybercoreservicetrace.md](06-kybercoreservicetrace.md)

### KyberGHSAnnotationEmissionEvent

- KyberGHSAnnotationEmissionEvent — see [07-kyberghsannotationemissionevent.md](07-kyberghsannotationemissionevent.md)

### KyberVMAHealthSignals

- KyberVMAHealthSignals — see [08-kybervmahealthsignals.md](08-kybervmahealthsignals.md)

### KyberVmAvailabilityMetricEmission

- KyberVmAvailabilityMetricEmission — see [09-kybervmavailabilitymetricemission.md](09-kybervmavailabilitymetricemission.md)

### KyberVmAvailabilityMetricEmission by VmId

- KyberVmAvailabilityMetricEmissionByVMID — see [10-kybervmavailabilitymetricemission-by-vmid.md](10-kybervmavailabilitymetricemission-by-vmid.md)

### LogContainerHealthSnapshot

- LogContainerHealthSnapshot_RH_VMId_CM — see [11-logcontainerhealthsnapshot.md](11-logcontainerhealthsnapshot.md)
- LogContainerHealthSnapshot_ResourceHealth DS — see [11-logcontainerhealthsnapshot.md](11-logcontainerhealthsnapshot.md)

### Node Snapshot Table

- LogNodeSnapshot — see [12-node-snapshot-table.md](12-node-snapshot-table.md)

### Node State Changes

- TMMgmtNodeStateChangedEtwTable DS — see [13-node-state-changes.md](13-node-state-changes.md)

### RdAgentAzPubSubEtwTable

- RdAgentAzPubSubEtwTable — see [14-rdagentazpubsubetwtable.md](14-rdagentazpubsubetwtable.md)

### Resource Health Unavailable for Linux 6.2 Kernel

- RH_Unavailable_Linux_6_2 — see [15-resource-health-unavailable-for-linux-6-2-kernel.md](15-resource-health-unavailable-for-linux-6-2-kernel.md)

### ResourceHealthAnnotationEvent

- ResourceHealthAnnotationEvent DS — see [16-resourcehealthannotationevent.md](16-resourcehealthannotationevent.md)

### ResourceHealthAzureActivityLogEvent

- ResourceHealthAzureActivityLogEvent — see [17-resourcehealthazureactivitylogevent.md](17-resourcehealthazureactivitylogevent.md)

### ResourceHealthStatusTransitionEvent

- ResourceHealthStatusTransitionEvent DS — see [18-resourcehealthstatustransitionevent.md](18-resourcehealthstatustransitionevent.md)

### RhcAnnotationReportsEtwTable

- RhcAnnotationReportsEtwTable DS — see [19-rhcannotationreportsetwtable.md](19-rhcannotationreportsetwtable.md)

### RhcWatchdogReportsErrorEtwTable

- RhcWatchdogReportsErrorEtwTable DS — see [20-rhcwatchdogreportserroretwtable.md](20-rhcwatchdogreportserroretwtable.md)

### RoleInstanceDownTimeEvents

- RoleInstanceDowntimeEvent — see [21-roleinstancedowntimeevents.md](21-roleinstancedowntimeevents.md)

### Scheduled Event Notifications

- AzPEWorkflowEvent — see [22-scheduled-event-notifications.md](22-scheduled-event-notifications.md)

### Tenant Management Events

- Query TMMgmtTenantEventsEtwTable — see [23-tenant-management-events.md](23-tenant-management-events.md)

### VM placement thru time on host node(s)

- Container History DS — see [24-vm-placement-thru-time-on-host-node-s.md](24-vm-placement-thru-time-on-host-node-s.md)

### VMA

- VMA1 DS — see [25-vma.md](25-vma.md)

### VmHealthRawStateEtwTable

- VmHealthRawStateEtwTable_ResourceHealth DS — see [26-vmhealthrawstateetwtable.md](26-vmhealthrawstateetwtable.md)

### Windows Events for VM

- WindowsEventsForVM — see [27-windows-events-for-vm.md](27-windows-events-for-vm.md)
