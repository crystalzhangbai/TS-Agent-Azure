# Peregrine_ContainerEvents — Investigation Guide

Chapter-keyed reference derived from the **Peregrine_ContainerEvents** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 15 queries
- [AgentNfcHttpDownloadFileEtwTable](02-agentnfchttpdownloadfileetwtable.md) — 1 queries
- [AzCiMadariOperationEvent](03-azcimadarioperationevent.md) — 1 queries
- [AzCiMContainerWas](04-azcimcontainerwas.md) — 1 queries
- [AzCiMContainerWillBe](05-azcimcontainerwillbe.md) — 1 queries
- [NodeServiceEvents](06-nodeserviceevents.md) — 1 queries
- [NodeServiceMadariEvents](07-nodeservicemadarievents.md) — 1 queries

**Total queries: 21**

## Query index (by file)

### (top-level)

- Retrieve Resource "Peregrine_ContainerEvents" — see [01-top-level.md](01-top-level.md)
- WillBePublishesToMadariFromAzCiM — see [01-top-level.md](01-top-level.md)
- NS Madari WillBe/Was Interactions — see [01-top-level.md](01-top-level.md)
- NodeService Completed Operations — see [01-top-level.md](01-top-level.md)
- NodeService Started Operations — see [01-top-level.md](01-top-level.md)
- ContainerTimeline — see [01-top-level.md](01-top-level.md)
- Fault Events — see [01-top-level.md](01-top-level.md)
- IsTip — see [01-top-level.md](01-top-level.md)
- Was/WillBe publishes (Madari POV) — see [01-top-level.md](01-top-level.md)
- AzPubSub Publishing — see [01-top-level.md](01-top-level.md)
- lxprov — see [01-top-level.md](01-top-level.md)
- ApSvcMgr State — see [01-top-level.md](01-top-level.md)
- LogNodeSnapshot - NodeState — see [01-top-level.md](01-top-level.md)
- Fault Information — see [01-top-level.md](01-top-level.md)
- EG links — see [01-top-level.md](01-top-level.md)

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
