# (top-level)

> Source: **Managed Disk - Managed by VM** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Managed by VM"

Cluster: `AzureCM` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
// print cluster = local_Tenant, tenantName = local_tenantName, containerId = local_containerId, nodeId = local_nodeId, vmid = local_virtualMachineUniqueId, roleInstanceName = 
// | extend vmid = iff(isnotempty(vmid), vmid, "nodata")
cluster('azcsupfollower.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between ((globalFrom - 6h) .. (globalTo + 6h))
| where containerId == local_containerid and roleInstanceName == local_roleInstanceName
| where isnotempty(roleInstanceName)
| top 1 by PreciseTimeStamp
| project cluster = Tenant, tenantName, containerId, nodeId, vmid=virtualMachineUniqueId, roleInstanceName, subscriptionId, creationTime = todatetime(creationTime), additionalContainerProperties, containerType, billingType, priority, tenantOwners, Region, RegionFriendlyName
| extend Dummy = "***"
```

**Params:** `{local_cluster}`, `{local_containerid}`, `{local_nodeid}`, `{local_Region}`, `{local_roleInstanceName}`, `{local_subscriptionId}`, `{local_tenantname}`, `{local_vmid}`, `{globalFrom}`, `{globalTo}`

---
