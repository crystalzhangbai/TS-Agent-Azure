# NRP - Firewall — Investigation Guide

Chapter-keyed reference derived from the **NRP - Firewall** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Application Rules](02-application-rules.md) — 2 queries
- [Firewall Snapshots](03-firewall-snapshots.md) — 1 queries
- [FW Operations](04-fw-operations.md) — 1 queries
- [NAT Rules](05-nat-rules.md) — 2 queries
- [Rule Collections](06-rule-collections.md) — 2 queries

**Total queries: 9**

## Query index (by file)

### (top-level)

- Retrieve Resource "Firewall" — see [01-top-level.md](01-top-level.md)

### Application Rules

- Firewall - ApplicationRuleCollections — see [02-application-rules.md](02-application-rules.md)
- Firewall - ApplicationRuleCollections - Rules — see [02-application-rules.md](02-application-rules.md)

### Firewall Snapshots

- Az firewall snapshots — see [03-firewall-snapshots.md](03-firewall-snapshots.md)

### FW Operations

- AZ Firewall Operation Timline — see [04-fw-operations.md](04-fw-operations.md)

### NAT Rules

- Firewall - NatRuleCollections — see [05-nat-rules.md](05-nat-rules.md)
- Firewall - NatRuleCollections - Rules — see [05-nat-rules.md](05-nat-rules.md)

### Rule Collections

- Firewall - Network Rule Collections — see [06-rule-collections.md](06-rule-collections.md)
- Firewall - NetworkRuleCollections - Rules — see [06-rule-collections.md](06-rule-collections.md)
