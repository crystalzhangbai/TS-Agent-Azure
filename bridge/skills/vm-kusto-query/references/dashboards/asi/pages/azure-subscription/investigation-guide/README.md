# Azure Subscription Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Azure Subscription Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Active Disks for the Subscription](02-active-disks-for-the-subscription.md) — 1 queries
- [AIR-BP with RCA](03-air-bp-with-rca.md) — 1 queries
- [Charts](04-charts.md) — 4 queries
- [Disk Limits Stats](05-disk-limits-stats.md) — 1 queries
- [DiskTier Stats](06-disktier-stats.md) — 1 queries
- [Info](07-info.md) — 1 queries
- [List of VMs](08-list-of-vms.md) — 1 queries
- [Stats](09-stats.md) — 2 queries
- [StorageAccounts](10-storageaccounts.md) — 1 queries
- [Summary by Histogram](11-summary-by-histogram.md) — 1 queries
- [Timeline Chart](12-timeline-chart.md) — 1 queries
- [Usage Stats](13-usage-stats.md) — 2 queries
- [VM Stats](14-vm-stats.md) — 2 queries
- [VMs Availability (AIR-R)](15-vms-availability-air-r.md) — 1 queries

**Total queries: 21**

## Query index (by file)

### (top-level)

- Retrieve Resource "Azure Subscription" — see [01-top-level.md](01-top-level.md)

### Active Disks for the Subscription

- Azure Host Subscription Disks — see [02-active-disks-for-the-subscription.md](02-active-disks-for-the-subscription.md)

### AIR-BP with RCA

- Azure Host Subscription Disk AIR-BP — see [03-air-bp-with-rca.md](03-air-bp-with-rca.md)

### Charts

- Azure Host Subscription Active Disks — see [04-charts.md](04-charts.md)
- Azure Host Subscriptions Surface Stats Region — see [04-charts.md](04-charts.md)
- Azure Host Analyzer Subscription Disk Stats by ResourceGroup — see [04-charts.md](04-charts.md)
- Azure Host Subscription Surface IO Stats — see [04-charts.md](04-charts.md)

### Disk Limits Stats

- Azure Host Subscription Disk Limits Stats — see [05-disk-limits-stats.md](05-disk-limits-stats.md)

### DiskTier Stats

- Azure Host Subscription Disk Stats by Tier — see [06-disktier-stats.md](06-disktier-stats.md)

### Info

- SubscriptionDetails — see [07-info.md](07-info.md)

### List of VMs

- Azure Host Subscription VMs — see [08-list-of-vms.md](08-list-of-vms.md)

### Stats

- Azure Host Subscription VMs Timeline — see [09-stats.md](09-stats.md)
- Azure Host Subscriptions VMs by Type — see [09-stats.md](09-stats.md)

### StorageAccounts

- Azure Host Subscription StorageAccounts — see [10-storageaccounts.md](10-storageaccounts.md)

### Summary by Histogram

- Azure Host Subscription AIR-BP by Histogram — see [11-summary-by-histogram.md](11-summary-by-histogram.md)

### Timeline Chart

- Azure Host Subscription Disk AIR-BP Timeline — see [12-timeline-chart.md](12-timeline-chart.md)

### Usage Stats

- Azure Host Analyzer Subscription Disk Stats — see [13-usage-stats.md](13-usage-stats.md)
- Azure Host Subscription Disk MBPS Stats — see [13-usage-stats.md](13-usage-stats.md)

### VM Stats

- Azure Host Subscription VM Shoebox Counter Stats — see [14-vm-stats.md](14-vm-stats.md)
- Azure Host Subscription VM Shoebox Top VMs doing Max — see [14-vm-stats.md](14-vm-stats.md)

### VMs Availability (AIR-R)

- Azure Host Subscription AIR-R — see [15-vms-availability-air-r.md](15-vms-availability-air-r.md)
