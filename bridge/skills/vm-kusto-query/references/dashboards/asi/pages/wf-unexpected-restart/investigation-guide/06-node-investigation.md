# Node Investigation

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Node Investigation** (53 queries across 27 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Anvil

### Anvil DS

_Widget purpose:_ Anvil events

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`
Source panel: `Node Investigation > Anvil > Anvil events`

```kusto
AnvilRepairServiceForgeEvents 
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where ResourceDependencies has_any (query_NodeId)
| where TreeNodeKey !in ('Root', 'Node') 
| summarize arg_max(PreciseTimeStamp, *) by RequestIdentifier, TreeNodeKey 
| order by RequestIdentifier, PreciseTimeStamp asc 
| project PreciseTimeStamp, AnvilOperation=TreeNodeKey, NodeId=tostring(parse_json(ResourceDependencies).NodeId), AnvilRequestIdentifier=RequestIdentifier, ResourceId, ResourceType 
| sort by PreciseTimeStamp asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## ASC HA Runs

### HAruns DS

_Widget purpose:_ ASC HA Runs

Cluster: `Azds` · Database: `adsmds` · Type: `Table`
Source panel: `Node Investigation > ASC HA Runs > ASC HA Runs`

```kusto
TraceEvent
| where Output contains 'HostAnalyzer.ps1' and Output contains 'Start to run HA report for '
            and env_cloud_environment == 'Prod'
            and env_time between ((startTime - 6h) .. (endTime + 6h)) 
| parse Output with * '-cluster \'' Cluster '\' -nodeId \'' NodeId '\' -containerId \'' ContainerId '\' -startTime \'' StartTime '\' -endTime \'' EndTime '\' -ExecutedFromGetSub -resourceId \'' ResourceId '\'' *
| distinct StartTime, EndTime, Cluster, NodeId, ContainerId, ResourceId, RequestId
| where NodeId == '$($nodeId)'
| join kind=inner(
    TraceEvent
    | where env_time between ((startTime - 6h) .. (endTime + 6h)) and Output contains 'successfully upload'
    | parse Output with * ' to ' ReportUrl
    | extend ReportUrl = substring(ReportUrl, 0, strlen(ReportUrl)-1)
    | distinct RequestId, ReportUrl
) on RequestId
| project-away RequestId1
| sort by StartTime desc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `Output contains "HostAnalyzer.ps1"` · `NodeId == "$($nodeId)"`

---

## Azure Profiler

### WF_UR_AzureProfiler

_Widget purpose:_ Azure Profiler

Cluster: `azureprofilerfollower.westus2.kusto.windows.net` · Database: `azureprofiler` · Type: `Table`
Source panel: `Node Investigation > Azure Profiler > Azure Profiler`

```kusto
cluster('azureprofilerfollower').database('azureprofiler').Identifiers
| where TraceStartTime between ((query_BeginTime) .. (query_EndTime)) and NodeId == query_NodeId
| project Timestamp, TraceStartTime, NodeId, Cluster, PublishBlob, ViewerUrl, ActiveCPU, Fuse
| join kind = inner (
    cluster('azureprofilerfollower').database('azureprofiler').TraceInsights
    | where Timestamp between ((query_BeginTime - 3h) .. (query_EndTime + 3h)) and Name == "Top Processes by Active CPU"
    | extend TopProcess=tostring(SupportingData.TopActiveProcesses.Processes[0].Name), TopProcessCPU=todecimal(SupportingData.TopActiveProcesses.Processes[0].CPUPercentage)
) on PublishBlob
| join kind = inner (
    cluster('azureprofilerfollower').database('azureprofiler').TraceInsights
    | where Timestamp between ((query_BeginTime - 3h) .. (query_EndTime + 3h)) and Name == "Hot Function"
    | extend HotFunction = tostring(SupportingData.HotFunction.Function), TopProcess = substring(Scope,8)
) on PublishBlob, TopProcess
| project TraceStartTime, Fuse, HotFunction, ViewerUrl
| sort by TraceStartTime asc nulls last
| sort by TraceStartTime asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## Azure Watson

### AzureWatson DS

_Widget purpose:_ Azure Watson

Cluster: `Azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `Table`
Source panel: `Node Investigation > Azure Watson > Azure Watson`

```kusto
CustomerCrashOccurredV2
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime)
| where nodeIdentity == query_NodeId and crashMode == "km"
| project crashMode, crashProcessFullPath, process, dumpUid, nodeIdentity
| join kind=leftouter(
    CustomerDumpAnalysisResultV2 | where PreciseTimeStamp between (query_BeginTime .. query_EndTime)
) on dumpUid
| distinct crashTime, crashMode, bucketString, followup, faultingModule, faultingModuleVersion, bugLink,  dumpUid
| sort by crashTime asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## E17

### DiskFailureXStoreTriage DS

Cluster: `Xlivesite` · Database: `XHealthDiskTriage` · Type: `Table`
Source panel: `Node Investigation > E17 > DiskFailureXStoreTriage`

