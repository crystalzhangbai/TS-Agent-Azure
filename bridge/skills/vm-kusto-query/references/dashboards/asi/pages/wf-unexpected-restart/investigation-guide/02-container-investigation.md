# Container Investigation

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Container Investigation** (13 queries across 13 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## CAD

### CAD_UnexpectedRestart DS

_Widget purpose:_ CAD events

Cluster: `vmainsight.kusto.windows.net` · Database: `CAD` · Type: `Table`
Source panel: `Container Investigation > CAD > CAD events`

```kusto
CAD
| where PreciseTimeStamp > query_BeginTime and PreciseTimeStamp < query_EndTime
| where ContainerId == query_ContainerId
| project StartTime, EndTime, RoleInstanceName, AvailabilityState, VmVhds, Storage_AccountName, Storage_VhdCount, TotalDowntimeInMin, TotalUptimeInMin, DurationInMin
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## Container Health

### LogContainerHealthSnapshot_UnexpectedRestart DS

_Widget purpose:_ Container health state investigation

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Table`
Source panel: `Container Investigation > Container Health > Container health state investigation`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime 
| where ContainerId =~ query_ContainerId
| project PreciseTimeStamp, ContainerState, OsState , ActualOperationalState, LifecycleState, ActualVMHealthState, ContainerId, NodeId, FaultInfo, TenantName, RoleInstanceName
```

**Params:** `{query_ContainerId}`, `{query_BeginTime}`, `{query_EndTime}`

---

## Container History

### LogContainerSnapshot_UnexpectedRestart DS

_Widget purpose:_ VM placement thru time on host node(s)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Table`
Source panel: `Container Investigation > Container History > VM placement thru time on host node(s)`

```kusto
MycroftContainerSnapshot
| where SubscriptionId =~ query_SubscriptionId and RoleInstanceName has query_VMName
| extend ext_prop = parse_json(AdditionalContainerProperties)
| extend diskController = tostring(ext_prop.DiskControllerType)
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp) by RoleInstanceName, CreationTime, VirtualMachineUniqueId, ClusterName, ContainerId, NodeId, TenantName, ContainerType, UpdateDomain,  SubscriptionId, diskController
| project ContainerCreationTime=todatetime(CreationTime), StartTimeStamp=min_PreciseTimeStamp, EndTimeStamp=max_PreciseTimeStamp, VMName=RoleInstanceName, VirtualMachineUniqueId, Cluster=ClusterName, NodeId, ContainerId, TenantName, ContainerType, UpdateDomain,  SubscriptionId, diskController
| order by ContainerCreationTime asc
| join kind=leftouter (cluster('azurevmcentral.westus2.kusto.windows.net').database('azurevmcentral').latest_vm_definitions) on $left.ContainerType == $right.fabricname
```

**Params:** `{query_SubscriptionId}`, `{query_VMName}`

---

## ContainerTrace

### TMMgmtContainerTraceEtwTable DS

_Widget purpose:_ Container trace events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Container Investigation > ContainerTrace > Container trace events`

```kusto
TMMgmtContainerTraceEtwTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where ContainerID == query_ContainerId
| project PreciseTimeStamp ,  Message
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## Guest Agent Logs

### GuestAgentLogs DS

_Widget purpose:_ Guest Agent logs

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Container Investigation > Guest Agent Logs > Guest Agent logs`

```kusto
GuestAgentGenericLogs
| where PreciseTimeStamp  > query_BeginTime 
| where PreciseTimeStamp < query_EndTime
| where ContainerId == query_ContainerId
| project Context2, Cluster, GAVersion, Context1
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## Guest OS Details

### GuestOSDetails DS

_Widget purpose:_ Guest OS Details

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Container Investigation > Guest OS Details > Guest OS Details`

```kusto
GuestOSDetailEtwTable
| where PreciseTimeStamp  > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| where ContainerId == query_ContainerId
| distinct  ContainerId, VMType, OSType, OSName
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## SLA Table

### TMMgmtSlaMeasurementEventEtwTable_UnexpectedRestart2 DS

_Widget purpose:_ SLA Table for Container

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Container Investigation > SLA Table > SLA Table for Container`

```kusto
TMMgmtSlaMeasurementEventEtwTable
| where ContainerID == query_ContainerId 
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime 
| project PreciseTimeStamp, TenantName, RoleInstanceName, Context, EntityState, ContainerID, NodeID, Detail0, Region
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## TenantChangeProfiling

### TMMgmtTenantChangeProfilingEventEtwTable

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Container Investigation > TenantChangeProfiling > TMMgmtTenantChangeProfilingEventEtwTable`

```kusto
TMMgmtTenantChangeProfilingEventEtwTable
| where PreciseTimeStamp between(queryFrom..queryTo)
| where ContainerId =~ queryContainerId 
| project PreciseTimeStamp, Tenant, TenantName, ContainerId, RoleInstanceName, UserField,ChangeEventType, FromState,ToState
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---

## TenantEvents

### TMMgmtTenantEventsEtwTable DS

_Widget purpose:_ Tenant events investigation

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Container Investigation > TenantEvents > Tenant events investigation`

```kusto
TMMgmtTenantEventsEtwTable
| where TenantName == query_TenantName
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| project PreciseTimeStamp, Tenant,  Message
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_TenantName}`

---

## VM Restart Events

### GetVMRestartEvents DS

_Widget purpose:_ VM Restart Events

Cluster: `moseisley.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `Container Investigation > VM Restart Events > VM Restart Events`

```kusto
GetVMRestartEvents(query_vmId, query_BeginTime, query_EndTime)
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_vmId}`

---

## VMA

### VMA5 DS

_Widget purpose:_ VM Availability analysis

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `Container Investigation > VMA > VM Availability analysis`

```kusto
cluster("https://vmainsight.kusto.windows.net").database("vmadb").VMA()
| where PreciseTimeStamp between (_startDateTime .. _endDateTime) 
| where (isnotempty(_vmid) and VmUniqueId == _vmid) or (isempty(_vmid) and ContainerId == _containerId) and RCALevel1 != "Unknown" 
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2
| join kind=leftouter ( cluster("https://vmainsight.kusto.windows.net").database("Air").VmRestartRcaLevel1Level2ArticleMapping ) on $left.RCALevel1 == $right.RCALevel1 and $left.RCALevel2 == $right.RCALevel2
| join kind=leftouter ( cluster("https://vmainsight.kusto.windows.net").database("Air").VmRestartArticleCssWikiLinkMapping ) on $left.ArticleId == $right.ArticleId
| project Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2, ArticleId, CssWikiLink
```

**Params:** `{_startDateTime}`, `{_endDateTime}`, `{_vmid}`, `{_containerId}`

---

## VMHealthState

### VmHealthRawStateEtwTable_UnexpectedRestart DS

_Widget purpose:_ VM health state investigation

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Container Investigation > VMHealthState > VM health state investigation`

```kusto
VmHealthRawStateEtwTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where ContainerId == query_ContainerId
| project PreciseTimeStamp, Cluster, NodeId, ContainerId, VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted, Context
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## VmServiceContainerOperations

### VmServiceContainerOperations

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Container Investigation > VmServiceContainerOperations`

```kusto
VmServiceContainerOperations
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where ContainerId == queryContainerId
|project PreciseTimeStamp, ContainerId, Operation, Stage, ResultCode , ActivityId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---
