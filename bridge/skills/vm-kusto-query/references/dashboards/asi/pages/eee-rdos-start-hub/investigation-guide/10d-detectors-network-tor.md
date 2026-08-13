# Detectors — Network & TOR

> Source: EEE RDOS Start Hub dashboard (7 queries).

TOR switch and platform network failure signatures. Run when guest network connectivity dropped or TOR failures are flagged.

---

### IssueDetector_NetworkIssues

_Purpose:_ Automated Detector

Cluster: `icmcluster` · Database: `IcmDataWarehouse` · Type: `IssueDetector`

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

### IssueDetector_EI_StopDestroy Fails with STORVSP_VspDeviceCreate*

_Purpose:_ Automated Detector

Cluster: `azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `IssueDetector`

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

### IssueDetector_TORFailures

_Purpose:_ Automated Detector

Cluster: `azuredcm.kusto.windows.net` · Database: `AzureDCMDb` · Type: `IssueDetector`

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

_Purpose:_ Automated Detector

Cluster: `azphynet` · Database: `azdhmds` · Type: `IssueDetector`

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

### IssueDetector_EI_HostNetworkIssue_FPGA_GFT_Unhealthy_on_Overlake

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`

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

### IssueDetector_TOR_Update

_Purpose:_ Automated Detector

Cluster: `azphynet.kusto.windows.net` · Database: `azdhmds` · Type: `IssueDetector`

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

### IssueDetector_EI_NetworkContainer_AllocationIncarnation

_Purpose:_ Automated Detector

Cluster: `azureallocator.westcentralus.kusto.windows.net` · Database: `AzureAllocator` · Type: `IssueDetector`

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
