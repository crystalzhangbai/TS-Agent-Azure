# CRP Subscriptions Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **CRP Subscriptions Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [ASC Tab - Use the same queries from ASC](02-asc-tab-use-the-same-queries-from-asc.md) — 7 queries
- [CSS Tab - Customized queries for CSS](03-css-tab-customized-queries-for-css.md) — 2 queries
- [Resource Groups](04-resource-groups.md) — 1 queries
- [Scale Sets / VMSS](05-scale-sets-vmss.md) — 1 queries
- [Throttling](06-throttling.md) — 1 queries
- [VMs](07-vms.md) — 1 queries

**Total queries: 16**

## Query index (by file)

### (top-level)

- Retrieve Resource "Subscriptions" — see [01-top-level.md](01-top-level.md)
- Query Sub from CommonDims — see [01-top-level.md](01-top-level.md)
- Subscription Availability Zones — see [01-top-level.md](01-top-level.md)

### ASC Tab - Use the same queries from ASC

- Current Maintenance-Control Status by Subscription — see [02-asc-tab-use-the-same-queries-from-asc.md](02-asc-tab-use-the-same-queries-from-asc.md)
- Maintenance-Control Status History by Subscription — see [02-asc-tab-use-the-same-queries-from-asc.md](02-asc-tab-use-the-same-queries-from-asc.md)
- Planned Maintenance History by Subscription — see [02-asc-tab-use-the-same-queries-from-asc.md](02-asc-tab-use-the-same-queries-from-asc.md)
- GetCommunicationsForSupport — see [02-asc-tab-use-the-same-queries-from-asc.md](02-asc-tab-use-the-same-queries-from-asc.md)
- Query Planned Maintenance Phase Details by Subscription — see [02-asc-tab-use-the-same-queries-from-asc.md](02-asc-tab-use-the-same-queries-from-asc.md)
- Query Planned Maintenance Status Summary by Subscription — see [02-asc-tab-use-the-same-queries-from-asc.md](02-asc-tab-use-the-same-queries-from-asc.md)
- Get Service Healing due to Planned Maintenance by Sub — see [02-asc-tab-use-the-same-queries-from-asc.md](02-asc-tab-use-the-same-queries-from-asc.md)

### CSS Tab - Customized queries for CSS

- GetPlannedMaintenanceCommunicationsForSupport — see [03-css-tab-customized-queries-for-css.md](03-css-tab-customized-queries-for-css.md)
- Get Current Maintenance Status By Subscription — see [03-css-tab-customized-queries-for-css.md](03-css-tab-customized-queries-for-css.md)

### Resource Groups

- Resource Groups — see [04-resource-groups.md](04-resource-groups.md)

### Scale Sets / VMSS

- Resource Group Scale Sets — see [05-scale-sets-vmss.md](05-scale-sets-vmss.md)

### Throttling

- Subscription Throttling — see [06-throttling.md](06-throttling.md)

### VMs

- Subscription VMs — see [07-vms.md](07-vms.md)
