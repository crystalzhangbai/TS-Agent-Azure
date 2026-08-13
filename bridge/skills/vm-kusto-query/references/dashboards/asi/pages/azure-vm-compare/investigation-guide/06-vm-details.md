# VM Details

> Source: **Azure VM Compare Investigation Guide** dashboard, chapter **VM Details** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Container1 Details

### Retrieve Resource "Azure VM"

_Widget purpose:_ Container1 Details

Cluster: `AzureCM` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Card`
Source panel: `VM Details > Container1 Details`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and assert(isnotempty(local_containerId) or isnotempty(local_virtualMachineUniqueId), "Either a container Id or VM Id must be specified")
| where (isempty(local_containerId) or containerId == local_containerId) and (isempty(local_virtualMachineUniqueId) or virtualMachineUniqueId == local_virtualMachineUniqueId)
| union (
    cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and assert(isnotempty(local_containerId) or isnotempty(local_virtualMachineUniqueId), "Either a container Id or VM Id must be specified")
    | where (isempty(local_containerId) or ContainerId == local_containerId) and (isempty(local_virtualMachineUniqueId) or VirtualMachineUniqueId == local_virtualMachineUniqueId) and isnotempty(RoleInstanceName)
    | extend containerId = ContainerId, creationTime = tostring(CreationTime), roleInstanceName = RoleInstanceName, 
         subscriptionId = SubscriptionId, containerType = PolicyName, virtualMachineUniqueId = VirtualMachineUniqueId,
         nodeId = NodeId, tipNodeSessionId = TipNodeSessionId, tenantName = TenantName, availabilitySetName = AvailabilitySetName,
         billingType = "", roleType = RoleType, additionalContainerProperties = AdditionalContainerProperties, Tenant = ClusterName
)
| summarize arg_max(PreciseTimeStamp, creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, nodeId, tipNodeSessionId, Tenant, tenantName, availabilitySetName, billingType, roleType, additionalContainerProperties, RegionFriendlyName) by containerId
| distinct creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, containerId, nodeId, tipNodeSessionId, Tenant, tenantName, availabilitySetName, billingType, roleType, additionalContainerProperties, RegionFriendlyName
| parse roleInstanceName with "_" VMName
| extend additionalContainerProperties = parse_json(additionalContainerProperties)
| extend DiskControllerType = tostring(additionalContainerProperties.DiskControllerType)
| join kind=leftouter (
    LogContainerPolicySnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h))
    | summarize arg_min(PreciseTimeStamp, memoryInMB, hostMemoryReservationInMBytes) by Tenant, policyInstanceName
    | project Tenant, policyInstanceName, memoryInMB, hostMemoryReservationInMBytes
) on Tenant and $left.containerType == $right.policyInstanceName
| join kind=inner(
    LogClusterSnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h))
    | distinct shoeboxMdmAccountName, Tenant
) on Tenant
| join kind=leftouter (
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').GuestOSDetailEtwTable
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and ContainerId =~ local_containerId
    | summarize arg_max(PreciseTimeStamp, OSType, OSVersion, VMType, OSName, OSKernelVersion) by ContainerId
    | project ContainerId, GuestOSType = OSType, GuestOSName = OSName, GuestOSVersion = OSVersion, GuestOSKernelVersion = OSKernelVersion, VMType
) on $left.containerId == $right.ContainerId
| project-away Tenant1, Tenant2, policyInstanceName, ContainerId
| extend globalFrom = globalFrom, globalTo = globalTo
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_containerId}`, `{local_nodeId}`, `{local_virtualMachineUniqueId}`

---

## Container2 Details

### Retrieve Resource "Azure VM"

_Widget purpose:_ Container2 Details

Cluster: `AzureCM` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Card`
Source panel: `VM Details > Container2 Details`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and assert(isnotempty(local_containerId) or isnotempty(local_virtualMachineUniqueId), "Either a container Id or VM Id must be specified")
| where (isempty(local_containerId) or containerId == local_containerId) and (isempty(local_virtualMachineUniqueId) or virtualMachineUniqueId == local_virtualMachineUniqueId)
| union (
    cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and assert(isnotempty(local_containerId) or isnotempty(local_virtualMachineUniqueId), "Either a container Id or VM Id must be specified")
    | where (isempty(local_containerId) or ContainerId == local_containerId) and (isempty(local_virtualMachineUniqueId) or VirtualMachineUniqueId == local_virtualMachineUniqueId) and isnotempty(RoleInstanceName)
    | extend containerId = ContainerId, creationTime = tostring(CreationTime), roleInstanceName = RoleInstanceName, 
         subscriptionId = SubscriptionId, containerType = PolicyName, virtualMachineUniqueId = VirtualMachineUniqueId,
         nodeId = NodeId, tipNodeSessionId = TipNodeSessionId, tenantName = TenantName, availabilitySetName = AvailabilitySetName,
         billingType = "", roleType = RoleType, additionalContainerProperties = AdditionalContainerProperties, Tenant = ClusterName
)
| summarize arg_max(PreciseTimeStamp, creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, nodeId, tipNodeSessionId, Tenant, tenantName, availabilitySetName, billingType, roleType, additionalContainerProperties, RegionFriendlyName) by containerId
| distinct creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, containerId, nodeId, tipNodeSessionId, Tenant, tenantName, availabilitySetName, billingType, roleType, additionalContainerProperties, RegionFriendlyName
| parse roleInstanceName with "_" VMName
| extend additionalContainerProperties = parse_json(additionalContainerProperties)
| extend DiskControllerType = tostring(additionalContainerProperties.DiskControllerType)
| join kind=leftouter (
    LogContainerPolicySnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h))
    | summarize arg_min(PreciseTimeStamp, memoryInMB, hostMemoryReservationInMBytes) by Tenant, policyInstanceName
    | project Tenant, policyInstanceName, memoryInMB, hostMemoryReservationInMBytes
) on Tenant and $left.containerType == $right.policyInstanceName
| join kind=inner(
    LogClusterSnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h))
    | distinct shoeboxMdmAccountName, Tenant
) on Tenant
| join kind=leftouter (
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').GuestOSDetailEtwTable
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and ContainerId =~ local_containerId
    | summarize arg_max(PreciseTimeStamp, OSType, OSVersion, VMType, OSName, OSKernelVersion) by ContainerId
    | project ContainerId, GuestOSType = OSType, GuestOSName = OSName, GuestOSVersion = OSVersion, GuestOSKernelVersion = OSKernelVersion, VMType
) on $left.containerId == $right.ContainerId
| project-away Tenant1, Tenant2, policyInstanceName, ContainerId
| extend globalFrom = globalFrom, globalTo = globalTo
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_containerId}`, `{local_nodeId}`, `{local_virtualMachineUniqueId}`

---
