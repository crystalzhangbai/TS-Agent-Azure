# NodeServiceMadariEvents

> Source: **NodeService - Peregrine_ContainerEvents** dashboard, chapter **NodeServiceMadariEvents** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### NodeServiceMadariEventsEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `NodeServiceMadariEvents`

```kusto
NodeServiceMadariEventsEtwTable
| where PreciseTimeStamp between (queryFrom..queryTo)
| where RelativePath contains containerId or (vmUniqueId != "" and ContextSelector contains vmUniqueId) or (azLogicalContainerId != "" and ContextSelector contains azLogicalContainerId)
| project PreciseTimeStamp, Message, Operation, RelativePath, ContextSelector
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{vmUniqueId}`, `{azLogicalContainerId}`

---