```kusto
cluster('Xlivesite').database('XHealthDiskTriage').XHealth_DiskFailureXStoreTriage
| where env_time  between (query_StartTime..query_EndTime)
| where NodeId == query_NodeId
| project env_time, AccountName, BlobPath, DiskPath, TriageCategory, TriageReason, TriageTimestamp, HostErrorCode, HostErrorString, StorageRegion, StorageTenant, EscalationTarget
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_NodeId}`

---

### E17_for_container DS

_Widget purpose:_ E17s for container

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > E17 > E17s for container > E17s for container`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime) and NodeId == query_nodeid
| extend ContainerId = tostring(split(split(SurfaceName, "_")[0], "~")[0])
| where ContainerId == query_containerid
| union (cluster("azcore.centralus.kusto.windows.net").database("Fa").OsUltraSSDCounterTable 
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime) and NodeId ==  query_nodeid and ContainerId has query_containerid)
| parse ArmId with * "/disks/" DiskName
| parse BlobPath with * "/" NewBlobPath "?" *
| extend BlobPath = case(isnotempty(NewBlobPath), NewBlobPath, BlobPath)
| extend StorageAccount = tostring(split(BlobPath, "/")[1])
| extend SurfaceName = case(isempty(SurfaceName), SurfaceGUID, SurfaceName)
| distinct  SurfaceName, BlobPath, ContainerId, StorageAccount, StorageTenant, SDFTenant, Cluster,  DiskName, NodeId
| extend StorageTenant = case(isempty(StorageTenant), tolower(tostring(split(SDFTenant, "-")[1])), StorageTenant)
| join kind = inner (
    cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where TIMESTAMP between (query_BeginTime..query_EndTime) and EventId == 17 and ProviderName == 'VhdDiskPrt' ) on $left.NodeId == $right.NodeId
| join kind = leftouter ( 
    cluster('xlivesite.kusto.windows.net').database('XHealthDiskTriage').XHealth_DiskFailureXStoreTriage
| where TimeStamp between (query_BeginTime..query_EndTime) ) on $left.NodeId == $right.NodeId
| join kind = leftouter (
    cluster("azcore.centralus.kusto.windows.net").database("Fa").OsConfigTable
    | where PreciseTimeStamp between ((query_BeginTime - 4h)  .. (query_EndTime + 5h))
            and NodeId ==  query_nodeid  and Component == "blobprop" 
    | extend BlobProperties = parse_json(ConfigValue)
    | extend 
             DiskAccessTier = tostring(BlobProperties.blobproperties['x-ms-access-tier']),
             EnhancedConnectionVersion = BlobProperties.blobproperties["x-ms-enhancedconnectionversion"],
             StorageTenant = tostring(BlobProperties.storagecluster)
    | extend BlobProperties = BlobProperties.blobproperties
    | summarize hint.strategy=shuffle arg_max(PreciseTimeStamp, *) by ConfigName
    | project BlobPath = ConfigName, DiskAccessTier, EnhancedConnectionVersion, BlobProperties, StorageTenant, NodeId
    | parse BlobPath with * "/" BlobPath
) on BlobPath
| project-away BlobPath1
| where BlobPath != "" and Description has BlobPath and TriageCategory != "Unknown"
| distinct TimeCreated,NodeId,ContainerId, EventId, Description, DiskName, BlobPath,TriageCategory, TriageReason,ClusterFailureReportUrl
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_nodeid}`, `{query_containerid}`

---

### Event17 DS

_Widget purpose:_ E17s on host node 

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `Node Investigation > E17 > E17s on host node  > E17s on host node `

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (dateTime_StartTime..dateTime_EndTime) and NodeId == query_NodeId
| extend ContainerId = tostring(split(split(SurfaceName, "_")[0], "~")[0])
| union (cluster("azcore.centralus.kusto.windows.net").database("Fa").OsUltraSSDCounterTable 
| where PreciseTimeStamp between (dateTime_StartTime..dateTime_EndTime) and NodeId == query_NodeId)
| parse ArmId with * "/disks/" DiskName
| parse BlobPath with * "/" NewBlobPath "?" *
| extend BlobPath = case(isnotempty(NewBlobPath), NewBlobPath, BlobPath)
| extend StorageAccount = tostring(split(BlobPath, "/")[1])
| extend SurfaceName = case(isempty(SurfaceName), SurfaceGUID, SurfaceName)
| join kind = inner (
    cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where TIMESTAMP between (dateTime_StartTime..dateTime_EndTime) and EventId == 17 and ProviderName == 'VhdDiskPrt'
) on $left.NodeId == $right.NodeId
| join kind = leftouter ( 
    cluster("xlivesite.kusto.windows.net").database("XHealthDiskTriage").XHealth_DiskFailureXStoreTriage
| where TimeStamp between (dateTime_StartTime..dateTime_EndTime) 
) on $left.NodeId == $right.NodeId
| join kind = leftouter (
   cluster("Vmainsight.kusto.windows.net").database("vmadb").VMA
| where PreciseTimeStamp between (dateTime_StartTime..dateTime_EndTime) and RoleInstanceName !contains "_pps-vm" 
) on $left.NodeId == $right.NodeId and $left.ContainerId == $right.ContainerId
| where BlobPath != "" and Description has BlobPath
| summarize arg_max(env_time, *) by BlobPath  
| distinct  TIMESTAMP,NodeId, ContainerId,RoleInstanceName, DiskName, BlobPath, EventId1, Description,TriageCategory, TriageReason,ClusterFailureReportUrl, RCA_CSS
```

**Params:** `{dateTime_StartTime}`, `{dateTime_EndTime}`, `{query_NodeId}`

---

### RDOSE17Triage

_Widget purpose:_ RDOS E17 Triage

Cluster: `Rdosdata.kusto.windows.net` · Database: `rdosdatapath` · Type: `Table`
Source panel: `Node Investigation > E17 > RDOS E17 Triage > RDOS E17 Triage`

```kusto
GetRDOSE17Triage(queryCluster,queryFrom,queryTo)
| where NodeId == queryNode
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCluster}`, `{queryNode}`

---

### VDC_E17

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > E17 > VDC E17`

