# Aztec Service Healing Investigations Guide — Investigation Guide

Chapter-keyed reference derived from the **Aztec Service Healing Investigations Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 5 queries
- [AzSM Service Healing Step Result Events table](02-azsm-service-healing-step-result-events-table.md) — 1 queries
- [AzSM Service Healing Summary](03-azsm-service-healing-summary.md) — 1 queries
- [Tenant Service Healing Events Table](04-tenant-service-healing-events-table.md) — 1 queries

**Total queries: 8**

## Query index (by file)

### (top-level)

- Container Metedata Query from mycroft — see [01-top-level.md](01-top-level.md)
- Mycroft container health summary — see [01-top-level.md](01-top-level.md)
- Mycroft Node Health Summary — see [01-top-level.md](01-top-level.md)
- Tenant Summary Query — see [01-top-level.md](01-top-level.md)
- FC Service Healing Trigger QUery — see [01-top-level.md](01-top-level.md)

### AzSM Service Healing Step Result Events table

- AzSM Service Healing Summary Query — see [02-azsm-service-healing-step-result-events-table.md](02-azsm-service-healing-step-result-events-table.md)

### AzSM Service Healing Summary

- AzSM Service Healing Trigger and Result details — see [03-azsm-service-healing-summary.md](03-azsm-service-healing-summary.md)

### Tenant Service Healing Events Table

- Tenant Events Service Healing Trigger Events — see [04-tenant-service-healing-events-table.md](04-tenant-service-healing-events-table.md)
