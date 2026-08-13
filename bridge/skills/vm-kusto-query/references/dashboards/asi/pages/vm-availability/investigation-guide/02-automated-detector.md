# Automated Detector

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Automated Detector** (59 queries).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## (no subgroup)

### IssueDetector_NetworkIssues

_Widget purpose:_ Automated Detector

Cluster: `icmcluster` · Database: `IcmDataWarehouse` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
let devicename = toscalar(cluster('azphynet').database('azdhmds').Servers
| where NodeId =~ queryNodeId
| project DeviceName);
let torDeviceName = toscalar(cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice == devicename
| project EndDevice);
let incidents = IncidentsSnapshotV2
| where ImpactStartDate between ((queryFrom-12h) .. (queryTo+12h)) or MitigateDate  between ((queryFrom-12h) .. (queryTo+12h))
| where Summary contains torDeviceName or Title contains torDeviceName 
  or Summary contains queryNodeId or Title contains queryNodeId 
  or Summary contains queryContainerId or Title contains queryContainerId
| project IncidentId, IncidentSeverity = Severity, Status, Title
| extend Description = strcat("Title: ", Title)
| extend Title  = strcat("IncidentId: ", IncidentId, ", Seveirty: ", IncidentSeverity, ", Status: ", Status)
| extend Severity  = "Warning"
| extend Id = tostring(IncidentId)
| extend Uri = strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId)
| extend UriText = Uri
| order by IncidentId asc
| take 100;
let problemVNetAgent = cluster("storageclient.eastus.kusto.windows.net").database("AutopilotDeployment").ServiceManagerInstrumentation
| where PreciseTimeStamp between ((queryFrom-1h).. (queryTo+1h)) 
| where NodeId == queryNodeId
| where ServiceName contains "VNetAgent" and ServiceVersion =~ "VNetAgent_2_3_useast_6_4_1_690"
| distinct ServiceName, ServiceVersion
| extend Severity = "Error"
| extend Title = "VM deployment failure due to the problematic version VNetAgent_2_3_useast_6_4_1_690 on the host node"
| extend Description = "An Emerging issue is reported for this VNetAgent version. Please refer to the primary incident for the latest Update https://portal.microsofticm.com/imp/v3/incidents/details/404142883/home"
| extend Uri = "https://microsoft.sharepoint.com/teams/AzureSupportability/_layouts/OneNote.aspx?id=%2Fteams%2FAzureSupportability%2FShared%20Documents%2FAzure%20EEE%2FAzure%20EEE&wd=target%28EMERGING%20REPORTED%20ISSUES.one%7C9BB67A72-351E-4F85-9379-CFB8CDC0A975%2FOSPTO%20-%20Failed%20to%20obtain%20DHCP%20lease%20due%20to%20VNET%7CA65D57AD-0034-4EAE-806C-4BC6A9BF7182%2F%29"
| extend UriText = "TSG for this Emerging Issue";
let socID = toscalar(cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').GetSocOrNodeFromResourceId(queryNodeId));
let portIDs = materialize(cluster('aznwsdn').database('aznwmds').ContainerInformationEvent
| where socID != "00000000-0000-0000-0000-000000000000"
| where ContainerId =~ queryContainerId
| where PreciseTimeStamp >= queryFrom - 96h and PreciseTimeStamp <= queryTo + 24h
| distinct PortId);
let SocCreatePortError = cluster('azcore.centralus.kusto.windows.net').database('OvlProd').LinuxOverlakeSystemd()
| where socID != "00000000-0000-0000-0000-000000000000"
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId =~ queryNodeId or NodeId =~ socID
| where SYSLOG_IDENTIFIER == "vnetagent"
| where PRIORITY == "4" 
| where MESSAGE has_any (portIDs) 
| where MESSAGE matches regex "Create port failed for port External_\\d* with error 0x2"
| summarize arg_max(PreciseTimeStamp, MESSAGE)
| where isnotempty(PreciseTimeStamp)
| extend Severity = "Error"
| extend Title = "VM deployment failure because of create port 0x2 error on SoC"
| extend Description = "An Emerging issue is reported for this create port 0x2 failure. Please refer to the primary incident for the latest Update: https://portal.microsofticm.com/imp/v3/incidents/details/404142883/home"
| extend Uri = "https://microsoft.sharepoint.com/teams/AzureSupportability/_layouts/OneNote.aspx?id=%2Fteams%2FAzureSupportability%2FShared%20Documents%2FAzure%20EEE%2FAzure%20EEE&wd=target%28EMERGING%20REPORTED%20ISSUES.one%7C9BB67A72-351E-4F85-9379-CFB8CDC0A975%2FOSPTO%20-%20VNetAgent%20Failed%20to%20create%20port%200x2%20error%20on%7CE806B004-9821-468A-B397-099FBB7F986D%2F%29"
| extend UriText = "TSG for this Emerging Issue";
union incidents, problemVNetAgent, SocCreatePortError
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`, `{queryRoleInstanceName}`, `{queryTenantName}`, `{querySubId}`

**Signal filters seen in KQL:** `ServiceName contains "VNetAgent"` · `socID != "00000000-0000-0000-0000-000000000000"` · `SYSLOG_IDENTIFIER == "vnetagent"` · `PRIORITY == "4"`

---

### IssueDetector_AzSMServiceHealing

_Widget purpose:_ Automated Detector

Cluster: `accp.centralus` · Database: `AZSM` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName =~ queryTenantName
| where triggerObjectId == queryContainerId
| order by PreciseTimeStamp asc
| summarize StartTime = min(PreciseTimeStamp), arg_max(PreciseTimeStamp, triggerType, faultCode, faultReason, faultCode) by triggerId
| join kind=leftouter (AzSMServiceHealingStepResultEvents
    | where PreciseTimeStamp between(queryFrom .. queryTo)
    | where tenantName == queryTenantName
    | where targetContainerId <> '00000000-0000-0000-0000-000000000000'
    | summarize EndTime = max(PreciseTimeStamp), arg_max(PreciseTimeStamp, result) by triggerId, failureReason, targetContainerId 
) on triggerId
| project StartTime, EndTime, triggerType, triggerId, faultReason, targetContainerId, result
| extend Description = strcat("VM was service healed due to ", triggerType)
| extend Severity = 'critical'
//| extend Health = iif (result != "Succeeded", "Error", "Degraded")
//| extend Content = triggerType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryContainerId}`

**Signal filters seen in KQL:** `targetContainerId <> "00000000-0000-0000-0000-000000000000"`

---

### IssueDetector_TooManyUnhealthyNode

_Widget purpose:_ Automated Detector

Cluster: `icmcluster` · Database: `IcMDataWarehouse` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster('icmcluster.kusto.windows.net').database('IcMDataWarehouse').Incidents
| where CreateDate between (queryFrom .. queryTo)
| where (Title contains "Too many Unhealthy nodes" and Title contains queryCluster)
| order by ModifiedDate asc
| extend flag = case(IncidentId <> prev(IncidentId), "changed", "")
| where flag <> ""
| extend Severity = 'Error', Description = strcat("Too many unhealthy nodes in cluster", queryCluster , " were detected by monitoring tool.")
| project IncidentId, StartTime = CreateDate, Severity, Title, InitialOwningTeam = OwningTeamName, IncidentType, SupportTicketId, SubscriptionId, Description
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCluster}`

---

### IssueDetector_EI_StopDestroy Fails with STORVSP_VspDeviceCreate*

_Widget purpose:_ Automated Detector

Cluster: `azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. 2h)
| where nodeIdentity == NodeId and crashMode == "km"
| project crashMode, crashProcessFullPath, process, dumpUid, nodeIdentity
| join kind=leftouter(
CustomerDumpAnalysisResultV2
| where PreciseTimeStamp between (queryFrom .. 2h)
) on dumpUid
| where bucketString == "LKD_MANUALLY_INITIATED_CRASHLKD_MANUALLY_INITIATED_CRASH_STORVSP_VspDeviceCreate_ParserOverride_Avhdparser"
| distinct crashTime, crashMode, bucketString, followup, dumpUid
| take 1
|extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",roleInstanceName,"&query_ContainerId=",containerId,"&query_TenantName=",tenantName,"&query_NodeId=",NodeId,"&query_vmId=",virtualMachineUniqueId,"&query_cluster=",Tenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%221fc4dc43-dc6f-4db3-b674-419d141b55a5%22%7D%7D"),"'>Emerging issue StopDestroy Fails with STORVSP_VspDeviceCreate_ParserOverride_Avhdparser</a>")
|extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{NodeId}`, `{querySubscription}`, `{containerId}`, `{roleInstanceName}`, `{tenantName}`, `{Tenant}`, `{virtualMachineUniqueId}`

**Signal filters seen in KQL:** `bucketString == "LKD_MANUALLY_INITIATED_CRASHLKD_MANUALLY_INITIATED_CRASH_STORVSP_VspDeviceCreate_ParserOverride_Avhdparser"`

---

### IssueDetector_SoC_Crash

_Widget purpose:_ Automated Detector

Cluster: `azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
let _NodeId = queryNodeId;
let _startTime = queryStart;
let _endTime = queryEnd;
let socID = toscalar(cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').GetSocOrNodeFromResourceId(_NodeId));
let SocName = toscalar(
    cluster('Azuredcm').database('AzureDCMDb').dcmInventoryMachines
    | where AzureNodeId =~ socID
    | project MachineName);
let socdumps=cluster('azurewatsoncustomer').database('AzureWatsonCustomer').CustomerCrashOccurredV2
    | extend CrashTimeDt = PreciseTimeStamp
    | where PreciseTimeStamp >= _startTime and PreciseTimeStamp <= _endTime
    | where apMachine =~ SocName;
socdumps
| where socID != "00000000-0000-0000-0000-000000000000" and apMachine endswith "SOC"
| project CrashTimeDt, process
| take 1
| extend Severity = "Critical"
| extend Title = strcat("Crash found: ",process)
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/VM%20Availability?containerId=",queryContainerId,"&nodeId=",queryNodeId,"&Tenant=",queryCluster,"&tenantName=",queryTenantName,"&virtualMachineUniqueId=",queryVmId,"&roleInstanceName=",queryRoleInstanceName,"&globalFrom=",queryStart,"&globalTo=",queryEnd,"&__userData=%7B%22nodeData%22%3A%7B%22d30a6308-e96a-4b4f-8788-0848ca12e329%22%3A%223d9520f4-d3e4-4bf1-aaea-dd1f44714c31%22%2C%22e5e26ca1-7248-4667-8318-673024d48eee%22%3A%22a2bafed4-b13d-4719-b6d0-c58ddea78a39%22%7D%7D"),"'>Check VM General Availability Page-Network-SOC for details</a>")
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryNodeId}`, `{queryContainerId}`, `{queryCluster}`, `{queryRoleInstanceName}`, `{queryTenantName}`, `{queryVmId}`

**Signal filters seen in KQL:** `socID != "00000000-0000-0000-0000-000000000000"`

---

### IssueDetector_EI_RHSendsIncorrectVMAvailableStateRepeatedly

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
let latestcontainertime = toscalar( cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogContainerSnapshot| where virtualMachineUniqueId =~ VMId | summarize max(todatetime(creationTime)));
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogContainerSnapshot
| where virtualMachineUniqueId =~ VMId
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp) by roleInstanceName, creationTime, virtualMachineUniqueId, containerId
| project VMName=roleInstanceName, VirtualMachineUniqueId=virtualMachineUniqueId, ContainerIdLCS=containerId,
    ContainerCreationTime=todatetime(creationTime), StartTimeStamp=min_PreciseTimeStamp, EndTimeStamp=max_PreciseTimeStamp
| where ContainerCreationTime < queryFrom and ContainerCreationTime == latestcontainertime
| join kind = inner
(cluster('aplat.westcentralus.kusto.windows.net').database('APlat').KyberContainerHealthMetricData
| where PreciseTimeStamp between (queryFrom ..2h)) on $left.VirtualMachineUniqueId == $right.VirtualMachineUniqueId
| where  ContainerId != ContainerIdLCS
| distinct  PreciseTimeStamp, ContainerId,IcHeartbeat,PowerState,HyperVHandshake,HealthUpdateTimeStamp,ApiVersion
|extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",roleInstanceName,"&query_ContainerId=",containerId,"&query_TenantName=",tenantName,"&query_NodeId=",NodeId,"&query_vmId=",VMId,"&query_cluster=",Tenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%223172ad68-f252-4429-beeb-e32a3cc70057%22%7D%7D"),"'>Emerging issue Resource Health Sends Incorrect VM Availability state repeatedly</a>")
|extend Severity = "critical"
| take 1;
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').KyberVmAvailabilityMetricEmission
| where PreciseTimeStamp between (queryFrom ..2h)
| where VirtualMachineUniqueId == VMId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{NodeId}`, `{querySubscription}`, `{Tenant}`, `{containerId}`, `{roleInstanceName}`, `{tenantName}`, `{VMId}`

