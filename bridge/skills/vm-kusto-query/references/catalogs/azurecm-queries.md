# AzureCM Queries — Container, Node, Fault, Recovery, Service Healing, Live Migration, Capacity

Cluster: `azurecm.kusto.windows.net` (or `Azcsupfollower.kusto.windows.net`)
Database: `AzureCM`

---

## Container State & Operation

### LogContainerSnapshot — VM host placement history

```kusto
let sid="{SubscriptionId}";
let vmname="{VMName}";
cluster("AzureCM").database("AzureCM").LogContainerSnapshot
| where subscriptionId == sid and roleInstanceName has vmname
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp) by roleInstanceName, creationTime, virtualMachineUniqueId, Tenant, containerId, nodeId, tenantName, containerType, updateDomain, availabilitySetName, subscriptionId
| project VMName=roleInstanceName, VirtualMachineUniqueId=virtualMachineUniqueId, Cluster=Tenant, NodeId=nodeId, ContainerId=containerId,
    ContainerCreationTime=todatetime(creationTime), StartTimeStamp=min_PreciseTimeStamp, EndTimeStamp=max_PreciseTimeStamp, tenantName, containerType, updateDomain, availabilitySetName, subscriptionId
| order by ContainerCreationTime asc
```

### LogContainerSnapshot — VMs on a specific node (last 3 days)

```kusto
cluster("AzureCM").database("AzureCM").LogContainerSnapshot
| where nodeId == "{NodeId}"
| where PreciseTimeStamp > ago(3d)
| distinct creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, nodeId, containerId
```

### LogContainerHealthSnapshot — Container health & OS state

```kusto
cluster('Azcsupfollower.kusto.windows.net').database('AzureCM').LogContainerHealthSnapshot
| where PreciseTimeStamp between (datetime({BeginTime}) .. datetime({EndTime}))
| where roleInstanceName contains "{VMName}"
| project PreciseTimeStamp, Tenant, roleInstanceName, tenantName, containerId, nodeId,
  containerState, actualOperationalState, containerLifecycleState, containerOsState, faultInfo, vmExpectedHealthState, virtualMachineUniqueId,
  containerIsolationState, AvailabilityZone, Region
```

Filter tips:
- `containerOsState == "ContainerOsStateUnresponsive"` — guest OS unresponsive
- `containerOsState == "GuestOsStateProvisioningRecovery"` — provisioning recovery
- `faultInfo <> ""` — CreateContainer failures

### LogContainerSnapshot + Gandalf — Unallocatable node check

```kusto
let dateTime_StartTime = datetime_add('day', -8, {BeginTime});
let dateTime_EndTime = datetime_add('hour', +1, {BeginTime});
let subscriptionId = '{SubscriptionId}';
let vmName = '{VMName}';
cluster('Azcsupfollower').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between(dateTime_StartTime..dateTime_EndTime)
| where subscriptionId =~ subscriptionId and roleInstanceName has vmName
| project-rename ContainerId = containerId
| distinct nodeId, ContainerId
| join kind = inner
(cluster('Gandalf').database('gandalf').GandalfUnallocableNodesHistorical
| project-rename FoundTimestamp = PreciseTimeStamp
| where State == "Unallocatable") on $left.nodeId == $right.NodeId
| join kind = inner
(cluster('Azcsupfollower').database('AzureCM').LogContainerHealthSnapshot
| where PreciseTimeStamp >= {BeginTime} and containerState has "ContainerStateDestroyed"
| project-rename IssueTimestamp = PreciseTimeStamp
) on $left.nodeId == $right.nodeId
| where containerId == ContainerId
| where (IssueTimestamp - datetime_add('day', +7, FoundTimestamp)) between (0min .. 10min)
| distinct FoundTimestamp, State, nodeId, IssueTimestamp, ContainerId, containerState
```

---

## Node Events on Cluster Manager

### TMMgmtNodeStateChangedEtwTable — Node state changes / reboots

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtNodeStateChangedEtwTable
| where BladeID == "{NodeId}"
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| project PreciseTimeStamp, BladeID, OldState, NewState
```

### TMMgmtNodeStateChangedEtwTable — Multiple node reboots on same cluster

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtNodeStateChangedEtwTable
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| where Tenant == "{Cluster}"
| where NewState == "Booting"
| project PreciseTimeStamp, BladeID, OldState, NewState
```

### LogNodeSnapshot — Node inventory / count by machinePoolName for a cluster

Use this for questions like "how many nodes per machine pool", "why only N nodes can host SKU X", "cluster node breakdown". This is the ONLY table for machine pool analysis — do NOT try other tables.

```kusto
cluster('Azcsupfollower.kusto.windows.net').database('AzureCM').LogNodeSnapshot
| where Tenant == "{Cluster}" and PreciseTimeStamp > ago(2h)
| summarize arg_max(PreciseTimeStamp, *) by nodeId
| summarize NodeCount=dcount(nodeId) by machinePoolName, nodeState
| order by NodeCount desc
```

