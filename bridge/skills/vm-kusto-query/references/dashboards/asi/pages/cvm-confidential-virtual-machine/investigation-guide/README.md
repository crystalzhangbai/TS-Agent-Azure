# Confidential Virtual Machines - Confidential Virtual Machine — Investigation Guide

Chapter-keyed reference derived from the **Confidential Virtual Machines - Confidential Virtual Machine** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Counters](02-counters.md) — 1 queries
- [CRP Event Logs](03-crp-event-logs.md) — 2 queries
- [CRP VMSS VM Event Logs](04-crp-vmss-vm-event-logs.md) — 1 queries
- [Disk Manager Events](05-disk-manager-events.md) — 1 queries
- [IGVM Agent Logs](06-igvm-agent-logs.md) — 1 queries
- [Windows Event Logs](07-windows-event-logs.md) — 1 queries

**Total queries: 12**

## Query index (by file)

### (top-level)

- Retrieve Resource "Confidential Virtual Machine" — see [01-top-level.md](01-top-level.md)
- CRP VM Events — see [01-top-level.md](01-top-level.md)
- Container Events — see [01-top-level.md](01-top-level.md)
- VM Containers — see [01-top-level.md](01-top-level.md)
- Execution Graph — see [01-top-level.md](01-top-level.md)

### Counters

- VM Performance Counters — see [02-counters.md](02-counters.md)

### CRP Event Logs

- CRP VM Event Logs — see [03-crp-event-logs.md](03-crp-event-logs.md)
- VMSS VM ApiQosEvent — see [03-crp-event-logs.md](03-crp-event-logs.md)

### CRP VMSS VM Event Logs

- VMSS VM ApiQosEvent — see [04-crp-vmss-vm-event-logs.md](04-crp-vmss-vm-event-logs.md)

### Disk Manager Events

- Disk Manager Events — see [05-disk-manager-events.md](05-disk-manager-events.md)

### IGVM Agent Logs

- IGVM Agent Logs — see [06-igvm-agent-logs.md](06-igvm-agent-logs.md)

### Windows Event Logs

- Windows Event Table — see [07-windows-event-logs.md](07-windows-event-logs.md)
