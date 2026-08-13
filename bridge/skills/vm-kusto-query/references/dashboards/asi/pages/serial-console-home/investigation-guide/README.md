# Serial Console Home — Investigation Guide

Chapter-keyed reference derived from the **Serial Console Home** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [Config Audits](02-config-audits.md) — 1 queries
- [Current DRI](03-current-dri.md) — 1 queries
- [Exposed Secrets](04-exposed-secrets.md) — 1 queries
- [Gateway Health Check Failure Percentage](05-gateway-health-check-failure-percentage.md) — 1 queries
- [ICM Incidents](06-icm-incidents.md) — 1 queries
- [Vulnerabilities](07-vulnerabilities.md) — 2 queries

**Total queries: 8**

## Query index (by file)

### (top-level)

- Portal Image Tag  — see [01-top-level.md](01-top-level.md)

### Config Audits

- WIP Trivy Config Audits — see [02-config-audits.md](02-config-audits.md)

### Current DRI

- Get Current On-Call — see [03-current-dri.md](03-current-dri.md)

### Exposed Secrets

- WIP Trivy Exposed Secrets — see [04-exposed-secrets.md](04-exposed-secrets.md)

### Gateway Health Check Failure Percentage

- Gateway To RP Healthcheck — see [05-gateway-health-check-failure-percentage.md](05-gateway-health-check-failure-percentage.md)

### ICM Incidents

- Homepage - ICM incidents — see [06-icm-incidents.md](06-icm-incidents.md)

### Vulnerabilities

- WIP Trivy Vulernabilities by Severity — see [07-vulnerabilities.md](07-vulnerabilities.md)
- WIP Trivy Vulnerabilities — see [07-vulnerabilities.md](07-vulnerabilities.md)