```kusto
VdcEtwEventTable
   | where NodeId == querynodeId
   | where TIMESTAMP between (queryFrom .. queryTo )
   | where ChannelName == "Microsoft-Azure-VDC/E17Monitor"
   | where EventId == 17
   | parse Message with * 'ActivityId="' ActivityId '"' *
                         'DiskId="' DiskId '"' *
                       'SliceId="' SliceId:long '"' *
                       'Message="' Msg '"' *
   | project TIMESTAMP, NodeId, ActivityId, DiskId, SliceId, Msg,  Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querynodeId}`

**Signal filters seen in KQL:** `ChannelName == "Microsoft-Azure-VDC/E17Monitor"`

---

### DiskEventsQuery

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > E17 > VhdDiskEtwEventTable`

```kusto
VhdDiskEtwEventTable
| where PreciseTimeStamp between(queryFrom..queryTo)
| where NodeId == queryNodeId
| parse Message with * "Blobpath=\"" BlobPath "\" TransportProtocol=\"" TransportProtocol "\"" *
| extend TransportProtocolName = case (TransportProtocol == "1", "RDMA", TransportProtocol == "2", "Http", TransportProtocol == "4", "Stcp", TransportProtocol == "8", "Max", "Unknown")
| project PreciseTimeStamp, Cluster, Level, ChannelName, ProviderName, EventId, EventMessage, Message, KeywordName, TaskName, BlobPath, TransportProtocol, TransportProtocolName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### DiskLeaseOperations

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > E17 > VhdumXdiskLeaseOperations`

```kusto
VhdumXdiskLeaseOperations()
| where PreciseTimeStamp between(queryFrom..queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, EventId, TimeCreated, Blobpath, RequestOpcode, LeaseDuration, CurrentLeaseGuid, ProposedLeaseGuid, LeaseName, NTStatus, ErrorCode, ErrorMessage
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

## FaultHandlingRecoveryEvents

### FaultHandlingRecoveryEvent DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Node Investigation > FaultHandlingRecoveryEvents`

```kusto
FaultHandlingRecoveryEventEtwTable 
| where PreciseTimeStamp between (query_BeginTime..query_EndTime) and NodeId == query_NodeId
| project PreciseTimeStamp, FaultDetectionTime,FaultRecoveryDurationInMinutes, RecoveryAction, RecoveryResult, Details, CmNodeWasChannelHealthStatus, FaultSignature
| order by PreciseTimeStamp desc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## Hawkeye

### WF_UR_Hawkeye

_Widget purpose:_ Hawkeye

Cluster: `hawkeyedataexplorer.westus2.kusto.windows.net` · Database: `HawkeyeLogs` · Type: `Table`
Source panel: `Node Investigation > Hawkeye > Hawkeye`

```kusto
// GetLatestHawkeyeRCAEvents
// | where RCATimestamp >= query_BeginTime and RCATimestamp < query_EndTime
// | where NodeId == query_NodeId
// | distinct NodeId, Scenario, FaultTime, RCALevel1, RCALevel2, EscalateToOrg, EscalateToTeam
// 
// GetLatestHawkeyeRCAEvents is a VERY BAD function and keeps blowing the Kusto memory budget ...
// If you are reading this then please fit is to at least take a NodeId
cluster("hawkeyedataexplorer.westus2").database("HawkeyeLogs").HawkeyeRCAEvents
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime)
| where NodeId =~ query_NodeId
| extend EscalateToOrg = iff(EscalateToTeam == "CSI", "CSI", EscalateToTeam)
| distinct NodeId, Scenario, FaultTime, RCALevel1, RCALevel2, EscalateToOrg, EscalateToTeam
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## HostAgentEventsETW

### HostAgentEventsETW

Cluster: `azcore.centralus.kusto.windows.net` · Database: `fa` · Type: `Table`
Source panel: `Node Investigation > HostAgentEventsETW`

```kusto
HostAgentEventsEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo) and NodeId == queryNodeId 
| project PreciseTimeStamp, Context, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

## HyperVAnalyticEvents

### HyperVAnalyticEvents DS

_Widget purpose:_ HyperVAnalyticEvents

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > HyperVAnalyticEvents > HyperVAnalyticEvents`

