# Unhealthy Node Analysis - Node In Place Recovery Status — Investigation Guide

Chapter-keyed reference derived from the **Unhealthy Node Analysis - Node In Place Recovery Status** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Hit Detail](02-hit-detail.md) — 1 queries
- [In Place Recovery output Distribution](03-in-place-recovery-output-distribution.md) — 1 queries

**Total queries: 4**

## Query index (by file)

### (top-level)

- In Place Impact Details — see [01-top-level.md](01-top-level.md)
- NodeInPlaceStimEvents — see [01-top-level.md](01-top-level.md)

### Hit Detail

- Impact Hits — see [02-hit-detail.md](02-hit-detail.md)

### In Place Recovery output Distribution

- Node In Place Output distribution — see [03-in-place-recovery-output-distribution.md](03-in-place-recovery-output-distribution.md)
