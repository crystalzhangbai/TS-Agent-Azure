# ARM Correlation Ids Investigation Guide — Investigation Guide

Chapter-keyed reference derived from the **ARM Correlation Ids Investigation Guide** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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
- [CoBe Timeline](02-cobe-timeline.md) — 1 queries
- [Deployment Operations](03-deployment-operations.md) — 2 queries
- [Deployments](04-deployments.md) — 1 queries
- [Execution Graph](05-execution-graph.md) — 1 queries
- [Incoming Requests](06-incoming-requests.md) — 2 queries
- [Outgoing Requests](07-outgoing-requests.md) — 2 queries
- [Preflight Operations](08-preflight-operations.md) — 1 queries

**Total queries: 11**

## Query index (by file)

### (top-level)

- Retrieve Resource "Correlation Ids" — see [01-top-level.md](01-top-level.md)

### CoBe Timeline

- ARMCorrelationId — see [02-cobe-timeline.md](02-cobe-timeline.md)

### Deployment Operations

- Deployment Operations — see [03-deployment-operations.md](03-deployment-operations.md)
- All or Errors — see [03-deployment-operations.md](03-deployment-operations.md)

### Deployments

- Deployments by Correlation Id — see [04-deployments.md](04-deployments.md)

### Execution Graph

- Lookup up EG — see [05-execution-graph.md](05-execution-graph.md)

### Incoming Requests

- Incoming Requests — see [06-incoming-requests.md](06-incoming-requests.md)
- All or Errors — see [06-incoming-requests.md](06-incoming-requests.md)

### Outgoing Requests

- Outgoing Requests — see [07-outgoing-requests.md](07-outgoing-requests.md)
- All or Errors — see [07-outgoing-requests.md](07-outgoing-requests.md)

### Preflight Operations

- Correlation ID - Preflight Ops — see [08-preflight-operations.md](08-preflight-operations.md)