---

### IssueDetector_EI_DppPluginOrPfDatapathServiceRequired

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where NodeId =~ query_NodeId and Message has "ContainerWorkflow is blocked, reason:[DppPluginOrPfDatapathServiceRequired]"
| project PreciseTimeStamp, Message
| take 1
|extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22d4b82ec8-93ea-4ab9-b287-1f0749ba52b8%22%7D%7D"),"'>Emerging issue ContainerWorkflow is blocked due to DppPluginOrPfDatapathServiceRequired</a>")
|extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_CreateContainer_fails_with_0x80070002_L-Series

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").IfxOperationV2v1EtwTable
| where TIMESTAMP  between (queryFrom .. 2h) and NodeId =~ queryNodeId and OperationName == "RdosUtils::StorageManagement::WriteRandomDataToDisk" and ResultSignature == "0x80070002"
| join hint.strategy = broadcast 
(cluster("azcore.centralus").database("Fc").TMMgmtNodeEventsEtwTable
| where TIMESTAMP between (queryFrom .. 2h) and Message has queryContainerId and Message has "0x80070002") on $left.NodeId == $right.NodeId
| project Cluster,TIMESTAMP, NodeId, OperationName, ResultType, ResultSignature, Region
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",roleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",tenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",virtualMachineUniqueId,"&query_cluster=",Tenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%228ff3efc9-6135-4996-afc0-4dc7694d4b52%22%7D%7D"),"'>Emerging issue CreateContainer fails with 0x80070002 on L-Series VMs</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{roleInstanceName}`, `{queryContainerId}`, `{queryNodeId}`, `{tenantName}`, `{virtualMachineUniqueId}`, `{Tenant}`

---

### IssueDetector_EI_CreateContainer_failed_with_0xc3510153

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster('Azcore.centralus').database('Fa').VmServiceEventsEtwTable
| where PreciseTimeStamp between (startTime .. 2h)
| where NodeId =~ nodeId
| where Context == "Repreparation" and Message has 'VmAbstractionLayer::Vm::PerformPreCreateOperations' and Message has '0xc3510153'
| project-rename  VMServiceMessage = Message
| join hint.strategy = broadcast 
(cluster("azcore.centralus").database("Fc").TMMgmtNodeEventsEtwTable  
| where TIMESTAMP between (startTime .. 2h) and Message has 'CreateContainer' and Message has '0xC3510153') on $left.NodeId == $right.NodeId
| project PreciseTimeStamp, NodeId, ContainerId, VMServiceMessage, Message
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",roleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",tenantName,"&query_NodeId=",nodeId,"&query_vmId=",virtualMachineUniqueId,"&query_cluster=",Tenant,"&globalFrom=",startTime,"&globalTo=",endTime,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2249f3a76e-1b91-4ec9-8e45-33e9c4e779fa%22%7D%7D"),"'>Emerging issue CreateContainer failed with 0xc3510153</a>")
| extend Severity = "critical"
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{querySubscription}`, `{roleInstanceName}`, `{queryContainerId}`, `{tenantName}`, `{virtualMachineUniqueId}`, `{Tenant}`

**Signal filters seen in KQL:** `Context == "Repreparation"`

---

### IssueDetector_EI_VM reboot when trying to detach disks 

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").VmServiceVirtualDiskOperations
| where PreciseTimeStamp between (queryFrom .. 2h) and NodeId =~ nodeId and Operation == "DestroyVirtualDisk" and ResultCode in ("0x80070961","0x8abc0303") and ContainerId == containerId
| join kind=inner (cluster("azcore.centralus.kusto.windows.net").database("Fc").TMMgmtNodeEventsEtwTable
| where TIMESTAMP between (queryFrom .. 2h) 
| where NodeId =~ nodeId and Message has containerId and Message has "since data disks change") on $left.NodeId == $right.NodeId
| project PreciseTimeStamp, ContainerId, Operation, Stage,  DiskType, DiskFullPath, DiskBackingStore, ResultCode, DurationMillis, DiskLocation, Message
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",roleInstanceName,"&query_ContainerId=",containerId,"&query_TenantName=",tenantName,"&query_NodeId=",nodeId,"&query_vmId=",virtualMachineUniqueId,"&query_cluster=",Tenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%22380baabc-4c6c-44ba-8c6a-225be0dac693%22%3A%22945974d7-5b3d-4c30-8ed8-6955d5db169d%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22fd7523ba-86c5-4c12-8452-27d809811d9e%22%7D%7D"),"'>Emerging issue VM reboot when trying to detach disks (UpdateContainer failure 0x80070961)</a>")
| extend Severity = "critical"
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmName}`, `{virtualMachineID}`, `{containerId}`, `{nodeId}`, `{querySubscription}`, `{subId}`, `{roleInstanceName}`, `{tenantName}`, `{virtualMachineUniqueId}`, `{Tenant}`

---

### IssueDetector_EI_EQ stuck_on_EQn_0x4

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where NodeId =~ query_NodeId
| where EventId == 20 and ProviderName == "mlnx5"
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%227cd435d3-8b55-432c-a24b-8d95455f2dcd%22%7D%7D"),"'>Emerging issue EQ stuck on EQn 0x4</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_AirDiskBlip_BlobCache_Write_during_Congestion

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
HyperVStorageStackTable 
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where Message has_any (querycontainerId) and EventId == 9 and NodeId == query_NodeId
| extend HyperVTimestamp = PreciseTimeStamp
| project HyperVTimestamp, Level, EventId, TaskName, EventMessage, Message, NodeId
| join kind=inner(
OsBlobCacheInternalCounterTable
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where (DeltaBSWaitForOldData > 0 or DeltaBSPausedWrites > 0 or DeltaBSPausedWritesTimeout > 0)
| extend DriverTimestamp = PreciseTimeStamp)
on $left.NodeId == $right.NodeId
| distinct DriverTimestamp, DeltaFUnmapLinkReferenced, DeltaBSWaitForOldData, DeltaBSWaitForWriteLimit, BSPausedWrites, DeltaBSPausedWrites, DeltaBSPausedWritesTimeout, BSPausedWritesTimeout, DeltaBSLargeReadCount,  EventId, TaskName, HyperVTimestamp, EventMessage, NodeId
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%222032b226-fc19-46b5-950b-ad67300490dc%22%7D%7D"),"'>Emerging issue AirDiskBlip BlobCache Write during Congestion</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{queryroleInstanceName}`, `{querySubscription}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_NV6_v5_VMs_Fail_to_Start_due_to_Low_Memory

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where nodeId =~ query_NodeId and nodeAvailabilityState == "Unallocatable" and faultInfo has "0x80078014"
| project-rename node_faultInfo = faultInfo
| join kind=inner (LogContainerSnapshot
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where containerType has "A10_v5" and containerId == querycontainerId) on $left.nodeId == $right.nodeId
| join kind=inner (LogContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom .. 2h)  
| where faultInfo has "Operation 'StartContainer' is configured to surface a fault after 4 successive failures" and faultInfo has "0x80078014"
| project-rename container_faultInfo = faultInfo
) on $left.containerId == $right.containerId
| project PreciseTimeStamp,RoleInstance,nodeAvailabilityState,nodeState,containerCount,diskConfiguration,node_faultInfo,containerId,containerType, container_faultInfo
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2267f84bfd-16e5-4330-9da6-be550f6f01a9%22%2C%22d0b9dbe3-f20b-4b34-b861-30b1b43cbd34%22%3A%22ac441037-231d-4a41-a3ee-7cbfb7b0b236%22%7D%7D"),"'>Emerging issue NV6 v5 VMs Fail to Start due to Low Memory</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `containerType has "A10_v5"` · `faultInfo has "Operation 'StartContainer' is configured to surface a fault after 4 successive failures"`

