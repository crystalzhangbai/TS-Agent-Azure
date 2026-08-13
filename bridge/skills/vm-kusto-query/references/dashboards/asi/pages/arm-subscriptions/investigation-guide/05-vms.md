# VMs

> Source: **ARM — Subscriptions** dashboard, chapter **VMs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VMs

### Subscription VMs

_Widget purpose:_ VMs

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `VMs > VMs`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between(queryFrom..queryTo) and subscriptionId == querySubscription
| distinct creationTime, roleInstanceName, containerId, virtualMachineUniqueId, nodeId, tenantName, Tenant, Region
| extend creationTime = todatetime(creationTime)
```

**Params:** `{querySubscription}`, `{queryFrom}`, `{queryTo}`

---
