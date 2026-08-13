# VM Scuba - VM Details — Investigation Guide

Chapter-keyed reference derived from the **VM Scuba - VM Details** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Container Health status](02-container-health-status.md) — 1 queries
- [Get HostOS Updates](03-get-hostos-updates.md) — 1 queries
- [Get Maintenance details ](04-get-maintenance-details.md) — 1 queries
- [Get Updates on Node](05-get-updates-on-node.md) — 1 queries
- [Live Migration Errors ](06-live-migration-errors.md) — 1 queries
- [Live Migrations Events](07-live-migrations-events.md) — 1 queries
- [Node state change](08-node-state-change.md) — 1 queries
- [Overlake Config](09-overlake-config.md) — 1 queries
- [Resource Health](10-resource-health.md) — 1 queries
- [TOR Health](11-tor-health.md) — 1 queries
- [VM Config](12-vm-config.md) — 1 queries
- [VM Insights for a given TIMESTAMP](13-vm-insights-for-a-given-timestamp.md) — 1 queries
- [VM Node to TOR Health](14-vm-node-to-tor-health.md) — 1 queries
- [VM Restart Events](15-vm-restart-events.md) — 1 queries

**Total queries: 17**

## Query index (by file)

### (top-level)

- Get-VMDetails — see [01-top-level.md](01-top-level.md)
- Get-TOR — see [01-top-level.md](01-top-level.md)
- Get-SessionId — see [01-top-level.md](01-top-level.md)

### Container Health status

- Get-ContainerHealthStatus — see [02-container-health-status.md](02-container-health-status.md)

### Get HostOS Updates

- Get-HostOSUpdates — see [03-get-hostos-updates.md](03-get-hostos-updates.md)

### Get Maintenance details 

- Get-MaintenanceDetails — see [04-get-maintenance-details.md](04-get-maintenance-details.md)

### Get Updates on Node

- Get-NodeUpdates — see [05-get-updates-on-node.md](05-get-updates-on-node.md)

### Live Migration Errors 

- Get-LiveMigrationErrors — see [06-live-migration-errors.md](06-live-migration-errors.md)

### Live Migrations Events

- Get-LiveMigrationsEvents — see [07-live-migrations-events.md](07-live-migrations-events.md)

### Node state change

- Get-NodeStateChange — see [08-node-state-change.md](08-node-state-change.md)

### Overlake Config

- Get-Overlake Config — see [09-overlake-config.md](09-overlake-config.md)

### Resource Health

- Get-ResourceHealth — see [10-resource-health.md](10-resource-health.md)

### TOR Health

- Get-TORHealth — see [11-tor-health.md](11-tor-health.md)

### VM Config

- Get-VMSummary — see [12-vm-config.md](12-vm-config.md)

### VM Insights for a given TIMESTAMP

- Get-VMInsights — see [13-vm-insights-for-a-given-timestamp.md](13-vm-insights-for-a-given-timestamp.md)

### VM Node to TOR Health

- Get-VMNodetoTORHealth — see [14-vm-node-to-tor-health.md](14-vm-node-to-tor-health.md)

### VM Restart Events

- Get-VMRestartEvents — see [15-vm-restart-events.md](15-vm-restart-events.md)