---

### IssueDetector_EI_CRUD operationFailuresDueToContainerWorkflow*

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp between(queryFrom .. 2h)
| where NodeId == NodeID
| where Message has "Container workflow blocked: MissingStorageConfigurationsWillbe"
| project PreciseTimeStamp,NodeId, Message
| sort by PreciseTimeStamp asc
| take 1
|extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",roleInstanceName,"&query_ContainerId=",containerId,"&query_TenantName=",tenantName,"&query_NodeId=",NodeID,"&query_vmId=",virtualMachineUniqueId,"&query_cluster=",Tenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%222d07723c-bcfe-41a3-befb-ae2b63301622%22%7D%7D"),"'>Emerging issue CRUD operation failures due to container workflow blocker 'MissingStorageConfigurationsWillbe'</a>")
|extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{Tenant}`, `{containerId}`, `{NodeID}`, `{roleInstanceName}`, `{tenantName}`, `{virtualMachineUniqueId}`

**Signal filters seen in KQL:** `Message has "Container workflow blocked: MissingStorageConfigurationsWillbe"`

---

### IssueDetector_EI_Resource_Health_Unavailable_for_Linux_6.2Kernel

_Widget purpose:_ Automated Detector

Cluster: `Vmainsight` · Database: `CAD` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster('Vmainsight').database('CAD').VMA_Daily
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where ContainerId == querycontainerId
| where GA_GuestOSVersion has "6.2.0" and GA_GuestOSVersion has "Linux" and StartTime >= ago(30d)
| join kind=inner
(cluster('Azcore.centralus').database('Fa').VmHealthRawStateEtwTable
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where  HasHyperVHandshakeCompleted == "false") on $left.ContainerId == $right.ContainerId
| summarize max(PreciseTimeStamp) by GA_GuestOSVersion, ContainerId, HasHyperVHandshakeCompleted
| order by max_PreciseTimeStamp desc 
| take 5
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%22d0b9dbe3-f20b-4b34-b861-30b1b43cbd34%22%3A%222cb0de43-c217-4b92-a896-fdfd03eaf8b6%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%220c399ad2-7a86-4fbd-9457-8a22f743d60e%22%7D%7D"),"'>Emerging issue Resource Health Unavailable for Linux 6.2 Kernel</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `GA_GuestOSVersion has "6.2.0"` · `HasHyperVHandshakeCompleted == "false"`

---

### IssueDetector_EI_High_Flush_latencies_due_to_driver_issue

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

> ⚠️ Verbose machine-generated KQL (75 KB, e.g. histogram aggregations expanded across many bins). Full body extracted to [`02-automated-detector--issuedetector-ei-high-flush-latencies-due-to-driver-issue.kql`](02-automated-detector--issuedetector-ei-high-flush-latencies-due-to-driver-issue.kql); the opening lines are shown below for context. Nothing is truncated — the full query is preserved verbatim in the `.kql` file.

```kusto
let blobs = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (queryFrom .. 2h) and NodeId == query_NodeId and (SurfaceName has querycontainerId or SurfaceName has queryvirtualMachineUniqueId)
| parse BlobPath with * "/" BlobPath "?" *
| distinct BlobPath;
VhdDiskEtwEventTable
| where PreciseTimeStamp between (queryFrom .. 2h)
| where NodeId == query_NodeId and EventId == 13
| project PreciseTimeStamp, EventMessage, NodeId
| parse EventMessage with * 'blobpath:/' BlobPath '.' * 'TransportType:' TransportType '.' * 'RequestOpCode:' RequestOpCode '.' * 'RequestElapsedTimeMs:' RequestElapsedTimeMs '.' * "ResubmitCount:" ResubmitCount "." *
| where BlobPath in (blobs)
| extend RequestElapsedTimeMs = tolong(RequestElapsedTimeMs)
| extend IoType = iff(RequestOpCode == 6, "Read", "Write")
| extend Transport = case(TransportType == 1, "RDMA", TransportType == 2, "HTTP", "STCP")
| summarize count(), MaxRequestElapsedTimeMs = max(RequestElapsedTimeMs), AvgRequestElapsedTimeMs = round(avg(RequestElapsedTimeMs), 2), 
            MinRequestElapsedTimeMs = min(RequestElapsedTimeMs),
            MaxResubmitCount = max(tolong(ResubmitCount)), AvgResubmitCount = round(avg(tolong(ResubmitCount)), 2)
            by bin(PreciseTimeStamp, 1m), IoType_Transport = strcat(IoType,'-',Transport), BlobPath, NodeId
| sort by PreciseTimeStamp asc
| join kind=rightanti (
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (queryFrom..queryTo) and NodeId == query_NodeId and SurfaceName has querycontainerId) on $left.NodeId==$right.NodeId
| where HistogramTypeEnum != 4 // Removing Flush, since Flush and Flush with throttling are the same.
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
    | union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (queryFrom..queryTo) and SurfaceName contains querycontainerId)
| extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (queryFrom..queryTo) and ContainerId == querycontainerId
    | extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    | extend IOSizeBucket = case(IOSizeBucket in (0, 1) and TelemetryVersion >= 2, 0, // 0 - 8k
                                IOSizeBucket == 2 and TelemetryVersion >= 2, 1, // 8 - 64k
                                IOSizeBucket == 3 and TelemetryVersion >= 2, 2, // 64+
                                IOSizeBucket == 4 and TelemetryVersion >= 2, 3, // all IO Sizes
                                IOSizeBucket)
    | where SurfaceName contains querycontainerId)
| extend HistogramTypeEnum = case(HistogramTypeDesc contains "Ultra", strcat("Ultra_", HistogramTypeEnum), tostring(HistogramTypeEnum))
| where IOSizeBucket != 3
| where isempty(blobPath) or BlobPath == blobPath
| summarize hint.strategy=shuffle
                Bin_Count = sum(Bin_Count),
                Bin_01 = sum(Bin_01), Bin_02 = sum(Bin_02), Bin_03 = sum(Bin_03), Bin_04 = sum(Bin_04), Bin_05 = sum(Bin_05), Bin_06 = sum(Bin_06), Bin_07 = sum(Bin_07), Bin_08 = sum(Bin_08),
                Bin_09 = sum(Bin_09), Bin_10 = sum(Bin_10), Bin_11 = sum(Bin_11), Bin_12 = sum(Bin_12), Bin_13 = sum(Bin_13), Bin_14 = sum(Bin_14), Bin_15 = sum(Bin_15), Bin_16 = sum(Bin_16),
                Bin_17 = sum(Bin_17), Bin_18 = sum(Bin_18), Bin_19 = sum(Bin_19), Bin_20 = sum(Bin_20), Bin_21 = sum(Bin_21), Bin_22 = sum(Bin_22), Bin_23 = sum(Bin_23), Bin_24 = sum(Bin_24),
                Bin_25 = sum(Bin_25), Bin_26 = sum(Bin_26), Bin_27 = sum(Bin_27), Bin_28 = sum(Bin_28), Bin_29 = sum(Bin_29), Bin_30 = sum(Bin_30), Bin_31 = sum(Bin_31), Bin_32 = sum(Bin_32),
                Bin_33 = sum(Bin_33), Bin_34 = sum(Bin_34), Bin_35 = sum(Bin_35), Bin_36 = sum(Bin_36), Bin_37 = sum(Bin_37), Bin_38 = sum(Bin_38), Bin_39 = sum(Bin_39), Bin_40 = sum(Bin_40),
                Bin_41 = sum(Bin_41), Bin_42 = sum(Bin_42), Bin_43 = sum(Bin_43), Bin_44 = sum(Bin_44), Bin_45 = sum(Bin_45), Bin_46 = sum(Bin_46), Bin_47 = sum(Bin_47), Bin_48 = sum(Bin_48),
                Bin_49 = sum(Bin_49), Bin_50 = sum(Bin_50), Bin_51 = sum(Bin_51), Bin_52 = sum(Bin_52), Bin_53 = sum(Bin_53), Bin_54 = sum(Bin_54), Bin_55 = sum(Bin_55), Bin_56 = sum(Bin_56),
                Bin_57 = sum(Bin_57), Bin_58 = sum(Bin_58), Bin_59 = sum(Bin_59), Bin_60 = sum(Bin_60), Bin_61 = sum(Bin_61), Bin_62 = sum(Bin_62), Bin_63 = sum(Bin_63), Bin_64 = sum(Bin_64),
                Bin_65 = sum(Bin_65), Bin_66 = sum(Bin_66), Bin_67 = sum(Bin_67), Bin_68 = sum(Bin_68), Bin_69 = sum(Bin_69), Bin_70 = sum(Bin_70), Bin_71 = sum(Bin_71), Bin_72 = sum(Bin_72),
                Bin_73 = sum(Bin_73), Bin_74 = sum(Bin_74), Bin_75 = sum(Bin_75), Bin_76 = sum(Bin_76), Bin_77 = sum(Bin_77), Bin_78 = sum(Bin_78), Bin_79 = sum(Bin_79), Bin_80 = sum(Bin_80),
                Bin_81 = sum(Bin_81), Bin_82 = sum(Bin_82), Bin_83 = sum(Bin_83), Bin_84 = sum(Bin_84), Bin_85 = sum(Bin_85), Bin_86 = sum(Bin_86), Bin_87 = sum(Bin_87), Bin_88 = sum(Bin_88),
                Bin_89 = sum(Bin_89), Bin_90 = sum(Bin_90), Bin_91 = sum(Bin_91), Bin_92 = sum(Bin_92), Bin_93 = sum(Bin_93), Bin_94 = sum(Bin_94), Bin_95 = sum(Bin_95), Bin_96 = sum(Bin_96),
                Bin_97 = sum(Bin_97), Bin_98 = sum(Bin_98), Bin_99 = sum(Bin_99), Bin_100 = sum(Bin_100), Bin_101 = sum(Bin_101), Bin_102 = sum(Bin_102), Bin_103 = sum(Bin_103), Bin_104 = sum(Bin_104),
                Bin_105 = sum(Bin_105), Bin_106 = sum(Bin_106), Bin_107 = sum(Bin_107), Bin_108 = sum(Bin_108), Bin_109 = sum(Bin_109), Bin_110 = sum(Bin_110), Bin_111 = sum(Bin_111), Bin_112 = sum(Bin_112),
                Bin_113 = sum(Bin_113), Bin_114 = sum(Bin_114), Bin_115 = sum(Bin_115), Bin_116 = sum(Bin_116), Bin_117 = sum(Bin_117), Bin_118 = sum(Bin_118), Bin_119 = sum(Bin_119), Bin_120 = sum(Bin_120),
                Bin_121 = sum(Bin_121), Bin_122 = sum(Bin_122), Bin_123 = sum(Bin_123), Bin_124 = sum(Bin_124), Bin_125 = sum(Bin_125), Bin_126 = sum(Bin_126), Bin_127 = sum(Bin_127), Bin_128 = sum(Bin_128),
                Bin_129 = sum(Bin_129), Bin_130 = sum(Bin_130), Bin_131 = sum(Bin_131), Bin_132 = sum(Bin_132), Bin_133 = sum(Bin_133), Bin_134 = sum(Bin_134), Bin_135 = sum(Bin_135), Bin_136 = sum(Bin_136),
