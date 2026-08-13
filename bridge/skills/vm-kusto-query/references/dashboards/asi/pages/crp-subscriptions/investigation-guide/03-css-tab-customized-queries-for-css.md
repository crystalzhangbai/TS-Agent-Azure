# CSS Tab - Customized queries for CSS

> Source: **CRP Subscriptions Investigation Guide** dashboard, chapter **CSS Tab - Customized queries for CSS** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Planned Maintenance Communications/Emails

### GetPlannedMaintenanceCommunicationsForSupport

_Widget purpose:_ Planned Maintenance Communications/Emails

Cluster: `Icmcluster` · Database: `ACM.Backend` · Type: `Table`
Source panel: `CSS Tab - Customized queries for CSS > Planned Maintenance Communications/Emails`

```kusto
cluster("Icmcluster").database("ACM.Publisher").AlbnTargets_Expanded
| where PublishDateTime between (queryFrom .. queryTo)
| where Subscription == querySub
| project CommunicationId, PublishDateTime
| join kind=inner cluster('Icmcluster').database("ACM.Backend").PublishRequest on CommunicationId
| where CommunicationDateTime between (queryFrom .. queryTo)
| order by CommunicationDateTime desc
| where CommunicationType == "Maintenance"
| where ImpactedServices contains "virtualmachines" or Title contains "virtual machines"
| extend maintenanceType = tostring(parse_json(AdditionalProperties).maintenanceType)
| extend eventType = tostring(parse_json(AdditionalProperties).eventType)
| extend EventStartTime = tostring(parse_json(AdditionalProperties).impactStartTime)
| extend EventEndTime = tostring(parse_json(AdditionalProperties).impactMitigationTime)
//| where RichTextMessage contains "self-service phase" or RichTextMessage contains "scheduled maintenance phase"
| summarize arg_max(CommunicationDateTime, *) by TrackingId =  IncidentId
| order by EventStartTime  asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySub}`

**Signal filters seen in KQL:** `CommunicationType == "Maintenance"` · `ImpactedServices contains "virtualmachines"` · `RichTextMessage contains "self-service phase"`

---

## Planned Maintenance Status

### Get Current Maintenance Status By Subscription

_Widget purpose:_ Planned Maintenance Status

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `CSS Tab - Customized queries for CSS > Planned Maintenance Status`

