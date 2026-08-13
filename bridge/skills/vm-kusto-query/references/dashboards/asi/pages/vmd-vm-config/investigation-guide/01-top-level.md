# (top-level)

> Source: **VM Details - VM Config** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "VM Config"

Cluster: `azcsupfollower.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
cluster('azcsupfollower.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and assert(isnotempty(local_containerId) or isnotempty(local_nodeId) or isnotempty(local_roleInstanceName), "Either a container Id or node Id must be specified")
| where (isempty(local_containerId) or containerId == local_containerId) and (isempty(local_nodeId) or nodeId == local_nodeId) and (isempty(local_roleInstanceName) or roleInstanceName contains local_roleInstanceName) 
| summarize arg_max(PreciseTimeStamp, creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, nodeId, Tenant, tenantName, availabilitySetName, billingType, roleType, additionalContainerProperties, RegionFriendlyName, AvailabilityZone) by containerId
| join kind = leftouter 
(cluster('vmainsight.kusto.windows.net').database('vmadb').CADDAILY
    | where PreciseTimeStamp >= ago(2d)) on $left.containerId == $right.ContainerId
| distinct creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, containerId, nodeId, Tenant, tenantName, availabilitySetName, billingType, roleType, additionalContainerProperties, RegionFriendlyName, FD, UD, Region, Usage_VMScaleSetId, AvailabilityZone, Hardware_Generation 
| join kind=inner(
    cluster('azcsupfollower.kusto.windows.net').database('AzureCM').LogClusterSnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h))
    | distinct shoeboxMdmAccountName, Tenant
) on Tenant
| project-away Tenant1 
| extend globalFrom = globalFrom, globalTo = globalTo
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_containerId}`, `{local_nodeId}`, `{local_roleInstanceName}`

---
