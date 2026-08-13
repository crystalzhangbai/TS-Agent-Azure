# NRP - Subscriptions — Investigation Guide

Chapter-keyed reference derived from the **NRP - Subscriptions** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Firewalls](02-firewalls.md) — 1 queries
- [Load Balancers](03-load-balancers.md) — 1 queries
- [NSGs](04-nsgs.md) — 1 queries
- [Private Endpoints](05-private-endpoints.md) — 1 queries
- [Public IPs](06-public-ips.md) — 1 queries
- [Subnets](07-subnets.md) — 1 queries
- [Subscription NICs](08-subscription-nics.md) — 1 queries
- [VNets](09-vnets.md) — 1 queries

**Total queries: 10**

## Query index (by file)

### (top-level)

- Retrieve Resource "Subscriptions" — see [01-top-level.md](01-top-level.md)
- Sub or RG Route Tables — see [01-top-level.md](01-top-level.md)

### Firewalls

- Subscription Firewalls — see [02-firewalls.md](02-firewalls.md)

### Load Balancers

- NRP Sub and RG Load Balancers — see [03-load-balancers.md](03-load-balancers.md)

### NSGs

- Subscription NSGs — see [04-nsgs.md](04-nsgs.md)

### Private Endpoints

- NRP Sub and RG Private Endpoints — see [05-private-endpoints.md](05-private-endpoints.md)

### Public IPs

- NRP Public IPs by Sub and RG — see [06-public-ips.md](06-public-ips.md)

### Subnets

- Subscription Subnets — see [07-subnets.md](07-subnets.md)

### Subscription NICs

- Get Subscription NICs — see [08-subscription-nics.md](08-subscription-nics.md)

### VNets

- Subscription VNets — see [09-vnets.md](09-vnets.md)
