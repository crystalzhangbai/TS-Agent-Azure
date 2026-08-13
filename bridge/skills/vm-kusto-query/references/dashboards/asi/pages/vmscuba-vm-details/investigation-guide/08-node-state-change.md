# Node state change

> Source: **VM Scuba - VM Details** dashboard, chapter **Node state change** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-NodeStateChange

_Widget purpose:_ Node state change

Cluster: `AzureCM.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `Node state change`

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtNodeStateChangedEtwTable  
| where BladeID == nodeId
| project PreciseTimeStamp, RoleInstance, Tenant, OldState, NewState, BladeID
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---
