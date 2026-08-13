# (top-level)

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Azure VM" ResourceHealth DS

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `ResourceGet` · Widget: `Card`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and assert(isnotempty(local_containerId) or isnotempty(local_virtualMachineUniqueId), "Either a container Id or VM Id must be specified")
| where (isempty(local_containerId) or containerId == local_containerId) and (isempty(local_virtualMachineUniqueId) or virtualMachineUniqueId == local_virtualMachineUniqueId)
| summarize arg_max(PreciseTimeStamp, creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, nodeId, tipNodeSessionId, Tenant, tenantName, availabilitySetName, billingType, roleType, additionalContainerProperties, RegionFriendlyName) by containerId
| distinct creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, containerId, nodeId, tipNodeSessionId, Tenant, tenantName, availabilitySetName, billingType, roleType, additionalContainerProperties, RegionFriendlyName
| extend additionalContainerProperties = parse_json(additionalContainerProperties)
| join kind=leftouter (
    cluster('azcore.centralus').database('Fc').LogContainerPolicySnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h))
    | summarize arg_min(PreciseTimeStamp, memoryInMB, hostMemoryReservationInMBytes) by Tenant, policyInstanceName
    | project Tenant, policyInstanceName, memoryInMB, hostMemoryReservationInMBytes
) on $left.Tenant == $right.Tenant and $left.containerType == $right.policyInstanceName
| join kind=inner(
    cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogClusterSnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h))
    | distinct shoeboxMdmAccountName, Tenant
) on Tenant
| project-away Tenant1, Tenant, policyInstanceName
| extend globalFrom = globalFrom, globalTo = globalTo
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_containerId}`, `{local_nodeId}`, `{local_virtualMachineUniqueId}`

---

### LogContainerHealthSnapshot_RH_VMId_CM

Cluster: `Azurecm` · Database: `AzureCM` · Type: `Table` · Widget: `Card`

```kusto
union cluster('Azcim-centralus.centralus').database('AZCIM').AzTMHealthAnnotationEvent,LogHealthAnnotationEvent 
| where PreciseTimeStamp >= query_StartTime and PreciseTimeStamp <= query_EndTime
| where * contains query_VMId
| project-away TIMESTAMP, Role, Tid, SourceNamespace, SourceMoniker, NodeId, SourceVersion, CloudName, Region, DataCenterName, AvailabilityZone, RoleInstance 
| sort by PreciseTimeStamp asc
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_VMId}`

---

### VmShoeboxCounterTable DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Card`

```kusto
VmShoeboxCounterTable
| where PreciseTimeStamp between ((query_StartTime - 1h) .. (query_EndTime + 1h)) and VmId =~ query_ContainerId
| distinct ArmId
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_ContainerId}`

---
