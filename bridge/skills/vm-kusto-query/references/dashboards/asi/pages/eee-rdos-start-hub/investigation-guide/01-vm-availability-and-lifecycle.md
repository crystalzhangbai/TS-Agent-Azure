# VM Availability & Lifecycle

> Source: EEE RDOS Start Hub dashboard (9 queries).

Use when investigating: **VM down / unexpected restart / unavailability / redeploy / customer-reported VM outage**. These queries answer *"why did the VM stop working"*, who initiated it, and what the platform did about it. Always start here for VM-level incidents.

---

### Hyper-V Heartbeat State

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").VmHealthRawStateEtwTable
| where PreciseTimeStamp between (queryStart .. queryEnd)
| where VirtualMachineUniqueId == queryVmUniqueId or ContainerId == queryContainerId
| where VmContext <> 'NotImplemented'
| project  StartTime = PreciseTimeStamp, IsVscStateOperational, Content = VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted, Context, ContainerId
| order by StartTime asc
| extend flag = case (
    ContainerId <> next(ContainerId), 'ended', 
    Content != prev(Content) 
    or VmPowerState != prev(VmPowerState)
    or Context != prev(Context) 
    or HasHyperVHandshakeCompleted != prev(HasHyperVHandshakeCompleted)
    or Content != prev(Content), "changed", '')
| where flag <> ""
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), queryEnd)
| extend flag1 = case((next(Content) != Content and prev(Content) == Content) or flag == 'ended', 1 ,0)
| extend Health = case (Content in ("HeartBeatStateNoContact", "HeartBeatStateNonRecoverableError", "HeartBeatStateLostCommunication"), "Unhealthy", 
    (Content == "HeartBeatStateOk" and VmPowerState == "PowerStateEnabled" and HasHyperVHandshakeCompleted == "true"), "Healthy", 
    Content in ("NotMonitored", "HeartBeatStateDegraded"), "Degraded", 
    "Neutral")
| where flag1 <> 1
| project StartTime, EndTime, Content, Health, VmPowerState, HasHyperVHandshakeCompleted, Context, ContainerId
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryVmUniqueId}`, `{queryContainerId}`

**Signal filters seen in KQL:** `VmContext <> "NotImplemented"`

---

### Hyper-V Power State

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").VmHealthRawStateEtwTable
| where PreciseTimeStamp between (queryStart .. queryEnd)
| where ContainerId == queryContainerId or (isnotempty(VirtualMachineUniqueId) and VirtualMachineUniqueId == queryVmUniqueId)
| project  StartTime = PreciseTimeStamp, Content = VmPowerState, HasHyperVHandshakeCompleted, Context, ContainerId
| order by StartTime asc
| extend flag = case (ContainerId <> next(ContainerId), 'ended', 
    Content != prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), datetime(null))
| where flag <> "ended"
| extend Health = case (Content in ("EnabledStateStopping", "EnabledStatePaused", "EnabledStateDisabled","EnabledStateStarting"), "Unexpected VM restart", 
    (Content == "PowerStateEnabled"), "Healthy", 
    Content in ("NotMonitored", "PowerStateUnknown"), "Degraded", 
    "Neutral")
| project StartTime, EndTime, Health,  Content, HasHyperVHandshakeCompleted, Context
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryVmUniqueId}`, `{queryContainerId}`

**Signal filters seen in KQL:** `flag <> "ended"`

---

### VMAvailabilityMetric

