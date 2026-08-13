# Emerging Issues (part 3/4)

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Emerging Issues** (31 queries, part 3 of 4).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## HostNetworkIssue_FPGA_GFT_Unhealthy on Overlake Nodes

### HostNetworkIssue_FPGA_GFT_Unhealthy

Cluster: `Vmainsight` · Database: `vmadb` · Type: `Table`
Source panel: `Emerging Issues > HostNetworkIssue_FPGA_GFT_Unhealthy on Overlake Nodes`

```kusto
cluster("Vmainsight").database("vmadb").VMA
| where PreciseTimeStamp between (queryFrom..queryTo)
| where NodeId == querynodeid
| where RCALevel2 == "HostNetworkIssue_FPGA_GFT_Unhealthy"
| where RCAEngineCategory != "CustomerInitiated"
| distinct  bin(StartTime,2m), bin(EndTime,2m), Cluster, NodeId, ContainerId, RoleInstanceName,RCALevel1,RCALevel2, RCAEngineCategory
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querynodeid}`

**Signal filters seen in KQL:** `RCALevel2 == "HostNetworkIssue_FPGA_GFT_Unhealthy"` · `RCAEngineCategory != "CustomerInitiated"`

---

## Impact of Staging Node Images download on Gen9.0 host

### stagingnodeimagesGen9

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > Impact of Staging Node Images download on Gen9.0 host`

```kusto
TMMgmtNodeEventsEtwTable 
| where PreciseTimeStamp between(queryFrom..queryTo) and Message has "Staging node images" and NodeId == queryNodeId
| project-rename FoundTimestamp = PreciseTimeStamp
| join (cluster('azcore.centralus').database('Fa').WindowsEventTable
| where PreciseTimeStamp between(queryFrom..queryTo) and EventId == 505) on NodeId
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
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

## LiveMigrationFailed due to Flexible IO Device Restore Failure

### LMFailed_FlexibleIODeviceRestoreFailure

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `Emerging Issues > LiveMigrationFailed due to Flexible IO Device Restore Failure`

```kusto
VMA 
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime 
| where Subscription =~ query_SubscriptionId and RoleInstanceName has query_VMName and RCALevel2 has "Flexible IO Device Restore Failure"
| distinct  PreciseTimeStamp,NodeId,ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_SubscriptionId}`, `{query_VMName}`

---

## LM / SH due to NVMe Device End of Life

