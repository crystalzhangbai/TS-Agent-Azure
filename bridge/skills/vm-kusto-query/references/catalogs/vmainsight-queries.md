# VMInsight Queries — VMA RCA, Host Updates, CPU, Windows Events, Air Events

Cluster: `vmainsight.kusto.windows.net`
Databases: `vmadb`, `Air`, `Vmadiag`

---

## Host Node Updates

### RootHENodeGoalVersionChange — Updates running on node

```kusto
cluster("vmainsight").database("vmadb").RootHENodeGoalVersionChange
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp < datetime({EndTime})
| where NodeId == "{NodeId}"
```

### Combined update query (ServiceManager + RootHE + Gandalf + NMAgent)

```kusto
let ServiceManger = (cluster("AzureCM").database("AzureCM").ServiceManagerInstrumentation);
let RootHE = (cluster("Vmainsight").database("vmadb").RootHENodeGoalVersionChange
| extend RootHE_OldValue=OldValue, RootHE_NewValue=NewValue);
let RootHEGaldaf = (cluster('Azcsupfollower').database('AzureCM').RootHEGandalfInformationalEventEtwTable
| extend RootHEGandalf_OldValue=OldVersion, RootHE_NewValueGandalf=NewVersion);
let NMAgent = (cluster('vmainsight.kusto.windows.net').database('Air').AirMaintenanceEvents
| extend PreciseTimeStamp = EventTime
| extend Diagnostics=tostring(Diagnostics));
union ServiceManger, RootHE, RootHEGaldaf, NMAgent
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp < datetime({EndTime})
| where NodeId == "{NodeId}"
| summarize NodeUpdatedAtApprox=min(PreciseTimeStamp) by ServiceVersion, ServiceName, RootHE_OldValue, RootHE_NewValue, RootHEGandalf_OldValue, RootHE_NewValueGandalf, EventCategoryLevel2, EventCategoryLevel3, Component, OutageType, Diagnostics, NodeId
| project-reorder NodeUpdatedAtApprox, NodeId
| order by NodeUpdatedAtApprox asc
```

### ServiceManagerInstrumentation — NMAgent updates

```kusto
cluster("AzureCM").database("AzureCM").ServiceManagerInstrumentation
| where NodeId == "{NodeId}" and ServiceName == "NmAgent" and PreciseTimeStamp > datetime({StartTime})
| summarize min(PreciseTimeStamp) by ServiceVersion, ServiceName
```

---

## Air Events

### AirHostNetworkingUpdateEvents — NMAgent updates & details

```kusto
cluster('vmainsight.kusto.windows.net').database('Air').AirHostNetworkingUpdateEvents
| where EventTime > datetime({StartTime}) and EventTime < datetime({EndTime})
| where NodeId =~ "{NodeId}"
| distinct EventTime, EventCategoryLevel3, EventSource, RCALevel1, OutageType, NodeId
```

### AirManagedEventsBrownouts — HostNetworking update pauses & duration

```kusto
let startTime = datetime({StartTime});
let endTime = datetime({EndTime});
let nodeId = "{NodeId}";
cluster('vmainsight.kusto.windows.net').database('Air').AirManagedEventsBrownouts
| where EventTime between (startTime .. endTime) and NodeId == nodeId
| project EventTime, NodeId, EventType, EventSource, ObjectType, ObjectId, Duration, EventCategoryLevel1, EventCategoryLevel2, EventCategoryLevel3, RCALevel1, RCALevel2, RCALevel3
```

### AirManagedEvents — Host node update investigation

```kusto
let startTime = datetime({StartTime});
let endTime = datetime({EndTime});
let nodeId = "{NodeId}";
cluster('vmainsight.kusto.windows.net').database('Air').AirManagedEvents
| where EventTime between (startTime .. endTime) and NodeId == nodeId
| project EventTime, EventType, EventSource, ObjectType, ObjectId, Duration, EventCategoryLevel1, EventCategoryLevel2, EventCategoryLevel3, RCALevel1
```

### AirDiskIOBlipEvents — Disk IO blip events

```kusto
let startTime = datetime({StartTime});
let endTime = datetime({EndTime});
let nodeId = "{NodeId}";
cluster('vmainsight.kusto.windows.net').database('Air').AirDiskIOBlipEvents
| where EventTime between (startTime .. endTime) and NodeId == nodeId
```

### GetVMPhuEventsBySubId — VMPHU events at subscription level

```kusto
cluster('vmainsight.kusto.windows.net').database('Air').GetVMPhuEventsBySubId('{SubscriptionId}', datetime({StartTime}), datetime({EndTime}))
```

### GetArticleIdByFailureSignature — RCA article lookup