// ... [truncated — see 02-automated-detector--issuedetector-ei-high-flush-latencies-due-to-driver-issue.kql for full body]
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`, `{blobPath}`, `{Cloud}`

**Signal filters seen in KQL:** `HistogramTypeDesc == "Flush Latencies with Throttle time"`

---

### IssueDetector_EI_NetAssistMonitorTriggers_LM

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. 2h)
| where nodeId =~ query_NodeId and faultInfo has "Reason\":\"UnhealthyLinkWithLowSeverity" and faultInfo has "Value\":\"NetAssist" and nodeAvailabilityState == "Unallocatable"
| project PreciseTimeStamp,containerCount,nodeState,nodeAvailabilityState,faultInfo,cmNodeChannelAggregatedHealthStatus, isIsolated
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22094d0304-b537-42c7-8bc5-237aa74002a6%22%7D%7D"),"'>Emerging issue NetAssist Monitor triggers LM</a>")
| extend Severity = "Warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{query_NodeId}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_TORFailures

_Widget purpose:_ Automated Detector

Cluster: `azuredcm.kusto.windows.net` · Database: `AzureDCMDb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
let networkDeviceId = toscalar(cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(startofday(queryFrom) .. endofday(queryTo))
| where ResourceId == queryNodeId
| top 1 by PreciseTimeStamp desc
| project NetworkDeviceId);
cluster("aplat.westcentralus.kusto.windows.net").database("aplat").AnvilRepairServiceRequestSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ResourceId == networkDeviceId
| where SubStatus == "Received"
| extend Request = parse_json(Request)
| extend FaultCodeString = Request.RepairContext.FaultCodeString
| extend FaultReason = Request.RepairContext.FaultReason
| extend FaultTime = Request.RepairContext.Time
| project PreciseTimeStamp, RequestIdentifier, RequestAuthor, FaultCodeString, FaultReason, FaultTime, Request, Status, SubStatus, CorrelationIdentifier
| extend Content = tostring(FaultCodeString)
| extend StartTime = PreciseTimeStamp
| take 1
| extend Description = strcat("<a href='",strcat("https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496358/Network-TOR-Hardware-Failure_Restarts"),"'>TSG for TOR failure troubleshooting which contains RCA</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `SubStatus == "Received"`

---

### IssueDetector_TOR_DegradedUnhealthyEvents

_Widget purpose:_ Automated Detector

Cluster: `azphynet` · Database: `azdhmds` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
let devicename = toscalar(cluster('azphynet').database('azdhmds').Servers
| where NodeId =~ nodeid
| project DeviceName );
let tor = toscalar(cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice == devicename
| project EndDevice);
cluster('azphynet.kusto.windows.net').database('azdhmds').f_DeviceHealthLookupSimple(StartTime=queryFrom, EndTime=queryTo,SearchTerm=tor)
| where Persistence_1h > 50
| project StartTime = TIMESTAMP, DeviceName, FailureReason, FailureSignal, HealthCategory, Health, Confidence, Persistence_1h, MetricValue, endDeviceIP
| order by StartTime asc
| take 1
| extend Description = strcat("<a href='",strcat("https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496358/Network-TOR-Hardware-Failure_Restarts"),"'>Use TSG for TOR failure troubleshooting</a>")
| extend Severity = "error"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### IssueDetector_SoC_Update

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').OverlakeServiceManagerStatus
| where  PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h))
| where NodeId =~ querySocNodeId 
| where EventType == "versionswitch"
| order by PreciseTimeStamp desc
| extend detailsParsed = parse_json(detail)
| extend CurrentVersion=tostring(detailsParsed.Version)
| extend NewVersion=tostring(detailsParsed.NewVersion)
| project PreciseTimeStamp, ServiceName, CurrentVersion, NewVersion, NodeId, MachineName, Cluster
| extend StartTime = PreciseTimeStamp
| extend Content = strcat(ServiceName, ": ", NewVersion)
| take 1
| extend Description = strcat("<a href='",strcat("https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1206867/Host-Network-Investigation_Restarts?anchor=soc-investigation"),"'>Use TSG for SoC Update</a>")
| extend Severity = "warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySocNodeId}`

**Signal filters seen in KQL:** `EventType == "versionswitch"`

---

### IssueDetector_EI_HostNetworkIssue_FPGA_GFT_Unhealthy_on_Overlake

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
VMA
| where PreciseTimeStamp between (queryFrom..2h) and NodeId == query_NodeId
| where RCALevel2 == "HostNetworkIssue_FPGA_GFT_Unhealthy" and RCAEngineCategory != "CustomerInitiated"
| distinct bin(StartTime,2m), bin(EndTime,2m), Cluster, NodeId, ContainerId, RoleInstanceName, RCALevel1, RCALevel2, RCAEngineCategory
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22a82dfd71-ebf4-42d9-be00-6aab63d69335%22%7D%7D"),"'>Emerging issue HostNetworkIssue FPGA GFT Unhealthy on Overlake Nodes</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querytenantName}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{queryTenant}`, `{queryvirtualMachineUniqueId}`

**Signal filters seen in KQL:** `RCALevel2 == "HostNetworkIssue_FPGA_GFT_Unhealthy"`

---

### IssueDetector_EI_LM_failure_VFPRestoreFailure_NmAgentEventDelay

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("vmainsight.kusto.windows.net").database("vmadb").VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ querySubscription and RoleInstanceName has queryroleInstanceName and RCALevel2 has "LiveMigrationFailed Reason:VFPRestoreFailure_NmAgentEventDelay"
| join kind=inner (cluster("azcore.centralus.kusto.windows.net").database("Fc").LiveMigrationContainerDetailsEventLog
| where PreciseTimeStamp > queryFrom
| where PreciseTimeStamp < queryTo) on $left.ContainerId == $right.sourceContainerId
| distinct PreciseTimeStamp, Cluster, NodeId, ContainerId, RoleInstanceName,RCALevel1, RCALevel2, sessionId
| join kind=inner (cluster("vmainsight.kusto.windows.net").database("Air").LiveMigrationActivities
| where ActivitySource in (
"ActivityStream_LiveMigration_HyperVBlackoutStartEventDelay",
"ActivityStream_LiveMigration_NmAgentVfpDeserializationTime",
"ActivityStream_LiveMigration_NMAgentVfpRestoreEventDelay",
"ActivityStream_LiveMigration_NMAgentVfpSerializationStartDelay",
"ActivityStream_LiveMigration_NMAgentVfpSerializeTransferTime",
"ActivityStream_LiveMigration_VfpPollingDelay")
| where ActivityStart >= queryFrom and ActivityEnd <= queryTo
| extend Durationinsec = Duration / 1s
| project SessionId, ActivityStart, ActivityEnd, ActivityName, ActivityImpact, Durationinsec
| where Durationinsec > 5) on $left.sessionId == $right.SessionId
| distinct PreciseTimeStamp, Cluster, NodeId, ContainerId, RoleInstanceName,RCALevel1, RCALevel2, sessionId, ActivityStart, ActivityEnd, ActivityName, ActivityImpact, Durationinsec
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22491dfd95-3271-4e2e-971f-e658b6d36d12%22%7D%7D"),"'>Emerging issue LM failure due to VFPRestoreFailure_NmAgentEventDelay</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenant}`, `{queryvirtualMachineUniqueId}`, `{query_NodeId}`, `{querytenantName}`, `{querycontainerId}`, `{queryroleInstanceName}`, `{querySubscription}`

---

### IssueDetector_EI_Standard_ND96isr_H100_v5_HardwareFault_pCIfata

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("vmainsight.kusto.windows.net").database("vmadb").VMA()
| where PreciseTimeStamp between (queryFrom .. 2h)
| where RoleInstanceName == queryroleInstanceName and RCA_CSS == "Unplanned.HardwareFault.pCIfatal"
| join kind=inner 
(cluster("storageclient.eastus.kusto.windows.net").database("Fc").LogContainerSnapshot
| where containerType == "Standard_ND96isr_H100_v5") on $left.ContainerId == $right.containerId
| join kind=inner 
(cluster("storageclient.eastus.kusto.windows.net").database("Fc").LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. 2h)
| where faultInfo has "pCIfatal") on $left.NodeId == $right.nodeId
| project PreciseTimeStamp, Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCALevel1, RCALevel2, RCALevel3, RCA_CSS, containerType, faultInfo
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22a50c26bb-f673-4f43-a409-e849e4d0f84b%22%7D%7D"),"'>Emerging issue Standard_ND96isr_H100_v5 HardwareFault.pCIfatal</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryroleInstanceName}`, `{querySubscription}`, `{querycontainerId}`, `{querytenantName}`, `{query_NodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `containerType == "Standard_ND96isr_H100_v5"` · `faultInfo has "pCIfatal"`