_Purpose:_ Container / Tenant Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
let queryShoeboxAccount = toscalar(cluster('azurecm.kusto.windows.net').database('AzureCM').LogClusterSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Tenant == queryCluster
| project shoeboxMdmAccountName
| take 1);
let query = strcat(@"metricNamespace('Shoebox').metric('VMAvailabilityMetric').dimensions('resourceId').samplingTypes('Average', 'Count') | where resourceId == '", queryVmId, "'");
evaluate geneva_metrics_request(queryShoeboxAccount, query, queryFrom, queryTo)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = todatetime(column_ifexists("TimestampUtc", 0)), Availability = column_ifexists("Average", 0)
| order by TimestampUtc asc
// for debug
//| extend Availability = case (TimestampUtc between (datetime(2025-04-22 00:04:00.0000000) .. datetime(2025-04-22 00:10:00.0000000)), 0, 1)
//| where not (TimestampUtc between (datetime(2025-04-22 20:00:00.0000000) .. datetime(2025-04-22 23:00:00.0000000)))
| extend flag = case ((TimestampUtc - 1m) <> prev(TimestampUtc) or Availability <> prev(Availability), 'begin', '')
| extend flag = case (flag == '' and next(flag) == 'begin', 'end', 
                      isempty(next(TimestampUtc)), 'end', flag)
| where flag <> ''
| extend StartTime = iff(flag == 'begin', TimestampUtc, datetime(null))
| extend EndTime = iff(flag == 'begin', next(TimestampUtc), datetime(null))
| where flag <> 'end'
| extend Health = iff (Availability == 1, 'Healthy', 'Unhealthy')
| extend Content = Health
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCluster}`, `{queryVmId}`

**Signal filters seen in KQL:** `resourceId == "", queryVmId, ""` · `flag <> "end"`

---

### Container Live Migration

_Purpose:_ Container / Tenant Health

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`

```kusto
let containers = cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogContainerSnapshot
    | where PreciseTimeStamp between(queryFrom ..queryTo)
    | where (isnotempty(vmid) and virtualMachineUniqueId == vmid) or (isempty(vmid) and containerId == queryContainerId)
    | distinct containerId;
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LiveMigrationSessionCompleteLog
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where sourceContainerId in (containers)
| extend elapsedSec = totimespan(elapsedTime) / 1s
| extend Health = case (status == "Completed", "Healthy", status == "Faulted" , "Unhealthy", "Degraded")
| extend Content = triggerType
| extend StartTime = PreciseTimeStamp - totimespan(elapsedTime)
| project StartTime, EndTime = PreciseTimeStamp, Health, Content, sessionId, status, elapsedTime, reason, message, sourceContainerId, sourceNodeId, destinationContainerId, destinationNodeId
| join kind=leftouter (cluster("azcsupfollower.kusto.windows.net").database("Air").LiveMigrationFailureEvents
| where EventTime between (queryFrom .. queryTo)
| where ObjectId in (containers)
| project RCALevel1, RCALevel2, Diagnostics = parse_json(Diagnostics), sessionId = tostring(parse_json(Diagnostics)["SessionId"])) on sessionId
| project-away sessionId1
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmid}`, `{queryContainerId}`

---

### Service Healing(TM)

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fc').ServiceHealingTriggerEtwTable
| where PreciseTimeStamp between (starttime .. endtime)
| where TenantName == tenantName
| where RoleInstanceName contains roleInstanceName
| parse RoleInstanceName with "Name:" VMName ";RoleType" * 
| where VMName =~ roleInstanceName
// | where RoleInstanceName !contains "_IN_"
| project StartTime = PreciseTimeStamp, Tenant, VMName, TriggerId, TriggerObjectId, TriggerType, FaultInfoFabricOperation, TenantName, 
  RoleInstanceName, Region
| extend Content = TriggerType, Health = "Unhealthy"
```

**Params:** `{starttime}`, `{endtime}`, `{roleInstanceName}`, `{tenantName}`

---

### Service Healing(AzSM)

_Purpose:_ Container / Tenant Health

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Timeline`

