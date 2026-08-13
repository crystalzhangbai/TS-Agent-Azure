# Detectors — Node Lifecycle / Unallocatable

> Source: EEE RDOS Start Hub dashboard (11 queries).

Unallocatable node, node-restart-due-to-PM, staging, and cluster-wide node health signatures.

---

### IssueDetector_TooManyUnhealthyNode

_Purpose:_ Automated Detector

Cluster: `icmcluster` · Database: `IcMDataWarehouse` · Type: `IssueDetector`

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

### IssueDetector_EI_RHSendsIncorrectVMAvailableStateRepeatedly

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

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

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

### IssueDetector_EI_CRUD operationFailuresDueToContainerWorkflow*

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

_Purpose:_ Automated Detector

Cluster: `Vmainsight` · Database: `CAD` · Type: `IssueDetector`

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

### IssueDetector_EI_AKS_Linux_instances_are_reported_as_Windows

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

### IssueDetector_EI_StagingNodeImagesGen9

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

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

### IssueDetector_Node_Restart_Due_to_Planned_Maintenance

_Purpose:_ Automated Detector

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `IssueDetector`

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

_Purpose:_ Automated Detector

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `IssueDetector`

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

### IssueDetector_EI_Unallocatable_Node_due_to_XDisk_leaks

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

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

### IssueDetector_Booting_of_host_node_detected

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

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
