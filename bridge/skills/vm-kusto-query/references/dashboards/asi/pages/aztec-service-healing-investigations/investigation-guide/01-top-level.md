# (top-level)

> Source: **Aztec Service Healing Investigations Guide** dashboard, chapter **(top-level)** (5 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Container Metedata Query from mycroft

_Widget purpose:_ Source Container Metadata

Cluster: `mycroft.westcentralus.kusto.windows.net` · Database: `Mycroft` · Type: `Single` · Widget: `Card`

```kusto
let containerMetadata = cluster('azcore.centralus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
| where ContainerId == _sourceContainerIdToHeal
| where PreciseTimeStamp between ((queryFrom-1d) .. (queryTo+1d))
| summarize arg_min(PreciseTimeStamp, *) by ContainerId
| extend p = bag_pack("ContainerId", ContainerId,
    "FcName", ClusterName,
    "AzCluster", Cluster,
    "NodeId", NodeId,
    "VMid", VirtualMachineUniqueId,
    "TenantName", TenantName,
    "RoleInstanceName", RoleInstanceName,
    "AvSetName", AvailabilitySetName,
    "RoleType", RoleType,
    "CreationTIme", CreationTime,
    "ContainerLifeCycleOwner", ContainerLifeCycleOwner,
    "ContainerType", ContainerType,
    "RoleInstaneFamilyId", RoleInstanceFamilyIds,
    "RegionName", Region,
    "IsContainerAzPEEnabled", IsContainerAzPEEnabled,
    "IsManageMentRole", IsManagementRoleEnabled,
    "Priority", Priority)
;
containerMetadata
| project CreationTime, ContainerId, Cluster, FcName = ClusterName, NodeId, VirtualMachineUniqueId,
    TenantName, RoleInstanceName, AvailabilitySetName, RoleType, ContainerLifeCycleOwner, ContainerType,
    RoleInstanceFamilyIds, Region, IsContainerAzPEEnabled, IsManagementRoleEnabled, Priority, SubscriptionId,
        PolicyName, IsEphemeralVM, IsLMDestinationContainer
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_sourceContainerIdToHeal}`

---

### Mycroft container health summary

_Widget purpose:_ Container Health Summary

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Single` · Widget: `Card`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp between ((queryFrom-1h) .. (queryTo+1h))
| where ContainerId == queryContainerId
| summarize arg_min(PreciseTimeStamp, *)
| project PreciseTimeStamp, ContainerState, IsFaulted, IsInGoalState, IsRunning, ExpectedVMHealthState, LastStartedTime, FirstStartedTime,
    LifecycleState, ActualOperationalState, LifecycleStateChangeTime, OsState, IsolationState,
    IsGoalUnachievable, IsTombstoned, ProvisioningState, ActualVMHealthState, FaultInfo
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---

### Mycroft Node Health Summary

_Widget purpose:_ Node Health Summary

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Single` · Widget: `Card`

```kusto
let nId = (MycroftContainerHealthSnapshot
| where PreciseTimeStamp between ((queryFrom-1h) .. (queryTo+1h))
| where ContainerId == queryContainerId
| distinct NodeId);
MycroftNodeHealthSnapshot
| where NodeId in (nId)
| extend nFaultInfo = parse_json(FaultInfo)
| extend FaultScope = toint(nFaultInfo['FaultScope']), FaultTime = todatetime(nFaultInfo['Time']),
    FaultCode = toint(nFaultInfo['FaultCode']), FaultReason = tostring(nFaultInfo['Reason'])
// | where AvailabilityState == 'Faulted' and NsdState == 'HumanInvestigate' and FaultScope == 3
| where PreciseTimeStamp between ((queryFrom-1h) .. (queryTo+1h))
| summarize arg_min(PreciseTimeStamp, *) by NsdState, AvailabilityState
| project PreciseTimeStamp, Cluster, ClusterName, FaultScope, FaultTime, FaultCode, FaultReason, ContainerCount, AliveContainerCount, AlivePreemptibleContainerCount,
    NodeBugCheckIsolationStatus, IsTombstoned,
    AvailabilityState, IsIsolated, IsOffline, NsdState, NodeServiceAggregatedHealthStatus,
    NsdStateChangeTime, NodeServiceWasChannelHealthStatus, NodeServiceWillBeChannelHealthStatus, NodeServiceProgressHealthStatus,
    IsMaintenanceOs, nFaultInfo
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

**Signal filters seen in KQL:** `AvailabilityState == "Faulted"`

---

### Tenant Summary Query

_Widget purpose:_ Tenant Snapshot Summary

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Single` · Widget: `Card`

```kusto
alias database mycroftDb = cluster('azcore.centralus.kusto.windows.net').database('AzureCP');
//alias database azureCmDb = cluster('hawkeyekustocluster.centralus.kusto.windows.net').database('AzureCM');
alias database azureCmDb = cluster('azurecm.kusto.windows.net').database('AzureCM');
let tenantDetails = toscalar(database('mycroftDb').MycroftContainerHealthSnapshot
| where PreciseTimeStamp between ((queryFrom-1h) .. (queryTo+1h))
| where ContainerId == queryContainerId
| extend p = bag_pack('FcClusterName', ClusterName, 'TenantNameToCheck', TenantName)
| summarize make_bag(p));
let spannedClustersData = toscalar(database('azureCmDb').LogTenantSnapshot
| where PreciseTimeStamp between ((queryFrom-1h) .. (queryTo+1h))
| where tenantName == tenantDetails['TenantNameToCheck'] // 
| summarize arg_max(PreciseTimeStamp, *) by Tenant
| summarize make_list(Tenant))
;
database('azureCmDb').LogTenantSnapshot
| where PreciseTimeStamp between ((queryFrom-1h) .. (queryTo+1h))
| where tenantName == tenantDetails['TenantNameToCheck'] and Tenant == tenantDetails['FcClusterName']
| summarize arg_max(PreciseTimeStamp, *)
| extend spannedClusters = spannedClustersData
| join kind=inner(
database('azureCmDb').LogTenantOverridableSettingsSnapshot
| where PreciseTimeStamp between ((queryFrom-1d) .. (queryTo+1h))
| where tenantName == tenantDetails['TenantNameToCheck'] and Tenant == tenantDetails['FcClusterName']
| where name == 'AzSMTenantSliceLocation'
| summarize arg_max(PreciseTimeStamp, *)
| project PreciseTimeStamp, tenantName, name, AzSMSliceLocation= value
) on tenantName
| extend
    AzSMTenantDataUrl = strcat(
        "https://",
        AzSMSliceLocation,
        "/TM/api/v1/Tenants/",
        tenantName,
        "/TenantDataV2"), // https://asiaeast-prod-c.azcp.fc.core.windows.net/debug/Manual/AzLifecycle-Slice2-P1/TM/api/v1/Tenants/ccbe44c0-5538-4fca-87d9-0e9e4530331a/TenantDataV2
    AzSMTMSwaggerUrl = strcat(
        "https://",
        AzSMSliceLocation,
        "/TM/Swagger/ui/index"), // https://uscentraleuap-prod-b.azcp.fc.core.windows.net/debug/Manual/AzSM-Slice0/TM/Swagger/ui/index
    AzSM_Tenant_View = strcat(
        "https://",
        AzSMSliceLocation,
        "/TM/api/v1/Tenants/",
        tenantName)
| project PreciseTimeStamp, AvailabilityZone, Tenant, AzSMTenantDataUrl, AzSMTMSwaggerUrl, tenantName, AzSM_Tenant_View, spannedClusters, isSpanned,
    isAzPEEnabled, numRoleInstances, subscriptionId,
    hasManagementRole, state, lastUpdateDomainChangeTime, isProtected, tenantOwners,
    dateCreated, serviceInstanceTags, serviceTreeId,
    tipNodeSessionId, tenantId, isFcServiceHealingDisabled = isServiceHealingDisabled, FcServiceHealingDisabledReason = serviceHealingDisabledReason,
        tenantUpgradeRolloutWaitReason, serviceInstancesDetails, productionFeatures, isPreprovisionedTenant,
        secretCount, ownershipMigrationDetails, isSpannable, isCreatedViaReserveActivate,
        mrPrivilegeType, isCrossTenantApprovalEnabled, isSqlMITenant
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

**Signal filters seen in KQL:** `name == "AzSMTenantSliceLocation"`

---

### FC Service Healing Trigger QUery

_Widget purpose:_ FC Service Healing Summary

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
ServiceHealingTriggerEtwTable
| where TriggerObjectId == _sourceContainerIdToHeal
| where PreciseTimeStamp between ((queryFrom-1d) .. (queryTo+1d))
| summarize arg_max(PreciseTimeStamp, *)
| project PreciseTimeStamp, TenantName, TriggerId, TriggerType, TriggerObjectId,
    FaultCode, FaultReason, AffectedUpdateDomain, RoleInstanceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_sourceContainerIdToHeal}`

---