```kusto
HyperVAnalyticEvents
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId and Level < 4 and EventMessage !has "Attempt to complete a WMI operation that has already been completed"
| extend leveldescription = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, NodeId, Level, leveldescription, ProviderName, TaskName, EventMessage, Message
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## HyperVStorageStack

### HyperVStorageStackTable DS

_Widget purpose:_ HyperVStorageStack

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > HyperVStorageStack > HyperVStorageStack`

```kusto
HyperVStorageStackTable
| where NodeId =~ query_NodeId and PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where Message contains query_ContainerId or  Message contains query_vmId
| extend leveldescription = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, Level, leveldescription, ProviderName, TaskName, Message
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`, `{query_ContainerId}`, `{query_vmId}`

---

## HyperVWorker

### HyperVWorkerTable DS

_Widget purpose:_ HyperVWorker

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > HyperVWorker > HyperVWorker`

```kusto
HyperVWorkerTable
| where NodeId  =~ query_NodeId
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where Message contains query_ContainerId or Message contains query_vmId
| where Level <= 4 
| project PreciseTimeStamp, EventId,Level, ProviderName, TaskName, Message
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`, `{query_ContainerId}`, `{query_vmId}`

---

## ICMs for Host Node

### Incidents DS

_Widget purpose:_ ICMs for host node

Cluster: `icmcluster` · Database: `IcmDataWarehouse` · Type: `Table`
Source panel: `Node Investigation > ICMs for Host Node > ICMs for host node`

```kusto
let incidentCustomFields = IncidentCustomFieldEntries | where ModifiedDate between ((query_BeginTime - 1d) .. (query_EndTime + 1d)) 
| where Value contains query_NodeId | distinct IncidentId;
Incidents
| where (CreateDate between ((query_BeginTime - 1d) .. (query_EndTime + 1d)) and * contains query_NodeId) or (IncidentId in (incidentCustomFields))
| summarize arg_max(ModifiedDate, *) by IncidentId
| distinct CreateDate, ModifiedDate, IncidentId, Status, Title, OwningTeamName
| extend IncidentLink = strcat('https://portal.microsofticm.com/imp/v3/incidents/details/', IncidentId, '/home')
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## LogNodeSnapshot

### LogNodeSnapshot DS

_Widget purpose:_ Node Snapshot Table

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Node Investigation > LogNodeSnapshot > Node Snapshot Table`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp >= query_BeginTime and nodeId == query_NodeId
| project PreciseTimeStamp,nodeId,nodeState,nodeAvailabilityState,containerCount,diskConfiguration,faultInfo,rootUpdateAllocationType,cmNodeChannelAggregatedHealthStatus,isIsolated
```

**Params:** `{query_BeginTime}`, `{query_NodeId}`

---

## Low Host Memory Investigation

### OSCo

_Widget purpose:_ Low Host Memory Investigation

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Tab`
Source panel: `Node Investigation > Low Host Memory Investigation`

```kusto
OsConfigTable
| where TIMESTAMP between ((queryFrom-2d)..queryTo)
| where NodeId == queryNodeId
| where Component == "windows" and ConfigPath  has "cloudcore"
| where ConfigName == "ubr"
| extend OsUbr = toint(ConfigValue)
| extend OsFriendlyName = case (OsUbr == 1050, "RS 1.7", OsUbr == 1116, "RS 1.8", OsUbr == 2021, "RS 1.85", OsUbr == 3034, "RS 1.86", OsUbr == 1098, "AH 2020", OsUbr == 1075, "AH 2021", OsUbr == 1088, "AH 2022", OsUbr > 3034, "AH", "other" )
| summarize arg_max(PreciseTimeStamp, *) by NodeId
| project OsVersion=OsFriendlyName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Component == "windows"` · `ConfigName == "ubr"`

---

### HawkeyeRCAEvents_lowmemory

Cluster: `hawkeyedataexplorer.westus2.kusto.windows.net` · Database: `HawkeyeLogs` · Type: `Table`
Source panel: `Node Investigation > Low Host Memory Investigation > HawkeyeRCAEvents`

```kusto
HawkeyeRCAEvents
| where PreciseTimeStamp between (queryFrom .. queryTo) and Scenario == 'ContainerCreateStartRCA_Hot'
| where NodeId == queryNodeId
| parse AdditionalDetails with * "ContainerId: " ContainerId "\\\"," *
| parse AdditionalDetails with * "Host Generation ID: " HostGenId "\\\"," *
| parse AdditionalDetails with * "Host SKU: " SKU "\\\"," *
| parse AdditionalDetails with * "Container memory size: " ContainerMemorySize: long "MB" *
| parse AdditionalDetails with * "System available size: " SystemAvailableMemorySize: long "MB" *
| parse AdditionalDetails with * "VM used memory: " VmUsedMemory: long "MB" *
| parse AdditionalDetails with * "Host memory reserve: " HostMemoryReserve: long "MB" *
| extend FcShellAdditionalDetails=parse_json(AdditionalDetails).FcShellAdditionalDetails[0]
| project FaultTime, NodeId, ContainerId, HostGenId, SKU, ContainerMemorySize, SystemAvailableMemorySize, VmUsedMemory, HostMemoryReserve, RCALevel1, RCALevel2, EscalateToTeam, FcShellAdditionalDetails
| summarize arg_max(FaultTime, *), count() by RCALevel2, EscalateToTeam
| order by count_
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### kaconfig

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `Single` · Widget: `Card`
Source panel: `Node Investigation > Low Host Memory Investigation > Host overview`

