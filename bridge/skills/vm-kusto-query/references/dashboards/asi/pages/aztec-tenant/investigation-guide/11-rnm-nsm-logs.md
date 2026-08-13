# RNM & NSM Logs

> Source: **Aztec — Tenant** dashboard, chapter **RNM & NSM Logs** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## RNM & NSM Logs

### Query DeleteResourceEvent

_Widget purpose:_ Aznwmds - DeleteResourceEvent

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Table`
Source panel: `RNM & NSM Logs > RNM & NSM Logs > Aznwmds - DeleteResourceEvent`

```kusto
DeleteResourceEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where AssociatedServiceId contains queryTenantName
| project PreciseTimeStamp, SubscriptionId, AssociatedServiceId, ResourceOwnerId, ResourceOwnerType, DeletedResourceId, DeletedResourceType, DeletedEvent, OperationDuration, RnmTimestamp, FabricId
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query ResourceReleaseEvent

_Widget purpose:_ ResourceReleaseEvent

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Table`
Source panel: `RNM & NSM Logs > RNM & NSM Logs > ResourceReleaseEvent`

```kusto
ResourceReleaseEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where Region contains queryRegion
| where Message contains queryTenantName
| summarize arg_max(PreciseTimeStamp, *) by Message
| extend ServiceId = extract(@'service: ([^\s]+) ', 1, Message)
| extend ServiceId = iff(ServiceId == '', extract(@'ServiceId: ([^\s]+) ', 1, Message), ServiceId)
| extend ServiceId = iff(ServiceId == '', extract(@'ServiceInstanceId:\s*([^\s\.]+) ', 1, Message), ServiceId)
| extend FabricId = extract(@'Cleanup of resource in fabric ([^\s]+) exceeded', 1, Message)
| extend FabricId = iff(FabricId == '', extract(@'FabricId:\s*([\w-]+)', 1, Message), FabricId)
| extend PendingReason = case(
    Message has "Fabric role instance container of" and Message has 'not created for the AzSM', 'AzSM: FRIC not created',
    Message has 'Cleanup of PreProvisionedVm AllocatedMac' and Message has "in AzSM", 'AzSM: FRIC release not received (PPS)',
    Message has 'Cleanup of role instance' and Message has 'in AzSM', 'AzSM: FRIC release not received (regular)',
    Message has 'Cleanup of resource in fabric ' and Message has 'VipToCheck' and Message has 'pending in NSM', "NSM: VIP cleanup",
    Message has 'Cleanup of resource in fabric ' and Message has 'VipToCheck' and Message has 'pending in TM', "TM: VIP cleanup",
    Message has 'Cleanup of resource in fabric ' and Message has 'VipToCheck' and Message has 'IsPendingCleanupInTM:False IsPendingCleanupInNsm:False', "RNM: VIP TBD pending delete",
    Message has 'Cleanup of resource in fabric ' and Message has 'VipToCheck' and Message has 'pending in NsmPlus' and Message has 'IsRevert:False', "NsmPlus: VIP cleanup (no revert from NSM)",
    Message has 'Cleanup of resource in fabric ' and Message has 'VipToCheck' and Message has 'pending in NsmPlus' and Message has 'ProgramStatus:Programmed, IsRevert:True', "NsmPlus: VIP cleanup (reverted and completed)",
    Message has 'Cleanup of resource in fabric ' and Message has 'VipToCheck' and Message has 'pending in NsmPlus', "NsmPlus: VIP cleanup (VipToCheck)",
    Message has 'Cleanup of resource in fabric ' and Message has 'VipToCheck' and Message has 'IsSpanned:True', "NsmPlus: VIP cleanup (to be investigated)",
    Message has 'Cleanup of resource in fabric ' and Message has 'LBVipToCheck' and Message has 'IsPendingCleanupInTM:False IsPendingCleanupInNsm:False', "RNM: LB VIP TBD cleanup",
    Message has 'Cleanup of resource in fabric ' and Message has 'LBVipToCheck' and Message has 'IsSpanned:True', "NsmPlus: VIP cleanup (LBVipToCheck)",
    Message has 'Cleanup of resource in fabric ' and Message has 'LBVipToCheck' and Message has 'IsSpanned:False', "NSM: VIP cleanup",
    Message has 'Cleanup of resource in fabric ' and Message has 'FabricRoleInstanceContainerToCheck' and Message has 'NsmPlus pending release of', "NsmPlus: VIP cleanup (FRIC)",
    Message has 'Cleanup of resource in fabric ' and Message has 'FabricRoleInstanceContainerToCheck' and Message has 'Fabric(TM)', "TM: role instance cleanup",
    Message has 'Cleanup of resource in fabric ' and Message has 'FabricRoleInstanceContainerToCheck' and Message has 'Fabric(NSM)', "NSM: CA cleanup",
    Message has 'Cleanup of resource in fabric ' and Message has 'FabricRoleInstanceContainerToCheck', 'NsmPlus: FRIC check pending for fabric (to be investigated)',
    Message has 'Cleanup of resource in fabric ' and Message has 'RoleInstanceToCheck' and Message has 'Fabric(TM)', "TM: role instance cleanup",
    Message has 'Cleanup of resource in fabric ' and Message has 'RoleInstanceToCheck' and Message has 'Fabric(NSM)', "NSM: CA cleanup",
    Message has 'Cleanup of resource in fabric ' and Message has 'RoleInstanceToCheck' and Message has 'SuspectComponentForCleanupDelay:PIP, IsPendingCleanupInTM:False IsPendingCleanupInNsm:True', 'NSM: public IP cleanup',
    Message has 'Cleanup of resource in fabric ' and Message has 'RoleInstanceToCheck' and Message has 'SuspectComponentForCleanupDelay:RoleInstance, IsPendingCleanupInTM:True IsPendingCleanupInNsm:True', 'TM: role instance cleanup',
    Message has 'Cleanup of resource in fabric ' and Message has 'RoleInstanceToCheck' and Message has 'SuspectComponentForCleanupDelay:UDWalkPending', 'TM: UD walk pending',
    Message has 'Cleanup of resource in fabric ' and Message has 'RoleInstanceToCheck' and Message has 'SuspectComponentForCleanupDelay:UDWalkNotInitiated', 'TM: UD walk not initiated',
    Message has 'Cleanup of resource in fabric ' and Message has 'RoleInstanceToCheck' and Message has 'SuspectComponentForCleanupDelay:RoleInstance, IsPendingCleanupInTM:False IsPendingCleanupInNsm:True', 'NSM: role instance (CA) cleanup',
    Message has 'Cleanup of resource in fabric ' and Message has 'RoleInstanceToCheck' and Message has 'IsPendingCleanupInTM:True', 'TM: role instance cleanup',
    Message has 'Cleanup of resource in fabric ' and Message has 'RoleInstanceToCheck' and Message has 'IsPendingCleanupInTM:False IsPendingCleanupInNsm:True', 'NSM: role instance cleanup',
    Message has 'Cleanup of resource in fabric ' and Message has 'PreProvisionedVmToCheck' and Message has 'SuspectComponentForCleanupDelay:CA, IsPendingCleanupInTM:False IsPendingCleanupInNsm:True', "NSM: PPS VM CA cleanup",
    Message has 'Cleanup of resource in fabric ' and Message has 'PreProvisionedVmToCheck' and Message has 'SuspectComponentForCleanupDelay:RoleInstance, IsPendingCleanupInTM:True', "TM: PPS VM role instance cleanup",
    Message has 'Cleanup of resource in fabric ' and Message has 'PreProvisionedVmToCheck' and Message has 'IsPendingCleanupInTM:True', "TM: PPS VM cleanup",
    'Uncategorized'
)
| where ServiceId contains queryTenantName
| project PreciseTimeStamp, Region, RnmPartitionId, PendingReason, FabricId, ServiceId, Message
| sort by Region, PendingReason asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRegion}`

---

### Query ServiceExecutionEvent

_Widget purpose:_ ServiceExecutionEvent

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Table`
Source panel: `RNM & NSM Logs > RNM & NSM Logs > ServiceExecutionEvent`

```kusto
ServiceExecutionEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region contains queryRegionName
| where Message  contains queryTenantName
| project PreciseTimeStamp, OpName, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRegionName}`

---
