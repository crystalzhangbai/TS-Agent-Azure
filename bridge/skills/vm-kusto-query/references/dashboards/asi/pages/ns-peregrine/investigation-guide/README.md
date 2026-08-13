# NodeService - NodeService_Peregrine — Investigation Guide

Chapter-keyed reference derived from the **NodeService - NodeService_Peregrine** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 3 queries
- [AgentNfcHttpDownloadFileEtwTable](02-agentnfchttpdownloadfileetwtable.md) — 1 queries
- [AzCiMadariOperationEvent](03-azcimadarioperationevent.md) — 1 queries
- [AzCiMContainerWas](04-azcimcontainerwas.md) — 1 queries
- [AzCiMContainerWillBe](05-azcimcontainerwillbe.md) — 1 queries
- [NodeServiceEvents](06-nodeserviceevents.md) — 1 queries
- [NodeServiceMadariEvents](07-nodeservicemadarievents.md) — 1 queries

**Total queries: 9**

## Query index (by file)

### (top-level)

- WillBePublishesToMadariFromAzCiM — see [01-top-level.md](01-top-level.md)
- WillBeReceiptsFromMadari — see [01-top-level.md](01-top-level.md)
- ContainerWorkflowBlocked — see [01-top-level.md](01-top-level.md)

### AgentNfcHttpDownloadFileEtwTable

- AgentNfcHttpDownloadFileEtwTable — see [02-agentnfchttpdownloadfileetwtable.md](02-agentnfchttpdownloadfileetwtable.md)

### AzCiMadariOperationEvent

- AzCiMMadariOperationEvent — see [03-azcimadarioperationevent.md](03-azcimadarioperationevent.md)

### AzCiMContainerWas

- AzCiMContainerWas — see [04-azcimcontainerwas.md](04-azcimcontainerwas.md)

### AzCiMContainerWillBe

- AzCiMContainerWillBe — see [05-azcimcontainerwillbe.md](05-azcimcontainerwillbe.md)

### NodeServiceEvents

- NodeServiceEventsEtwTable — see [06-nodeserviceevents.md](06-nodeserviceevents.md)

### NodeServiceMadariEvents

- NodeServiceMadariEventsEtwTable — see [07-nodeservicemadarievents.md](07-nodeservicemadarievents.md)
