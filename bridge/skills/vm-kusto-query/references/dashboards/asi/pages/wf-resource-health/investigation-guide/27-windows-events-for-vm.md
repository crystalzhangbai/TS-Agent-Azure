# Windows Events for VM

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **Windows Events for VM** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### WindowsEventsForVM

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Windows Events for VM`

```kusto
WindowsEventTable
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where NodeId =~ queryNodeId and Description contains queryContainerId
| where EventId in (18500, 18502, 18504, 18508, 18512, 18514, 18560, 18590, 18603)
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| order by TimeCreated asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

---
