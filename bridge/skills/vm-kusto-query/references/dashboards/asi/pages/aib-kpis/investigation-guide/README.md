# AIB KPIs — Investigation Guide

Chapter-keyed reference derived from the **AIB KPIs** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [AsyncQos](01-asyncqos.md) — 1 queries
- [Daily Builds - {{ binTime }}](02-daily-builds-bintime.md) — 1 queries
- [FrontEndQos](03-frontendqos.md) — 1 queries
- [Latest Data](04-latest-data.md) — 1 queries
- [Low KPIs ( < 99 )](05-low-kpis-99.md) — 1 queries
- [Region Hit Count](06-region-hit-count.md) — 1 queries
- [Success Rate](07-success-rate.md) — 1 queries
- [Success Rate by Request Type - {{binTime}}](08-success-rate-by-request-type-bintime.md) — 1 queries

**Total queries: 8**

## Query index (by file)

### AsyncQos

- Improved AsyncQoS — see [01-asyncqos.md](01-asyncqos.md)

### Daily Builds - {{ binTime }}

- Daily Build Success Rate — see [02-daily-builds-bintime.md](02-daily-builds-bintime.md)

### FrontEndQos

- AIB FrontEndQOS Failures — see [03-frontendqos.md](03-frontendqos.md)

### Latest Data

- Latest Refresh DateTime — see [04-latest-data.md](04-latest-data.md)

### Low KPIs ( < 99 )

- Operation Warnings — see [05-low-kpis-99.md](05-low-kpis-99.md)

### Region Hit Count

- Region AsyncQoSEvent Count — see [06-region-hit-count.md](06-region-hit-count.md)

### Success Rate

- Overall Success Rate — see [07-success-rate.md](07-success-rate.md)

### Success Rate by Request Type - {{binTime}}

- Daily Build Success by Operation Type — see [08-success-rate-by-request-type-bintime.md](08-success-rate-by-request-type-bintime.md)