### LMSHduetoNVMeDeviceEndofLife

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > LM / SH due to NVMe Device End of Life`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. 4h) and nodeId == queryNodeId and nodeAvailabilityState == "Unallocatable" and faultInfo has "0030 Generic NVMe SSD End of Life Rule" and faultInfo has "32038"
| project PreciseTimeStamp,nodeId,nodeState,nodeAvailabilityState,containerCount,diskConfiguration,faultInfo,rootUpdateAllocationType,cmNodeChannelAggregatedHealthStatus,isIsolated
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

## LM failure - VFPRestoreFailure_Serialization_Issue_0x5aa

### LMfailure_VFPRestoreFailure_Serialization_Issue_0x5aa_2

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `Emerging Issues > LM failure - VFPRestoreFailure_Serialization_Issue_0x5aa > LM failure check`

```kusto
cluster("vmainsight.kusto.windows.net").database("Air").LiveMigrationFailureEvents
| where EventTime >=queryStartTime and EventTime < queryEndTime
| where (ObjectId == queryContainerId or VirtualMachineUniqueId == queryVMId) and RCALevel2 =="VFPRestoreFailure_Serialization_Issue_0x5aa"
| project SessionId = tostring(Diagnostics.SessionId),LMStartTime=todatetime(Diagnostics.LiveMigrationStartTime),LMEndTime = EventTime,
IsLMSuccessful = false,RoleInstanceName, FailureReason=RCALevel2
```

**Params:** `{queryStartTime}`, `{queryEndTime}`, `{queryContainerId}`, `{queryVMId}`

---

### LMfailure_VFPRestoreFailure_Serialization_Issue_0x5aa

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `Emerging Issues > LM failure - VFPRestoreFailure_Serialization_Issue_0x5aa > VMA check`

```kusto
VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ querySubscription and RoleInstanceName has queryroleInstanceName and RCALevel2 has "VFPRestoreFailure_Serialization_Issue_0x5aa"
| distinct  PreciseTimeStamp,NodeId,ContainerId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscription}`, `{queryroleInstanceName}`

---

## LM failure due to VFPRestoreFailure_Deserialization_Issue_Port_0x51a

### VFPRestoreFailure_Deserialization_Issue_Port_0x51a

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `Emerging Issues > LM failure due to VFPRestoreFailure_Deserialization_Issue_Port_0x51a`

```kusto
LiveMigrationFailureEvents
| where EventTime between (queryFrom .. queryTo) and NodeId == queryNodeId and RoleInstanceName == queryVMName and RCALevel2 == "VFPRestoreFailure_Deserialization_Issue_Port_0x51a"
| project EventTime, Cluster, RCALevel1, ObjectId, NodeId, RCALevel2, RoleInstanceName, Customer, EscalateTo
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVMName}`, `{queryNodeId}`

---

## LM failure due to VFPRestoreFailure_NmAgentEventDelay

### LM_failure_due_to_VFPRestoreFailure_NmAgentEventDelay

Cluster: `Vmainsight` · Database: `vmadb` · Type: `Table`
Source panel: `Emerging Issues > LM failure due to VFPRestoreFailure_NmAgentEventDelay`

```kusto
cluster("Vmainsight").database("vmadb").VMA 
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime 
| where Subscription =~ query_SubscriptionId and RoleInstanceName has query_VMName and RCALevel2 has "LiveMigrationFailed Reason:VFPRestoreFailure_NmAgentEventDelay"
| join kind=inner (cluster("azurecm.kusto.windows.net").database("AzureCM").LiveMigrationContainerDetailsEventLog
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime) on $left.ContainerId == $right.sourceContainerId
| distinct PreciseTimeStamp, Cluster, NodeId, ContainerId, RoleInstanceName,RCALevel1, RCALevel2, sessionId
| join kind=inner (cluster('vmainsight.kusto.windows.net').database('Air').LiveMigrationActivities
| where ActivitySource in (
"ActivityStream_LiveMigration_HyperVBlackoutStartEventDelay",
"ActivityStream_LiveMigration_NmAgentVfpDeserializationTime",
"ActivityStream_LiveMigration_NMAgentVfpRestoreEventDelay",
"ActivityStream_LiveMigration_NMAgentVfpSerializationStartDelay",
"ActivityStream_LiveMigration_NMAgentVfpSerializeTransferTime",
"ActivityStream_LiveMigration_VfpPollingDelay")
| where ActivityStart >= query_BeginTime and ActivityEnd <= query_EndTime
| extend Durationinsec = Duration / 1s
| project SessionId, ActivityStart, ActivityEnd, ActivityName, ActivityImpact, Durationinsec
| where Durationinsec > 5) on $left.sessionId == $right.SessionId
| distinct PreciseTimeStamp, Cluster, NodeId, ContainerId, RoleInstanceName,RCALevel1, RCALevel2, sessionId, ActivityStart, ActivityEnd, ActivityName, ActivityImpact, Durationinsec
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_SubscriptionId}`, `{query_VMName}`

---

## Local NVMe disks are missing in Lv4 series

### LocalNVMeDisksAreMissingInLv4series

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > Local NVMe disks are missing in Lv4 series`

```kusto
IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom - 2h .. queryFrom + 2h) and NodeId == queryNodeId and ContextInCsv contains queryContainerId and ResultSignature == "0x8007045d"
| extend Time = DurationIn100ns/10000000.0
| extend StartTime = TIMESTAMP - (Time * 1s)
| project StartTime, EndTime = PreciseTimeStamp, Time, NodeId, OperationName, Tid, ResultSignature, ResultType, RootOperationId, ContextInCsv
| order by StartTime asc, EndTime asc
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

---

## Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR

### IssueDetector_EI_AW_Check_0x20001_HYPERVISOR_ERROR

Cluster: `azurewatsoncustomer.kusto.windows.net` · Database: `AzureWatsonCustomer` · Type: `Table`
Source panel: `Emerging Issues > Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR > AzureWatson Check`

```kusto
CustomerCrashOccurredV2
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime + 10h)
| where nodeIdentity == query_NodeId and crashMode == "km"
| project crashMode, crashProcessFullPath, process, dumpUid, nodeIdentity
| join kind=inner (CustomerDumpAnalysisResultV2 | where PreciseTimeStamp between (query_BeginTime .. query_EndTime + 10h) and bucketString has "NOBLOB_HYPERVISOR_ERROR_Unhandled_PageFault") on dumpUid
| distinct crashTime, crashMode, bucketString, followup, faultingModule, faultingModuleVersion, bugLink, dumpUid
| sort by crashTime asc
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

