# Container Health status

> Source: **VM Scuba - VM Details** dashboard, chapter **Container Health status** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-ContainerHealthStatus

_Widget purpose:_ Container Health status

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `Container Health status`

```kusto
cluster('azurecm.kusto.windows.net').database('AzureCM').LogContainerHealthSnapshot
| where containerId == containerId
| project PreciseTimeStamp, Tenant, roleInstanceName,tenantName, containerId, nodeId,containerState, containerLifecycleState, containerOsState, faultInfo
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
