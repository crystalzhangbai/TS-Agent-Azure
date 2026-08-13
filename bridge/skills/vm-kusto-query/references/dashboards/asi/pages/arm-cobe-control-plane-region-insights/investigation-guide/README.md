# ARM CoBe Control Plane Region Insights Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **ARM CoBe Control Plane Region Insights Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [Outage](01-outage.md) — 14 queries
- [Release](02-release.md) — 5 queries

**Total queries: 19**

## Query index (by file)

### Outage

- AAD Outages — see [01-outage.md](01-outage.md)
- ARM Outages — see [01-outage.md](01-outage.md)
- AzPolicy Outages — see [01-outage.md](01-outage.md)
- CosmosDB Outages — see [01-outage.md](01-outage.md)
- Virtual Machines Outages — see [01-outage.md](01-outage.md)
- Network Outages — see [01-outage.md](01-outage.md)
- AKS Outages — see [01-outage.md](01-outage.md)
- Storage Outages — see [01-outage.md](01-outage.md)
- SQL Database Outages — see [01-outage.md](01-outage.md)
- App Services Outages — see [01-outage.md](01-outage.md)
- Container Instances Outages — see [01-outage.md](01-outage.md)
- PostgreSQL Outages — see [01-outage.md](01-outage.md)
- LogicApps Outages — see [01-outage.md](01-outage.md)
- Region Outages — see [01-outage.md](01-outage.md)

### Release

- CRP Release — see [02-release.md](02-release.md)
- NRP Release — see [02-release.md](02-release.md)
- AKS Release — see [02-release.md](02-release.md)
- ARM Release — see [02-release.md](02-release.md)
- Release — see [02-release.md](02-release.md)