```kusto
cluster('vmainsight').database('Air').GetArticleIdByFailureSignature("HardwareFault.DCM FaultCode 60017")
```

### GetCssWikiLinkByArticleId — Wiki/GitHub link for RCA article

```kusto
cluster('vmainsight').database('Air').GetCssWikiLinkByArticleId("VMA_RCA_Hardware_NodeReboot_Memory_Failure")
```

---

## AirLiveMigrationEvents — Live Migration sessions

> **Table**: `cluster('vmainsight.kusto.windows.net').database('Air').AirLiveMigrationEvents`
> **Retention**: ~2 years. **Granularity**: one row = one LM session completion.
> **Key columns**: `EventTime`, `SubscriptionId`, `VirtualMachineUniqueId`, `SessionId`, `RegionFriendlyName`, `RCALevel1`, `Cluster`, `NodeId`, `DestinationNodeId`, `ComputeBlackoutInSec`
> Preferred over AzureCM `LiveMigrationContainerDetailsEventLog` (~90d retention) for long-range LM analysis.

```kusto
let subId = "{SubscriptionId}";
cluster('vmainsight.kusto.windows.net').database('Air').AirLiveMigrationEvents
| where EventTime between (datetime({StartTime}) .. datetime({EndTime}))
| where SubscriptionId == subId
| project EventTime, SessionId, VirtualMachineUniqueId, RegionFriendlyName, RCALevel1, ComputeBlackoutInSec, NodeId, DestinationNodeId
| order by EventTime asc
```

---

## Host CPU & Windows Events

### HighCpuCounterNodeTable — High CPU on node

```kusto
cluster("vmainsight").database("vmadb").HighCpuCounterNodeTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
```

### WindowsEventTable (vmadb) — Windows events on host node

```kusto
cluster("vmainsight").database("vmadb").WindowsEventTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where EventId != "0" and EventId != "505" and EventId != "504" and EventId != "3095"
| project TimeCreated, Cluster, EventId, ProviderName, Description
| order by TimeCreated asc nulls last
```

EventId filter tips:
- `18500, 18502, 18504, 18508, 18510, 18512, 18514, 18516, 18596, 18590, 19060, 18190, 18560` — HyperV container events
- `2004, 3050, 3122, 12030` — low memory condition
- `ProviderName contains "UpdateNotification"` — VM-PHU update details

---

## VMA RCA Tables

### VMA — Fault info, RCA category, support article link

```kusto
let myTable = cluster("Vmainsight").database("vmadb").VMA
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == "{NodeId}" and RoleInstanceName has "{VMName}"
| distinct PreciseTimeStamp, NodeId, RoleInstanceName, RCAEngineCategory, RCALevel1, RCALevel2, RCA_CSS, Cluster, ContainerId;
myTable
| extend StartTime = now(), EndTime = now(), RCAEngineCategory = ""
| invoke cluster("Vmainsight").database('Air').AddVmRestartSupportArticle()
| project-away StartTime, EndTime, RCAEngineCategory, InternalArticleId
```

### VMA — Filter by subscription, excluding customer-initiated & network

```kusto
cluster("vmainsight").database("vmadb").VMA
| where PreciseTimeStamp >= ago(65d)
| where Subscription == "{SubscriptionId}"
| where Usage_ResourceGroupName == "{ResourceGroupName}"
| where RCALevel1 != "NetworkAvailability"
| summarize count() by bin(StartTime, 15min), RoleInstanceName, RCA, EG_Url
| where count_ > 0
```

### VMALENS — 30-day VM availability impact

```kusto
cluster("vmainsight").database("vmadb").VMALENS()
| where StartTime >= ago(30d)
| where Subscription == "{SubscriptionId}"
| project StartTime, RoleInstanceName, PreciseTimeStamp, LastKnownSubscriptionId, Cluster, NodeId, RCA, RCALevel1, RCALevel2, RCALevel3, SEL_RCA, EscalateToBucket, RCAEngineCategory, LastEvents, EG_Followup, EG_Url
| order by StartTime asc nulls last
```

---

## Resource Health & Platform Events

### AirUnmanagedEvents — Unmanaged/unexpected availability events

```kusto
let startTime = datetime({StartTime});
let endTime = datetime({EndTime});
let nodeId = "{NodeId}";
cluster('vmainsight.kusto.windows.net').database('Air').AirUnmanagedEvents
| where EventTime between (startTime .. endTime) and NodeId == nodeId
| project EventTime, NodeId, EventType, EventSource, ObjectType, ObjectId,
    Duration, EventCategoryLevel1, EventCategoryLevel2, EventCategoryLevel3,
    RCALevel1, RCALevel2, RCALevel3, OutageType
| order by EventTime asc
```

