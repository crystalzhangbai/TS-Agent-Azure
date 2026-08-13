# VMs

> Source: **CRP Resource Groups Investigation Guide** dashboard, chapter **VMs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VMs

### Resource Group VMs

_Widget purpose:_ VMs

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `VMs > VMs`

```kusto
VMApiQosEvent
| where subscriptionId == local_subscriptionId and resourceGroupName =~ local_resourceGroup
| summarize FirstSeen = arg_min(PreciseTimeStamp, *), LastSeen = max(PreciseTimeStamp) by resourceName, vMId, MonitoringApplication
```

**Params:** `{local_subscriptionId}`, `{local_resourceGroup}`

---
