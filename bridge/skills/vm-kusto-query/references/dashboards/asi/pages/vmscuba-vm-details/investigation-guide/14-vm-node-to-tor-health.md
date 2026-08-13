# VM Node to TOR Health

> Source: **VM Scuba - VM Details** dashboard, chapter **VM Node to TOR Health** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-VMNodetoTORHealth

_Widget purpose:_ VM Node to TOR Health

Cluster: `aznwsdn.kusto.windows.net` · Database: `aznwmds` · Type: `Table`
Source panel: `VM Node to TOR Health`

```kusto
cluster('aznwsdn').database('aznwmds').TorPingSendAggreEvent
                | where TIMESTAMP >= datetime({startTime}) and TIMESTAMP < datetime({endTime}) 
                | where NodeId =~ nodeId
                | summarize SendCount = max(SendCount) by TIMESTAMP, NodeId
                | join kind = leftouter
                (
                 cluster('aznwsdn').database('aznwmds').TorPingRecvAggreEvent
                | where TIMESTAMP >= datetime({startTime}) and TIMESTAMP < datetime({endTime}) 
                | where NodeId =~ '{nodeId}'
                | summarize RecvCount = max(RecvCount) by TIMESTAMP, NodeId
                )on TIMESTAMP, NodeId
                | extend RecvCount = iff(isnull(RecvCount), 0, RecvCount)
                | project TIMESTAMP, NodeId, Availability = todouble(RecvCount) / todouble(SendCount) * 100
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

**Signal filters seen in KQL:** `NodeId =~ "{nodeId}"`

---
