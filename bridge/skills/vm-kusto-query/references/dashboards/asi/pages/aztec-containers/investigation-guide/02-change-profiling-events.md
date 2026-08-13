# Change Profiling Events

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Change Profiling Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Change Profiling Events

### Change Profiling Events

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Change Profiling Events > Change Profiling Events`

```kusto
TMMgmtTenantChangeProfilingEventEtwTable
| where PreciseTimeStamp between(global_startTime..global_endTime) and ContainerId == queryContainerId
//| project PreciseTimeStamp, CurrentUD, ChangeEventType, FromState, ToState, RoleName, RoleInstanceName
| order by PreciseTimeStamp desc
```

**Params:** `{queryContainerId}`

---