Variant — include hardware generation / disk config:

```kusto
cluster('Azcsupfollower.kusto.windows.net').database('AzureCM').LogNodeSnapshot
| where Tenant == "{Cluster}" and PreciseTimeStamp > ago(2h)
| summarize arg_max(PreciseTimeStamp, *) by nodeId
| summarize NodeCount=dcount(nodeId) by machinePoolName, nodeState, diskConfiguration
| order by machinePoolName asc, NodeCount desc
```

Key columns (all on `LogNodeSnapshot`): `nodeId`, `nodeState`, `nodeAvailabilityState`, `machinePoolName`, `Tenant`, `containerCount`, `diskConfiguration`, `faultInfo`, `rootUpdateAllocationType`.

### LogNodeSnapshot — Unallocatable, OFR, node state

```kusto
cluster('Azcsupfollower.kusto.windows.net').database('AzureCM').LogNodeSnapshot
| where nodeId =~ "{NodeId}" and PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| project PreciseTimeStamp, nodeState, nodeAvailabilityState, containerCount, diskConfiguration, faultInfo, rootUpdateAllocationType, RoleInstance
```

Filter tips:
- `nodeState == "PoweringOn"` — node restart
- `nodeAvailabilityState == "Unallocatable"` — node marked unallocatable
- `diskConfiguration == "AllDisksInStripe"` — disk config change

### LogNodeSnapshot — Check if node is OFR

```kusto
cluster("AzureCM").database("AzureCM").LogNodeSnapshot
| where PreciseTimeStamp >= ago(2h) and nodeId == "{NodeId}" and Tenant == "{Cluster}" and nodeState == "OutForRepair"
```

### LogNodeSnapshot — ABC (Azure Blob Cache) host configuration detection

Use this to determine whether a host node has ABC enabled. Standard-storage VMs on "mixed-storage" host nodes (where premium VMs also live) get ABC and therefore expose disk-utilization counters; on "pure standard" hosts they don't. Critical when the customer reports missing/unexpected disk shoebox metrics.

```kusto
cluster('Azcsupfollower').database('AzureCM').LogNodeSnapshot
| where nodeId == "{NodeId}" and PreciseTimeStamp > ago(2h)
| distinct diskConfiguration
```

Interpretation:
- `AllDisksAbc` — ABC enabled (mixed-storage host) → disk shoebox/disk-utilization counters available for all VMs on this node.
- `AllDisksInStripe` — pure standard-storage host → ABC disabled, standard VMs will NOT show disk-utilization metrics.
- TSG: [Disk Metrics_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/Disk-Metrics_Perf) — explains "why doesn't my standard-storage VM show disk metrics".

### TMMgmtNodeEventsEtwTable — Detailed node operations

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtNodeEventsEtwTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| project PreciseTimeStamp = tostring(PreciseTimeStamp), Message
| sort by PreciseTimeStamp asc
```

Message filter tips:
- `"Node reboot event: EventType:"` — reboot events
- `"->"` — state transitions (e.g., Ready -> HumanInvestigate)
- `"Marking container"` — VM stopped by fabric
- `"Fault Code: 10005"` — start container failures
- `"Not enough memory"` — OOM conditions
- `"PrepareMode"` — disk config changes requiring reboot

### TMMgmtNodeEventsEtwTable — Dirty shutdown confirmation

```kusto
let timeSpan = 7d;
let NodeIdentifier = "{NodeId}";
cluster("AzureCM").database("AzureCM").TMMgmtNodeEventsEtwTable
| where NodeId == NodeIdentifier and PreciseTimeStamp >= ago(timeSpan) and Message contains "Node reboot event: EventType: "
| parse Message with "Node reboot event: EventType: " eventType "," * "EventTimeStamp: " eventTimeStamp:datetime "," *
| project PreciseTimeStamp, eventTimeStamp, RoleInstance, Tenant, NodeId, eventType, Message
| where eventType in ("DirtyShutdown", "BugCheck", "PXEEvent")
| union(
cluster("AzureCM").database("AzureCM").TMMgmtNodeEventsEtwTable
| where NodeId == NodeIdentifier and PreciseTimeStamp >= ago(timeSpan) and Message contains "EventType: FabricInitiatedPowerCycleFaultHandler"
| project PreciseTimeStamp, eventTimeStamp = PreciseTimeStamp, RoleInstance, Tenant, NodeId, eventType = "UnhealthyNodePowerCycle", Message
)
| where eventType == "DirtyShutdown"
```

### TMMgmtContainerTraceEtwTable — Detailed container events

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtContainerTraceEtwTable
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp < datetime({EndTime})
| where ContainerID == "{ContainerId}"
| project PreciseTimeStamp, ContainerID, Message
```

