# Storage Billing Drilldown Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Storage Billing Drilldown Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Account Billing Daily](02-account-billing-daily.md) — 1 queries
- [Billable Transactions, Ingress & Egress](03-billable-transactions-ingress-egress.md) — 1 queries
- [Pages - Storage Tools](04-pages-storage-tools.md) — 2 queries
- [Sum of the total Transaction, Ingress & Egress](05-sum-of-the-total-transaction-ingress-egress.md) — 1 queries

**Total queries: 6**

## Query index (by file)

### (top-level)

- Get Tenant Info by Account — see [01-top-level.md](01-top-level.md)

### Account Billing Daily

- List Account Billing Daily — see [02-account-billing-daily.md](02-account-billing-daily.md)

### Billable Transactions, Ingress & Egress

- Get Account Billable Transactions — see [03-billable-transactions-ingress-egress.md](03-billable-transactions-ingress-egress.md)

### Pages - Storage Tools

- Get Tenant Info by Account — see [04-pages-storage-tools.md](04-pages-storage-tools.md)
- TrimStorageName — see [04-pages-storage-tools.md](04-pages-storage-tools.md)

### Sum of the total Transaction, Ingress & Egress

- Sum of total Transaction, Ingress & Egress — see [05-sum-of-the-total-transaction-ingress-egress.md](05-sum-of-the-total-transaction-ingress-egress.md)
