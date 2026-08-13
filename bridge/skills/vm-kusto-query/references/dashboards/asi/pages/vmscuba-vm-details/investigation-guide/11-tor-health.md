# TOR Health

> Source: **VM Scuba - VM Details** dashboard, chapter **TOR Health** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-TORHealth

_Widget purpose:_ TOR Health

Cluster: `azphynet.kusto.windows.net` · Database: `azdhmds` · Type: `Table`
Source panel: `TOR Health`

```kusto
let nodeIdlist = (cluster('azphynet').database('azdhmds').DeviceInterfaceLinks
                | where EndDevice =~ '{TOR}' and LinkType =~ 'DeviceInterfaceLink'
                | summarize by DeviceName = StartDevice
                | join kind = inner (
                    cluster('azphynet').database('azdhmds').Servers
                ) on DeviceName
                | summarize by NodeId);
                cluster('aznwsdn').database('aznwmds').TorPingSendAggreEvent
                | where TIMESTAMP >= bin(datetime({startTime}), 5m) and TIMESTAMP < datetime({endTime}) 
                | where NodeId in~ (nodeIdlist)
                | summarize SendCount = max(SendCount) by TIMESTAMP, NodeId
                | join kind = leftouter (
                    cluster('aznwsdn').database('aznwmds').TorPingRecvAggreEvent
                    | where TIMESTAMP >= bin(datetime({startTime}), 5m) and TIMESTAMP < datetime({endTime})  
                    | where NodeId in~ (nodeIdlist)
                    | summarize RecvCount = max(RecvCount) by TIMESTAMP, NodeId
                ) on TIMESTAMP, NodeId
                | extend RecvCount = iff(isnull(RecvCount), 0, RecvCount)
                | project TIMESTAMP, rate = todouble(RecvCount)/todouble(SendCount) * 100, NodeId, RecvCount, SendCount
                | summarize rate = max(rate) by TIMESTAMP
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `EndDevice =~ "{TOR}"`

---
