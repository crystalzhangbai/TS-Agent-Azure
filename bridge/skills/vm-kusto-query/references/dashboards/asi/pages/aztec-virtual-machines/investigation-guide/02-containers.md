# Containers

> Source: **Aztec Virtual Machines Investigation Guide** dashboard, chapter **Containers** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Containers

### Virtual Machine Containers Table

_Widget purpose:_ Containers

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Containers > Containers`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where virtualMachineUniqueId == queryVmId
| summarize StartTime = min(PreciseTimeStamp), EndTime = arg_max(PreciseTimeStamp, *) by containerId
| extend tableNodeId = nodeId, tableContainerId = containerId, tableCluster = Tenant
| order by StartTime desc
```

**Params:** `{queryVmId}`

---