```kusto
let fn_startTime = queryFrom - 1h;
let fn_endTime = queryTo + 1h;
KaHostSummary
| where TIMESTAMP between (fn_startTime .. fn_endTime)
| where NodeId == queryNodeId
| summarize arg_max(TIMESTAMP, *) by VmPartitionTotalMB
| project TIMESTAMP, Cluster, NodeId, VmPartitionTotalMB
| join kind=inner (cluster('wdgeventstore').database('hostosdeploy').nodes
| project NodeId=nodeId, HostGenId, SKU
| where NodeId == queryNodeId) on NodeId
| extend MemoryPartition = iff(VmPartitionTotalMB == 0, false, true)
| project TIMESTAMP, NodeId, MemoryPartition, HostGenId, SKU
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### OSConf

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Card`
Source panel: `Node Investigation > Low Host Memory Investigation > Host overview`

```kusto
OsConfigTable
| where TIMESTAMP between ((queryFrom-2d)..queryTo)
| where NodeId == queryNodeId
| where Component == "windows" and ConfigPath  has "cloudcore"
| where ConfigName == "ubr"
| extend OsUbr = toint(ConfigValue)
| extend OsFriendlyName = case (OsUbr == 1050, "RS 1.7", OsUbr == 1116, "RS 1.8", OsUbr == 2021, "RS 1.85", OsUbr == 3034, "RS 1.86", OsUbr == 1098, "AH 2020", OsUbr == 1075, "AH 2021", OsUbr == 1088, "AH 2022", OsUbr > 3034, "AH", "other" )
| summarize arg_max(PreciseTimeStamp, *) by NodeId
| project NodeId, OsVersion=OsFriendlyName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Component == "windows"` · `ConfigName == "ubr"`

---

### GetSnapshot

Cluster: `gandalfnodehealth.centralus.kusto.windows.net` · Database: `gandalfdev` · Type: `Single` · Widget: `Card`
Source panel: `Node Investigation > Low Host Memory Investigation > Host overview`

```kusto
let baseline_ts = toscalar(LeakDetection_AggHrmMemoryStats_Undelegated_v2 | where TIMESTAMP <= queryFrom | summarize max(TIMESTAMP));
cluster('azcore.centralus.kusto.windows.net').database('KernelAgent').HostResourceManagerResourceSnapshotEntries
| where PreciseTimeStamp <= queryFrom and PreciseTimeStamp <= queryTo and NodeId == query_NodeId
| project SnapshotId, NodeId, IdentifierLevel0, IdentifierLevel1, IdentifierLevel2, IdentifierLevel3
| join kind=inner (LeakDetection_AggHrmMemoryStats_Undelegated_v2 
| where TIMESTAMP == baseline_ts
| where MemoryPartition == True
| where HostGenId == queryHostGen
| where OSVersion == queryOSVer
) on IdentifierLevel0, IdentifierLevel1, IdentifierLevel2, IdentifierLevel3
| summarize count() by SnapshotId
| where count_ > 1
| project SnapshotId
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{queryHostGen}`, `{queryOSVer}`

---

### HostResourceManagerResourceSnapshotMetadata

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `Table`
Source panel: `Node Investigation > Low Host Memory Investigation > HostResourceManagerResourceSnapshotMetadata`

```kusto
HostResourceManagerResourceSnapshotMetadata
| where NodeId == queryNodeId
| where PreciseTimeStamp between (queryFrom-1d .. queryTo)
| project PreciseTimeStamp, SnapshotId, NodeId, ReasonLevel1, ReasonLevel2, ReasonLevel3
| summarize count(), arg_max(PreciseTimeStamp, *) by ReasonLevel1, ReasonLevel2, ReasonLevel3
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### KaHostSummary_lowmemory2

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `Table`
Source panel: `Node Investigation > Low Host Memory Investigation > KaHostSummaryMetrics`

```kusto
KaHostSummary
| where NodeId == queryNodeId
| where TIMESTAMP between ((queryFrom-2h) .. queryTo)
| extend CalculatedAvailableMB = min_of(AvailableMB_Min, CommitLimitMB - CommittedMB, ResidentAvailableMB_Min)
| project TIMESTAMP, NodeId, AvailableMB_Min, CommitLimitMB, CommittedMB, ResidentAvailableMB_Min, CalculatedAvailableMB
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### KaHost

_Widget purpose:_ LeakDetection

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `Single` · Widget: `Tab`
Source panel: `Node Investigation > Low Host Memory Investigation > LeakDetection`

