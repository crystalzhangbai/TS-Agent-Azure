# VM placement thru time on host node(s)

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **VM placement thru time on host node(s)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Container History DS

_Widget purpose:_ VM placement thru time on host node(s)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `VM placement thru time on host node(s)`

```kusto
LogContainerSnapshot
| where subscriptionId =~ query_SubscriptionId and roleInstanceName has query_VMName
| extend ext_prop = parse_json(additionalContainerProperties)
| extend diskController = tostring(ext_prop.DiskControllerType)
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp) by roleInstanceName, creationTime, virtualMachineUniqueId, Tenant, containerId, nodeId, tenantName,containerType, updateDomain,  subscriptionId, diskController
| project ContainerCreationTime=todatetime(creationTime), StartTimeStamp=min_PreciseTimeStamp, EndTimeStamp=max_PreciseTimeStamp, VMName=roleInstanceName, virtualMachineUniqueId, Cluster=Tenant, nodeId, containerId, tenantName, containerType, updateDomain,  subscriptionId, diskController
| order by ContainerCreationTime asc
| join kind=leftouter (cluster('azurevmcentral.westus2.kusto.windows.net').database('azurevmcentral').latest_vm_definitions) on $left.containerType == $right.fabricname
```

**Params:** `{query_SubscriptionId}`, `{query_VMName}`

---