Interpretation:
- Unmanaged events are unexpected (not planned maintenance)
- `EventCategoryLevel1` — high-level category (Hardware, Software, Network, Unknown)
- `RCALevel1/2/3` — root cause classification
- `OutageType` — `Reboot`, `Freeze`, `Crash`, `NetworkBlip`
- Cross-reference with `VMA` table for support article links

### AirMaintenanceEvents — Platform maintenance on node

```kusto
let startTime = datetime({StartTime});
let endTime = datetime({EndTime});
let nodeId = "{NodeId}";
cluster('vmainsight.kusto.windows.net').database('Air').AirMaintenanceEvents
| where EventTime between (startTime .. endTime) and NodeId == nodeId
| project EventTime, NodeId, EventType, EventSource, Component, OutageType,
    Diagnostics, EventCategoryLevel1, EventCategoryLevel2, EventCategoryLevel3
| order by EventTime asc
```

Interpretation:
- Shows all maintenance events on the node (host updates, security patches, etc.)
- `Component` — which component was updated
- `Diagnostics` — detailed maintenance info (JSON, parse with `parse_json()`)
- Correlate with `RootHENodeGoalVersionChange` to see version changes

### VMADowntimeV2 — Detailed downtime analysis with RCA

```kusto
cluster("vmainsight").database("vmadb").VMADowntimeV2
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == "{NodeId}" and RoleInstanceName has "{VMName}"
| project PreciseTimeStamp, RoleInstanceName, NodeId, ContainerId,
    DowntimeStartTime, DowntimeEndTime, DowntimeDurationSeconds,
    RCALevel1, RCALevel2, RCALevel3, RCAEngineCategory,
    IsPlannedMaintenance, ImpactType, Cluster
| order by DowntimeStartTime asc
```

Interpretation:
- Consolidates all downtime events with root cause
- `DowntimeDurationSeconds` — precise downtime measurement
- `IsPlannedMaintenance` — distinguishes planned vs unplanned
- `ImpactType` — `Reboot`, `Freeze`, `Redeploy`, `LiveMigration`

---

## VM-PHU (Planned Host Update) Deep Dive

### GetVMPhuEventsByNodeId — VM-PHU events on a node

```kusto
cluster('vmainsight.kusto.windows.net').database('Air').GetVMPhuEventsByNodeId('{NodeId}', datetime({StartTime}), datetime({EndTime}))
```

Interpretation:
- Shows all VM-PHU events on a specific node (complements `GetVMPhuEventsBySubId`)
- Useful when you have the NodeId and want to see all update activity on that host

### RootHENodeUpdateStatus — Node update rollout status

```kusto
cluster("vmainsight").database("vmadb").RootHENodeUpdateStatus
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == "{NodeId}"
| project PreciseTimeStamp, NodeId, UpdateState, GoalVersion, CurrentVersion,
    UpdateStartTime, UpdateEndTime, FailureReason
| order by PreciseTimeStamp asc
```

Interpretation:
- Tracks the state of host updates on a node
- `UpdateState` — `Pending`, `InProgress`, `Completed`, `Failed`, `Cancelled`
- `GoalVersion` vs `CurrentVersion` — shows which update is being applied
- If `FailureReason` is present, the update failed and may have caused a node impact

---

## VMA RCA via moseisley Follower

### VMA() — RCA classification with CustomerInitiated exclusion + duration calc

Get the RCA engine's root cause classification for a VM impact event. Provides `RCAEngineCategory`, `RCALevel1/2/3`, impact duration, and availability state. Excludes customer-initiated events.

Cluster: `moseisley.kusto.windows.net` → Database: `vmadb`

```kusto
let queryFrom = datetime('{Start}');
let queryTo   = datetime('{End}');
cluster('moseisley.kusto.windows.net').database('vmadb').VMA()
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ContainerId == '{ContainerId}'
| where RCAEngineCategory != 'CustomerInitiated'
| extend DurationSec = datetime_diff("Second", EndTime, StartTime)
| extend DurationInMin = DurationSec / 60.0
| extend StartTime = format_datetime(StartTime, 'yyyy-MM-dd HH:mm:ss.fffffff'),
         EndTime   = format_datetime(EndTime,   'yyyy-MM-dd HH:mm:ss.fffffff')
| summarize arg_max(PreciseTimeStamp, *) by Cluster, StartTime, EndTime, AvailabilityState,
    TenantName, RoleInstanceName, VmUniqueId, ContainerId, NodeId, ResourceId,
    RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3
| project-reorder PreciseTimeStamp, Cluster, StartTime, EndTime, DurationInMin, AvailabilityState,
    TenantName, RoleInstanceName, VmUniqueId, ContainerId, NodeId, ResourceId,
    RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3, DurationSec
| order by PreciseTimeStamp asc
| take 1
```

