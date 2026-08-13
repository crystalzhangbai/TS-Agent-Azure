# Emerging Issues (part 1/4)

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Emerging Issues** (13 queries, part 1 of 4).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

##  Resource Health Sends Incorrect VM Availability state repeatedly

###  RH Sends Incorrect VM Availability state repeatedly

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues >  Resource Health Sends Incorrect VM Availability state repeatedly`

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
| where PreciseTimeStamp between (queryFrom ..queryTo)) on $left.VirtualMachineUniqueId == $right.VirtualMachineUniqueId
| where  ContainerId != ContainerIdLCS
| distinct  PreciseTimeStamp, ContainerId,IcHeartbeat,PowerState,HyperVHandshake,HealthUpdateTimeStamp,ApiVersion;
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').KyberVmAvailabilityMetricEmission
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where VirtualMachineUniqueId == VMId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{VMId}`

---

## "EQ stuck" on EQn 0x4

### "EQ stuck" on EQn 0x4 DS

_Widget purpose:_ "EQ stuck" on EQn 0x4

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > "EQ stuck" on EQn 0x4 > "EQ stuck" on EQn 0x4`

```kusto
WindowsEventTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId
| where EventId == 20 and ProviderName == "mlnx5"
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## AirDiskBlip BlobCache Write during Congestion

### HyperVStorageStackAndBlobcacheInternal_EE

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > AirDiskBlip BlobCache Write during Congestion > HyperVStorageStack and BlobcacheInternal`

```kusto
HyperVStorageStackTable 
| where PreciseTimeStamp between (startTime .. endTime) 
| where Message has_any (containerId) and EventId == 9 and NodeId == nodeId
| extend HyperVTimestamp = PreciseTimeStamp
| project HyperVTimestamp, Level, EventId, TaskName, EventMessage, Message, NodeId
| join kind=inner(
OsBlobCacheInternalCounterTable
| where PreciseTimeStamp > startTime and PreciseTimeStamp  < endTime
| where (DeltaBSWaitForOldData > 0 or DeltaBSPausedWrites > 0 or DeltaBSPausedWritesTimeout > 0)
| extend DriverTimestamp = PreciseTimeStamp)
on $left.NodeId == $right.NodeId
| distinct DriverTimestamp, DeltaFUnmapLinkReferenced, DeltaBSWaitForOldData, DeltaBSWaitForWriteLimit, BSPausedWrites, DeltaBSPausedWrites, DeltaBSPausedWritesTimeout, BSPausedWritesTimeout, DeltaBSLargeReadCount,  EventId, TaskName, HyperVTimestamp, EventMessage, NodeId
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

## AKS Linux instances are reported as running Windows

### AKS_Linux_instances_are_reported_as_Windows

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > AKS Linux instances are reported as running Windows`

```kusto
FaComputeHourUsageEventCentralBondTable 
| where PreciseTimeStamp between (queryFrom..queryTo) 
| where NodeId == queryNodeId 
| where ContainerId == queryContainerId 
| where BillingContext has "Linux" and HypervContextRank == "Windows"
| project PreciseTimeStamp, ContainerId, BillingContext, HypervContextRank, OSContext, UsageResourceKind, VPCount, Quantity, VMMemory
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

**Signal filters seen in KQL:** `BillingContext has "Linux"`

---

## Attaching Multiple Data Disks Over Nvme may lead to VM Restart

### Attaching_Multiple_DataDisks_Over_Nvme_may_lead_to_VM_Restart

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > Attaching Multiple Data Disks Over Nvme may lead to VM Restart`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where NodeId == queryNodeId
| where OperationName has_any("VmAbstractionLayer::Vm::AttachAllDataVhds","VmAbstractionLayer::Update::DiskUpdateHelper::VerifySingleDiskChanges") and ResultSignature has_any ("0x80004003","0x80070bc2")
| join kind=inner   
(cluster("azcore.centralus.kusto.windows.net").database("Fa").NodeServiceOperationEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where Identifier contains queryContainerId
| where OperationName == "UpdateContainer"
| where Result <> 1
| extend ResultCode = tohex(toint(ResultCode), 8), Health = "Unhealthy"
| extend Content = strcat ("0x", ResultCode)) on $left.NodeId==$right.NodeId
| join kind=inner 
(cluster("azcore.centralus.kusto.windows.net").database("Fc").TMMgmtNodeEventsEtwTable
| where TIMESTAMP between (queryFrom .. queryTo) 
| where Message has_any ("data disks change","Dormant_VM_stopped") and Message has queryContainerId) on $left.NodeId==$right.NodeId
| project PreciseTimeStamp,NodeId, OperationName, ContextInCsv, ResultSignature,ResultType, CompleteTime, Identifier, ResultCode, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`

**Signal filters seen in KQL:** `OperationName == "UpdateContainer"`

---

## Backplane service crash on SoC impacts VM accessibility

### SoC_impacts_VM_accessibility

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `Emerging Issues > Backplane service crash on SoC impacts VM accessibility`

```kusto
VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ querySubscriptionId and RoleInstanceName has queryVMName and RCALevel2 == "backplane deadlocked"
| join kind=inner(cluster("Gandalfdeepad.kusto.windows.net").database("gandalf_deepAD").GetSocCrashData()
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where bucketString contains "LINUX_SIGNAL_SIGABRT_CODE_0xfffffffa_e0534947_vfp.so!"
| where (faultingProcess contains 'dpdk' or faultingProcess contains "vfp" or faultingProcess contains 'netdatapath'))on $left.NodeId == $right.NodeId
| distinct PreciseTimeStamp, Cluster, NodeId, ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2, RCA_CSS, bucketString
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscriptionId}`, `{queryVMName}`