### IssueDetector_EI_VMA_Check_Multiple_host_nodes_crashed_with_0x20

Cluster: `https://vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `Emerging Issues > Multiple host nodes crashed with 0x20001 HYPERVISOR_ERROR > VMA Check`

```kusto
cluster("https://vmainsight.kusto.windows.net").database("vmadb").VMA()
| where PreciseTimeStamp between (queryFrom .. queryTo) and RCALevel1 == "HostOSCrash" and RCALevel2 == "BugCheckCode: 0x20001"
| where (isnotempty(_vmid) and VmUniqueId == _vmid) or (isempty(_vmid) and ContainerId == _containerId) 
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCAEngineCategory, RCALevel1, RCALevel2
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_vmid}`, `{_containerId}`

---

## NetAssist Monitor triggers Node Fault UnhealthyLinkWithLowSeverity leading to excessive LM

### NetAssist_LM

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > NetAssist Monitor triggers Node Fault UnhealthyLinkWithLowSeverity leading to excessive LM`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp >= queryFrom and  PreciseTimeStamp <= queryTo
| where nodeId =~ query_NodeId and faultInfo has "Reason\":\"UnhealthyLinkWithLowSeverity" and faultInfo has "Value\":\"NetAssist" and nodeAvailabilityState == "Unallocatable"
| project PreciseTimeStamp,containerCount,nodeState,nodeAvailabilityState,faultInfo,cmNodeChannelAggregatedHealthStatus, isIsolated
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`

---

## Node bugcheck 0x50 (PAGE_FAULT_IN_NONPAGED_AREA) in netdatapathagent_1908_app_model_5_0_5_12_v_5_0_0_441

### nodebugcheck_after_netdatapathupdate

Cluster: `overlakedata.southcentralus.kusto.windows.net` · Database: `overlake-syslog` · Type: `Table`
Source panel: `Emerging Issues > Node bugcheck 0x50 (PAGE_FAULT_IN_NONPAGED_AREA) in netdatapathagent_1908_app_model_5_0_5_12_v_5_0_0_441`

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
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

**Signal filters seen in KQL:** `EventType == "versionswitch"` · `CadPrimaryKey contains "LegacyHB"` · `RCAEngineCategory <> "CustomerInitiated"` · `RCALevel2 contains "0x00000050"`

---

## Node Crash due to 0xBC0000D6_BlobCache!BcReferenceTailPfnList

### NodeCrash_0xBC0000D6_BlobCache!BcReferenceTailPfnList

Cluster: `azurewatsoncustomer.kusto.windows.net` · Database: `AzureWatsonCustomer` · Type: `Table`
Source panel: `Emerging Issues > Node Crash due to 0xBC0000D6_BlobCache!BcReferenceTailPfnList`

```kusto
CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeIdentity == queryNodeId and crashMode == "km"
| project crashMode, crashProcessFullPath, process, dumpUid, nodeIdentity
| join kind=inner(
    CustomerDumpAnalysisResultV2 | where PreciseTimeStamp between (queryFrom .. queryTo) and bucketString == "0xBC0000D6_BlobCache!BcReferenceTailPfnList"
) on dumpUid
| distinct crashTime, nodeIdentity, crashMode, bucketString, followup, faultingModule, faultingModuleVersion, dumpUid, process
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

## NV6 v5 VMs Fail to Start due to Low Memory