### TMMgmtTenantEventsEtwTable — Fabric-triggered operations

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtTenantEventsEtwTable
| where TenantName == "{TenantName}"
| where PreciseTimeStamp > datetime({BeginTime}) and PreciseTimeStamp < datetime({EndTime})
| project PreciseTimeStamp, TaskName, TenantName, Message
```

Message filter tips:
- `"unhealthy"` — unhealthy node trigger of SH
- `"LiveMigration"` — live migration events
- `"Not enough memory in the system to start"` — host node OOM

### TMMgmtTenantEventsEtwTable — OOM at cluster level

```kusto
let err = "Not enough memory in the system to start";
cluster("AzureCM").database("AzureCM").TMMgmtTenantEventsEtwTable
| where Message contains err
| where PreciseTimeStamp >= datetime({BeginTime})
| parse Message with * ' NodeId: ' NodeId '. StatusCode:' SC
| project PreciseTimeStamp, Tenant, NodeId, TenantName
| summarize count() by NodeId, Tenant
```

### TMMgmtSlaMeasurementEventEtwTable — Container & tenant state details

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtSlaMeasurementEventEtwTable
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp < datetime({EndTime})
| where ContainerID == "{ContainerId}"
| project PreciseTimeStamp, Context, EntityState, Detail0, Tenant, TenantName, RoleInstanceName, NodeID, ContainerID, Region
```

Filter: `EntityState == "GuestOsStateHardPowerOff"` — hard power off

### ServiceManagerInstrumentation — Host Agent service versions on a node

Use this to check the deployed version of all host-side services/agents (NodeService, GenevaAgent, VmphuSvc, NmAgent, LmAgent, etc.) at a specific point in time. Useful for verifying whether a known fix has been deployed to a node.

```kusto
cluster("Azcsupfollower.kusto.windows.net").database("AzureCM").ServiceManagerInstrumentation
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| summarize arg_max(PreciseTimeStamp, ServiceName) by ServiceVersion
| project PreciseTimeStamp, ServiceName, ServiceVersion
| sort by ServiceName asc
```

Key services to check:
- `NodeService` — NodeService version (e.g., `NodeService_8_19_0_2355`)
- `GenevaAgent` — Geneva monitoring agent (e.g., `ap_2024_09_20_20009_icm541907848`)
- `GenevaMetricsExtension` — Geneva metrics extension
- `VmphuSvc` — VM PHU service (e.g., `20251113_pf_master_144_0_10_614`)
- `RdAgentUpdater` — RD Agent with HA release name (e.g., `r_oct_2025_151_25_10_63`)
- `NmAgent` — NM Agent
- `LmAgent` — Live Migration Agent
- `DCMUpdater` — DCM version

### ServiceVersionSwitch — Storage Datapath (DPP) updates on a node

Detect storage-side datapath updates on a specific host node. The storage datapath update (DPP = DataPath Plugin) is rolled per-node and freezes disk I/O for ~9 seconds during the cut-over; commonly mis-attributed to "random VM slow". Use this to confirm a perf blip was a DPP cut-over.

```kusto
let queryFrom = datetime({StartTime});
let queryTo   = datetime({EndTime});
let queryNodeId = "{NodeId}";
cluster("azcsupfollower").database("AzureCM").ServiceVersionSwitch
| where NodeId == queryNodeId and PreciseTimeStamp between (queryFrom .. queryTo)
| project PreciseTimeStamp, ServiceName, CurrentVersion, NewVersion, SourceOfService, Tenant, NodeId
| order by PreciseTimeStamp asc
| where NewVersion contains 'Datapath'
| project StartTime = PreciseTimeStamp, Content = ServiceName, ServiceName, CurrentVersion, NewVersion, SourceOfService, Tenant, NodeId
```

Sample version strings: `Datapath_7_10_0_94_153_10_0_94` → `Datapath_7_10_0_173_153_10_0_173` (DPP 153 rollout).

Interpretation:
- A row landing inside the customer's impact window confirms DPP cut-over correlation. Expected `DiskImpact = Freeze`, `EstimatedImpactDurationInSeconds = 9` (verify via `AzPEWorkflowEvent` for `AzPEHostUpdateMonitor` — see `operations-queries.md`).
- Customers can preempt this via the IMDS Scheduled Events API; perf-sensitive workloads can request VMPhu disablement.
- For region-wide rollout progress ("is DPP X done in eastus?"), use `GetSimpleDeploymentProgress()` on `storageclient.eastus.kusto.windows.net` — see `operations-queries.md`.
- TSG: [Datapath Update Impact_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/Datapath-Update-Impact_Perf).

---

## Node Fault & Recovery (Anvil/Tardigrade)

### AnvilRepairServiceForgeEvents — Anvil recovery actions

```kusto
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceForgeEvents
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| where ResourceDependencies has_any ("{NodeId}")
| where TreeNodeKey !in ('Root', 'Node')
| summarize arg_max(PreciseTimeStamp, *) by RequestIdentifier, TreeNodeKey
| order by RequestIdentifier, PreciseTimeStamp asc
| project PreciseTimeStamp, AnvilOperation=TreeNodeKey, NodeId=tostring(parse_json(ResourceDependencies).NodeId), AnvilRequestIdentifier=RequestIdentifier, ResourceId, ResourceType
| sort by PreciseTimeStamp asc
```

