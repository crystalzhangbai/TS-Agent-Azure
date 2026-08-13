# Azure Host Compare Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **Azure Host Compare Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [File Versions](01-file-versions.md) — 2 queries
- [Host Charts](02-host-charts.md) — 10 queries
- [Host Details](03-host-details.md) — 8 queries
- [Host Storage Charts](04-host-storage-charts.md) — 4 queries
- [Host Storage Internal (test VMs only)](05-host-storage-internal-test-vms-only.md) — 2 queries
- [Host Tables](06-host-tables.md) — 5 queries
- [HostStorage CoPilot](07-hoststorage-copilot.md) — 1 queries
- [Registry Keys](08-registry-keys.md) — 1 queries
- [TDPR](09-tdpr.md) — 2 queries
- [VM Charts](10-vm-charts.md) — 8 queries

**Total queries: 43**

## Query index (by file)

### File Versions

- Azure Host FileVersion Compare — see [01-file-versions.md](01-file-versions.md)
- Azure Host PF Services Compare — see [01-file-versions.md](01-file-versions.md)

### Host Charts

- Azure Host Node Available Memory — see [02-host-charts.md](02-host-charts.md)
- Azure Host Node Available Memory — see [02-host-charts.md](02-host-charts.md)
- Azure Host VP CPU — see [02-host-charts.md](02-host-charts.md)
- Azure Host VP CPU — see [02-host-charts.md](02-host-charts.md)
- CPU Jitter (High granularity) — see [02-host-charts.md](02-host-charts.md)
- CPU Jitter (High granularity) — see [02-host-charts.md](02-host-charts.md)
- Azure Host Node NPP Bytes — see [02-host-charts.md](02-host-charts.md)
- Azure Host Node NPP Bytes — see [02-host-charts.md](02-host-charts.md)
- Azure Host Node Process Handle Count — see [02-host-charts.md](02-host-charts.md)
- Azure Host Node Process Handle Count — see [02-host-charts.md](02-host-charts.md)

### Host Details

- Retrieve Resource "Azure Host Node" — see [03-host-details.md](03-host-details.md)
- Retrieve Node Hardware Details — see [03-host-details.md](03-host-details.md)
- Host OS Version — see [03-host-details.md](03-host-details.md)
- Retrieve Resource "Azure Host Node" — see [03-host-details.md](03-host-details.md)
- Retrieve Node Hardware Details — see [03-host-details.md](03-host-details.md)
- Host OS Version — see [03-host-details.md](03-host-details.md)
- Azure Host Running VMs Query — see [03-host-details.md](03-host-details.md)
- Azure Host Running VMs Query — see [03-host-details.md](03-host-details.md)

### Host Storage Charts

- Azure Host Node ASAP 2.0 IO Stats — see [04-host-storage-charts.md](04-host-storage-charts.md)
- Azure Host Node ASAP 2.0 IO Stats — see [04-host-storage-charts.md](04-host-storage-charts.md)
- Azure Host Surface Stats for Node — see [04-host-storage-charts.md](04-host-storage-charts.md)
- Azure Host Surface Stats for Node — see [04-host-storage-charts.md](04-host-storage-charts.md)

### Host Storage Internal (test VMs only)

- Azure Host Test VMs Max Latencies — see [05-host-storage-internal-test-vms-only.md](05-host-storage-internal-test-vms-only.md)
- Azure Host Test VMs Max Latencies — see [05-host-storage-internal-test-vms-only.md](05-host-storage-internal-test-vms-only.md)

### Host Tables

- Azure Host HighCPUTable — see [06-host-tables.md](06-host-tables.md)
- Azure Host HighCPUTable — see [06-host-tables.md](06-host-tables.md)
- Azure Host Compare Windows Event Comparison — see [06-host-tables.md](06-host-tables.md)
- Azure Host WindowsEventTable — see [06-host-tables.md](06-host-tables.md)
- Azure Host WindowsEventTable — see [06-host-tables.md](06-host-tables.md)

### HostStorage CoPilot

- node_insights_summary — see [07-hoststorage-copilot.md](07-hoststorage-copilot.md)

### Registry Keys

- Azure Host Node Compare Registry Keys — see [08-registry-keys.md](08-registry-keys.md)

### TDPR

- Azure Host TDPR — see [09-tdpr.md](09-tdpr.md)
- Azure Host TDPR — see [09-tdpr.md](09-tdpr.md)

### VM Charts

- Azure Host VMs Memory Usage — see [10-vm-charts.md](10-vm-charts.md)
- Azure Host VMs Memory Usage — see [10-vm-charts.md](10-vm-charts.md)
- Azure Host VMs CPU Usage — see [10-vm-charts.md](10-vm-charts.md)
- Azure Host VMs CPU Usage — see [10-vm-charts.md](10-vm-charts.md)
- Azure Host StorageClient VMs Disk IOPS — see [10-vm-charts.md](10-vm-charts.md)
- Azure Host StorageClient VMs Disk IOPS — see [10-vm-charts.md](10-vm-charts.md)
- Azure Host VM StorageClient Disk MBPS — see [10-vm-charts.md](10-vm-charts.md)
- Azure Host VM StorageClient Disk MBPS — see [10-vm-charts.md](10-vm-charts.md)
