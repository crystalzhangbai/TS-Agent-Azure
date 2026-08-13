# Emerging Issues — High Flush latencies due to driver issue

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Emerging Issues** (1 queries, part 2 of 4).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## High Flush latencies due to driver issue

### HighFlushLatenciesDueToDriverIssue

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > High Flush latencies due to driver issue`

> ⚠️ Verbose machine-generated KQL (75 KB, e.g. histogram aggregations expanded across many bins). Full body extracted to [`03b-emerging-issues--high-flush-latencies-due-to-driver-issue--highflushlatenciesduetodriverissue.kql`](03b-emerging-issues--high-flush-latencies-due-to-driver-issue--highflushlatenciesduetodriverissue.kql); the opening lines are shown below for context. Nothing is truncated — the full query is preserved verbatim in the `.kql` file.

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
// ... [truncated — see 03b-emerging-issues--high-flush-latencies-due-to-driver-issue--highflushlatenciesduetodriverissue.kql for full body]
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{querySubscription}`, `{queryroleInstanceName}`, `{querycontainerId}`, `{querytenantName}`, `{queryvirtualMachineUniqueId}`, `{queryTenant}`, `{blobPath}`, `{Cloud}`

**Signal filters seen in KQL:** `HistogramTypeDesc == "Flush Latencies with Throttle time"`

---