### FaultHandlingRecoveryEventEtwTable — Fabric recovery actions

```kusto
cluster("AzureCM").database("AzureCM").FaultHandlingRecoveryEventEtwTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| project PreciseTimeStamp, NodeId, Reason, RecoveryAction, RecoveryResult
```

RecoveryAction values: `PowerCycle`, `RestartNodeService`, `HumanInvestigate`, `ResetNodeHealth`, `RebootNode`, `MarkNodeAsUnallocatable`

### DCMLMResourceResultEtwTable — BMC-SEL hardware faults at node restart

```kusto
cluster("AzureCM").database("AzureCM").DCMLMResourceResultEtwTable
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| where ResourceId == "{NodeId}"
| project PreciseTimeStamp, ResourceId, ResultType, ActivityName, FaultCode, FaultReason, DeviceType
```

---

## Service Healing

### ServiceHealingTriggerEtwTable — SH confirmation & details

```kusto
cluster("AzureCM").database("AzureCM").ServiceHealingTriggerEtwTable
| where NodeId == "{NodeId}"
| where TenantName == "{TenantName}"
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp < datetime({EndTime})
```

### AzSMTenantEvents — Alternate tenant event view

```kusto
cluster("AzureCM").database("AzureCM").AzSMTenantEvents
| where PreciseTimeStamp > datetime({BeginTime}) and PreciseTimeStamp < datetime({EndTime})
| where tenantName =~ "{TenantName}"
| project PreciseTimeStamp, Tenant, message
```

### AzSMTenantSnapshotV2 — Which AzLifecycle slice owns the tenant

Use this to identify which AzLifecycle service slice (`AzLifecycle-SliceN-Pn`) currently owns the tenant. Required input to figure out which `accp.centralus / AZSM` slice logs to read next when investigating `OutOfTimeBudgetException` / `FabricInternalOperationError`.

```kusto
cluster("Azcsupfollower").database("AzureCM").AzSMTenantSnapshotV2
| where PreciseTimeStamp between (datetime({StartTime}) .. 1d) and tenantName == "{TenantName}"
| distinct applicationName
// applicationName contains "fabric:/AzLifecycle-Slice3-P0" etc.
```

---

## AzLifecycle / AZSM (accp.centralus)

Cluster: `accp.centralus.kusto.windows.net`
Database: `AZSM`

This is the **AzLifecycle / AzSM** service slice's own logs (separate cluster from `AzureCM`). Required when CRP returns `OutOfTimeBudgetException` or `FabricInternalOperationError` — the failure root cause is usually in the AzSM tenant-update state machine, which is NOT in `AzureCM.TMMgmt*` tables. First get the owning slice via `AzSMTenantSnapshotV2` above (the slice/region influences which `accp.*` cluster to read; `accp.centralus` is the common entry point).

### AzSMUpdateTenantEvents — UpdateTenant operation events

```kusto
cluster("accp.centralus").database("AZSM").AzSMUpdateTenantEvents
| where PreciseTimeStamp between (datetime({StartTime}) .. 1d)
| where tenantName == "{TenantName}"
| project PreciseTimeStamp, message
```

Use for: "did the UpdateTenant call from CRP land on AzLifecycle and what happened next."

### AzSMTenantEvents — Tenant-level events on the AzSM slice

```kusto
cluster("accp.centralus").database("AZSM").AzSMTenantEvents
| where PreciseTimeStamp between (datetime({StartTime}) .. 2d)
| where tenantName contains "{TenantName}"
| project PreciseTimeStamp, tenantName, Tenant, message
```

### AzSMTenantStatemachineEvents — Tenant state-machine traces

```kusto
cluster("accp.centralus").database("AZSM").AzSMTenantStatemachineEvents
| where PreciseTimeStamp between (datetime({StartTime}) .. 2d)
| where tenantName == "{TenantName}"
| where message contains "UpdateTenant"
| project PreciseTimeStamp, message
```

Use for: "where did the UpdateTenant state machine get stuck."

### AzSMExceptionsEvents — AzSM exceptions

```kusto
cluster("accp.centralus").database("AZSM").AzSMExceptionsEvents
| where PreciseTimeStamp between (datetime({StartTime}) .. 2d)
| where tenantName == "{TenantName}"
| project PreciseTimeStamp, message
```

Use for: actual exception stacks thrown inside the slice during the failed operation. Often the smoking gun for `OutOfTimeBudgetException`.

**Routing**: All four `accp.centralus / AZSM` tables are referenced from
[`playbook-B-cant-start-stop-deep.md`](../playbooks/playbook-B-cant-start-stop-deep.md) § OP-FabricTimeout.
TSG anchor: [OutofTimeBudgetException wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495454).

---

## Disk-Configuration Switch (Stripe ↔ ABC)

