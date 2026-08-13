# NodeService - NodeService_NodeView — Investigation Guide

Chapter-keyed reference derived from the **NodeService - NodeService_NodeView** dashboard. Every KQL query backing the dashboard is included here, organized by the dashboard's own chapter hierarchy (no curation, no symptom-based re-categorization). An AI agent or human investigator can route from the chapter title (e.g. *"Hardware Investigation"*, *"Service Healing"*) directly to the queries that answer it.

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

- [(top-level)](01-top-level.md) — 33 queries
- [CMWorkerNodeServiceChannel failures](02-cmworkernodeservicechannel-failures.md) — 1 queries
- [NodeService Events](03-nodeservice-events.md) — 1 queries
- [NodeService Exits](04-nodeservice-exits.md) — 1 queries
- [NodeService SoC Logs](05-nodeservice-soc-logs.md) — 1 queries
- [NodeService Watchdog events](06-nodeservice-watchdog-events.md) — 1 queries
- [TMMgmtNodeEvents](07-tmmgmtnodeevents.md) — 1 queries
- [WindowsEvents](08-windowsevents.md) — 1 queries

**Total queries: 40**

## Query index (by file)

### (top-level)

- Retrieve Resource "NodeService_NodeView" — see [01-top-level.md](01-top-level.md)
- Networking dashboard query — see [01-top-level.md](01-top-level.md)
- NodeServiceVersion — see [01-top-level.md](01-top-level.md)
- SDP Phase — see [01-top-level.md](01-top-level.md)
- SocId — see [01-top-level.md](01-top-level.md)
- ApSvcMgr State — see [01-top-level.md](01-top-level.md)
- LogNodeSnapshot - NodeState — see [01-top-level.md](01-top-level.md)
- Madari errors — see [01-top-level.md](01-top-level.md)
- Anvil Repair Diagnostics — see [01-top-level.md](01-top-level.md)
- NodeService Exits — see [01-top-level.md](01-top-level.md)
- Fabric incarnations — see [01-top-level.md](01-top-level.md)
- SEL Events — see [01-top-level.md](01-top-level.md)
- TOR Send Packet Health — see [01-top-level.md](01-top-level.md)
- TOR Recv Packet Health — see [01-top-level.md](01-top-level.md)
- TOR InMaintenance — see [01-top-level.md](01-top-level.md)
- CM WillBe Generation — see [01-top-level.md](01-top-level.md)
- TOR in Quarantine Network — see [01-top-level.md](01-top-level.md)
- Soc Health — see [01-top-level.md](01-top-level.md)
- SeedIncarnation query — see [01-top-level.md](01-top-level.md)
- SocHB — see [01-top-level.md](01-top-level.md)
- WindowsEvents — see [01-top-level.md](01-top-level.md)
- ContainerState and ASILink — see [01-top-level.md](01-top-level.md)
- Events Count — see [01-top-level.md](01-top-level.md)
- Overlake Healthstore Data — see [01-top-level.md](01-top-level.md)
- Cluster level node unhealthy metrics — see [01-top-level.md](01-top-level.md)
- Node Snapshot — see [01-top-level.md](01-top-level.md)
- CMWorkerNodeServiceWas — see [01-top-level.md](01-top-level.md)
- CMWorkerNodeServiceWillBe — see [01-top-level.md](01-top-level.md)
- CMWorkerNodeEvents — see [01-top-level.md](01-top-level.md)
- MemoryReport — see [01-top-level.md](01-top-level.md)
- CPU_Usage — see [01-top-level.md](01-top-level.md)
- CPU Graph — see [01-top-level.md](01-top-level.md)
- ProcessMemUsage — see [01-top-level.md](01-top-level.md)

### CMWorkerNodeServiceChannel failures

- CMWorkerNodeServiceChannel failures — see [02-cmworkernodeservicechannel-failures.md](02-cmworkernodeservicechannel-failures.md)

### NodeService Events

- NodeService Events — see [03-nodeservice-events.md](03-nodeservice-events.md)

### NodeService Exits

- NodeService Exits — see [04-nodeservice-exits.md](04-nodeservice-exits.md)

### NodeService SoC Logs

- Echo — see [05-nodeservice-soc-logs.md](05-nodeservice-soc-logs.md)

### NodeService Watchdog events

- NodeServiceWatchdogEtwTable — see [06-nodeservice-watchdog-events.md](06-nodeservice-watchdog-events.md)

### TMMgmtNodeEvents

- TMMgmtNodeEventsTable — see [07-tmmgmtnodeevents.md](07-tmmgmtnodeevents.md)

### WindowsEvents

- WindowsEventsTable — see [08-windowsevents.md](08-windowsevents.md)
