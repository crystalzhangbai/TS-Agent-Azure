# Guest Agent & Extensions

> Source: EEE RDOS Start Hub dashboard (3 queries).

Use when investigating: **guest agent provisioning failures, extension install failures, scheduled events, ICM impact reports**. These cover guest-side platform integration.

---

### Tenant Scheduled Events

_Purpose:_ Container / Tenant Health

Cluster: `azpe` · Database: `azpe` · Type: `Timeline`

```kusto
cluster("azpe.kusto.windows.net").database("azpe").AzPEWorkflowEvent 
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where EntityId == queryTenantName    
| extend impactedInstances = tostring((parse_json(WorkflowEventData).Containers))
| project StartTime = PreciseTimeStamp,  impactedInstances, WorkflowInstanceGuid, WorkflowType, WorkflowEventType, WorkflowId, WorkflowEventData
//| project StartTime = PreciseTimeStamp, AzPEWorkflowId, WorkflowType, impactedInstances, WorkflowEventType, EventId, TenantManagementJobMessage, WorkflowEventData 
| extend Content = strcat (WorkflowType, " - ", WorkflowEventType), Health = iif (impactedInstances contains queryInstanceName, "Degraded", "Neutral")
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryInstanceName}`

---

### ICM Report

_Purpose:_ Container / Tenant Health

Cluster: `icmcluster` · Database: `IcMDataWarehouse` · Type: `Timeline`

```kusto
let devicename = toscalar(cluster('azphynet').database('azdhmds').Servers
| where NodeId =~ queryNodeId
| project DeviceName );
let _torName = toscalar(cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice == devicename
| project NodeName=StartDevice, NodePort=StartPort, NodeSonicPort=StartSonicPort, TorDevice=EndDevice, TorSonicPort=EndSonicPort, BandwidthInGbps, DataCenter
| take 1
| project TorDevice);
let queryTorName = iff(isempty(_torName), "tor00-0000-0000-00t0-dummy", _torName);
cluster('icmcluster.kusto.windows.net').database('IcMDataWarehouse').Incidents
| where CreateDate between (queryFrom .. queryTo)
| where * has queryNodeId or * has queryContainerId or * has queryTenantName or Title contains queryTorName or (Title contains "Too many Unhealthy nodes" and Title contains queryCluster)
| order by ModifiedDate asc
| extend flag = case(IncidentId <> prev(IncidentId), "changed", "")
| where flag <> ""
| extend Content = strcat(iff(IncidentType == "CustomerReported", "CRI", "LSI"), " - ", IncidentId)
| project IncidentId, StartTime = CreateDate, Title, InitialOwningTeam = OwningTeamName, IncidentType, SupportTicketId, SubscriptionId, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`, `{queryTenantName}`, `{queryCluster}`

---

### GuestAgentAndExtensionTimeline

_Purpose:_ Guest Agent & Extension Provisioning

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where PreciseTimeStamp between( queryFrom.. queryTo) 
| where ContainerId == queryContainerid
//| project PreciseTimeStamp, Level, RoleInstanceName, ContainerId, Name, TaskName, Operation, OperationSuccess, Message, OpcodeName
| where (TaskName == "Daemon") or (TaskName == "ExtHandler" and Operation == "GoalState") or OperationSuccess == "False" or (Name !contains "WALinuxAgent" and Name !contains "WindowsAzureGuestAgent")
| extend StartTime = todatetime(OpcodeName), Content = Operation
| extend GroupBy = case(Name contains "Agent", strcat(Name, "/", TaskName, "/", Operation), Name)
| extend Health = case (OperationSuccess <> "True", "Unhealthy", Message contains "transitioning" or Message contains "NotReady" or Message contains "error", "Degraded", "Healthy")
| project StartTime, GroupBy, PreciseTimeStamp, RoleInstanceName, ContainerId, Name, TaskName, Operation, OperationSuccess, Message, Content, Health
| order by GroupBy, StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerid}`

---