### NV6_v5_VMs_Fail_to_Start_due_to_Low_Memory

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > NV6 v5 VMs Fail to Start due to Low Memory`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where nodeId =~ query_NodeId and nodeAvailabilityState == "Unallocatable" and faultInfo has "0x80078014"
| project-rename node_faultInfo = faultInfo
| join kind=inner (LogContainerSnapshot
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where containerType has "A10_v5" and containerId == querycontainerId) on $left.nodeId == $right.nodeId
| join kind=inner (LogContainerHealthSnapshot
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where faultInfo has "Operation 'StartContainer' is configured to surface a fault after 4 successive failures" and faultInfo has "0x80078014"
| project-rename container_faultInfo = faultInfo
) on $left.containerId == $right.containerId
| project PreciseTimeStamp,RoleInstance,nodeAvailabilityState,nodeState,containerCount,diskConfiguration,node_faultInfo,containerId,containerType, container_faultInfo
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querycontainerId}`

**Signal filters seen in KQL:** `containerType has "A10_v5"` · `faultInfo has "Operation 'StartContainer' is configured to surface a fault after 4 successive failures"`

---

## NVMe controller VM experience stornvme reset or bugcheck due to IOTimeoutValue too short

### NVMeControllerVMexperienceStornvmeResetOrBugcheck

_Widget purpose:_ WindowsEventTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > NVMe controller VM experience stornvme reset or bugcheck due to IOTimeoutValue too short > WindowsEventTable`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (_startDateTime .. _endDateTime) and NodeId == _nodeId
| where (EventId == 902 and ProviderName == "Microsoft-Windows-Kernel-PnP") or (EventId == 5116 and ProviderName == "Microsoft-Windows-Hyper-V-VID")
| project PreciseTimeStamp,NodeId,EventId,ProviderName,Description
| join kind=inner (cluster("azcore.centralus.kusto.windows.net").database("Fa").AsapNvmeEtwTraceLogEventTable
| where PreciseTimeStamp between (_startDateTime .. _endDateTime)
| parse TaskName with StrEVID ' - ' *
| extend EventId = toint(StrEVID)
| extend ResetMs = extract(@"ResetMsPassed""\s*:\s*(\d+)", 1, Message)
| extend ResetMs = tolong(ResetMs)
| where TaskName contains 'AsapUmedControllerReset' and EventId in (26,35) and ResetMs > 10000
| project PreciseTimeStamp, Level, NodeId, EventId, TaskName, Message, ResetMs) on $left.NodeId == $right.NodeId
| take 1
```

**Params:** `{_startDateTime}`, `{_endDateTime}`, `{_nodeId}`

**Signal filters seen in KQL:** `TaskName contains "AsapUmedControllerReset"`

---

## NVMe VM high disk latency due to Cache Hint Noisy Neighbor

### NVMeVMhighdisklatency_dueto_CacheHintNoisyNeighbor

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `Emerging Issues > NVMe VM high disk latency due to Cache Hint Noisy Neighbor`

```kusto
let tempEndTime = iff(datetime_diff('day', startTime, endTime) > 1, startTime + 1d, endTime);
cluster("storageclient.eastus.kusto.windows.net").database("SharedWorkspace").StorageClientInsightsForNodeV2(nodeId, startTime, tempEndTime) 
| project PreciseTimeStamp, EventName, NodeId
| join kind=inner (cluster("storageclient.eastus.kusto.windows.net").database("Fa").OsAsapCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and ContainerId has containerId) on $left.NodeId == $right.NodeId
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
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

## OSProvisioningTimedOut due to failure to obtain DHCP lease with Vnet encryption enabled

### OSProvisioningTimedOut_DHCP_VNET_encryption_enabled

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > OSProvisioningTimedOut due to failure to obtain DHCP lease with Vnet encryption enabled`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom..queryTo)
| where containerId == queryContainerId and containerOsState == "ContainerOsStateProvisioningTimedOut"
| project PreciseTimeStamp, roleInstanceName, nodeId, Tenant, containerId, containerOsState, containerState, containerLifecycleState, containerIsolationState, tenantName
| take 1
| join kind=inner 
(cluster('aznwsdn.kusto.windows.net').database('aznwmds').CriticalFailureEvent
| where TIMESTAMP between (queryFrom..queryTo)
| where Message has queryContainerId and Message has "ValidateInterfaceDependencies failed for Container" and Message has "due to missing encryption dependencies" ) on $left.nodeId == $right.NodeId
| project PreciseTimeStamp, roleInstanceName, nodeId, Tenant, containerId, containerOsState, containerState, containerLifecycleState, containerIsolationState, tenantName, TIMESTAMP, Message
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---

