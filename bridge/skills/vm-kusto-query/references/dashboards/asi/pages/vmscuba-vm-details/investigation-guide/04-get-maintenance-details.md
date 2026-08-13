# Get Maintenance details 

> Source: **VM Scuba - VM Details** dashboard, chapter **Get Maintenance details ** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-MaintenanceDetails

_Widget purpose:_ Get Maintenance details 

Cluster: `Azdeployer.kusto.windows.net` · Database: `AzDeployerKusto` · Type: `Table`
Source panel: `Get Maintenance details `

```kusto
cluster('Azdeployer').database('AzDeployerKusto').GetCurrentMaintenanceStatus_Batching(subscriptionId,roleInstanceName,tenantName)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subscriptionId}`, `{roleInstanceName}`, `{tenantName}`

---
