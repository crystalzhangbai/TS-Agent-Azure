# Aztec Subscription Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Aztec Subscription Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Availability Sets](02-availability-sets.md) — 1 queries
- [Related Activity Ids](03-related-activity-ids.md) — 1 queries
- [Role Instances / VMs](04-role-instances-vms.md) — 1 queries

**Total queries: 4**

## Query index (by file)

### (top-level)

- Retrieve Resource "Subscription" — see [01-top-level.md](01-top-level.md)

### Availability Sets

- Subscription AvailabilitySet List — see [02-availability-sets.md](02-availability-sets.md)

### Related Activity Ids

- Subscription RelatedActivityId List — see [03-related-activity-ids.md](03-related-activity-ids.md)

### Role Instances / VMs

- Subscription RoleInstance List — see [04-role-instances-vms.md](04-role-instances-vms.md)
