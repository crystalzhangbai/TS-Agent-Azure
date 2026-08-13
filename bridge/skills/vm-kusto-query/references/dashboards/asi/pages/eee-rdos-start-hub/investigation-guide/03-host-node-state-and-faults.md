# Host Node State & Faults

> Source: EEE RDOS Start Hub dashboard (23 queries).

Use when investigating: **host node faulted / OFR (Out For Repair) / HumanInvestigate / unallocatable / cluster-wide node health / service healing / live migration of containers off a node**. These queries answer *"is the node healthy, and if not, why"*.

---

### Fabricator Instance

_Purpose:_ Cluster Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
cluster('azcsupfollower').database('AzureCM').LogClusterSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
| where tenantName == cluster
| order by PreciseTimeStamp asc 
| project StartTime = PreciseTimeStamp, tenantName, roleInstanceName
| extend flag = case (prev(roleInstanceName) <> roleInstanceName, "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), endtime)
| extend Content = roleInstanceName
| extend Health = "Neutral"
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Fabricator Downtime

_Purpose:_ Cluster Health

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`

```kusto
let clusters = print Tenant = cluster;
FabricFailoverDowtimeRawDataPerCluster(clusters=clusters, startTime=starttime, endTime=endtime)
| project StartTime = DownTimeStart, EndTime = DownTimeEnd, Content = strcat(tostring(DurationInMs/1000), " secs"), Health = "Unhealthy"
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Allocatable State

_Purpose:_ Cluster Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
cluster('azcsupfollower').database('AzureCM').LogClusterCapacity
| where PreciseTimeStamp between (starttime .. endtime)
| where Tenant == cluster
| project PreciseTimeStamp, categoryByMachinePoolNameJson, isAcceptedNewDeployment = tostring(parse_json(newDeploymentStatusJson).isAcceptingNewDeployments), rejectReason = tostring(parse_json(newDeploymentStatusJson).rejectReason)
| order by PreciseTimeStamp asc
| extend flag = case (prev(isAcceptedNewDeployment) <> isAcceptedNewDeployment, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp, Content = ""
| extend EndTime = case (isnotempty(next(isAcceptedNewDeployment)), next(PreciseTimeStamp), endtime)
| extend Health = case (isAcceptedNewDeployment == "true", "healthy", 
    isAcceptedNewDeployment == "false", "unhealthy", 
    "degraded")
| project StartTime, EndTime, Content, Health
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Cluster Planned Maintenance

_Purpose:_ Cluster Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
cluster('azcsupfollower').database('AzureCM').MaintenancePhaseDetails
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where Tenant == queryClusterName
 | project PreciseTimeStamp, phaseId, todatetime(startTimeUTC), todatetime(endTimeUTC), maintenanceOperationType, scheduledMaintenanceId
 | order by PreciseTimeStamp asc
| extend flag = case (prev(scheduledMaintenanceId) <> scheduledMaintenanceId, "changed", 
    prev(phaseId) <> phaseId, "changed", 
    "") 
| where flag <> ""
| where queryFrom between(startTimeUTC .. endTimeUTC) or queryTo between(startTimeUTC .. endTimeUTC)
| extend StartTime = max_of(queryFrom, startTimeUTC)
| extend EndTime = min_of(queryTo, endTimeUTC)
| extend Health = "degraded" 
| extend Content = maintenanceOperationType
| join kind=leftouter cluster("Icmcluster.kusto.windows.net").database("ACM.Backend").PublishRequest on $left.scheduledMaintenanceId==$right.ExternalIncidentId
| extend AdditionalProperties = parse_json(AdditionalProperties)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryClusterName}`

---

### Cluster Service Healing

_Purpose:_ Cluster Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `Aplat` · Type: `Timeline`

```kusto
MycroftClusterSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where ClusterName == queryClusterName
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, IsClusterServiceHealingDisabled, Content = iif(IsClusterServiceHealingDisabled == true, "Disabled", "Enabled")
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = iif(IsClusterServiceHealingDisabled == false, "Healthy", "Unhealthy")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryClusterName}`

---

### NodeStateHumanInvestigateCount

_Purpose:_ HumanInvestigate Node Count / Hour

Cluster: `azurecm` · Database: `AzureCM` · Type: `TimeSeries`

```kusto
cluster('azcsupfollower.kusto.windows.net').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
// | where nodeId == nodeid
| where Tenant == cluster
| where nodeState == "HumanInvestigate"
| distinct bin(PreciseTimeStamp, 1h), nodeId, nodeState, machinePoolName
| order by PreciseTimeStamp asc 
| extend Counter = strcat(machinePoolName, ":", nodeState)
| summarize count() by PreciseTimeStamp, machinePoolName
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "HumanInvestigate"`

---

### NodeStateReadyCount

_Purpose:_ HumanInvestigate Node Count / Hour

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `TimeSeries`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
// | where nodeId == nodeid
| where Tenant == cluster
| where nodeState == "Ready"
| distinct bin(PreciseTimeStamp, 1h), nodeId, nodeState, machinePoolName
| order by PreciseTimeStamp asc 
| extend Counter = strcat(machinePoolName, ":", nodeState)
| summarize count() by PreciseTimeStamp, machinePoolName
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "Ready"`