```kusto
let fn_startTime = queryFrom - 1h;
let fn_endTime = queryTo + 1h;
KaHostSummary
| where TIMESTAMP between (fn_startTime .. fn_endTime)
| where NodeId == queryNodeId
| summarize arg_max(TIMESTAMP, *) by VmPartitionTotalMB
| project TIMESTAMP, Cluster, NodeId, VmPartitionTotalMB
| join kind=inner (cluster('wdgeventstore').database('hostosdeploy').nodes
| project NodeId=nodeId, HostGenId, SKU
| where NodeId == queryNodeId) on NodeId
| extend MemoryPartition = iff(VmPartitionTotalMB == 0, false, true)
| project HostGenId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### leakdetection

Cluster: `gandalfnodehealth.centralus.kusto.windows.net` · Database: `gandalfdev` · Type: `Table`
Source panel: `Node Investigation > Low Host Memory Investigation > LeakDetection`

```kusto
let baseline_ts = toscalar(LeakDetection_AggHrmMemoryStats_Undelegated_v2 | where TIMESTAMP <= queryFrom | summarize max(TIMESTAMP));
cluster('azcore.centralus.kusto.windows.net').database('KernelAgent').HostResourceManagerResourceSnapshotEntries
| where NodeId == query_NodeId and SnapshotId == querySnapshotId
| project IdentifierLevel0, IdentifierLevel1, IdentifierLevel2, IdentifierLevel3, CommitUsageMB_Undelegated=round(CommitUsageBytes_Undelegated/1024.0/1024.0, 4), CommitUsageMB_Undelegated_Avg=round(CommitUsageBytes_Undelegated_Avg/1024.0/1024.0, 4), CommitUsageMB_Undelegated_Max=round(CommitUsageBytes_Undelegated_Max/1024.0/1024.0, 4)
| join kind=inner (LeakDetection_AggHrmMemoryStats_Undelegated_v2 
| where TIMESTAMP == baseline_ts
| where MemoryPartition == True
| where HostGenId == queryHostGen
| where OSVersion == queryOSVer
) on IdentifierLevel0, IdentifierLevel1, IdentifierLevel2, IdentifierLevel3
| project IdentifierLevel0, IdentifierLevel1, IdentifierLevel2, IdentifierLevel3, NodeCount, CommitUsageMB_Undelegated_Max, CommitUsageMB_Undelegated_P50, CommitUsageMB_Undelegated_P75, Diff_Max_P50=round(CommitUsageMB_Undelegated_Max-CommitUsageMB_Undelegated_P50, 4), Diff_Max_P75=round(CommitUsageMB_Undelegated_Max-CommitUsageMB_Undelegated_P75, 4)
| where Diff_Max_P50 > 50
| where isnotempty(IdentifierLevel1) and isnotempty(IdentifierLevel2)
| where IdentifierLevel1 != 'ApService'
| extend Component=case(IdentifierLevel1 == 'Process' and IdentifierLevel2 endswith '.exe' and isnotempty(IdentifierLevel3), strcat(substring(IdentifierLevel2, 0, strlen(IdentifierLevel2)-4), '|', IdentifierLevel3)
                        , IdentifierLevel1 == 'Process' and IdentifierLevel2 endswith '.exe', substring(IdentifierLevel2, 0, strlen(IdentifierLevel2)-4)
                        , IdentifierLevel1 == 'Process', IdentifierLevel2, IdentifierLevel3)
                        , Diff_Metric=round(Diff_Max_P50+Diff_Max_P75, 4)
| where Component != 'EtwB'
| join kind=leftouter (database('gandalf').LeakDetection_TeamMapping
| project Component, IcmTeam, OwningService, OwningTeam) on Component
| project-away Component1
| order by Diff_Metric
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{queryHostGen}`, `{queryOSVer}`, `{querySnapshotId}`

**Signal filters seen in KQL:** `IdentifierLevel1 != "ApService"` · `Component != "EtwB"`

---

### GetSnapshot

Cluster: `gandalfnodehealth.centralus.kusto.windows.net` · Database: `gandalfdev` · Type: `Single` · Widget: `Table`
Source panel: `Node Investigation > Low Host Memory Investigation > LeakDetection`

```kusto
let baseline_ts = toscalar(LeakDetection_AggHrmMemoryStats_Undelegated_v2 | where TIMESTAMP <= queryFrom | summarize max(TIMESTAMP));
cluster('azcore.centralus.kusto.windows.net').database('KernelAgent').HostResourceManagerResourceSnapshotEntries
| where PreciseTimeStamp <= queryFrom and PreciseTimeStamp <= queryTo and NodeId == query_NodeId
| project SnapshotId, NodeId, IdentifierLevel0, IdentifierLevel1, IdentifierLevel2, IdentifierLevel3
| join kind=inner (LeakDetection_AggHrmMemoryStats_Undelegated_v2 
| where TIMESTAMP == baseline_ts
| where MemoryPartition == True
| where HostGenId == queryHostGen
| where OSVersion == queryOSVer
) on IdentifierLevel0, IdentifierLevel1, IdentifierLevel2, IdentifierLevel3
| summarize count() by SnapshotId
| where count_ > 1
| project SnapshotId
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{queryHostGen}`, `{queryOSVer}`

---

### kaconfig

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `Single` · Widget: `Table`
Source panel: `Node Investigation > Low Host Memory Investigation > LeakDetection`

```kusto
let fn_startTime = queryFrom - 1h;
let fn_endTime = queryTo + 1h;
KaHostSummary
| where TIMESTAMP between (fn_startTime .. fn_endTime)
| where NodeId == queryNodeId
| summarize arg_max(TIMESTAMP, *) by VmPartitionTotalMB
| project TIMESTAMP, Cluster, NodeId, VmPartitionTotalMB
| join kind=inner (cluster('wdgeventstore').database('hostosdeploy').nodes
| project NodeId=nodeId, HostGenId, SKU
| where NodeId == queryNodeId) on NodeId
| extend MemoryPartition = iff(VmPartitionTotalMB == 0, false, true)
| project TIMESTAMP, NodeId, MemoryPartition, HostGenId, SKU
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

