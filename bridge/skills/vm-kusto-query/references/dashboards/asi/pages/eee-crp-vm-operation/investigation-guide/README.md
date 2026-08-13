# EEE CRP — VM Operation — Investigation Guide

Chapter-keyed reference derived from the **EEE CRP — VM Operation** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 3 queries
- [Resource Operations](02-resource-operations.md) — 8 queries
- [VM / VMSS Activity](03-vm-vmss-activity.md) — 8 queries

**Total queries: 19**

## Query index (by file)

### (top-level)

- Retrieve Resource "VM Operation" — see [01-top-level.md](01-top-level.md)
- Preemption — see [01-top-level.md](01-top-level.md)
- CRP Operation Info — see [01-top-level.md](01-top-level.md)

### Resource Operations

- ARM Operation Timeline — see [02-resource-operations.md](02-resource-operations.md)
- CRP Operation Table — see [02-resource-operations.md](02-resource-operations.md)
- CRP Operation Table — see [02-resource-operations.md](02-resource-operations.md)
- ARM Operation for VM — see [02-resource-operations.md](02-resource-operations.md)
- ARM Operation — see [02-resource-operations.md](02-resource-operations.md)
- CRP Operations for VM — see [02-resource-operations.md](02-resource-operations.md)
- Retrieve Resource "VM Operation" — see [02-resource-operations.md](02-resource-operations.md)
- VM Operation — see [02-resource-operations.md](02-resource-operations.md)

### VM / VMSS Activity

- Component Call — see [03-vm-vmss-activity.md](03-vm-vmss-activity.md)
- CRP Context Operation — see [03-vm-vmss-activity.md](03-vm-vmss-activity.md)
- Component Call — see [03-vm-vmss-activity.md](03-vm-vmss-activity.md)
- NRP Operation Log — see [03-vm-vmss-activity.md](03-vm-vmss-activity.md)
- NRP Operation Timeline — see [03-vm-vmss-activity.md](03-vm-vmss-activity.md)
- VM Allocation in CRP — see [03-vm-vmss-activity.md](03-vm-vmss-activity.md)
- VMSS Container Goal Seeking Timeline — see [03-vm-vmss-activity.md](03-vm-vmss-activity.md)
- VMSS Goal Seeking Operation — see [03-vm-vmss-activity.md](03-vm-vmss-activity.md)