---

### IssueDetector_EI_Attaching_Multiple_DataDisks_Over_Nvme_restart

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where NodeId == queryNodeId
| where OperationName has_any("VmAbstractionLayer::Vm::AttachAllDataVhds","VmAbstractionLayer::Update::DiskUpdateHelper::VerifySingleDiskChanges") and ResultSignature has_any ("0x80004003","0x80070bc2")
| join kind=inner   
(cluster("azcore.centralus.kusto.windows.net").database("Fa").NodeServiceOperationEtwTable
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where Identifier contains queryContainerId
| where OperationName == "UpdateContainer"
| where Result <> 1
| extend ResultCode = tohex(toint(ResultCode), 8), Health = "Unhealthy"
| extend Content = strcat ("0x", ResultCode)) on $left.NodeId==$right.NodeId
| join kind=inner 
(cluster("azcore.centralus.kusto.windows.net").database("Fc").TMMgmtNodeEventsEtwTable
| where TIMESTAMP between (queryFrom .. 2h) 
| where Message has_any ("data disks change","Dormant_VM_stopped") and Message has queryContainerId) on $left.NodeId==$right.NodeId
| project PreciseTimeStamp,NodeId, OperationName, ContextInCsv, ResultSignature,ResultType, CompleteTime, Identifier, ResultCode, Message
| order by PreciseTimeStamp asc
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22e1de19b9-623e-4dcd-84f2-fa764f101b9c%22%7D%7D"),"'>Emerging issue Attaching Multiple Data Disks Over Nvme may lead to VM Restart</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryroleInstanceName}`, `{queryContainerId}`, `{querytenantName}`, `{queryNodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `OperationName == "UpdateContainer"`

---

### IssueDetector_EI_OSProvisioningTimedOut_failure_DHCP_lease

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom..2h)
| where containerId == queryContainerId and containerOsState == "ContainerOsStateProvisioningTimedOut"
| project PreciseTimeStamp, roleInstanceName, nodeId, Tenant, containerId, containerOsState, containerState, containerLifecycleState, containerIsolationState, tenantName
| take 1
| join kind=inner 
(cluster('aznwsdn.kusto.windows.net').database('aznwmds').CriticalFailureEvent
| where TIMESTAMP between (queryFrom..2h)
| where Message has queryContainerId and Message has "ValidateInterfaceDependencies failed for Container" and Message has "due to missing encryption dependencies" ) on $left.nodeId == $right.NodeId
| project PreciseTimeStamp, roleInstanceName, nodeId, Tenant, containerId, containerOsState, containerState, containerLifecycleState, containerIsolationState, tenantName, TIMESTAMP, Message
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22ac41118c-7a6e-4b0c-aa22-613eeb920e61%22%7D%7D"),"'>Emerging issue OSProvisioningTimedOut due to failure to obtain DHCP lease with Vnet encryption enabled</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{query_NodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_AKS_Linux_instances_are_reported_as_Windows

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
FaComputeHourUsageEventCentralBondTable 
| where PreciseTimeStamp between (queryFrom..2h) 
| where NodeId == queryNodeId 
| where ContainerId == queryContainerId 
| where BillingContext has "Linux" and HypervContextRank == "Windows"
| project PreciseTimeStamp, ContainerId, BillingContext, HypervContextRank, OSContext, UsageResourceKind, VPCount, Quantity, VMMemory
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%229be1e34d-ca98-49b7-ab7b-56620b642347%22%7D%7D"),"'>Emerging issue AKS Linux instances are reported as running Windows</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `BillingContext has "Linux"`

---

### IssueDetector_EI_Dalds_v6_Windows_2025_datadisk_perf

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogContainerSnapshot
| where PreciseTimeStamp between ((queryFrom - 1d) .. (queryTo + 1d))
| where virtualMachineUniqueId == queryVmid and containerType == "Standard_D8alds_v6"
| summarize arg_max(PreciseTimeStamp, *) by containerId
| project roleInstanceName, vmSize = tostring(split(billingType, "|")[1]), containerType, containerId, nodeId, subscriptionId, virtualMachineUniqueId
| join kind=inner
(cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where TIMESTAMP between ((queryFrom - 1d) .. (queryTo + 1d))and OSVersion has "Windows Server 2025") on $left.virtualMachineUniqueId == $right.VMId
| distinct Cluster, NodeId, VMId, RoleInstanceName, OSVersion, vmSize, containerType
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%220ccf662e-c513-4cb5-a7ac-4b6e3f626a27%22%7D%7D"),"'>Emerging issue Dalds_v6: Windows 2025 Azure edition Sluggish after adding data disk</a>")
| extend Severity = "Warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmid}`, `{querySubscription}`, `{queryroleInstanceName}`, `{queryContainerId}`, `{querytenantName}`, `{queryNodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_LM_VFPRestoreFailure_Deserialization_Issue_Port

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
LiveMigrationFailureEvents
| where EventTime between (queryFrom .. queryTo) and NodeId == queryNodeId and RoleInstanceName == queryVMName and RCALevel2 == "VFPRestoreFailure_Deserialization_Issue_Port_0x51a"
| project EventTime, Cluster, RCALevel1, ObjectId, NodeId, RCALevel2, RoleInstanceName, Customer, EscalateTo
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryVMName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22e8a73279-3d11-4bea-a464-d5791d6a77be%22%7D%7D"),"'>Emerging issue LM:VFPRestoreFailure_Deserialization_Issue_Port_0x51a</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryVMName}`, `{querycontainerId}`, `{querytenantName}`, `{queryNodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_NVME_HW_troubleshooting

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
let fn_startTime = queryFrom - 2d;
let fn_endTime = queryTo + 2d;
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp >= fn_startTime and PreciseTimeStamp <= fn_endTime
| where NodeId =~ queryNodeId
| where EventId in (6002,6003)
| join kind=inner 
(cluster('sparkle.eastus.kusto.windows.net').database('defaultdb').Partner_NVMeHealthLog
| where PreciseTimeStamp between (fn_startTime .. fn_endTime)
| where MediaErrors > 0 ) on $left.NodeId == $right.NodeId
| distinct TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description, PreciseTimeStamp, Serial, MediaErrors
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%222f92bc27-ac4f-453b-be2b-75792f7bca17%22%2C%22380baabc-4c6c-44ba-8c6a-225be0dac693%22%3A%223eacbdc5-c397-4f1e-99d3-4fe4bc980f4c%22%2C%220a5dc75c-6b0a-453a-bc3a-ac60eb3a3fa3%22%3A%223e53fc9b-35a1-47a0-86bb-985d3f2a5689%22%2C%224a6593e9-828a-4df7-bade-477091591d88%22%3A%22ecac3cc0-dfe3-485f-aa61-1411e6dabf07%22%2C%228861522f-119f-40aa-9bb8-b46fea82bec1%22%3A%22a51c5d23-b817-4f94-8242-91badf8c33f2%22%7D%7D"),"'>Potential NVME HW issues</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_node_bugcheck_0x50_netdatapath

_Widget purpose:_ Automated Detector

Cluster: `overlakedata.southcentralus.kusto.windows.net` · Database: `overlake-syslog` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
let QueryFilterByNodeId = cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMap_Latest
| where NodeId =~ queryNodeId;
QueryFilterByNodeId
| summarize count()
| extend OverlakeState = iff(count_ == 0, "Not Enabled", "Enabled")
| project OverlakeState, NodeId = tolower(queryNodeId)
| join kind=leftouter (QueryFilterByNodeId) on NodeId
| project OverlakeState, QNodeId=NodeId, SocNodeId
| join kind=inner
(cluster("azcore.centralus.kusto.windows.net").database("OvlProd").OverlakeServiceManagerStatus
| where  PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h))
| where EventType == "versionswitch" and ServiceName == "netdatapathagent"
| order by PreciseTimeStamp desc
| extend detailsParsed = parse_json(detail)
| extend CurrentVersion=tostring(detailsParsed.Version)
| extend NewVersion=tostring(detailsParsed.NewVersion)
| extend StartTime = PreciseTimeStamp
| extend Content = strcat(ServiceName, ": ", NewVersion)
| project-rename UpdateTimestamp = StartTime) on $left.SocNodeId == $right.NodeId
| join kind=inner
(cluster('vmainsight.kusto.windows.net').database('vmadb').VMA()
| where PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h)) and ContainerId == queryContainerId
| where CadPrimaryKey contains "LegacyHB"
| where RCAEngineCategory <> "CustomerInitiated"
| where RCALevel2 contains '0x00000050' or RCALevel2 contains 'WRONG_SYMBOLS'
| project-rename IssueTimestamp = PreciseTimeStamp) on $left.QNodeId == $right.NodeId
| where (IssueTimestamp - UpdateTimestamp) between (0min .. 5min)
| project UpdateTimestamp, ServiceName, EventType, detail, IssueTimestamp, NodeId, ContainerId, RCALevel1, RCALevel2, RCALevel3
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%222bac6a78-fe94-4269-ac0c-482d7b6091cc%22%7D%7D"),"'>Emerging issue ode bugcheck 0x50 (PAGE_FAULT_IN_NONPAGED_AREA) in netdatapathagent_1908_app_model_5_0_5_12_v_5_0_0_441</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `EventType == "versionswitch"` · `CadPrimaryKey contains "LegacyHB"` · `RCAEngineCategory <> "CustomerInitiated"` · `RCALevel2 contains "0x00000050"`

---

