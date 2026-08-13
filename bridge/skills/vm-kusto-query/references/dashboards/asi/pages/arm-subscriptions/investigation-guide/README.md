# ARM — Subscriptions — Investigation Guide

Chapter-keyed reference derived from the **ARM — Subscriptions** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 4 queries
- [Deployments](02-deployments.md) — 1 queries
- [Resource Groups](03-resource-groups.md) — 1 queries
- [Resources](04-resources.md) — 1 queries
- [VMs](05-vms.md) — 1 queries

**Total queries: 8**

## Query index (by file)

### (top-level)

- Retrieve Resource "Subscriptions" — see [01-top-level.md](01-top-level.md)
- Subscription Requests — see [01-top-level.md](01-top-level.md)
- Subscription Requests by User Agent — see [01-top-level.md](01-top-level.md)
- Filter - Request Errors — see [01-top-level.md](01-top-level.md)

### Deployments

- Subscription Deployments — see [02-deployments.md](02-deployments.md)

### Resource Groups

- Subscription Resource Groups — see [03-resource-groups.md](03-resource-groups.md)

### Resources

- Subscription Resources — see [04-resources.md](04-resources.md)

### VMs

- Subscription VMs — see [05-vms.md](05-vms.md)
