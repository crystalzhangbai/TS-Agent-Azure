# NRP - Load Balancer — Investigation Guide

Chapter-keyed reference derived from the **NRP - Load Balancer** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 2 queries
- [Backend Address Pools](02-backend-address-pools.md) — 1 queries
- [Frontend IP Configs](03-frontend-ip-configs.md) — 1 queries
- [Inbound Nat Pools](04-inbound-nat-pools.md) — 1 queries
- [Inbound Nat Rules](05-inbound-nat-rules.md) — 1 queries
- [Load Balancer Snapshots](06-load-balancer-snapshots.md) — 1 queries
- [Load Balancing Rules](07-load-balancing-rules.md) — 1 queries
- [Outbound Rules](08-outbound-rules.md) — 1 queries
- [Probes](09-probes.md) — 1 queries

**Total queries: 10**

## Query index (by file)

### (top-level)

- Retrieve Resource "Load Balancer" — see [01-top-level.md](01-top-level.md)
- Load Balancer Operation Timeline — see [01-top-level.md](01-top-level.md)

### Backend Address Pools

- SLB - Backend Address Pools — see [02-backend-address-pools.md](02-backend-address-pools.md)

### Frontend IP Configs

- SLB - Front End IP Configurations — see [03-frontend-ip-configs.md](03-frontend-ip-configs.md)

### Inbound Nat Pools

- SLB - Inbound NAT Pools — see [04-inbound-nat-pools.md](04-inbound-nat-pools.md)

### Inbound Nat Rules

- SLB - Inbound Nat Rules — see [05-inbound-nat-rules.md](05-inbound-nat-rules.md)

### Load Balancer Snapshots

- Load Balancer Snapshots — see [06-load-balancer-snapshots.md](06-load-balancer-snapshots.md)

### Load Balancing Rules

- SLB - Load Balancing Rules — see [07-load-balancing-rules.md](07-load-balancing-rules.md)

### Outbound Rules

- SLB - Outbound Rules — see [08-outbound-rules.md](08-outbound-rules.md)

### Probes

- SLB - Probes — see [09-probes.md](09-probes.md)
