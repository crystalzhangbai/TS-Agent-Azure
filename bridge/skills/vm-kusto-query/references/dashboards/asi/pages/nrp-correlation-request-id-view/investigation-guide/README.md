# NRP - CorrelationRequestIdView — Investigation Guide

Chapter-keyed reference derived from the **NRP - CorrelationRequestIdView** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [Activity](01-activity.md) — 1 queries
- [correlId](02-correlid.md) — 7 queries
- [NRPQosErrors](03-nrpqoserrors.md) — 1 queries

**Total queries: 9**

## Query index (by file)

### Activity

- correl_activity — see [01-activity.md](01-activity.md)

### correlId

- correlId — see [02-correlid.md](02-correlid.md)
- correlActivity — see [02-correlid.md](02-correlid.md)
- ARM_Correl — see [02-correlid.md](02-correlid.md)
- crp_apiqos — see [02-correlid.md](02-correlid.md)
- fe_popup — see [02-correlid.md](02-correlid.md)
- GetRequestBody — see [02-correlid.md](02-correlid.md)
- FE_Tid_query — see [02-correlid.md](02-correlid.md)

### NRPQosErrors

- qos_errs — see [03-nrpqoserrors.md](03-nrpqoserrors.md)