**Signal filters seen in KQL:** `bucketString contains "LINUX_SIGNAL_SIGABRT_CODE_0xfffffffa_e0534947_vfp.so!"`

---

## ContainerWorkflow is blocked due to DppPluginOrPfDatapathServiceRequired

### DppPluginOrPfDatapathServiceRequired

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > ContainerWorkflow is blocked due to DppPluginOrPfDatapathServiceRequired`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp >= queryFrom and  PreciseTimeStamp <= queryTo
| where NodeId =~ query_NodeId and Message has "ContainerWorkflow is blocked, reason:[DppPluginOrPfDatapathServiceRequired]"
| project PreciseTimeStamp, Message
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`

---

## CreateContainer failed with 0xc3510153

### CreateContainer_failed_with_0xc3510153

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > CreateContainer failed with 0xc3510153`

```kusto
cluster('Azcore.centralus').database('Fa').VmServiceEventsEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId =~ nodeId
| where Context == "Repreparation" and Message has 'VmAbstractionLayer::Vm::PerformPreCreateOperations' and Message has '0xc3510153'
| project-rename  VMServiceMessage = Message
| join hint.strategy = broadcast 
(cluster("azcsupfollower").database("AzureCM").TMMgmtNodeEventsEtwTable  
| where TIMESTAMP between (startTime .. endTime) and Message has 'CreateContainer' and Message has '0xC3510153') on $left.NodeId == $right.NodeId
| project PreciseTimeStamp, NodeId, ContainerId, VMServiceMessage, Message
| take 1
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `Context == "Repreparation"`

---

## CreateContainer fails with "0x80070002 HRESULT_FROM_WIN32(ERROR_FILE_NOT_FOUND)" on L-Series VMs

### CreateContainer fails with 0x80070002 ERROR_FILE_NOT_FOUND

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > CreateContainer fails with "0x80070002 HRESULT_FROM_WIN32(ERROR_FILE_NOT_FOUND)" on L-Series VMs`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").IfxOperationV2v1EtwTable
| where TIMESTAMP  between (queryFrom .. queryTo) and NodeId =~ queryNodeId and OperationName == "RdosUtils::StorageManagement::WriteRandomDataToDisk" and ResultSignature == "0x80070002"
| join hint.strategy = broadcast 
(cluster("azcsupfollower").database("AzureCM").TMMgmtNodeEventsEtwTable
| where TIMESTAMP between (queryFrom .. queryTo) and Message has queryContainerId and Message has "0x80070002") on $left.NodeId == $right.NodeId
| project Cluster,TIMESTAMP, NodeId, OperationName, ResultType, ResultSignature, Region
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

---

## CRUD operation failures due to container workflow blocker "MissingStorageConfigurationsWillbe"

### CRUDoperationFailuresDueTo"MissingStorageConfigurationsWillbe"

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > CRUD operation failures due to container workflow blocker "MissingStorageConfigurationsWillbe"`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == NodeID
| where Message has "Container workflow blocked: MissingStorageConfigurationsWillbe"
| project PreciseTimeStamp,NodeId, Message
| sort by PreciseTimeStamp asc
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{NodeID}`

**Signal filters seen in KQL:** `Message has "Container workflow blocked: MissingStorageConfigurationsWillbe"`

---

## Dalds_v6: Windows 2025 Azure edition Sluggish after adding data disk

### Dalds_v6_Windows_2025_datadisk_perf 

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > Dalds_v6: Windows 2025 Azure edition Sluggish after adding data disk > Basic Check`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogContainerSnapshot
| where PreciseTimeStamp between ((queryFrom - 1d) .. (queryTo + 1d))
| where virtualMachineUniqueId == queryvmid and containerType == "Standard_D8alds_v6"
| summarize arg_max(PreciseTimeStamp, *) by containerId
| project roleInstanceName, vmSize = tostring(split(billingType, "|")[1]), containerType, containerId, nodeId, subscriptionId, virtualMachineUniqueId
| join kind=inner
(cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where TIMESTAMP between ((queryFrom - 1d) .. (queryTo + 1d))and OSVersion has "Windows Server 2025") on $left.virtualMachineUniqueId == $right.VMId
| distinct Cluster, NodeId, VMId, RoleInstanceName, OSVersion, vmSize, containerType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryvmid}`

---

### ASAP_completed_IOs

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > Dalds_v6: Windows 2025 Azure edition Sluggish after adding data disk > Details Check`

```kusto
union cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventTable, cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapNvmeEtwTraceLogEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| parse TaskName with StrEVID ' - ' *
| extend EVID=toint(StrEVID)
| where NodeId == queryNodeId and EVID == 1219
| project PreciseTimeStamp, Level, EVID, TaskName, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

## GPC VMs Fail to Start: IBManagerError 0x800704cd

### GPC_VMs_Fail_to_Start_IBManagerError_0x800704cd

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > GPC VMs Fail to Start: IBManagerError 0x800704cd`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
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
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryVmId}`

**Signal filters seen in KQL:** `flag <> "end"`

---