## Resource Health Unavailable for Linux 6.2 Kernel

### RH_Unavailable_Linux_6_2

Cluster: `Vmainsight` · Database: `CAD` · Type: `Table`
Source panel: `Emerging Issues > Resource Health Unavailable for Linux 6.2 Kernel`

```kusto
cluster('Vmainsight').database('CAD').VMA_Daily
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where ContainerId == query_ContainerId
| where GA_GuestOSVersion has "6.2.0" and GA_GuestOSVersion has "Linux" and StartTime >= ago(30d)
| join kind=inner
(cluster('Azcore.centralus').database('Fa').VmHealthRawStateEtwTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where  HasHyperVHandshakeCompleted == "false") on $left.ContainerId == $right.ContainerId
| summarize max(PreciseTimeStamp) by GA_GuestOSVersion, ContainerId, HasHyperVHandshakeCompleted
| order by max_PreciseTimeStamp desc 
| take 5
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

**Signal filters seen in KQL:** `GA_GuestOSVersion has "6.2.0"` · `HasHyperVHandshakeCompleted == "false"`

---

## Staging Node Images

### StagingNodeImages

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > Staging Node Images`

```kusto
TMMgmtNodeEventsEtwTable 
| where TIMESTAMP between (query_BeginTime..1h)
| where NodeId =~ query_NodeId and Message has 'Staging node images'
| project-rename FoundTimestamp = PreciseTimeStamp
| join kind=inner (cluster('Azcore.centralus').database('Fa').WindowsEventTable
| where PreciseTimeStamp between (query_BeginTime..1h) and EventId == 147) on NodeId
| project-rename DiskEventTimestamp = PreciseTimeStamp
| where (DiskEventTimestamp - FoundTimestamp) between (0min .. 40min)
| distinct FoundTimestamp, NodeId, Message, DiskEventTimestamp,Description
| take 1
```

**Params:** `{query_BeginTime}`, `{query_NodeId}`

---

## Standard_ND96isr_H100_v5_HardwareFault_pCIfata

### Standard_ND96isr_H100_v5_HardwareFault_pCIfata

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `Emerging Issues > Standard_ND96isr_H100_v5_HardwareFault_pCIfata`

```kusto
cluster("vmainsight.kusto.windows.net").database("vmadb").VMA()
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where RoleInstanceName == queryRoleInstanceName and RCA_CSS == "Unplanned.HardwareFault.pCIfatal"
| join kind=inner 
(cluster("storageclient.eastus.kusto.windows.net").database("Fc").LogContainerSnapshot
| where containerType == "Standard_ND96isr_H100_v5") on $left.ContainerId == $right.containerId
| join kind=inner 
(cluster("storageclient.eastus.kusto.windows.net").database("Fc").LogNodeSnapshot
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where faultInfo has "pCIfatal") on $left.NodeId == $right.nodeId
| project PreciseTimeStamp, Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, ResourceId, RCALevel1, RCALevel2, RCALevel3, RCA_CSS, containerType, faultInfo
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRoleInstanceName}`

**Signal filters seen in KQL:** `containerType == "Standard_ND96isr_H100_v5"` · `faultInfo has "pCIfatal"`

---

## StopDestroy Fails with STORVSP_VspDeviceCreate_ParserOverride_Avhdparser

### StopDestroy:STORVSP_VspDeviceCreate_ParserOverride_Avhdparser

