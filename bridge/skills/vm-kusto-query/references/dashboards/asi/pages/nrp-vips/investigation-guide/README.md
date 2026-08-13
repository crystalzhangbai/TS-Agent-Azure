# NRP - NRP VIPs — Investigation Guide

Chapter-keyed reference derived from the **NRP - NRP VIPs** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [VIP](01-vip.md) — 7 queries
- [VIP Prefix](02-vip-prefix.md) — 2 queries

**Total queries: 9**

## Query index (by file)

### VIP

- VIP Release Offline vs Sync — see [01-vip.md](01-vip.md)
- VIP QOS Errors — see [01-vip.md](01-vip.md)
- Put/Delete Public IP Health — see [01-vip.md](01-vip.md)
- VipAllocations Count — see [01-vip.md](01-vip.md)
- VIP Allocate/Release Trends — see [01-vip.md](01-vip.md)
- VipAllocation Perf — see [01-vip.md](01-vip.md)
- Transfer Count — see [01-vip.md](01-vip.md)

### VIP Prefix

- prefix allocated count — see [02-vip-prefix.md](02-vip-prefix.md)
- Put/Delete Public IP Prefix QOS Errors — see [02-vip-prefix.md](02-vip-prefix.md)