## NodeEvents

### TMMgmtNodeEventsEtwTable_UnexpectedRestart2 DS

_Widget purpose:_ Node Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Node Investigation > NodeEvents > Node Events`

```kusto
TMMgmtNodeEventsEtwTable
| where TIMESTAMP >= query_BeginTime and TIMESTAMP <= query_EndTime 
| where NodeId =~ query_NodeId and Message !contains '[AuditEvent]'
| project  PreciseTimeStamp, Message
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## NodeFaultEvents

### NodeFaultEvents DS

_Widget purpose:_ Node Fault Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Node Investigation > NodeFaultEvents > Node Fault Events`

```kusto
TMMgmtNodeFaultEtwTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where BladeID == query_NodeId
|project PreciseTimeStamp, Tenant, NodeId=BladeID, FaultCode, Reason
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## NodeServiceEvents

### NodeServiceEventEtwTable DS

_Widget purpose:_ Node Service Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > NodeServiceEvents > Node Service Events`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp >= query_BeginTime and  PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## NodeServiceOperation

### NodeServiceOperationEtwTable DS

_Widget purpose:_ Node Service Operations

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > NodeServiceOperation > Node Service Operations`

```kusto
NodeServiceOperationEtwTable
| where PreciseTimeStamp >= query_BeginTime
| where PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId
| project PreciseTimeStamp, OperationName, Identifier, Result, ResultCode, ResultCodeHex = tohex(ResultCode), RequestTime, CompleteTime
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## NodeStateChanges

### TMMgmtNodeStateChangedEtwTable DS

_Widget purpose:_ Node State Changes

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Node Investigation > NodeStateChanges > Node State Changes`

```kusto
TMMgmtNodeStateChangedEtwTable 
| where  BladeID =~ query_NodeId
| where PreciseTimeStamp >= query_BeginTime
| where PreciseTimeStamp <= query_EndTime 
| project PreciseTimeStamp, BladeID, OldState, NewState
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## NodeTraceEvents

### TMMgmtNodeTraceEtwTable DS

_Widget purpose:_ TMMgmtNodeTraceEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Node Investigation > NodeTraceEvents > TMMgmtNodeTraceEtwTable`

```kusto
TMMgmtNodeTraceEtwTable
| where TIMESTAMP >= startTime and TIMESTAMP <= endTime
| where BladeID == nodeId
| where Context != "Information"
| project TIMESTAMP, Tenant, Context,BladeID, Message,SecondaryLevel
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `Context != "Information"`

---

## NVME troubleshooting

### DirectAccessEvent

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > NVME troubleshooting > DirectAccessEvent`

```kusto
DirectAccessEvent
| where NodeId == queryNodeId
| where PreciseTimeStamp between (queryFrom..queryTo) and ContainerId == queryContainerId
| project PreciseTimeStamp, Cluster, NodeId, ContainerId, ResultCode, Operation, Stage, DirectAccessType, LocationPath, SerialNumber
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

---

### HyperVEventsV2

Cluster: `azcore.centralus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `Node Investigation > NVME troubleshooting > HyperVEventsV2`

```kusto
HyperVEventsV2
(fn_nodeId=['queryNodeId'], fn_containerId=['queryContainerId'], fn_startTime = ['queryFrom'], fn_endTime=['queryTo'])
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

---

### HyperVStorageStackErrors

Cluster: `azcore.centralus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `Node Investigation > NVME troubleshooting > HyperVStorageStackErrors`

```kusto
HyperVStorageStackErrors(queryNodeId, queryFrom, queryTo)
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, DeviceId, ProviderName, TaskName, Message, Level
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### HyperVStorageStackTable_NVME

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > NVME troubleshooting > HyperVStorageStackTable`

```kusto
HyperVStorageStackTable
| where ProviderName in ("Microsoft.Windows.HyperV.Storage.NvmeDirect", "Microsoft.Windows.HyperV.NvmeDirect.Telemetry", "Microsoft.Windows.HyperV.Storage.NvmeDirect2", "Microsoft.Windows.HyperV.Storage.NvmeDirect2.Activity")
| where NodeId == queryNodeId
| where PreciseTimeStamp between(queryFrom..queryTo)
| where Level < 3
| project PreciseTimeStamp, Pid, Tid, ProviderName, EventId, TaskName, Message, EventMessage, Level, Opcode
| order by PreciseTimeStamp desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### HyperVStorageStackTable_filter_controller

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > NVME troubleshooting > HyperVStorageStackTable Controller`