```kusto
AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between(starttime .. endtime)
| where tenantName =~ queryTenantName
| where triggerObjectId == queryContainerId
| order by PreciseTimeStamp asc
| summarize StartTime = min(PreciseTimeStamp), arg_max(PreciseTimeStamp, triggerType, faultCode, faultReason, faultCode) by triggerId
| join kind=leftouter (AzSMServiceHealingStepResultEvents
    | where PreciseTimeStamp between(starttime .. endtime)
    | where tenantName == queryTenantName
    | summarize EndTime = max(PreciseTimeStamp), arg_max(PreciseTimeStamp, result) by triggerId, failureReason, targetContainerId 
) on triggerId
| project StartTime, EndTime, triggerType, triggerId, faultReason, targetContainerId, result
| extend Health = iif (result != "Succeeded", "Error", "Degraded")
| extend Content = triggerType
```

**Params:** `{starttime}`, `{endtime}`, `{queryTenantName}`, `{queryContainerId}`

---

### Planned Maintenance

_Purpose:_ Container / Tenant Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`

```kusto
let maintenanceInformation = cluster('azcore.centralus.kusto.windows.net').database('Fc').ScheduledMaintenanceInformational
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where Tenant == queryClusterName
| where traceCode == "ScheduledMaintenance_BuildMaintenanceInformation_Succeeded"
| where message contains queryRoleInstanceName and message contains queryTenantName
| where message contains "MaintenanceInformation"
| parse message with * "for scheduled maintenance id: '" maintenanceId:string  "'. Elapsed time" * 
    "IsCustomerInitiatedMaintenanceAllowed: '" IsCustomerInitiatedMaintenanceAllowed:bool "'\r\n "
    "ControlledMaintenanceResultCode: '" ControlledMaintenanceResultCode:string "'\r\n "
    "ControlledMaintenanceResultCodeDetails: '" ControlledMaintenanceResultCodeDetails:string "'\r\n "
    "ControlledMaintenancePhaseStartTimeInUTC: '" ControlledMaintenancePhaseStartTimeInUTC:datetime "'\r\n "
    "ControlledMaintenancePhaseEndTimeInUTC: '" ControlledMaintenancePhaseEndTimeInUTC:datetime "'\r\n "
    "FabricMaintenanceOperationStartTimeInUTC: '" FabricMaintenanceOperationStartTimeInUTC:datetime "'\r\n "
    "FabricMaintenanceOperationEndTimeInUTC: '" FabricMaintenanceOperationEndTimeInUTC:datetime "'\r\n "
    "MaintenanceType: '" MaintenanceType:string "'\r\n "
    "ResourceMaintenanceType: '" ResourceMaintenanceType:string "'\r\n " *
| project PreciseTimeStamp, message, maintenanceId, IsCustomerInitiatedMaintenanceAllowed, ControlledMaintenanceResultCode, ControlledMaintenanceResultCodeDetails, 
    ControlledMaintenancePhaseStartTimeInUTC, ControlledMaintenancePhaseEndTimeInUTC,
    FabricMaintenanceOperationStartTimeInUTC, FabricMaintenanceOperationEndTimeInUTC,
    MaintenanceType, ResourceMaintenanceType
| distinct message, maintenanceId, IsCustomerInitiatedMaintenanceAllowed, ControlledMaintenanceResultCode, ControlledMaintenanceResultCodeDetails, 
    ControlledMaintenancePhaseStartTimeInUTC, ControlledMaintenancePhaseEndTimeInUTC,
    FabricMaintenanceOperationStartTimeInUTC, FabricMaintenanceOperationEndTimeInUTC,
    MaintenanceType, ResourceMaintenanceType;
