# Preview Dotnet Image Templates — Investigation Guide

Chapter-keyed reference derived from the **Preview Dotnet Image Templates** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 4 queries

**Total queries: 4**

## Query index (by file)

### (top-level)

- Preview Gen 2 Windows 2022 Dotnet Images — see [01-top-level.md](01-top-level.md)
- Dotnet 10 Preview Gen 2 Windows 2022 Dotnet Images — see [01-top-level.md](01-top-level.md)
- Preview Gen 1 Windows 2022 Dotnet Images — see [01-top-level.md](01-top-level.md)
- Dotnet 10 Preview Gen 2 Windows 2025 Dotnet Images — see [01-top-level.md](01-top-level.md)
