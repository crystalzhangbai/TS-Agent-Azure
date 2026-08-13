# Detectors — VM Start / CreateContainer Failures

> Source: EEE RDOS Start Hub dashboard (10 queries).

VM provisioning, CreateContainer, and start-time failure signatures. Run when a VM failed to start or be created.

---

### IssueDetector_EI_CreateContainer_fails_with_0x80070002_L-Series

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

### IssueDetector_EI_NV6_v5_VMs_Fail_to_Start_due_to_Low_Memory

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

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

### IssueDetector_EI_OSProvisioningTimedOut_failure_DHCP_lease

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

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

### IssueDetector_EI_GPC_VMs_Fail_to_Start_IBManagerError_0x800704c

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

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

### IssueDetector_EI_v6VM_TPM_fails_start_due_to_Underhill_VM

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

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

### IssueDetector_EI_Unable_to_create_VM_VMAL_error_0x8000ffff

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

### IssueDetector_EI_VM_creation_failure_0xc3510224_VMAL_ASAPPF

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

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

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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
