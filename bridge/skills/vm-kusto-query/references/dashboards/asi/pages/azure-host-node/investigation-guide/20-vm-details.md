# VM Details

> Source: **Azure Host — Azure Host Node** dashboard, chapter **VM Details** (3 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VM IO Limits

### Azure Host Node VM Cached Throttle Settings

_Widget purpose:_ VM's IO Throttle Limits (Cached) configured

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Details > VM IO Limits > VM's IO Throttle Limits (Cached) configured`

```kusto
cluster('azurecm.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (startTime .. endTime) and nodeId == nodeIdStr
| distinct containerId, containerType, roleInstanceName
| join kind=inner(
     cluster('azurecm.kusto.windows.net').database('AzureCM').LogContainerPolicySnapshot
     | where PreciseTimeStamp between (startTime .. endTime) and Tenant == cluster
     | distinct policyInstanceName, virtualCores
) on $left.containerType == $right.policyInstanceName
| project-away policyInstanceName
| join kind=inner(
    OsBlobCacheConfigTableV2
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeIdStr
            and EntityType == 3
    | where UserData contains "XioSettingsSsdThrottle"
    | parse UserData with * "Throttle" containerId '"' *
    | extend EntityConfig = parse_json(EntityConfig), UserData = parse_json(UserData)
    | summarize arg_max(PreciseTimeStamp, *) by EntityId
    | project containerId, IOPS = todouble(EntityConfig.max_iops), BPS = todouble(EntityConfig.max_bps) * todouble(EntityConfig.bps_multiplier) / 100.0,
                            BurstIOPS = todouble(EntityConfig.burst_iops),
                            BurstBPS = todouble(EntityConfig.burst_bps)
) on containerId
| project-away containerId1
| sort by virtualCores asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeIdStr}`, `{cluster}`

**Signal filters seen in KQL:** `UserData contains "XioSettingsSsdThrottle"`

---

### Azure Host Node VM Throttle Settings

_Widget purpose:_ VM's IO Throttle Limits (Uncached) configured

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Details > VM IO Limits > VM's IO Throttle Limits (Uncached) configured`

```kusto
cluster('azurecm.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (startTime .. endTime) and nodeId == nodeIdStr
| distinct containerId, containerType, roleInstanceName
| join kind=inner(
     cluster('azurecm.kusto.windows.net').database('AzureCM').LogContainerPolicySnapshot
     | where PreciseTimeStamp between (startTime .. endTime) and Tenant == cluster
     | distinct policyInstanceName, virtualCores
) on $left.containerType == $right.policyInstanceName
| project-away policyInstanceName
| join kind=inner(
    OsBlobCacheConfigTableV2
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeIdStr
            and EntityType == 3
    | where UserData contains "XioSettingsnetworkthrottle"
    | parse UserData with * "Throttle" containerId '"' *
    | extend EntityConfig = parse_json(EntityConfig), UserData = parse_json(UserData)
    | summarize arg_max(PreciseTimeStamp, *) by EntityId
    | project containerId, XIO_IOPS = todouble(EntityConfig.max_iops), XIO_BPS = todouble(EntityConfig.max_bps) * todouble(EntityConfig.bps_multiplier) / 100.0,
                            DD_IOPS = round(todouble(EntityConfig.max_iops) * todouble(UserData.user_data.IopsDirectDriveMultiplier)/100.0), 
                            DD_BPS = round(todouble(EntityConfig.max_bps) * (todouble(EntityConfig.bps_multiplier) / 100.0) * todouble(UserData.user_data.BpsDirectDriveMultiplier)/100.0),
                            XIO_BurstIOPS = todouble(EntityConfig.burst_iops),
                            XIO_BurstBPS = todouble(EntityConfig.burst_bps),
                            DDurstIOPS = round(todouble(EntityConfig.burst_iops) * todouble(UserData.user_data.IopsDirectDriveMultiplier)/100.0),
                            DD_BurstBPS = round(todouble(EntityConfig.burst_bps) * (todouble(EntityConfig.bps_multiplier) / 100.0) * todouble(UserData.user_data.BpsDirectDriveMultiplier)/100.0)
) on containerId
| project-away containerId1
| sort by virtualCores asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeIdStr}`, `{cluster}`

**Signal filters seen in KQL:** `UserData contains "XioSettingsnetworkthrottle"`

---

## VMs

### Azure Host Running VMs Query

_Widget purpose:_ VM Running in the Host Node

Cluster: `Storageclient.eastus` · Database: `AzureCP` · Type: `Table`
Source panel: `VM Details > VMs > VM Running in the Host Node`

```kusto
let vmDetails = MycroftContainerSnapshot
| where PreciseTimeStamp between ((_startTime - 1h) .. (_endTime + 1h)) and NodeId == _nodeId and isnotempty(RoleInstanceName)
| union (
    database("Fc").LogContainerSnapshot
    | where PreciseTimeStamp between ((_startTime - 1h) .. (_endTime + 1h)) and nodeId == _nodeId and isnotempty(roleInstanceName)
    | extend ContainerId = containerId, CreationTime = todatetime(creationTime), RoleInstanceName = roleInstanceName, AdditionalContainerProperties = additionalContainerProperties,
             NodeId = nodeId, ClusterName = Tenant, TipNodeSessionId = tipNodeSessionId, AvailabilitySetName = availabilitySetName, VirtualMachineUniqueId = virtualMachineUniqueId,
             PolicyName = containerType, SubscriptionId = subscriptionId
)
| extend DiskControllerType = tostring(parse_json(AdditionalContainerProperties).DiskControllerType) 
| extend ContainerId, tostring(CreationTime), RoleInstanceName, SubscriptionId, ContainerType = PolicyName, VirtualMachineUniqueId,
    NodeId, TipNodeSessionId, TenantName, AvailabilitySetName, billingType = "", RoleType, AdditionalContainerProperties, Tenant = ClusterName
| summarize arg_max(PreciseTimeStamp, CreationTime, RoleInstanceName, SubscriptionId, ContainerType, VirtualMachineUniqueId, NodeId, DiskControllerType) by ContainerId
| extend creationTime = todatetime(CreationTime), lastKnownTime = PreciseTimeStamp, DiskControllerType
| project creationTime, lastKnownTime, RoleInstanceName, DiskControllerType, ContainerType, ContainerId, VirtualMachineUniqueId, NodeId, SubscriptionId;
let subscriptionIds = vmDetails | distinct SubscriptionId;
let subscriptionDetailsDataStudio = cluster('datastudiostreaming').database('Shared').DataStudio_AzureSubscription_Snapshot
| where SubscriptionId in~ (subscriptionIds)
| distinct SubscriptionId, SubscriptionName, CustomerName;
let subscriptionDetailsCustomerDomData = cluster('customerdomrptwus3prod.westus3').database('CustomerDomData').CustomerModel
| where SubscriptionGuid_String in~ (subscriptionIds)
| distinct SubscriptionId = SubscriptionGuid_String, SubscriptionName = FriendlySubscriptionName, CloudCustomerName, TopParentName = TPNameTranslated;
let subscriptionDetails = union subscriptionDetailsDataStudio, subscriptionDetailsCustomerDomData
| summarize take_anyif(SubscriptionName, isnotempty(SubscriptionName)), 
            take_anyif(CustomerName, isnotempty(CustomerName)), 
            take_anyif(CloudCustomerName, isnotempty(CloudCustomerName)), 
            take_anyif(TopParentName, isnotempty(TopParentName))
            by SubscriptionId
| distinct SubscriptionId, SubscriptionName, 
           CustomerName = case(isnotempty(CustomerName), CustomerName, isnotempty(CloudCustomerName), CloudCustomerName, isnotempty(TopParentName), TopParentName, strcat(SubscriptionName, ' ', CloudCustomerName, ' ', TopParentName));
vmDetails | join kind = leftouter subscriptionDetails on SubscriptionId
| distinct creationTime, lastKnownTime, RoleInstanceName, DiskControllerType, ContainerType, ContainerId, VirtualMachineUniqueId, NodeId, SubscriptionId, SubscriptionName, CustomerName
| join kind = leftouter (
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventViewExtended
    | where PreciseTimeStamp between (_startTime.._endTime) and NodeId == _nodeId
    | extend ContainerId = tostring(json.ContainerId)
    | where isnotempty(containerId)
    | summarize arg_max(PreciseTimeStamp, VfId) by ContainerId
    | project PreciseTimeStamp, ContainerId, VfId
) on ContainerId
| distinct creationTime, lastKnownTime, RoleInstanceName, DiskControllerType, ContainerType, ContainerId, VfId, VirtualMachineUniqueId, NodeId, SubscriptionId, SubscriptionName, CustomerName
| order by creationTime asc
```

**Params:** `{_nodeId}`, `{_startTime}`, `{_endTime}`

---