### TMMgmtNodeEventsEtwTable — NodePrepareMode (disk configuration switch)

When a host node lands in `NodePrepareMode`, it can take ~30 min to switch between `AllDisksInStripe` ↔ `AllDisksAbc`. During that window VM start operations queue up and may exceed CRP's time budget — root cause for `Start-Stop-Operations-Taking-Too-Long` with EG signature "Host node switched disk configuration".

```kusto
cluster('azcsupfollower').database('AzureCM').TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp between(datetime({StartTime}) .. 24h) and NodeId == "{NodeId}"
| where Message contains "NodePrepareMode"
| project PreciseTimeStamp, Message
```

Pair with `TMMgmtSlaMeasurementEventEtwTable` (above — filter by `ContainerID` + project `EntityState`) to confirm the create-container call was waiting on the prepare-mode transition.

TSG anchor: [Start-Stop-Operations-Taking-Too-Long wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495465).

### EntityState dictionary (TMMgmtSlaMeasurementEventEtwTable)

Common `EntityState` values you'll see in the container lifecycle column — useful for recognizing the GuestOsStateProvisioningRecovery pattern:

| EntityState | Meaning |
|---|---|
| `GuestOsStateProvisioning` | Guest OS started provisioning |
| `GuestOsStateProvisioningRecovery` | Guest OS did NOT report success — Fabric is about to reboot the container |
| `Reboot` | Fabric-initiated reboot |
| `ContainerStateStopped` | Container stopped |
| `GuestOsStateGracefulShutdown` | Graceful shutdown in progress |
| `RoleStateDestroyed` | Role destroyed |
| `ContainerStateStarted` | Container started |
| `RoleStateStarted` | Role started (steady state) |
| `GuestOsStateHardPowerOff` | Hard power-off (no graceful shutdown) |

Sequence `GuestOsStateProvisioning` → `GuestOsStateProvisioningRecovery` → `Reboot` → `ContainerStateStarted` = guest OS was slow to start and Fabric did one auto-recovery reboot. Follow [GuestOsStateProvisioningRecovery wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495487) to determine why the guest OS was slow.

---

## Live Migration

### LiveMigrationContainerDetailsEventLog — Identify LM session ID

```kusto
cluster("AzureCM").database("AzureCM").LiveMigrationContainerDetailsEventLog
| where destinationContainerId == "{ContainerId}" or sourceContainerId == "{ContainerId}"
| where PreciseTimeStamp > datetime({BeginTime}) and PreciseTimeStamp < datetime({EndTime})
| project triggerType, migrationConstraint, sessionId
```

### LiveMigrationSessionCreatedLog — LM session creation

```kusto
cluster("AzureCM").database("AzureCM").LiveMigrationSessionCreatedLog
| where sourceContainerId == "{ContainerId}"
| where sessionId == "{LMSessionId}"
| project TIMESTAMP, message, sourceContainerId, containerState
```

### LiveMigrationSessionCompleteLog — LM completion

```kusto
cluster("AzureCM").database("AzureCM").LiveMigrationSessionCompleteLog
| where destinationContainerId == "{ContainerId}" or sourceContainerId == "{ContainerId}"
| where sessionId == "{LMSessionId}"
```

### LiveMigrationSessionStatusEventLog — LM status (errors)

```kusto
cluster("AzureCM").database("AzureCM").LiveMigrationSessionStatusEventLog
| where sessionId == "{LMSessionId}"
| where ['type'] == "Error"
| project ['state'], message
```

### LiveMigrationStateMachineTracesLog — Detailed LM tracing

```kusto
cluster("AzureCM").database("AzureCM").LiveMigrationStateMachineTracesLog
| where sessionId == "{LMSessionId}"
```

### LiveMigrationSessionCriticalLog — Critical LM errors

```kusto
cluster("AzureCM").database("AzureCM").LiveMigrationSessionCriticalLog
| where sessionId == "{LMSessionId}"
| project exceptionType, exception, lmContext
```

---

## Downtime & Unexpected Reboot Events

### TMMgmtRoleInstanceDowntimeEventEtwTable — VM downtime events

Key columns: `ContainerId`, `NodeId`, `DowntimeCategory`, `DowntimeDuration`, `FaultDomain`

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtRoleInstanceDowntimeEventEtwTable
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| where ContainerID == "{ContainerId}"
| project PreciseTimeStamp, ContainerID, NodeID, DowntimeCategory, DowntimeDuration,
    FaultDomain, RoleInstanceName, TenantName, Tenant, Message
| order by PreciseTimeStamp asc
```

Interpretation:
- `DowntimeCategory` — categorizes the reason (e.g., `HardwareError`, `ServiceHealing`, `PlannedMaintenance`, `UnexpectedReboot`)
- `DowntimeDuration` — total downtime in seconds
- Correlate with `TMMgmtNodeStateChangedEtwTable` to confirm node reboot vs container-only event

### DCMLMResourceUnexpectedRebootEtwTable — Unexpected reboot correlation

Key columns: `ResourceId`, `RebootTime`, `RebootCategory`, `RepairAction`

```kusto
cluster("AzureCM").database("AzureCM").DCMLMResourceUnexpectedRebootEtwTable
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| where ResourceId == "{NodeId}"
| project PreciseTimeStamp, ResourceId, RebootTime, RebootCategory, RepairAction,
    FaultCode, FaultReason, Tenant
