# NRP - BackupOperation — Investigation Guide

Chapter-keyed reference derived from the **NRP - BackupOperation** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [Backup Initiated Less than 20% of the total time.](01-backup-initiated-less-than-20-of-the-total-time.md) — 1 queries
- [Backup Scheduled vs Failed Per Region](02-backup-scheduled-vs-failed-per-region.md) — 1 queries
- [Top Error Code in Backup Operations](03-top-error-code-in-backup-operations.md) — 1 queries

**Total queries: 3**

## Query index (by file)

### Backup Initiated Less than 20% of the total time.

- Not scheduled backup — see [01-backup-initiated-less-than-20-of-the-total-time.md](01-backup-initiated-less-than-20-of-the-total-time.md)

### Backup Scheduled vs Failed Per Region

- Backup Scheduled — see [02-backup-scheduled-vs-failed-per-region.md](02-backup-scheduled-vs-failed-per-region.md)

### Top Error Code in Backup Operations

- Backup Top Error — see [03-top-error-code-in-backup-operations.md](03-top-error-code-in-backup-operations.md)
