# NRP - Management Nic — Investigation Guide

Chapter-keyed reference derived from the **NRP - Management Nic** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 8 queries
- [Elastic Nic Request](02-elastic-nic-request.md) — 3 queries
- [Enic Usage](03-enic-usage.md) — 4 queries
- [F5 Network](04-f5-network.md) — 1 queries
- [Operation Errors Summary](05-operation-errors-summary.md) — 3 queries

**Total queries: 19**

## Query index (by file)

### (top-level)

- F5 Enic Error Summary — see [01-top-level.md](01-top-level.md)
- NIC - Notifications fetched — see [01-top-level.md](01-top-level.md)
- NIC- Notifications started being processed — see [01-top-level.md](01-top-level.md)
- NIC- Notifications Processed — see [01-top-level.md](01-top-level.md)
- NIC- Create or Update — see [01-top-level.md](01-top-level.md)
- NIC - Delete — see [01-top-level.md](01-top-level.md)
-  NIC- Resource not exist but entry not deleted2 — see [01-top-level.md](01-top-level.md)
- invalidEnic — see [01-top-level.md](01-top-level.md)

### Elastic Nic Request

- Enic Change Distibution — see [02-elastic-nic-request.md](02-elastic-nic-request.md)
- Parent Nic Usage — see [02-elastic-nic-request.md](02-elastic-nic-request.md)
- VMSS Enic Hourly Summarize — see [02-elastic-nic-request.md](02-elastic-nic-request.md)

### Enic Usage

- Enic Usage per Customer — see [03-enic-usage.md](03-enic-usage.md)
- Enic Usage — see [03-enic-usage.md](03-enic-usage.md)
- Monthly Active Enic — see [03-enic-usage.md](03-enic-usage.md)
- Pnic Usage — see [03-enic-usage.md](03-enic-usage.md)

### F5 Network

- F5 Enic Usage — see [04-f5-network.md](04-f5-network.md)

### Operation Errors Summary

- ElasticNic Query — see [05-operation-errors-summary.md](05-operation-errors-summary.md)
- Parent Nic — see [05-operation-errors-summary.md](05-operation-errors-summary.md)
- VMSS with Mgmt Nic — see [05-operation-errors-summary.md](05-operation-errors-summary.md)
