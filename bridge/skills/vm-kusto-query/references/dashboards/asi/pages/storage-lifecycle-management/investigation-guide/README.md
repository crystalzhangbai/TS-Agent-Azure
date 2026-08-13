# Life Cycle Management Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Life Cycle Management Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [Aggregated LCM Account Policy Execution Summary (Below number of Rows)](01-aggregated-lcm-account-policy-execution-summary-below-number-of-rows.md) — 1 queries
- [LCM Account Policy Execution Stats](02-lcm-account-policy-execution-stats.md) — 1 queries
- [LCM Long Running Tasks](03-lcm-long-running-tasks.md) — 1 queries
- [LCM Policy](04-lcm-policy.md) — 1 queries
- [LCM Scheduler Actions](05-lcm-scheduler-actions.md) — 1 queries
- [LCM Task Execution Details ](06-lcm-task-execution-details.md) — 1 queries
- [LCM Transactions Summary](07-lcm-transactions-summary.md) — 1 queries
- [Quick Links](08-quick-links.md) — 3 queries

**Total queries: 10**

## Query index (by file)

### Aggregated LCM Account Policy Execution Summary (Below number of Rows)

- Aggregate Account LCM run result — see [01-aggregated-lcm-account-policy-execution-summary-below-number-of-rows.md](01-aggregated-lcm-account-policy-execution-summary-below-number-of-rows.md)

### LCM Account Policy Execution Stats

- LCM Account Policy Execution Stats — see [02-lcm-account-policy-execution-stats.md](02-lcm-account-policy-execution-stats.md)

### LCM Long Running Tasks

- LCM Long Running Task Stats — see [03-lcm-long-running-tasks.md](03-lcm-long-running-tasks.md)

### LCM Policy

- Get LCM policy definition — see [04-lcm-policy.md](04-lcm-policy.md)

### LCM Scheduler Actions

- Aggregate LCM Scheduler Actions — see [05-lcm-scheduler-actions.md](05-lcm-scheduler-actions.md)

### LCM Task Execution Details 

- Aggregate LCM Tasks — see [06-lcm-task-execution-details.md](06-lcm-task-execution-details.md)

### LCM Transactions Summary

- Get LCM Transactions — see [07-lcm-transactions-summary.md](07-lcm-transactions-summary.md)

### Quick Links

- Get Tenant Info by Account — see [08-quick-links.md](08-quick-links.md)
- Get Tenant Info by Account — see [08-quick-links.md](08-quick-links.md)
- TrimStorageName — see [08-quick-links.md](08-quick-links.md)
