# CRP — Scale Sets — Investigation Guide

Chapter-keyed reference derived from the **CRP — Scale Sets** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 8 queries
- [Extension Provisioning Failures](02-extension-provisioning-failures.md) — 1 queries
- [Fabric Placements](03-fabric-placements.md) — 1 queries
- [Insights](04-insights.md) — 1 queries
- [Ocular](05-ocular.md) — 1 queries
- [Requests](06-requests.md) — 1 queries
- [VMs](07-vms.md) — 2 queries
- [VMSS Extensions](08-vmss-extensions.md) — 1 queries

**Total queries: 16**

## Query index (by file)

### (top-level)

- Retrieve Resource "Scale Sets" — see [01-top-level.md](01-top-level.md)
- Find OS Prov Failures — see [01-top-level.md](01-top-level.md)
- Query SF Extension  — see [01-top-level.md](01-top-level.md)
- Locate SF Cluster  — see [01-top-level.md](01-top-level.md)
- VMSS Request Deltas — see [01-top-level.md](01-top-level.md)
- VMSS State — see [01-top-level.md](01-top-level.md)
- VMSS Operations — see [01-top-level.md](01-top-level.md)
- Query ResourceHealthAzureActivityLogEvent — see [01-top-level.md](01-top-level.md)

### Extension Provisioning Failures

- ScaleSet Extension Failures — see [02-extension-provisioning-failures.md](02-extension-provisioning-failures.md)

### Fabric Placements

- FabricPlacements — see [03-fabric-placements.md](03-fabric-placements.md)

### Insights

- GetVMSSImpactEvents — see [04-insights.md](04-insights.md)

### Ocular

- Ocular Summary Logs with Resource Name — see [05-ocular.md](05-ocular.md)

### Requests

- VMSS Requests — see [06-requests.md](06-requests.md)

### VMs

- Query VMSS Instance from BI — see [07-vms.md](07-vms.md)
- Scaleset instance health — see [07-vms.md](07-vms.md)

### VMSS Extensions

- Query VMSS Extensions — see [08-vmss-extensions.md](08-vmss-extensions.md)