| order by PreciseTimeStamp asc
```

Interpretation:
- Links unexpected reboots to DCM fault codes and repair actions
- `RebootCategory` — `HardwareFault`, `SoftwareFault`, `Unknown`
- Cross-reference `FaultCode` with `FaultCodeTeamMapping` in AzureDCMDb

---

## Container Fault Events

### FaultHandlingContainerFaultEventEtwTable — Container-level faults

Key columns: `ContainerId`, `NodeId`, `FaultType`, `FaultCode`, `FaultReason`

```kusto
cluster("AzureCM").database("AzureCM").FaultHandlingContainerFaultEventEtwTable
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| where ContainerId == "{ContainerId}"
| project PreciseTimeStamp, ContainerId, NodeId, FaultType, FaultCode, FaultReason,
    Tenant, TenantName
| order by PreciseTimeStamp asc
```

Interpretation:
- `FaultType` — `NodeFault`, `ContainerFault`, `DiskFault`
- Shows the fault that triggered recovery actions (pair with `FaultHandlingRecoveryEventEtwTable`)
- If `FaultCode` references a hardware issue, continue investigation with `hardware-queries.md`

### TMMgmtNodeFaultEtwTable — Node-level faults

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtNodeFaultEtwTable
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == "{NodeId}"
| project PreciseTimeStamp, NodeId, FaultType, FaultCode, FaultReason,
    Tenant, RecoveryAction
| order by PreciseTimeStamp asc
```

Interpretation:
- Node-level faults may affect all VMs on the same node
- `RecoveryAction` shows what the fabric did (PowerCycle, RebootNode, HumanInvestigate)
- Use `LogContainerSnapshot` with the same NodeId to find all affected VMs

---

## VM Platform Operations

### KronoxVmOperationEvent — Platform-initiated VM operations

Key columns: `ContainerId`, `OperationType`, `OperationStatus`, `TriggerSource`

```kusto
cluster("AzureCM").database("AzureCM").KronoxVmOperationEvent
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| where ContainerId == "{ContainerId}"
| project PreciseTimeStamp, ContainerId, NodeId, OperationType, OperationStatus,
    TriggerSource, Duration, ErrorCode, ErrorMessage, Tenant
| order by PreciseTimeStamp asc
```

Interpretation:
- Shows platform-initiated operations on the VM (e.g., redeploy, restart, stop)
- `TriggerSource` — identifies why the operation was triggered (ServiceHealing, HostUpdate, PlannedMaintenance, etc.)
- `OperationType` values: `RestartVM`, `RedeployVM`, `StopVM`, `LiveMigrateVM`
- `OperationStatus` — `Succeeded`, `Failed`, `InProgress`

---

## Service Healing — Extended Queries

### ServiceHealingDecisionEtwTable — SH decision details

```kusto
cluster("AzureCM").database("AzureCM").ServiceHealingDecisionEtwTable
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == "{NodeId}"
| project PreciseTimeStamp, NodeId, TenantName, Decision, Reason,
    AffectedContainers, HealingAction, Tenant
| order by PreciseTimeStamp asc
```

Interpretation:
- Shows the service healing decision-making process
- `Decision` — `Heal`, `Skip`, `Defer`
- `HealingAction` — `LiveMigrate`, `Reboot`, `Redeploy`, `PowerCycle`
- `AffectedContainers` — count of containers impacted by this SH decision

### ServiceHealingMigrationEtwTable — SH migration tracking

```kusto
cluster("AzureCM").database("AzureCM").ServiceHealingMigrationEtwTable
| where PreciseTimeStamp >= datetime({BeginTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == "{NodeId}" or ContainerId == "{ContainerId}"
| project PreciseTimeStamp, ContainerId, NodeId, SourceNode, DestinationNode,
    MigrationStatus, MigrationType, Duration, ErrorMessage
| order by PreciseTimeStamp asc
```

Interpretation:
- Tracks individual container migrations during service healing
- `MigrationType` — `LiveMigration`, `Redeploy`
- `MigrationStatus` — `Succeeded`, `Failed`, `InProgress`
- `SourceNode` / `DestinationNode` — shows where the VM moved from/to

---

## Live Migration — Extended Queries

### LiveMigrationSessionCompleteLog — LM summary by trigger type (subscription-wide)

> **NOTE**: `LiveMigrationTriggerLog` and `LiveMigrationPerformanceLog` do NOT exist. All trigger and performance data lives in `LiveMigrationSessionCompleteLog`.