Cluster: `azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `Table`
Source panel: `Emerging Issues > StopDestroy Fails with STORVSP_VspDeviceCreate_ParserOverride_Avhdparser`

```kusto
CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeIdentity == NodeId and crashMode == "km"
| project crashMode, crashProcessFullPath, process, dumpUid, nodeIdentity
| join kind=leftouter(
CustomerDumpAnalysisResultV2
| where PreciseTimeStamp between (queryFrom .. queryTo)
) on dumpUid
| where bucketString == "LKD_MANUALLY_INITIATED_CRASHLKD_MANUALLY_INITIATED_CRASH_STORVSP_VspDeviceCreate_ParserOverride_Avhdparser"
| distinct crashTime, crashMode, bucketString, followup, dumpUid
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{NodeId}`

**Signal filters seen in KQL:** `bucketString == "LKD_MANUALLY_INITIATED_CRASHLKD_MANUALLY_INITIATED_CRASH_STORVSP_VspDeviceCreate_ParserOverride_Avhdparser"`

---

## Ultra / Premium SSDv2 Disk Blip during VDC driver update

### Ultra_PremV2_DiskBlip_during_VDC_driver_update

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > Ultra / Premium SSDv2 Disk Blip during VDC driver update`

```kusto
HyperVStorageStackTable 
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where Message has_any (containerId) and EventId == 9
| parse EventMessage with * " took " TimeInMs " milliseconds" *
| project-rename IOSlowTimestamp = PreciseTimeStamp
|join kind = inner 
(cluster("storageclient.eastus.kusto.windows.net").database("AutopilotDeployment").ServiceVersionSwitch 
| where PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h)) and NewVersion == "storage_agent_vdc_rel47_3_0_10_480"
| project-rename UpdateTimestamp = PreciseTimeStamp) on $left.NodeId == $right.NodeId
| where (IOSlowTimestamp - UpdateTimestamp) between (0min .. 1min)
| project UpdateTimestamp, ServiceName, CurrentVersion, NewVersion, SourceOfService, IOSlowTimestamp, TimeInMs, EventMessage
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

## Unable to create a VM with a VMAL error 0x8000ffff

### VMAL_error_0x8000ffff

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > Unable to create a VM with a VMAL error 0x8000ffff`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp >= queryFrom and  PreciseTimeStamp <= queryTo
| where NodeId =~ query_NodeId and Message has "0x8000ffff" and Message has query_ContainerId and Message has "Recording new fault"
| project PreciseTimeStamp, NodeId, Message
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{query_ContainerId}`

---

## Unallocatable Node due to "XDisk leaks. Datapath from Azure Host Storage cannot update."

### UnallocatableNode_XDiskleaks

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > Unallocatable Node due to "XDisk leaks. Datapath from Azure Host Storage cannot update."`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. 2h) and nodeId == queryNodeId and nodeAvailabilityState == "Unallocatable" and faultInfo has "XDisk leaks. Datapath from Azure Host Storage cannot update"
| project PreciseTimeStamp,nodeId,nodeState,nodeAvailabilityState,containerCount,diskConfiguration,faultInfo,rootUpdateAllocationType,cmNodeChannelAggregatedHealthStatus,isIsolated
| take 1
```

**Params:** `{queryFrom}`, `{queryNodeId}`

---

## UnallocatableNode due to DestroyContainer workflow stuck with 0x8abc0503 (E_DELETETHROTTLE)

### UnallocatableNode_DestroyContainer_0x8abc0503

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`
Source panel: `Emerging Issues > UnallocatableNode due to DestroyContainer workflow stuck with 0x8abc0503 (E_DELETETHROTTLE)`

```kusto
AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where ResourceId == queryNodeid 
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
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeid}`

**Signal filters seen in KQL:** `MessageTrigger has "OnBeforeWalkTree"` · `FaultCodeString == "ZombieContainerFault"` · `Content == "0x8abc0503"`

---

## Unexpected Reboot due to node bugcheck 0xd1 - AV_Barbera!HbLldCompleteIrpOverlay

### bugcheck_0xd1_AV_Barbera!HbLldCompleteIrpOverlay

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `Emerging Issues > Unexpected Reboot due to node bugcheck 0xd1 - AV_Barbera!HbLldCompleteIrpOverlay`

```kusto
VMA
| where PreciseTimeStamp between(queryFrom .. queryTo) and RCALevel1 =="HostOSCrash" and RCALevel2 == "AV_Barbera!HbLldCompleteIrpOverlay"
| where (isnotempty(queryvmid) and VmUniqueId == queryvmid) or (isempty(queryvmid) and ContainerId == queryContainerId)
| distinct Cluster, StartTime, EndTime, AvailabilityState, TenantName, RoleInstanceName, ContainerId, NodeId, RCAEngineCategory, RCALevel1, RCALevel2, RCALevel3
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryvmid}`, `{queryContainerId}`