### IssueDetector_EI_StagingNodeImagesGen9

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
TMMgmtNodeEventsEtwTable 
| where PreciseTimeStamp between(queryFrom..(queryFrom + 2h)) and Message has "Staging node images" and NodeId == queryNodeId
| project-rename FoundTimestamp = PreciseTimeStamp
| join (cluster('azcore.centralus').database('Fa').WindowsEventTable
| where PreciseTimeStamp between(queryFrom..(queryFrom + 2h)) and EventId == 505) on NodeId
| extend length = strlen(Description), latstring = indexof(Description,"20000+ms")
| extend latencies = substring(Description,latstring+26, length-latstring)
| extend point = indexof(latencies, "."), llen = strlen(latencies)
| extend latfinal = substring(latencies, 0, point)
| extend commasix= split(latfinal,",",8), commaten= split(latfinal,",",9), commatwen= split(latfinal,",",10), commatwenplus= split(latfinal,",",11)
| extend csixlen = strlen(commasix), ctenlen = strlen(commaten), ctwenlen = strlen(commatwen), ctwenplen = strlen(commatwenplus)
| extend bucketsix = substring(commasix,2,csixlen-4)
| extend bucketten = substring(commaten,2,ctenlen-4)
| extend buckettwen = substring(commatwen,2,ctwenlen-4)
| extend buckettwenplus = substring(commatwenplus,2,ctwenplen-4)
| extend length3 = strlen(Description), latstring3 = indexof(Description,"10000+ms")   
| extend latencies3 = substring(Description,latstring3+26, length3-latstring3)
| extend point3 = indexof(latencies3, "."), llen = strlen(latencies3)
| extend latfinal3 = substring(latencies3, 0, point3)
| extend commaten2= split(latfinal3,",",12), commatenplus2= split(latfinal3,",",13)
| extend ctenlen2 = strlen(commaten2), ctenplen2 = strlen(commatenplus2)
| extend bucketten2 = substring(commaten2,2,ctenlen2-4)
| extend buckettenplus2 = substring(commatenplus2,2,ctenplen2-4)
| extend length2 = strlen(Description), point2 = indexof(Description,"5120+ms")   
| extend latency = substring(Description,point2+17, length2-point2)
| extend llen = strlen(latency), commafive= split(latency,",",3), commafiveplus= split(latency,",",4)
| extend clen = strlen(commafive), cplen = strlen(commafiveplus)
| extend bucketfive = substring(commafive,2,clen-4)
| extend bucketfiveplus = substring(commafiveplus,2, cplen-5)
| where ((point2 > 0 and toint(bucketfive) > 50) or (point2 > 0 and toint(bucketfiveplus) > 0)) or ((latstring3 > 0 and toint(bucketten2) > 0) or (latstring3 > 0 and toint(buckettenplus2) > 0)) or ((latstring > 0 and toint(bucketsix) > 50) or (latstring > 0 and (toint(bucketten) > 0 or toint(buckettwen) > 0 or toint(buckettwenplus) > 0)))
| project-rename DiskEventTimestamp = PreciseTimeStamp
| where (DiskEventTimestamp - FoundTimestamp) between (0min .. 50min)
| project FoundTimestamp, Message, DiskEventTimestamp, Description
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2227bf4263-d815-457e-9de7-e05b02f5f29c%22%7D%7D"),"'>Emerging issue Impact of Staging Node Images download on Gen9</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_Backplane_service_crash_on_SoC_impacts_VM

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
VMA 
| where PreciseTimeStamp between (queryFrom .. 2h) 
| where Subscription =~ querySubscriptionId and RoleInstanceName has queryVMName and RCALevel2 == "backplane deadlocked"
| join kind=inner(cluster("Gandalfdeepad.kusto.windows.net").database("gandalf_deepAD").GetSocCrashData()
| where PreciseTimeStamp between (queryFrom .. 2h)
| where bucketString contains "LINUX_SIGNAL_SIGABRT_CODE_0xfffffffa_e0534947_vfp.so!"
| where (faultingProcess contains 'dpdk' or faultingProcess contains "vfp" or faultingProcess contains 'netdatapath'))on $left.NodeId == $right.NodeId
| distinct PreciseTimeStamp, Cluster, NodeId, ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2, RCA_CSS, bucketString
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscriptionId,"&query_VMName=",queryVMName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22e5c1985f-06f5-4a6b-8956-574d54df8ab9%22%7D%7D"),"'>Emerging issue Backplane service crash on SoC impacts VM accessibility</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querycontainerId}`, `{querySubscriptionId}`, `{queryVMName}`, `{querytenantName}`, `{query_NodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `bucketString contains "LINUX_SIGNAL_SIGABRT_CODE_0xfffffffa_e0534947_vfp.so!"`

---

### IssueDetector_EI_Node Crash_due_to_0xBC0000D6_BlobCache!BcRefere

_Widget purpose:_ Automated Detector

Cluster: `azurewatsoncustomer.kusto.windows.net` · Database: `AzureWatsonCustomer` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. 2h)
| where nodeIdentity == queryNodeId and crashMode == "km"
| project crashMode, crashProcessFullPath, process, dumpUid, nodeIdentity
| join kind=inner(
    CustomerDumpAnalysisResultV2 | where PreciseTimeStamp between (queryFrom .. 2h) and bucketString == "0xBC0000D6_BlobCache!BcReferenceTailPfnList"
) on dumpUid
| distinct crashTime, nodeIdentity, crashMode, bucketString, followup, faultingModule, faultingModuleVersion, dumpUid
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%220a5dc75c-6b0a-453a-bc3a-ac60eb3a3fa3%22%3A%22b1aad33d-2e5c-4e1f-9563-7216117bf363%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%223a48a195-878c-4e4e-960b-b8ef08bcd28c%22%7D%7D"),"'>Emerging issue Node Crash due to 0xBC0000D6_BlobCache!BcReferenceTailPfnList</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryroleInstanceName}`, `{queryNodeId}`, `{queryContainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_GPC_VMs_Fail_to_Start_IBManagerError_0x800704c

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp  between (queryFrom .. 2h)
| where (isnotempty(queryVmId) and virtualMachineUniqueId == queryVmId) or (isempty(queryVmId) and containerId == queryContainerId)
| order by PreciseTimeStamp asc
| extend Health = iif(isnotempty(faultInfo),  "Unhealthy", "Healthy")
| extend flag = case (faultInfo <> prev(faultInfo), "start", faultInfo <> next(faultInfo), "end", "")
| where flag <> ""
| extend EndTime = case (flag == "start" and isnotnull(next(flag)), next(PreciseTimeStamp), flag == "end", PreciseTimeStamp, queryTo)
| where flag <> "end"
| where isnotempty(faultInfo)
| extend fault = parse_json(faultInfo)
| project StartTime = PreciseTimeStamp, EndTime, Content = tostring(fault.FaultCode), containerId, Health, 
    faultReason = tostring(fault.Reason), FabricOperationString = tostring(fault.FabricOperationString), faultInfo = fault
| where Content == 10005 and faultInfo has "0x800704cd" and faultInfo has "IBManagerError"
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryVmId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2202e90170-5a37-4ff0-9b93-18778da2472f%22%7D%7D"),"'>Emerging issue GPC VMs Fail to Start IBManagerError 0x800704cd</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`, `{queryContainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{query_NodeId}`, `{queryTenant}`

**Signal filters seen in KQL:** `flag <> "end"`

---

### IssueDetector_EI_Ultra_PremV2_DiskBlip_during_VDC_driver_update

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
HyperVStorageStackTable 
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == queryNodeId
| where Message has_any (queryContainerId) and EventId == 9
| parse EventMessage with * " took " TimeInMs " milliseconds" *
| project-rename IOSlowTimestamp = PreciseTimeStamp
|join kind = inner 
(cluster("storageclient.eastus.kusto.windows.net").database("AutopilotDeployment").ServiceVersionSwitch 
| where PreciseTimeStamp between ((queryFrom) .. (queryTo)) and NewVersion == "storage_agent_vdc_rel47_3_0_10_480"
| project-rename UpdateTimestamp = PreciseTimeStamp) on $left.NodeId == $right.NodeId
| where (IOSlowTimestamp - UpdateTimestamp) between (0min .. 1min)
| project UpdateTimestamp, ServiceName, CurrentVersion, NewVersion, SourceOfService, IOSlowTimestamp, TimeInMs, EventMessage
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2200d084a6-745d-4287-95f2-fa0bfb448207%22%7D%7D"),"'>Emerging issue Ultra / Premium SSDv2 Disk Blip during VDC driver update</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_v6VM_TPM_fails_start_due_to_Underhill_VM

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("storageclient.eastus.kusto.windows.net").database("Fc").LogContainerHealthSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where (isnotempty(queryVMID) and virtualMachineUniqueId == queryVMID) or (isempty(queryVMID) and containerId == queryContainerId)
| where nodeId == queryNodeId and faultInfo has "0x80078000" and faultInfo has "HyperVError" and faultInfo has "10005"
|join kind = inner 
(cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where EventId == 18590 and Description has queryContainerId and  Description has "underhill terminated unsuccessfully") on $left.nodeId == $right.NodeId
| project PreciseTimeStamp, containerState, containerOsState , actualOperationalState, containerLifecycleState, nodeId, containerId, roleInstanceName, faultInfo, TimeCreated, EventId, ProviderName, Description
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryVMID,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%22380baabc-4c6c-44ba-8c6a-225be0dac693%22%3A%223eacbdc5-c397-4f1e-99d3-4fe4bc980f4c%22%2C%22d0b9dbe3-f20b-4b34-b861-30b1b43cbd34%22%3A%22bfabf364-14d6-418c-9775-4b06da3b0952%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%224b312adf-e902-43b5-a8b0-0925b81684e4%22%7D%7D"),"'>Emerging issue v6 VM using TPM fails to start due to Underhill VM initialization failure</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVMID}`, `{queryContainerId}`, `{queryNodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryTenant}`

---

### IssueDetector_EI_node bugcheck_0xd1_AV_blobcache!BcPfnReferenc

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ querySubscription and RoleInstanceName has queryroleInstanceName and RCALevel2 ==  "AV_blobcache!BcPfnReferenceByCacheStorePfnAndIndex"
| distinct  PreciseTimeStamp,NodeId, RoleInstanceName,RCALevel1, RCALevel2
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%220d346752-05aa-4cf5-8756-dade446c1474%22%7D%7D"),"'>Emerging issue node bugcheck 0xd1 AV_blobcache!BcPfnReferenceByCacheStorePfnAndIndex</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{query_NodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_Unable_to_create_VM_VMAL_error_0x8000ffff

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp >= queryFrom and  PreciseTimeStamp <= queryTo
| where NodeId =~ query_NodeId and Message has "0x8000ffff" and Message has querycontainerId and Message has "Recording new fault"
| project PreciseTimeStamp, NodeId, Message
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22b35b5823-f963-4ab4-9f41-446d4dc3d97d%22%7D%7D"),"'>Emerging issue Unable to create a VM with a VMAL error 0x8000ffff</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querycontainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_TOR_Update