```kusto
HyperVStorageStackTable
| where NodeId == queryNodeId
| where PreciseTimeStamp between (queryFrom..queryTo) and Message contains "Controller"
| project PreciseTimeStamp, NodeId, TaskName,Message, EventMessage
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### WindowseEventsNVME

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > NVME troubleshooting > NVME events on WindowsEventsTable`

```kusto
WindowsEventTable
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where NodeId =~ queryNodeId
| where EventId in (6002,6003)
| distinct TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

## OsAnalyzerTable

### OsAnalyzer Host Node Analysis DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > OsAnalyzerTable`

```kusto
OsAnalyzerTable
| where PreciseTimeStamp between (query_startTime..query_endTime) and NodeId == query_nodeId
| project PreciseTimeStamp, NodeId,EventId, ErrorCode, AnalysisRCA, AnalysisText, ProviderName, VhdPath
```

**Params:** `{query_startTime}`, `{query_endTime}`, `{query_nodeId}`

---

## OsLoggerTable

### OsLogger DS

_Widget purpose:_ OsLoggerTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > OsLoggerTable > OsLoggerTable`

```kusto
OsLoggerTable
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime) and NodeId == query_NodeId
| extend level = case(LogErrorLevel == "Error", "error", LogErrorLevel == "Warning", "warning", LogErrorLevel == "Critical", "fatal", "info")
| project PreciseTimeStamp = tostring(PreciseTimeStamp), level, ComponentName, SubComponentName, FileName, FunctionName, LineNumber, ResultCode, ErrorDetails 
| sort by PreciseTimeStamp asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## RdAgent Tables

### HostAgentEventsEtwTable DS

_Widget purpose:_ HostAgentEventsEtw

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > RdAgent Tables > Host Agent Events > HostAgentEventsEtw`

```kusto
HostAgentEventsEtwTable()
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime)
| where NodeId == query_NodeId
| project PreciseTimeStamp, ProviderName, OpcodeName, Pid, TaskName, Message, Context, AgentPackage
| order by PreciseTimeStamp asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

### Azure Host VMAL Container Operations DS

_Widget purpose:_ VmServiceContainerOperations

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > RdAgent Tables > VMAL Container Operations > VmServiceContainerOperations`

```kusto
VmServiceContainerOperations
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, ContainerId, Operation, Stage,  ContainerSize, ResultCode, DurationMillis
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host VmServiceLeaseManagementOperation DS

_Widget purpose:_ VmServiceLeaseManagementOperation

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > RdAgent Tables > VMAL Disk Lease Operations > VmServiceLeaseManagementOperation`

```kusto
VmServiceLeaseManagementOperation
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, BlobPath, Operation, ExistingLease, NewLease, ResultCode, LocalFileName
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host VMAL Disk Service Table DS

_Widget purpose:_ VmServiceVirtualDiskOperations

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > RdAgent Tables > VMAL Disk Operations > VmServiceVirtualDiskOperations`

```kusto
VmServiceVirtualDiskOperations
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, ContainerId, Operation, Stage,  DiskType, DiskFullPath, DiskBackingStore, ResultCode, DurationMillis, DiskLocation
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host VmServiceEventsEtwTable DS

_Widget purpose:_ VmServiceEventsEtwTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > RdAgent Tables > VMAL Service Events > VmServiceEventsEtwTable`

```kusto
VmServiceEventsEtwTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, Message, AgentPackage, ContainerId, Context
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host VMAL Service Init DS

_Widget purpose:_ VmServiceInitialization

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > RdAgent Tables > VMAL Service Init > VmServiceInitialization`

```kusto
VmServiceInitialization
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, Operation, Stage, ResultCode, ServiceMode, VhdProvider, SerialNumber, DiskPreparation
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## SLA Table

### TMMgmtSlaMeasurementEventEtwTable_UnexpectedRestart DS

_Widget purpose:_ SLA Table for Node

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Node Investigation > SLA Table > SLA Table for Node`

```kusto
TMMgmtSlaMeasurementEventEtwTable
| where NodeID == query_NodeId 
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime 
| project PreciseTimeStamp, TenantName, RoleInstanceName, Context, EntityState, ContainerID, NodeID, Detail0, Region
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## VMA

### VMA4 DS

_Widget purpose:_ VM Availability analysis

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `Node Investigation > VMA > VM Availability analysis`

```kusto
VMA
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId and RCAEngineCategory !contains "Customer" 
| distinct  PreciseTimeStamp,Cluster,NodeId,ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2, RCA_CSS
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## WindowsEvents

### WF_UR_WindowsEvents

_Widget purpose:_ Windows Events from host node

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Node Investigation > WindowsEvents > Windows Events from host node`

```kusto
WindowsEventTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId
| where EventId !=1008 and EventId !=1023 and EventId !=3095 and EventId !=15 and EventId !=0 and EventId !=31
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| order by TimeCreated asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---
