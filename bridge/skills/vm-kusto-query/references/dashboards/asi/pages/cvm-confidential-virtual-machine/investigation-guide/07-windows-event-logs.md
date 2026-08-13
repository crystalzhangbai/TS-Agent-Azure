# Windows Event Logs

> Source: **Confidential Virtual Machines - Confidential Virtual Machine** dashboard, chapter **Windows Event Logs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Windows Event Table

_Widget purpose:_ Windows Event Logs

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Windows Event Logs`

```kusto
cluster('azcore.centralus').database('Fa').WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Description has_any (queryContainers)
| extend ext_containerId = extract(@"[[:alnum:]]{8}-[[:alnum:]]{4}-[[:alnum:]]{4}-[[:alnum:]]{4}-[[:alnum:]]{12}", 0, Description)
| where ext_containerId in(queryContainers)
| sort by ContainerId = ext_containerId, TimeCreated asc 
| project Level, TimeCreated, Channel, NodeId, Cluster, ContainerId = ext_containerId, Description
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainers}`

---