_Widget purpose:_ Automated Detector

Cluster: `azphynet.kusto.windows.net` · Database: `azdhmds` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
let devicename = toscalar(Servers
| where NodeId =~ querynodeid
| project DeviceName);
let TorName = toscalar(DeviceInterfaceLinks
| where StartDevice == devicename
| project TorDevice=EndDevice);
cluster('azphynet.kusto.windows.net').database('HwSwHealth').dhDeviceReload
| where TIMESTAMP between (queryFrom .. queryTo)
| where DeviceName has TorName and FailureReason has "Planned_Maintenance" and Confidence >= 75
| take 1
| extend Description = strcat("<a href='",strcat("https://supportability.visualstudio.com/AzureNetworking/_wiki/wikis/Wiki/140152/ToR-Reboots-and-Failures?anchor=how-to-spot-tor-maintenance"),"'>TSG for TOR Update</a>")
| extend Severity = "Warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querynodeid}`

---

### IssueDetector_Node_Restart_Due_to_Planned_Maintenance

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ query_SubscriptionId and RoleInstanceName has query_VMName and RCALevel1 == "RootHEUpdate Rebootful" and RCALevel2 == "Out_of_band_HE_update_by_BatchingManager"
| distinct PreciseTimeStamp, NodeId, ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2, RCA_CSS
| take 1
| extend Description = strcat("<a href='",strcat("https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2301548/Node-Restart-Due-to-Planned-Maintenance_Restarts"),"'>TSG for Node Restart Due to Planned Maintenance</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_SubscriptionId}`, `{query_VMName}`

---

### IssueDetector_EI_UnallocatableNode_DestroyContainer_0x8abc0503

_Widget purpose:_ Automated Detector

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where ResourceId == query_NodeId 
| where MessageTrigger has "OnBeforeWalkTree"
| project PreciseTimeStamp, MessageTrigger, Message, ResourceId, ResourceDependencies
| order by PreciseTimeStamp asc 
| extend StartTime = PreciseTimeStamp
| extend FaultCodeString = parse_json(Message).RepairContext.FaultCodeString
| extend Content = tostring(FaultCodeString)
| where FaultCodeString == "ZombieContainerFault"
| join kind=inner (cluster('azcore.centralus.kusto.windows.net').database('Fa').NodeServiceOperationEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where OperationName !contains "Query"
| where Result <> 1
| extend ResultCode = tohex(toint(ResultCode), 8), Health = "Unhealthy"
| extend Content = strcat("0x", ResultCode)
| where Content == "0x8abc0503"
| project NodeId, OperationName, Identifier, Result, ResultCode, Content, Health) on $left.ResourceId == $right.NodeId
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%228529581d-7b7a-405c-b7cc-fd448680100a%22%7D%7D"),"'>Emerging issue UnallocatableNode DestroyContainer 0x8abc0503</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `MessageTrigger has "OnBeforeWalkTree"` · `FaultCodeString == "ZombieContainerFault"` · `Content == "0x8abc0503"`

---

### IssueDetector_EI_bugcheck_0xd1_AV_Barbera!HbLldCompleteIrpOve

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
VMA
| where PreciseTimeStamp between(queryFrom .. queryTo) and RCALevel1 =="HostOSCrash" and RCALevel2 == "AV_Barbera!HbLldCompleteIrpOverlay"
| where (isnotempty(queryvirtualMachineUniqueId) and VmUniqueId == queryvirtualMachineUniqueId) or (isempty(queryvirtualMachineUniqueId) and ContainerId == querycontainerId)
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22c72ff279-86b1-49be-9429-9b66fcc1ae4d%22%7D%7D"),"'>Emerging issue node bugcheck 0xd1 - AV_Barbera!HbLldCompleteIrpOverlay</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryvirtualMachineUniqueId}`, `{querycontainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{query_NodeId}`, `{queryTenant}`

---

### IssueDetector_EI_Unallocatable_Node_due_to_XDisk_leaks

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. 2h) and nodeId == queryNodeId and nodeAvailabilityState == "Unallocatable" and faultInfo has "XDisk leaks. Datapath from Azure Host Storage cannot update"
| project PreciseTimeStamp,nodeId,nodeState,nodeAvailabilityState,containerCount,diskConfiguration,faultInfo,rootUpdateAllocationType,cmNodeChannelAggregatedHealthStatus,isIsolated
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22ede64c80-0ab7-4c5d-bf93-15414dd4dcab%22%7D%7D"),"'>Emerging issue Unallocatable Node due to XDisk leaks</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryNodeId}`, `{queryContainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`, `{queryTo}`

---

### IssueDetector_EI_Local_NVMe_Disks_Are_Missing_In_Lv4_Series

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom - 2h .. queryFrom + 2h) and NodeId == queryNodeId and ContextInCsv contains queryContainerId and ResultSignature == "0x8007045d"
| extend Time = DurationIn100ns/10000000.0
| extend StartTime = TIMESTAMP - (Time * 1s)
| project StartTime, EndTime = PreciseTimeStamp, Time, NodeId, OperationName, Tid, ResultSignature, ResultType, RootOperationId, ContextInCsv
| order by StartTime asc, EndTime asc
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2247eb1344-2e44-4d40-9a33-7672efe3f4e3%22%7D%7D"),"'>Emerging issue Local NVMe disks are missing in Lv4 series</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_LM_SH_due_to_NVMe_Device_End_of_Life

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. 4h) and nodeId == queryNodeId and nodeAvailabilityState == "Unallocatable" and faultInfo has "0030 Generic NVMe SSD End of Life Rule" and faultInfo has "32038"
| project PreciseTimeStamp,nodeId,nodeState,nodeAvailabilityState,containerCount,diskConfiguration,faultInfo,rootUpdateAllocationType,cmNodeChannelAggregatedHealthStatus,isIsolated
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2205754247-c1c2-457d-b283-cc3c04ba6275%22%7D%7D"),"'>Emerging issue LM / SH due to NVMe Device End of Life</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_LMFailed_FlexibleIODeviceRestore

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ querySubscription and RoleInstanceName has queryroleInstanceName and RCALevel2 has "Flexible IO Device Restore Failure"
| distinct  PreciseTimeStamp,NodeId,ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22e546ce07-6b37-411e-b9a2-07c7a458c9bd%22%7D%7D"),"'>Emerging issue LiveMigrationFailed due to Flexible IO Device Restore Failure</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryroleInstanceName}`, `{queryContainerId}`, `{querytenantName}`, `{queryNodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_NetworkContainer_AllocationIncarnation

_Widget purpose:_ Automated Detector

Cluster: `azureallocator.westcentralus.kusto.windows.net` · Database: `AzureAllocator` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster('https://azureallocator.westcentralus.kusto.windows.net').database('AzureAllocator').AllocatorContainerReuseRejectionReason
| where PreciseTimeStamp between (queryFrom..queryTo)
| where rejectedContainerId in (querycontainerId)
| where containerWorkflowStep == "ReuseContainer"
| where ruleName == "NetworkReuseRule"
| where reason contains "NetworkContainerAllocationIncarnation changed from 0 to"
| project PreciseTimeStamp, allocationId, containerWorkflowStep, rejectedContainerId, ruleName, reason
| join kind=inner (
cluster('https://azureallocator.westcentralus.kusto.windows.net').database('AzureAllocator').AllocatorAllocationResult
| where PreciseTimeStamp between (queryFrom .. queryTo)
| project allocationId, activityId, isSucceeded, allocationRequestType ) on allocationId
| join kind=inner (
cluster('Azcrpfollower').database("crp_allprod").ApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| project operationId, operationName, correlationId) on $left.activityId == $right.operationId
| extend reused= iff(containerWorkflowStep == "ReuseContainer" and ruleName =="NetworkReuseRule" and reason contains "NetworkContainerAllocationIncarnation" and allocationRequestType contains "UpdateTenant"  ,"Potentially caused by Known Issue","")
| extend Description = iif(reused == "Potentially caused by Known Issue",strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%22ca668014-11a6-43aa-8338-c47220868261%22%7D%7D"),"'>Emerging issue Unexpected Restart of VMs when PATCH/PUT operation is triggered to VMs</a>"),"")
| where isnotempty(Description)
| order by PreciseTimeStamp asc
| take 1
| project ContainerId=rejectedContainerId, CRPActivityId=operationId,correlationId, operationName, Description
| extend Severity = "Critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querycontainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{query_NodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

**Signal filters seen in KQL:** `containerWorkflowStep == "ReuseContainer"` · `ruleName == "NetworkReuseRule"` · `reason contains "NetworkContainerAllocationIncarnation changed from 0 to"`

---

### IssueDetector_EI_LMFailed_VFPSerializationIssue_0x5aa

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ querySubscription and RoleInstanceName has queryroleInstanceName and RCALevel2 has "VFPRestoreFailure_Serialization_Issue_0x5aa"
| distinct  PreciseTimeStamp,NodeId,ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2259fa4d3a-d620-4990-a50d-1e5cc8a7374f%22%2C%2207ff4c83-42c2-4b33-8bcf-26d9a4766ae5%22%3A%220f0ed074-9310-4bc7-a852-769018b665e3%22%7D%7D"),"'>Emerging issue LM failure VFPRestoreFailure SerializationIssue 0x5aa</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryroleInstanceName}`, `{queryContainerId}`, `{querytenantName}`, `{queryNodeId}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_NVMeVmHighDiskLatency_due_to_CacheHint

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
let tempEndTime = iff(datetime_diff('day', startTime, endTime) > 1, startTime + 1d, endTime);
cluster("storageclient.eastus.kusto.windows.net").database("SharedWorkspace").StorageClientInsightsForNodeV2(query_NodeId, startTime, tempEndTime) 
| project PreciseTimeStamp, EventName, nodeId
| join kind=inner (cluster("storageclient.eastus.kusto.windows.net").database("Fa").OsAsapCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and ContainerId has querycontainerId) on $left.nodeId == $right.NodeId
| extend MaxBqeWriteLatencyInMS = DeltaBqeLatencyDiskWriteIoBucketMaxLatency / 1000.0
| extend counter = MaxBqeWriteLatencyInMS
| summarize
        Gt_10_Sec = countif(counter >= 10000),
        Gt_15_Sec = countif(counter >= 15000),
        Gt_30_Sec = countif(counter >= 30000),
        Q100_InMS = max(counter) by HistogramTypeDesc = "ASAP Bqe Writes",
        NodeId,
        EventName
| where Gt_10_Sec > 0
| project HistogramTypeDesc, Gt_10_Sec, Gt_15_Sec, Gt_30_Sec, Q100_InMS, NodeId, EventName
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",startTime,"&globalTo=",endTime,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2271a5ef28-fa0b-4c33-8b6f-32cedb0ae151%22%7D%7D"),"'>Emerging issue NVMe VM high disk latency due to Cache Hint Noisy Neighbor</a>")
| extend Severity = "critical"
```

**Params:** `{startTime}`, `{endTime}`, `{query_NodeId}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`, `{querySubscription}`, `{queryroleInstanceName}`

---

### IssueDetector_Sudden_Power_Loss_of_host_node

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == _nodeId
| where EventId == 41 and ProviderName == "Microsoft-Windows-Kernel-Power"
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| take 1
| extend Description = "Sudden power loss of host node logged"
| extend Severity = "warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_nodeId}`