---

### DCM Node State

_Purpose:_ Node Health

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(starttime .. endtime)
| where ResourceId == nodeid
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, ResourceId, LifecycleState, PfState, PfRepairState, HealthSummary, FaultCode, FaultDescription
| extend flag = case(prev(LifecycleState) <> LifecycleState, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp), endtime)
| extend Content = LifecycleState
| extend Health = case (LifecycleState == "Production", "Healthy", 
    LifecycleState contains "OutForRepair", "Unhealthy", 
    "Degraded")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### DCM Node Fault

_Purpose:_ Node Health

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ResourceId == queryNodeId
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, ResourceId, LifecycleState, PfState, PfRepairState, HealthSummary, FaultCode, FaultDescription
| extend flag = case(prev(FaultCode) <> FaultCode, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp), queryTo)
| extend Content = tostring(FaultCode)
| extend Health = "Unhealthy"
| where FaultCode <> 0
| project StartTime, EndTime, LifecycleState, HealthSummary, FaultCode, FaultDescription, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Root Update Alloc Type

_Purpose:_ Node Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
cluster('azcsupfollower').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeId == nodeid
// | where nodeId == 'ee939a66-a270-48d4-a3bc-8687227fe2dc'
// | project PreciseTimeStamp, Tenant, nodeState, nodeAvailabilityState, containerCount, 
//   cmNodeChannelHealthStatus ,faultInfo, healthSignals
| project PreciseTimeStamp, rootUpdateAllocationType
| order by PreciseTimeStamp asc 
| extend flag = case (rootUpdateAllocationType <> prev(rootUpdateAllocationType), "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp, EndTime = case (isnotnull(next(PreciseTimeStamp)), next(PreciseTimeStamp), queryTo)
| extend Health = case ( rootUpdateAllocationType == 'MultipleUpdateSet', "Healthy", "Unknown")
| extend Content = rootUpdateAllocationType
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

**Signal filters seen in KQL:** `nodeId == "ee939a66-a270-48d4-a3bc-8687227fe2dc"`

---

### Node State

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Timeline`

```kusto
MycroftNodeHealthSnapshot
| where PreciseTimeStamp between (starttime..endtime)
| where NodeId == nodeid
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, Content = NsdState
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), endtime)
| extend Health = case(Content in ("Booting", "OutForRepair", "PoweringOn", "HumanInvestigate", "PoweredOff", "Dead", "Recovering"), "Unhealthy", Content in ("Unhealthy"), "Degraded", Content == "Ready", "Healthy", "Neutral")
| project StartTime, EndTime, Health, Content
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Node Availability

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Timeline`

```kusto
MycroftNodeHealthSnapshot
| where PreciseTimeStamp between (starttime..endtime)
| where NodeId == nodeid
| order by PreciseTimeStamp asc
| project StartTime = PreciseTimeStamp, Content = AvailabilityState
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), endtime)
| extend Health = case (Content in ("Faulted", "OutForRepair"), "Unhealthy", Content == "Available", "Healthy", "Degraded")
| project StartTime, EndTime, Health, Content
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Node Fault

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Timeline`

```kusto
MycroftNodeHealthSnapshot
| where PreciseTimeStamp between (starttime..endtime)
| where NodeId == nodeid
| order by PreciseTimeStamp asc
| extend flag = case (FaultInfo <> prev(FaultInfo), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp), endtime)
| extend Health = "Unhealthy"
| where FaultInfo <> ""
| project StartTime = PreciseTimeStamp, EndTime, Content = tostring(parse_json(FaultInfo)["FaultCode"]), tostring(parse_json(FaultInfo)["FabricOperationString"]), Health, parse_json(FaultInfo)
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Node WillBe Channel Health Status

_Purpose:_ Node Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where nodeId == queryNodeId
| project StartTime = PreciseTimeStamp, Content = cmNodeWillBeChannelHealthStatus
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = case(Content == "Unhealthy", "Unhealthy", Content in ("Unresponsive", "Unknown"), "Degraded", Content == "Healthy",  "Healthy", "Neutral")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Node WasChannel Health Status

