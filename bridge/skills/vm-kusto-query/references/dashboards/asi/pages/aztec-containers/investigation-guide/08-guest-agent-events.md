# Guest Agent Events

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Guest Agent Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Guest Agent Extension Events

### Container Guest Agent Extension Events

_Widget purpose:_ Guest Agent Extension Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Guest Agent Events > Guest Agent Extension Events`

```kusto
GuestAgentExtensionEvents
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where ContainerId == queryContainerId and Operation !in ("HeartBeat", "Firewall")
| extend OperationSuccess = tobool(OperationSuccess)
| extend level = iff(OperationSuccess == false, 'error', '')
| project 
    PreciseTimeStamp, NodeId, VMId, ContainerId, NodeIdentity, OSVersion, TenantName, Name, Version, level,
    Operation, OperationSuccess, Message, Duration, TaskName, ResourceGroupName, RoleName, RoleInstanceName
| order by PreciseTimeStamp desc
```

**Params:** `{queryContainerId}`, `{global_startTime}`, `{global_endTime}`

---