union
(maintenanceInformation
| extend StartTime = todatetime(ControlledMaintenancePhaseStartTimeInUTC), EndTime = todatetime(ControlledMaintenancePhaseEndTimeInUTC), Phase = "Customer Controlled Maintenance Phase"),
(maintenanceInformation
| extend StartTime = todatetime(FabricMaintenanceOperationStartTimeInUTC), EndTime = todatetime(FabricMaintenanceOperationEndTimeInUTC), Phase = "Fabric Maintenance Phase")
| extend Health = case(Phase contains 'Controlled', "Healthy", Phase contains 'Fabric', "Degraded", "Neutral"), Content = strcat(Phase, " - ", MaintenanceType)
| project StartTime, EndTime, Phase, MaintenanceType, ResourceMaintenanceType, maintenanceId, message, Content, Health
| join kind=leftouter cluster("Icmcluster.kusto.windows.net").database("ACM.Backend").PublishRequest on $left.maintenanceId==$right.ExternalIncidentId
| summarize arg_max(CommunicationDateTime, *) by Content, message, ExternalIncidentId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRoleInstanceName}`, `{queryClusterName}`

**Signal filters seen in KQL:** `traceCode == "ScheduledMaintenance_BuildMaintenanceInformation_Succeeded"` · `message contains "MaintenanceInformation"`

---

### VMA Event

_Purpose:_ Container / Tenant Health

Cluster: `vmainsight` · Database: `vmadb` · Type: `Timeline`

```kusto
cluster("vmainsight.kusto.windows.net").database("vmadb").VMA()
| where PreciseTimeStamp between(queryFrom .. queryTo)
//| where NodeId == nodeid
| where (isnotempty(vmid) and VmUniqueId == vmid) or (isempty(vmid) and ContainerId == queryContainerId)
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1,
  RCALevel2, RCALevel3, E17_StorageAccount, E17_StorageTenant, Network_TOR2 
| order by StartTime asc
| extend durationSec = datetime_diff("Second", EndTime, StartTime)
| extend Content = RCALevel2
| extend Health = iff (RCAEngineCategory == "CustomerInitiated", "Healthy", "Unhealthy")
| join kind=leftouter (
  cluster('vmainsight.kusto.windows.net').database('Air').VmRestartRcaLevel1Level2ArticleMapping
) on $left.RCALevel1 == $right.RCALevel1 and $left.RCALevel2 == $right.RCALevel2
| join kind=leftouter (
  cluster('vmainsight.kusto.windows.net').database('Air').VmRestartArticleCssWikiLinkMapping
) on $left.ArticleId == $right.ArticleId
| project Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, 
  RCALevel2, RCALevel3, E17_StorageAccount, E17_StorageTenant, Network_TOR2, ArticleId, CssWikiLink, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmid}`, `{queryContainerId}`

---

### AIR Events

_Purpose:_ Container / Tenant Health

Cluster: `vmainsight` · Database: `Air` · Type: `Timeline`

```kusto
let _vmid = iff(isempty(queryVmId), "dummyId", queryVmId);
union
(cluster('vmainsight.kusto.windows.net').database('Air').GetVMAvailabilityImpactEvents(VmId = _vmid, startTime = queryFrom, endTime = queryTo)
| project Timestamp, Cluster, RoleInstanceName, EventType, EventSource, ImpactCategory, TenantName, ObjectIds, FailureSignature, FailureDetails, StartTime = ImpactBeginTimeStamp, EndTime = ImpactEndTimeStamp, ImpactDurationTimeSpan, ImpactAIRGroup, InternalArticleId, CssWikiLink 
| extend EventId = tostring(new_guid()), Health="Unhealthy", Content = EventType),
(cluster('vmainsight.kusto.windows.net').database('Air').GetVMDiskBlipEvents(VmId = _vmid, startTime = queryFrom, endTime = queryTo)
| project Timestamp, Cluster, RoleInstanceName, EventType, EventSource, ImpactCategory, TenantName, ObjectIds, FailureSignature, FailureDetails, StartTime = ImpactBeginTimeStamp, EndTime = ImpactEndTimeStamp, ImpactDurationTimeSpan, ImpactAIRGroup, InternalArticleId, CssWikiLink
| extend EventId = tostring(new_guid()), Health="Unhealthy", Content = EventType)
| project StartTime, EndTime, ImpactDurationTimeSpan, EventId, FailureSignature, FailureDetails, ImpactAIRGroup, InternalArticleId, CssWikiLink, Health, Content
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`

---