Interpretation:
- `moseisley` is a follower cluster of `vmainsight` — same data, lower load
- `RCAEngineCategory` — the high-level RCA classification (e.g., `HardwareFault`, `SoftwareFault`, `PlannedMaintenance`)
- Excludes `CustomerInitiated` events (e.g., customer reboots, deallocations)
- `DurationInMin` — calculated impact duration in minutes
- Use after `LogContainerSnapshot` to get the `ContainerId`

### GetVMRestartEvents() — Structured VM restart events with failure signature

Get structured VM restart event timeline with `FailureSignature` and CSS wiki link for investigation guidance. Use after VMA RCA to get actionable failure details.

Cluster: `moseisley.kusto.windows.net` → Database: `Air`

```kusto
let queryFrom = datetime('{Start}');
let queryTo   = datetime('{End}');
cluster("moseisley.kusto.windows.net").database("Air").GetVMRestartEvents('{VirtualMachineUniqueId}', queryFrom, queryTo)
| extend DurationSec   = datetime_diff("Second", ImpactEndTimeStamp, ImpactBeginTimeStamp)
| extend DurationInMin = DurationSec / 60.0
| project-reorder Timestamp, ImpactBeginTimeStamp, ImpactEndTimeStamp, ImpactDurationTimeSpan,
    DurationInMin, RoleInstanceName, SubscriptionId, VMUniqueId, ContainerId,
    ObjectIds, Cluster, TenantName, FailureSignature, AdditionalInfo, CssWikiLink
```

Interpretation:
- `FailureSignature` — the specific failure type (e.g., `HardwareFault.DCM FaultCode 60017`)
- `CssWikiLink` — direct link to the CSS wiki article for the failure type
- Use `GetArticleIdByFailureSignature()` and `GetCssWikiLinkByArticleId()` for additional article lookup
- Requires `VirtualMachineUniqueId` (from `LogContainerSnapshot`)

---

## Vmadiag — Heartbeat & Data-Plane Diagnosis

### Atlas_VmStateTransitionEvent — VM-Host heartbeat state transitions

Trace VM-to-Host heartbeat state over time. Use to determine if the platform considered the VM healthy during a customer-reported outage. Confirms control-plane vs data-plane split when VM is Healthy but SSH/Ping fails. Also use to time-stamp exactly when Redeploy was initiated (`DoNotCare` transition = Redeploy start).

Cluster: `vmainsight.kusto.windows.net` → Database: `Vmadiag`

```kusto
let queryFrom = datetime('{Start}');
let queryTo   = datetime('{End}');
cluster('vmainsight.kusto.windows.net').database('Vmadiag').Atlas_VmStateTransitionEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ContainerId =~ '{ContainerId}'
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, ContainerId, NodeId, HealthState, Reason, osIncarnationId
```

Key interpretation:
- `Healthy` → platform sees heartbeat — control-plane OK
- `Unhealthy` → heartbeat lost briefly (often recovers in <2 min for transient faults)
- `DoNotCare` → Redeploy/Migration initiated; VM identity will change after this
- `NoSignal` → VM on new node, heartbeat not yet established
- `osIncarnationId = 00000000-...` throughout → OS never rebooted (cold reboot excluded)
- **If VM shows Healthy but SSH/Ping fails** → suspect VFP/SDN data-plane failure, check `vfp_restore_fails` and `EventData_SDN_DataPath`

### vfp_restore_fails — VFP agent process crash/restore failures

Check whether the VFP agent process crashed and failed to restore rules on a host node. If this table returns **no rows** during a network outage, the VFP process is alive — the failure is a **silent rule programming failure** (NMAgent partial programming), not a VFP process crash.

Cluster: `vmainsight.kusto.windows.net` → Database: `Vmadiag`

```kusto
let queryFrom = datetime('{Start}');
let queryTo   = datetime('{End}');
cluster('vmainsight.kusto.windows.net').database('Vmadiag').vfp_restore_fails
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId =~ '{NodeId}'
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, NodeId, ContainerId, FailReason
```

Interpretation:
- **If rows present**: VFP agent crashed → check `FailReason` for root cause
- **If no rows**: VFP process did not crash → suspect silent NMAgent VFP programming failure; escalate to network team with `Atlas_VmStateTransitionEvent` evidence
- Combine with `Atlas_VmStateTransitionEvent` to confirm control-plane vs data-plane split

### EventData_SDN_DataPath — SDN Controller data-path programming events

SDN Controller data-path programming events. Use when VFP silent failure is suspected and you need control-plane-issued rule programming evidence.

Cluster: `vmainsight.kusto.windows.net` → Database: `Vmadiag`

Key columns: `PreciseTimeStamp`, `NodeId`, `ContainerId`, `EventType`, `Message`
