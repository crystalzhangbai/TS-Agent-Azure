# Detectors — NVMe / Storage / Disk

> Source: EEE RDOS Start Hub dashboard (9 queries).

Local NVMe, BlobCache, data-disk, and storage driver signatures. Run when disk IO blips, missing local NVMe, or storage-related crashes are suspected.

---

### IssueDetector_EI_AirDiskBlip_BlobCache_Write_during_Congestion

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

### IssueDetector_EI_High_Flush_latencies_due_to_driver_issue

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

> ⚠️ Verbose machine-generated KQL (75 KB, e.g. histogram aggregations expanded across many bins). Full body extracted to [`10c-detectors-nvme-storage-disk--issuedetector-ei-high-flush-latencies-due-to-driver-issue.kql`](10c-detectors-nvme-storage-disk--issuedetector-ei-high-flush-latencies-due-to-driver-issue.kql); the opening lines are shown below for context. Nothing is truncated — the full query is preserved verbatim in the `.kql` file.

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
// ... [truncated — see 10c-detectors-nvme-storage-disk--issuedetector-ei-high-flush-latencies-due-to-driver-issue.kql for full body]
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`, `{blobPath}`, `{Cloud}`

**Signal filters seen in KQL:** `HistogramTypeDesc == "Flush Latencies with Throttle time"`

---

### IssueDetector_EI_Attaching_Multiple_DataDisks_Over_Nvme_restart

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

### IssueDetector_EI_Dalds_v6_Windows_2025_datadisk_perf

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

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

### IssueDetector_NVME_HW_troubleshooting

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

### IssueDetector_EI_Ultra_PremV2_DiskBlip_during_VDC_driver_update

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

### IssueDetector_EI_Local_NVMe_Disks_Are_Missing_In_Lv4_Series

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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

### IssueDetector_EI_NVMeVmHighDiskLatency_due_to_CacheHint

_Purpose:_ Automated Detector

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `IssueDetector`

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

### IssueDetector_EI_NVMe_Controller_VM_experience_stornvme_reset

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

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