---

### IssueDetector_Booting_of_host_node_detected

_Widget purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("storageclient.eastus.kusto.windows.net").database("Fc").LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo) and nodeId == _nodeId and nodeState == "Booting" 
| project PreciseTimeStamp,nodeId,nodeState,nodeAvailabilityState,containerCount,diskConfiguration,faultInfo,rootUpdateAllocationType,cmNodeChannelAggregatedHealthStatus,isIsolated
| take 1
| extend Description = "Booting of host node detected"
| extend Severity = "warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_nodeId}`

---

### IssueDetector_HighHostCPU_temp_throttle

_Widget purpose:_ Automated Detector

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("sparkle.eastus.kusto.windows.net").database("defaultdb").SparkleSELByNodeId(query_NodeId)
| where BMCSelTimestamp between (queryFrom .. queryTo) and ((SensorType == "Processor" and EventDataDetails1 == "Processor Automatically Throttled") or (SensorType == "Temperature" and EventDataDetails1 has "unspecified value") or (SensorType == "Fan" and EventDataDetails1 == "Pulse Width Modulation"))
| project Timestamp = BMCSelTimestamp, Source = GeneratorId, EventType, Sensor = SensorType, Details = EventDataDetails1, RawHex
| take 1
| extend Description = "High Host CPU temperatur or throttle found"
| extend Severity = "warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`

---

### IssueDetector_HighHostCPU_throttle

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == _nodeId
| where EventId == 37 and ProviderName == "Microsoft-Windows-Kernel-Processor-Power"
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| take 1
| extend Description = "Host CPU throttle found"
| extend Severity = "warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_nodeId}`

---

### IssueDetector_EI_NVMe_Controller_VM_experience_stornvme_reset

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == query_NodeId
| where (EventId == 902 and ProviderName == "Microsoft-Windows-Kernel-PnP") or (EventId == 5116 and ProviderName == "Microsoft-Windows-Hyper-V-VID")
| project PreciseTimeStamp,NodeId,EventId,ProviderName,Description
| join kind=inner (cluster("azcore.centralus.kusto.windows.net").database("Fa").AsapNvmeEtwTraceLogEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| parse TaskName with StrEVID ' - ' *
| extend EventId = toint(StrEVID)
| extend ResetMs = extract(@"ResetMsPassed""\s*:\s*(\d+)", 1, Message)
| extend ResetMs = tolong(ResetMs)
| where TaskName contains 'AsapUmedControllerReset' and EventId in (26,35) and ResetMs > 10000
| project PreciseTimeStamp, Level, NodeId, EventId, TaskName, Message, ResetMs) on $left.NodeId == $right.NodeId
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",querycontainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",query_NodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%225048c50d-a061-4856-8d39-36c8b60fe2e4%22%7D%7D"),"'>Emerging issue NVMe controller VM experiences stornvme reset or bugcheck due to IOTimeoutValue too short</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{queryvirtualMachineUniqueId}`, `{querytenantName}`, `{querycontainerId}`, `{queryroleInstanceName}`, `{querySubscription}`, `{queryTenant}`

**Signal filters seen in KQL:** `TaskName contains "AsapUmedControllerReset"`

---

### IssueDetector_EI_VMA_bugcheck_0x20001_HYPERVISOR_ERROR

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
cluster("https://vmainsight.kusto.windows.net").database("vmadb").VMA()
| where PreciseTimeStamp between (queryFrom .. queryTo) and RCALevel1 == "HostOSCrash" and RCALevel2 == "BugCheckCode: 0x20001"
| where (isnotempty(queryvirtualMachineUniqueId) and VmUniqueId == queryvirtualMachineUniqueId) or (isempty(queryvirtualMachineUniqueId) and ContainerId == queryContainerId) 
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%222b05cdb1-caf3-4d79-b5f1-d29cd1f5507b%22%2C%22c7defa0d-c1c4-4330-81b4-1ff67c1ad342%22%3A%224a61be78-02f0-422e-aa82-62f3358fceaf%22%7D%7D"),"'>Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryvirtualMachineUniqueId}`, `{queryContainerId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryNodeId}`, `{queryTenant}`

---

### IssueDetector_EI_AW_bugcheck_0x20001_HYPERVISOR_ERROR

_Widget purpose:_ Automated Detector

Cluster: `azurewatsoncustomer.kusto.windows.net` · Database: `AzureWatsonCustomer` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. queryTo + 10h)
| where nodeIdentity == queryNodeId and crashMode == "km"
| project crashMode, crashProcessFullPath, process, dumpUid, nodeIdentity
| join kind=inner (CustomerDumpAnalysisResultV2 | where PreciseTimeStamp between (queryFrom .. queryTo + 10h) and bucketString has "NOBLOB_HYPERVISOR_ERROR_Unhandled_PageFault") on dumpUid
| distinct PreciseTimeStamp,crashTime, crashMode, bucketString, followup, faultingModule, faultingModuleVersion, bugLink, dumpUid
| sort by crashTime asc
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%222b05cdb1-caf3-4d79-b5f1-d29cd1f5507b%22%2C%22c7defa0d-c1c4-4330-81b4-1ff67c1ad342%22%3A%22d4e88a82-7e43-45bf-a410-4d6271c7e614%22%7D%7D"),"'>Emerging issue Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryNodeId}`, `{queryroleInstanceName}`, `{queryContainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_EI_LMFailed_VFPSerializationIssue_0x5aa_2

_Widget purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
LiveMigrationFailureEvents
| where EventTime >=queryFrom and EventTime < queryTo
| where (ObjectId == queryContainerId or VirtualMachineUniqueId == queryvirtualMachineUniqueId) and RCALevel2 =="VFPRestoreFailure_Serialization_Issue_0x5aa"
| project SessionId = tostring(Diagnostics.SessionId),LMStartTime=todatetime(Diagnostics.LiveMigrationStartTime),LMEndTime = EventTime, IsLMSuccessful = false,RoleInstanceName, FailureReason=RCALevel2
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%2259fa4d3a-d620-4990-a50d-1e5cc8a7374f%22%2C%2207ff4c83-42c2-4b33-8bcf-26d9a4766ae5%22%3A%224592b02e-7455-4354-a445-3ec3b10f6d1e%22%7D%7D"),"'>Emerging issue LM failure VFPRestoreFailure SerializationIssue 0x5aa</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryvirtualMachineUniqueId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querytenantName}`, `{queryNodeId}`, `{queryTenant}`

---

### IssueDetector_EI_VM_creation_failure_0xc3510224_VMAL_ASAPPF

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Automated Detector`

```kusto
TMMgmtNodeEventsEtwTable  
| where TIMESTAMP between (queryFrom .. queryTo) and NodeId =~ queryNodeId  and (Message has '0xc3510224' and Message has 'VMAL_ASAPPF_NOT_RUNNING')
| project PreciseTimeStamp=TIMESTAMP, Message
| take 1
| extend Description = strcat("<a href='",strcat("https://azureserviceinsights.trafficmanager.net/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart?query_SubscriptionId=",querySubscription,"&query_VMName=",queryroleInstanceName,"&query_ContainerId=",queryContainerId,"&query_TenantName=",querytenantName,"&query_NodeId=",queryNodeId,"&query_vmId=",queryvirtualMachineUniqueId,"&query_cluster=",queryTenant,"&globalFrom=",queryFrom,"&globalTo=",queryTo,"&__userData=%7B%22nodeData%22%3A%7B%22bbd261dc-c6d5-45a0-b0f6-6a890f5a67ee%22%3A%22e44f1e85-b537-4420-88df-21b3b4875397%22%2C%228e11a227-ca25-47b0-8e15-aca9273d8904%22%3A%220db308ba-c59e-4b41-8e31-fb33dc5d3c58%22%7D%7D"),"'>Emerging issue VM creation failure due to 0xc3510224 VMAL_ASAPPF_NOT_RUNNING</a>")
| extend Severity = "critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{queryContainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`

---

### IssueDetector_E17_Key_Vault_Encryption_Key_not_found

_Widget purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`
Source panel: `Automated Detector`

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
| join kind = leftouter  ( 
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
| where BlobPath != "" and Description has BlobPath and TriageReason == "Key Vault Encryption Key Not Found_KeyVaultUpdated"
| distinct TimeCreated,NodeId,ContainerId, EventId, Description, DiskName, BlobPath, TriageReason
| take 1
| extend Description = strcat("<a href='",strcat("https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2647253/E17-Key-Vault-Encryption-Key-Not-Found_KeyVaultUpdated"),"'>TSG for E17 caused by Key Vault Encryption Key Not Found</a>")
| extend Severity = "critical"
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_containerid}`, `{query_nodeid}`

---
