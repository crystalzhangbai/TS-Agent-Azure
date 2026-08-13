# VM Restart Events

> Source: **VM Scuba - VM Details** dashboard, chapter **VM Restart Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-VMRestartEvents

_Widget purpose:_ VM Restart Events

Cluster: `moseisley.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `VM Restart Events`

```kusto
//let VMuniqueID == virtualMachineUniqueId
cluster('moseisley.kusto.windows.net').database('Air').GetVMRestartEvents(virtualMachineUniqueId,queryFrom,queryTo)
| project Timestamp,SubscriptionId,RoleInstanceName,EventType,IsCustomerInitiated,ImpactBeginTimeStamp,ImpactEndTimeStamp,ImpactDurationTimeSpan
```

**Params:** `{queryFrom}`, `{queryTo}`, `{virtualMachineUniqueId}`

---