```kusto
cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationSessionCompleteLog
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where subscriptionId =~ "{SubscriptionId}"
| summarize
    Count = count(),
    AvgBlackoutMs = avg(blackoutTimeInMs),
    MaxBlackoutMs = max(blackoutTimeInMs),
    AvgDurationMs = avg(durationInMs)
    by triggerType, result
```

Variant — LM breakdown by region for a subscription:

```kusto
cluster("moseisley.kusto.windows.net").database("AzureCM").LiveMigrationSessionCompleteLog
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where subscriptionId =~ "{SubscriptionId}"
| summarize Count = count() by triggerType, Region = Tenant
| order by Count desc
```

Interpretation:
- `triggerType` — `Defrag`, `PlannedMaintenance`, `OnDemand`, `ServiceHealing`
- `blackoutTimeInMs` — actual VM downtime during LM (typically < 1000ms for memory-preserving)
- `durationInMs` — end-to-end LM duration
- `result` — `Success` / `Failed` / `Cancelled`
- Use `sessionId` to correlate with `LiveMigrationSessionStatusEventLog` for error details

---

## Container State — Extended Queries

### LogContainerSnapshot — Flexible identity resolution (any identifier)

Resolve VM identity from any known identifier — `virtualMachineUniqueId`, `containerId`, or `roleInstanceName`. Uses `case()` to dynamically select the filter field.

```kusto
let queryFrom = datetime('{Start}');
let queryTo   = datetime('{End}');
cluster('Azurecm.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where case(
    isnotempty('{virtualMachineUniqueId}'), virtualMachineUniqueId =~ '{virtualMachineUniqueId}',
    isnotempty('{containerId}'),            containerId =~ '{containerId}',
    isnotempty('{roleInstanceName}'),       roleInstanceName =~ '{roleInstanceName}',
    false)
| summarize arg_max(PreciseTimeStamp, *) by tenantName, virtualMachineUniqueId, containerId, roleInstanceName
| project-reorder creationTime, PreciseTimeStamp, roleInstanceName, subscriptionId, containerType,
    virtualMachineUniqueId, containerId, nodeId, Tenant, tenantName,
    availabilitySetName, billingType, roleType, RegionFriendlyName
```

Interpretation:
- Use when you have any one VM identifier and need the others
- The `case()` approach avoids needing separate queries for each identifier type
- Returns the latest snapshot per unique (tenantName, vmUniqueId, containerId, roleInstanceName) combination

---

## VM Identity Change History

### LogContainerSnapshot — Detect Redeploy/Live Migration via identity changes

Detect whether a VM was Redeployed or Live Migrated over a time window by tracking `containerId` and `nodeId` changes. Each unique (containerId, nodeId) pair = one placement. Use to confirm number of Redeployments, map before/after identity, and determine exact transition time.

```kusto
let queryFrom = datetime('{Start}');
let queryTo   = datetime('{End}');
cluster('azcsupfollower.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where subscriptionId =~ '{SubscriptionId}'
| where roleInstanceName =~ '{VMName}'
| summarize
    FirstSeen = min(PreciseTimeStamp),
    LastSeen  = max(PreciseTimeStamp)
    by containerId, nodeId, roleInstanceName, subscriptionId
| order by FirstSeen asc
| extend IdentityChange = row_number() - 1
| project FirstSeen, LastSeen, containerId, nodeId, roleInstanceName, IdentityChange
```

Interpretation:
- Each row is one "life" of the VM on a given node
- `IdentityChange = 0` = original placement; each increment = one Redeploy or Migration
- **`ToBeDestroyedOnNode` timestamp = Redeploy initiation**, not the customer-visible recovery time
- Multiple rows indicate the VM moved between nodes during the time window

## Subscription Metadata

### HolmesSubscriptionMetadataEvents — Check if Live Migration is disabled for a subscription

Determine whether a subscription has opted out of Live Migration by checking the `nonLiveMigratable` flag. `True` = LM is disabled (VMs will be redeployed instead of live-migrated during maintenance). `False` = LM is enabled (default behavior).

```kusto
let queryFrom = datetime('{Start}');
let queryTo   = datetime('{End}');
let query_sub = '{SubscriptionId}';
cluster('azurecm.kusto.windows.net').database('AzureCM').HolmesSubscriptionMetadataEvents
| where PreciseTimeStamp between (queryFrom..queryTo)
    and subscriptionGUID == query_sub
| summarize arg_max(PreciseTimeStamp, *) by containerId
| summarize dcount(containerId) by subscriptionGUID, nonLiveMigratable
| project subscriptionGUID, nonLiveMigratable
```

Interpretation:
- `nonLiveMigratable = False` → Live Migration is **enabled** (default)
- `nonLiveMigratable = True` → Live Migration is **disabled** for this subscription
- The query takes the latest metadata snapshot per container, then aggregates by subscription to show the LM policy status

---

## Capacity / Allocatable VM Count