```kusto
let scheduleLookBackPeriod = ago(1d);
let lookBackPeriod = ago(2h);
let containerList = LogContainerSnapshot
| where PreciseTimeStamp >= lookBackPeriod and subscriptionId == querySub
| summarize arg_max(PreciseTimeStamp,*) by Tenant, tenantName, roleInstanceName
| project Cluster = Tenant, TenantName = tenantName, RoleInstanceName =  roleInstanceName, nodeId, VMId = virtualMachineUniqueId, ContainerId = containerId, ContainerCreationtime = creationTime;
let clusterList = containerList | distinct Cluster;
let scheduledMaintenances= ScheduledMaintenanceInformational 
| where PreciseTimeStamp >= scheduleLookBackPeriod
| where Tenant in (clusterList)
| where traceCode == "ScheduledMaintenance_BuildMaintenanceInformation_Succeeded"
//| where message contains queryRoleInstanceName and message contains queryTenantName
| where message contains "MaintenanceInformation"
| parse message with * "for scheduled maintenance id: '" maintenanceId:string  "'. Elapsed time" * 
    "Tenant: '" TenantName:string "'\r\n "
    "RoleInstance: '" RoleInstanceName:string "'\r\n "
    "IsCustomerInitiatedMaintenanceAllowed: '" IsCustomerInitiatedMaintenanceAllowed:bool "'\r\n "
    "ControlledMaintenanceResultCode: '" ConfntrolledMaintenanceResultCode:string "'\r\n "
    "ControlledMaintenanceResultCodeDetails: '" ControlledMaintenanceResultCodeDetails:string "'\r\n "
    "ControlledMaintenancePhaseStartTimeInUTC: '" ControlledMaintenancePhaseStartTimeInUTC:datetime "'\r\n "
    "ControlledMaintenancePhaseEndTimeInUTC: '" ControlledMaintenancePhaseEndTimeInUTC:datetime "'\r\n "
    "FabricMaintenanceOperationStartTimeInUTC: '" FabricMaintenanceOperationStartTimeInUTC:datetime "'\r\n "
    "FabricMaintenanceOperationEndTimeInUTC: '" FabricMaintenanceOperationEndTimeInUTC:datetime "'\r\n "
    "MaintenanceType: '" MaintenanceType:string "'\r\n "
    "ResourceMaintenanceType: '" ResourceMaintenanceType:string "'\r\n " *
 | summarize arg_max(PreciseTimeStamp, ScheduledMaintenanceId = scheduledMaintenanceId, Tenant, RoleInstanceName, 
    IsCustomerInitiatedMaintenanceAllowed, ConfntrolledMaintenanceResultCode, ControlledMaintenanceResultCodeDetails,
    ControlledMaintenancePhaseStartTimeInUTC, ControlledMaintenancePhaseEndTimeInUTC, 
    FabricMaintenanceOperationStartTimeInUTC, FabricMaintenanceOperationEndTimeInUTC,
    MaintenanceType, ResourceMaintenanceType
    ) by TenantName, RoleInstanceName
 | join hint.strategy = broadcast containerList on $left.Tenant == $right.Cluster, TenantName, RoleInstanceName;
let decommissionVMList =  scheduledMaintenances 
| where MaintenanceType == "Decommission"
| join kind = inner 
(
TMMgmtFabricSettingEtwTable
| where PreciseTimeStamp > lookBackPeriod
| where Name == "Fabric.TargetMachinePools" and Value != "(empty)"
| summarize arg_max(PreciseTimeStamp, Value) by Name, Tenant
| project Tenant, TargetMachinePools = Value
) on Tenant
| join kind=inner 
(
LogNodeSnapshot
| where PreciseTimeStamp > lookBackPeriod
| summarize arg_max(PreciseTimeStamp, CurrentMachinePool = machinePoolName) by Tenant, nodeId
) on Tenant, nodeId
| extend MaintenanceStatus =iff(TargetMachinePools has CurrentMachinePool, "Updated", "Pending")
| project VMId, ContainerCreationtime, ContainerId, NodeId = nodeId, Cluster = Tenant, TenantName, RoleInstanceName, 
    MaintenanceStatus, ScheduledMaintenanceId, 
    IsCustomerInitiatedMaintenanceAllowed, ConfntrolledMaintenanceResultCode, ControlledMaintenanceResultCodeDetails,
    ControlledMaintenancePhaseStartTimeInUTC, ControlledMaintenancePhaseEndTimeInUTC, 
    FabricMaintenanceOperationStartTimeInUTC, FabricMaintenanceOperationEndTimeInUTC,
    MaintenanceType, ResourceMaintenanceType;
let rootOSMaintenanceVMList = scheduledMaintenances 
| where MaintenanceType == "RootOSHEUpdate"
| join kind = inner 
(LogNodeSnapshot
| where PreciseTimeStamp > lookBackPeriod
| summarize arg_max(PreciseTimeStamp, *) by Tenant, CurrentMachinePool = machinePoolName, nodeId
| extend he = parsejson(hostingEnvironment)
| extend NodeOS = split(tostring(he.OSBaseImageName),".vhd",0)
| mv-expand NodeOS
| project Tenant, PreciseTimeStamp, CurrentMachinePool, nodeId, NodeOS
) on Tenant, nodeId
| join kind = inner 
(
cluster("azurecm").database("AzureCM").LogClusterSnapshot
| where PreciseTimeStamp > lookBackPeriod
| summarize arg_max(PreciseTimeStamp, *) by Tenant
| extend he = parsejson(hostingEnvironment)
| project Tenant, TargetOS= he.ServerStandardCore_HVBaseName
) on Tenant 
| extend MaintenanceStatus =iff(tostring(NodeOS) == tostring(TargetOS), "Updated", "Pending")
| project VMId, ContainerCreationtime, ContainerId, NodeId = nodeId, Cluster = Tenant, TenantName, RoleInstanceName, 
    MaintenanceStatus, ScheduledMaintenanceId, 
    IsCustomerInitiatedMaintenanceAllowed, ConfntrolledMaintenanceResultCode, ControlledMaintenanceResultCodeDetails,
    ControlledMaintenancePhaseStartTimeInUTC, ControlledMaintenancePhaseEndTimeInUTC, 
    FabricMaintenanceOperationStartTimeInUTC, FabricMaintenanceOperationEndTimeInUTC,
    MaintenanceType, ResourceMaintenanceType;
union decommissionVMList, rootOSMaintenanceVMList
| extend MaintenancePhase =  iff(now() between (ControlledMaintenancePhaseStartTimeInUTC  .. ControlledMaintenancePhaseEndTimeInUTC), 
    "Customer Controlled Maintenance Phase", 
    iif(now() between (FabricMaintenanceOperationStartTimeInUTC  .. FabricMaintenanceOperationEndTimeInUTC),"Fabric Maintenance Phase", "Out of Mainteannce Window"))
| join kind=leftouter cluster("Icmcluster").database("ACM.Backend").PublishRequest on $left.ScheduledMaintenanceId==$right.ExternalIncidentId
| summarize arg_max(CommunicationDateTime, *) by ContainerId, ExternalIncidentId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySub}`

**Signal filters seen in KQL:** `traceCode == "ScheduledMaintenance_BuildMaintenanceInformation_Succeeded"` · `message contains "MaintenanceInformation"` · `MaintenanceType == "Decommission"` · `Name == "Fabric.TargetMachinePools"` · `MaintenanceType == "RootOSHEUpdate"`

---
