# Azure VM Compare Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Azure VM Compare Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [HostStorage CoPilot](01-hoststorage-copilot.md) — 2 queries
- [HostStorage VM Charts](02-hoststorage-vm-charts.md) — 6 queries
- [Metrics Comparison](03-metrics-comparison.md) — 9 queries
- [TDPR](04-tdpr.md) — 1 queries
- [VM Charts](05-vm-charts.md) — 3 queries
- [VM Details](06-vm-details.md) — 2 queries
- [VM IO Histogram Stats](07-vm-io-histogram-stats.md) — 2 queries

**Total queries: 25**

## Query index (by file)

### HostStorage CoPilot

- Container_Insights_Summary — see [01-hoststorage-copilot.md](01-hoststorage-copilot.md)
- Container_Insights_Summary — see [01-hoststorage-copilot.md](01-hoststorage-copilot.md)

### HostStorage VM Charts

- Azure Host VM ASAP 2.0 IO Stats — see [02-hoststorage-vm-charts.md](02-hoststorage-vm-charts.md)
- Azure Host VM ASAP 2.0 IO Stats — see [02-hoststorage-vm-charts.md](02-hoststorage-vm-charts.md)
- Azure Host StorageClient Surface Counter Stats — see [02-hoststorage-vm-charts.md](02-hoststorage-vm-charts.md)
- Azure Host StorageClient Surface Counter Stats — see [02-hoststorage-vm-charts.md](02-hoststorage-vm-charts.md)
- Azure Host VM CacheUsagePct — see [02-hoststorage-vm-charts.md](02-hoststorage-vm-charts.md)
- Azure Host VM CacheUsagePct — see [02-hoststorage-vm-charts.md](02-hoststorage-vm-charts.md)

### Metrics Comparison

- get_control_startTime — see [03-metrics-comparison.md](03-metrics-comparison.md)
- Retrieve Resource "Azure VM" — see [03-metrics-comparison.md](03-metrics-comparison.md)
- Get Vm Details For Container 2 — see [03-metrics-comparison.md](03-metrics-comparison.md)
- Azure Host VM Active Blobs Filter — see [03-metrics-comparison.md](03-metrics-comparison.md)
- Azure Host VM Active Blobs Filter For Container 2 — see [03-metrics-comparison.md](03-metrics-comparison.md)
- HeatMap_Type_Filter — see [03-metrics-comparison.md](03-metrics-comparison.md)
- Flip Baseline Container — see [03-metrics-comparison.md](03-metrics-comparison.md)
- Time Difference in Page Time Range — see [03-metrics-comparison.md](03-metrics-comparison.md)
- Build_HeatMap — see [03-metrics-comparison.md](03-metrics-comparison.md)

### TDPR

- Azure Host VM Compare IFX Tables — see [04-tdpr.md](04-tdpr.md)

### VM Charts

- Azure VM MetricsPerContainer — see [05-vm-charts.md](05-vm-charts.md)
- Azure Host VM CPU Usage — see [05-vm-charts.md](05-vm-charts.md)
- Azure Host VM CPU Usage — see [05-vm-charts.md](05-vm-charts.md)

### VM Details

- Retrieve Resource "Azure VM" — see [06-vm-details.md](06-vm-details.md)
- Retrieve Resource "Azure VM" — see [06-vm-details.md](06-vm-details.md)

### VM IO Histogram Stats

- Azure Host VM StorageClient IO Latency Stats — see [07-vm-io-histogram-stats.md](07-vm-io-histogram-stats.md)
- Azure Host VM StorageClient IO Latency Stats — see [07-vm-io-histogram-stats.md](07-vm-io-histogram-stats.md)
