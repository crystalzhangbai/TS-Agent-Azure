# RoleInstanceDownTimeEvents

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **RoleInstanceDownTimeEvents** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### RoleInstanceDowntimeEvent

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `RoleInstanceDownTimeEvents`

```kusto
TMMgmtRoleInstanceDowntimeEventEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where RoleInstanceName contains vmname
|project Issuetimestamp= PreciseTimeStamp, RoleInstanceName,ActivityType, NodeId, ContainerId, ActivityDetail,Region
| order by Issuetimestamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmname}`

---
