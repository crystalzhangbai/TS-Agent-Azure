# Aztec — Clusters — Investigation Guide

Chapter-keyed reference derived from the **Aztec — Clusters** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 7 queries
- [Allocation Activity](02-allocation-activity.md) — 1 queries
- [Core Capacity](03-core-capacity.md) — 1 queries
- [Gateway Service](04-gateway-service.md) — 1 queries
- [LEGO EKG & Vitals](05-lego-ekg-vitals.md) — 1 queries
- [Node Capacity](06-node-capacity.md) — 1 queries
- [Nodes](07-nodes.md) — 1 queries
- [Tenants](08-tenants.md) — 1 queries
- [Utilization %](09-utilization.md) — 1 queries

**Total queries: 15**

## Query index (by file)

### (top-level)

- Retrieve Resource "Clusters" — see [01-top-level.md](01-top-level.md)
- Cluster Hosting Env — see [01-top-level.md](01-top-level.md)
- Cluster Setting Deletions — see [01-top-level.md](01-top-level.md)
- Cluster Incarnations — see [01-top-level.md](01-top-level.md)
- LEGO DC Health Status — see [01-top-level.md](01-top-level.md)
- FC Downtime — see [01-top-level.md](01-top-level.md)
- FC Failover — see [01-top-level.md](01-top-level.md)

### Allocation Activity

- Stamp Allocation Activity  — see [02-allocation-activity.md](02-allocation-activity.md)

### Core Capacity

- Cluster Cores — see [03-core-capacity.md](03-core-capacity.md)

### Gateway Service

- Check GatewayServiceTraceEvent by Cluster — see [04-gateway-service.md](04-gateway-service.md)

### LEGO EKG & Vitals

- LEGO - EKG & Vitals — see [05-lego-ekg-vitals.md](05-lego-ekg-vitals.md)

### Node Capacity

- Cluster Nodes — see [06-node-capacity.md](06-node-capacity.md)

### Nodes

- Cluster Nodes — see [07-nodes.md](07-nodes.md)

### Tenants

- Cluster Tenants — see [08-tenants.md](08-tenants.md)

### Utilization %

- Tenant Utilization Percent TimeSeries  — see [09-utilization.md](09-utilization.md)
