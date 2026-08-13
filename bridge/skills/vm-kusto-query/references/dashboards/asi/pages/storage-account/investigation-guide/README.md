# Storage Account Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Storage Account Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Account Limits & Usage (99% Percentile)](02-account-limits-usage-99-percentile.md) — 1 queries
- [Account Usage Metrics (Beta)](03-account-usage-metrics-beta.md) — 1 queries
- [ASI Pages](04-asi-pages.md) — 2 queries
- [DGrep Links](05-dgrep-links.md) — 2 queries
- [MDM Dashboards](06-mdm-dashboards.md) — 2 queries
- [Regional Account Distribution](07-regional-account-distribution.md) — 1 queries
- [Transactions by Request Type](08-transactions-by-request-type.md) — 1 queries
- [User Guide](09-user-guide.md) — 1 queries

**Total queries: 12**

## Query index (by file)

### (top-level)

- Retrieve Resource "Storage Account" — see [01-top-level.md](01-top-level.md)

### Account Limits & Usage (99% Percentile)

- Get Account Limit — see [02-account-limits-usage-99-percentile.md](02-account-limits-usage-99-percentile.md)

### Account Usage Metrics (Beta)

- Get Usage Metrics — see [03-account-usage-metrics-beta.md](03-account-usage-metrics-beta.md)

### ASI Pages

- Get Tenant Info by Account — see [04-asi-pages.md](04-asi-pages.md)
- TrimStorageName — see [04-asi-pages.md](04-asi-pages.md)

### DGrep Links

- Get Tenant RSRP name — see [05-dgrep-links.md](05-dgrep-links.md)
- Storage_Regions — see [05-dgrep-links.md](05-dgrep-links.md)

### MDM Dashboards

- Get Account Tenant Info — see [06-mdm-dashboards.md](06-mdm-dashboards.md)
- UnixTimeFormat_Converter — see [06-mdm-dashboards.md](06-mdm-dashboards.md)

### Regional Account Distribution

- Get Regional Accounts Distribution — see [07-regional-account-distribution.md](07-regional-account-distribution.md)

### Transactions by Request Type

- Get Storage Account Transactions By RequestType — see [08-transactions-by-request-type.md](08-transactions-by-request-type.md)

### User Guide

- Get_ServiceID — see [09-user-guide.md](09-user-guide.md)
