# Get HostOS Updates

> Source: **VM Scuba - VM Details** dashboard, chapter **Get HostOS Updates** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-HostOSUpdates

_Widget purpose:_ Get HostOS Updates

Cluster: `AzureCM.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `Get HostOS Updates`

```kusto
//cluster('AzureCM.kusto.windows.net').database('AzureCM').
TMMgmtNodeEventsEtwTable  
| where NodeId =~ nodeId  and (Message contains 'CreatePluginComplete' or Message contains 'UpdatePluginCompleted')
| parse kind = regex Message with * ' = HostPluginName:' Component:string ', HostPluginSetupFile:' * 'HostPluginPackage:'package:string ', Action:'* 
| project PreciseTimeStamp=TIMESTAMP, Component, NewVersion=package
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---