_Purpose:_ Node Health

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where nodeId == queryNodeId
| project StartTime = PreciseTimeStamp, Content = cmNodeWasChannelHealthStatus
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = case(Content == "Unhealthy", "Unhealthy", Content in ("Unresponsive", "Unknown"), "Degraded", Content == "Healthy",  "Healthy", "Neutral")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Node Service Error

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').NodeServiceOperationEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
// | where Identifier contains "{containerid}"
| where OperationName !contains "Query"
| where Result <> 1
| extend ResultCode = tohex(toint(ResultCode), 8), Health = "Unhealthy"
| extend Content = strcat("0x", ResultCode)
| project StartTime = RequestTime, EndTime = CompleteTime, OperationName, Identifier, Result, ResultCode, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Identifier contains "{containerid}"`

---

### VMAL Error

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
VmServiceContainerOperations
| where PreciseTimeStamp between ( queryFrom .. queryTo )  
| where NodeId == queryNodeId
// | where Identifier contains "{containerid}"
| where ResultCode !in ("0x0", "0x1")
| extend Content = ResultCode, Health = "Unhealthy"
| project StartTime, EndTime, DurationMillis, Cluster, Level, Operation, Stage, ResultCode, ContainerId, NodeId, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Identifier contains "{containerid}"`

---

### Node Live Migration

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fc').LiveMigrationContainerDetailsEventLog
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where sourceNodeId == nodeid
| project StartTime = PreciseTimeStamp, sessionId, triggerType, migrationConstraint, Tenant, sourceContainerId, sourceNodeId, sourceDip, sourceVlan, 
          destinationContainerId, destinationNodeId, destinationDip, destinationVlan
| join kind=inner(
    cluster('azcore.centralus.kusto.windows.net').database('Fc').LiveMigrationSessionCompleteLog
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where sourceNodeId == nodeid
    | project EndTime = PreciseTimeStamp, sessionId, status, elapsedTime, message, resourceId
) on $left.sessionId == $right.sessionId
| extend elapsedSec = totimespan(elapsedTime) / 1s
| extend Health = case (status == 'Faulted', 'Unhealthy', status == 'Completed', 'Healthy', 'Degraded' )
| extend Content = triggerType
| project StartTime, EndTime, sessionId, triggerType, migrationConstraint, status, elapsedTime, elapsedSec, message, Tenant, tenantName = resourceId, 
          sourceContainerId, sourceNodeId, sourceDip, sourceVlan, destinationContainerId, destinationNodeId, destinationDip, destinationVlan, Health, Content
| join kind=leftouter (cluster("azcsupfollower.kusto.windows.net").database("Air").LiveMigrationFailureEvents
| where EventTime between (queryFrom .. queryTo)
| project RCALevel1, RCALevel2, Diagnostics = parse_json(Diagnostics), sessionId = tostring(parse_json(Diagnostics)["SessionId"])) on sessionId
| project-away sessionId1
| order by StartTime asc             
| order by StartTime
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### Anvil Event - Node

_Purpose:_ Node Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Timeline`

```kusto
cluster("aplat.westcentralus.kusto.windows.net").database("APlat").AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where ResourceId == queryNodeId
| where MessageTrigger contains "OnBeforeWalkTree"
| project PreciseTimeStamp, Cluster, Role, MessageTrigger, TreeName, TreeNodeKey, TreeActionName, TreeActionInput, Properties, TaskStatus, Message, ResourceId, ResourceType, ResourceDependencies
| order by PreciseTimeStamp asc 
| extend StartTime = PreciseTimeStamp
| extend FaultCodeString = parse_json(Message).RepairContext.FaultCodeString
| extend Content = tostring(FaultCodeString)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `MessageTrigger contains "OnBeforeWalkTree"`

---

### Hyper-V State

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `fa` · Type: `Timeline`

```kusto
HostAgentEventsEtwTable
| where PreciseTimeStamp between ( queryFrom .. queryTo )  
| where NodeId == queryNodeId and Message has "Hyper-V is unresponsive"
| extend Content = Message, Health = "Unhealthy"
| project StartTime = PreciseTimeStamp, Message, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### NodeStateOFRCount

_Purpose:_ OutForRepair Node Count / Hour

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `TimeSeries`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
// | where nodeId == nodeid
| where Tenant == cluster
| where nodeState == "OutForRepair"
| distinct bin(PreciseTimeStamp, 1h), nodeId, nodeState, machinePoolName
| order by PreciseTimeStamp asc 
| extend Counter = strcat(machinePoolName, ":", nodeState)
| summarize count() by PreciseTimeStamp, machinePoolName
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "OutForRepair"`

---

### NodeStateReadyCount

_Purpose:_ Ready Node Count

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `TimeSeries`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
// | where nodeId == nodeid
| where Tenant == cluster
| where nodeState == "Ready"
| distinct bin(PreciseTimeStamp, 1h), nodeId, nodeState, machinePoolName
| order by PreciseTimeStamp asc 
| extend Counter = strcat(machinePoolName, ":", nodeState)
| summarize count() by PreciseTimeStamp, machinePoolName
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "Ready"`

---

### Unhealthy Node Count

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `TimeSeries`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
// | where nodeId == nodeid
| where Tenant == cluster
| where nodeState == "Unhealthy"
| distinct bin(PreciseTimeStamp, 30m), nodeId, nodeState, machinePoolName
| order by PreciseTimeStamp asc 
| extend Counter = strcat(machinePoolName, ":", nodeState)
| summarize count() by PreciseTimeStamp, machinePoolName
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "Unhealthy"`

---