> **TL;DR — which table is authoritative?** To answer *"can my customer actually deploy this SKU in this region/AZ right now?"*, trust the **Allocator** table `cluster('azureallocator.westcentralus').database('AzureAllocator').AllocatorMonitoringLogAllocableVMCount`. The AzureCM table `LogAllocatableVmCountMetric` is a **node-side cache** and is conservative / can be stale — it has been observed reporting **"no capacity" while the customer could still create VMs**. Use AzureCM for node-level/fleet trending, **not** for a deployability verdict.

### Two tables, fundamentally different telemetry

| | `azurecm` (or `Azcsupfollower`) **LogAllocatableVmCountMetric** | `azureallocator.westcentralus` **AllocatorMonitoringLogAllocableVMCount** |
|---|---|---|
| Emitter / source | Fabric node-side cached view (`VmCountSource = AllocableVmCache`) | Central **Allocator service** snapshot (`snapShotId`, `allocableVmLogs`) — the engine that actually makes placement decisions |
| Granularity | **Per-Node** (`SourceNodeId`) — must `sum` to roll node → cluster → region | **Per-Partition** (`partitionType` = `Cluster` / `AvailabilityZone` / `AvailabilityZoneAndRegionalClusters`) — already aggregated |
| "Limit" dimension | `limitType` (~12: ServiceHealing / NewDeployment / Enforced / Upgrade … ±MinusReserved / ±MinusReservedAndDecom) | `deploymentType` (same family, plus `…WithOverflow`, `SpotVNextNewDeployment`) |
| Priority / Spot | implicit (only via `vmType`) | explicit `priority` = `Normal` / `GeneralPurposeLow` (Spot) |
| Spanned tenants | n/a | `canHostSpannedTenants` true/false (**doubles rows** for same capacity) |
| Packing model | `occupiesWholeNode` / `takesExactlyOneCore` / `sellableAvailableCores` / `henToReserve` | none — engine's own count |

**Why AzureCM under-reports** (says 0 when capacity exists): node-side cache cannot see overflow capacity (`…WithOverflow`), cross-node repacking/defrag, or AZ-level availability when every individual node looks full; its `limitType` is also more conservative.

### Why a raw count comparison shows a huge gap (dimension fan-out)

Neither `vmCount` is meaningful until you **pin every dimension** — otherwise you sum across overlapping partitions/limit types:
- **AzureCM**: ~12 `limitType` values → ~12× inflation if not pinned. Always pin `VmCountSource` + a single `limitType`.
- **Allocator**: `partitionType`(3) × `priority`(2) × `deploymentType`(~12) × `canHostSpannedTenants`(2) → easily 100×+ if not pinned.

### Allocator team recommended query — AZSM-wise capacity (authoritative for deployability)

The Allocator team's endorsed pattern for "can this customer deploy" capacity analysis. Pin `partitionType == "AvailabilityZone"` and pick `deploymentType` by scenario:

```kusto
cluster('azureallocator.westcentralus').database('AzureAllocator').AllocatorMonitoringLogAllocableVMCount
| where PreciseTimeStamp >= ago(1d)
| where Cluster contains "{ClusterPrefix}"          // e.g. "europewest-prod-"
| where vmType contains "{VMSize}"                  // e.g. "Standard_D16s_v5"
| where deploymentType == "EnforcedMinusReservedAndDecom"   // pick per scenario — see table below
| where partitionType == "AvailabilityZone"
| summarize sum(vmCount) by partitionName, vmType, bin(PreciseTimeStamp, 5m)   // roll up multiple clusters per AZ
| render timechart
```

**`deploymentType` selection by scenario** (most common mistake — wrong口径 → misleading number):

| Scenario | `deploymentType` |
|---|---|
| New deployment | `NewDeploymentMinusReserved` or `EnforcedMinusReserved` |
| Resize / Upgrade (e.g. `Standard_D32ds_v5`) | `UpgradeMinusReserved` |
| Generic "real deployable" (reserved + decom nodes subtracted) | `EnforcedMinusReservedAndDecom` |

> ⚠️ With `partitionType == "AvailabilityZone"`, the same AZ surfaces multiple `Cluster` rows — always `summarize sum(vmCount) by partitionName, vmType, bin(...)`, don't `render timechart` on raw rows.

### AzureCM side — apples-to-apples (node-level trending only)

To compare against the Allocator number, roll node → region and pin a single limit口径:

```kusto
cluster('Azcsupfollower.kusto.windows.net').database('AzureCM').LogAllocatableVmCountMetric
| where PreciseTimeStamp > ago(1h)
| where Region =~ "{Region}" and vmType =~ "{VMSize}"
| where VmCountSource == "AllocableVmCache"
| where limitType == "NewDeployment"               // align with Allocator deploymentType
| summarize sum(vmCount) by bin(PreciseTimeStamp, 5m), Region, vmType
```

> `Azcsupfollower` is a read-only **follower** of `azurecm` — identical data (verified: <0.01% delta from replication lag). Prefer it for CSS read-heavy queries. It is **not** a third capacity source.