---

## Unexpected Reboot due to node bugcheck 0xd1 - AV_blobcache!BcPfnReferenceByCacheStorePfnAndIndex

### node_bugcheck_0xd1_AV_blobcache!BcPfnReferenceByCacheStorePfnA

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Table`
Source panel: `Emerging Issues > Unexpected Reboot due to node bugcheck 0xd1 - AV_blobcache!BcPfnReferenceByCacheStorePfnAndIndex`

```kusto
VMA 
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where Subscription =~ query_SubscriptionId and RoleInstanceName has query_VMName and RCALevel2 ==  "AV_blobcache!BcPfnReferenceByCacheStorePfnAndIndex"
| distinct  PreciseTimeStamp,NodeId, RoleInstanceName,RCALevel1, RCALevel2
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_SubscriptionId}`, `{query_VMName}`

---

## Unexpected Restart of VMs when PATCH/PUT operation is triggered to VMs

### EI_NetworkContainerAllocationIncarnation

Cluster: `azureallocator.westcentralus.kusto.windows.net` · Database: `AzureAllocator` · Type: `Table`
Source panel: `Emerging Issues > Unexpected Restart of VMs when PATCH/PUT operation is triggered to VMs`

```kusto
cluster('https://azureallocator.westcentralus.kusto.windows.net').database('AzureAllocator').AllocatorContainerReuseRejectionReason
| where PreciseTimeStamp between (queryFrom..queryTo)
| where rejectedContainerId in (query_ContainerId)
| where containerWorkflowStep == "ReuseContainer"
| where ruleName == "NetworkReuseRule"
| where reason contains "NetworkContainerAllocationIncarnation changed from 0 to"
| project PreciseTimeStamp, allocationId, containerWorkflowStep, rejectedContainerId, ruleName, reason
| join kind=inner (
cluster('https://azureallocator.westcentralus.kusto.windows.net').database('AzureAllocator').AllocatorAllocationResult
| where PreciseTimeStamp between (queryFrom .. queryTo)
| project allocationId, activityId, isSucceeded, allocationRequestType ) on allocationId
| join kind=inner (
cluster('Azcrp').database("crp_allprod").ApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| project operationId, operationName, correlationId) on $left.activityId == $right.operationId
| extend reused= iff(containerWorkflowStep == "ReuseContainer" and ruleName =="NetworkReuseRule" and reason contains "NetworkContainerAllocationIncarnation" and allocationRequestType contains "UpdateTenant"  ,"Potentially caused by Known Issue","")
| extend Recommendation = iif(reused == "Potentially caused by Known Issue","Please review the known issue information for more insights on current status.","")
| where isnotempty(Recommendation) 
| project ContainerId=rejectedContainerId,ruleName, reason, CRPActivityId=operationId,correlationId, operationName, Recommendation
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_ContainerId}`

**Signal filters seen in KQL:** `containerWorkflowStep == "ReuseContainer"` · `ruleName == "NetworkReuseRule"` · `reason contains "NetworkContainerAllocationIncarnation changed from 0 to"`

---

## v6 VM using TPM fails to start due to Underhill VM initialization failure

### v6VM_TPM_fails_start_due_to_Underhill_VM_initialization

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > v6 VM using TPM fails to start due to Underhill VM initialization failure`

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
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`, `{queryVMID}`

---

## VM creation failure due to 0xc3510224 VMAL_ASAPPF_NOT_RUNNING

### VM_creation_failure_0xc3510224_VMAL_ASAPPF_NOT_RUNNING

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > VM creation failure due to 0xc3510224 VMAL_ASAPPF_NOT_RUNNING`

```kusto
TMMgmtNodeEventsEtwTable  
| where TIMESTAMP between (queryFrom .. queryTo) and NodeId =~ querynodeId  and (Message has '0xc3510224' and Message has 'VMAL_ASAPPF_NOT_RUNNING')
| project PreciseTimeStamp=TIMESTAMP, Message
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querynodeId}`

---
