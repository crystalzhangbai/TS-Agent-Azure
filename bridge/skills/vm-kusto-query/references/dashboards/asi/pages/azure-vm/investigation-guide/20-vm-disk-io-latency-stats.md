# VM Disk IO Latency Stats

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Disk IO Latency Stats** (5 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ASAP Latency Bucket Summary

### Azure Host VM ASAP Latency Stats

_Widget purpose:_ ASAP Latency Bucket Summary

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Disk IO Latency Stats > ASAP Latency Bucket Summary`

**Tables:** `OsAsapCounterTable`
**Aggregations:** `summarize Gt_500us = countif(counter >= 0.5), Gt_1ms = countif(counter >= 1), Lt_2ms = cou by HistogramTypeDesc = "ASAP Bqe Reads"` · `summarize Gt_500us = countif(counter >= 0.5), Gt_1ms = countif(counter >= 1), Lt_2ms = cou by HistogramTypeDesc = "ASAP Bqe Writes"`

```kusto
let asap_max_counters = OsAsapCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and ContainerId contains containerId 
| extend MaxBqeReadLatencyInMS = DeltaBqeLatencyDiskReadIoBucketMaxLatency / 1000.0,
         MaxBqeWriteLatencyInMS = DeltaBqeLatencyDiskWriteIoBucketMaxLatency / 1000.0,
         MaxFOBackendReadLatencyInMS = DeltaBackendLatencyDiskReadIoBucketMaxLatency / 1000.0,
         MaxFOBackendWriteLatencyInMS = DeltaBackendLatencyDiskWriteIoBucketMaxLatency / 1000.0,
         MaxSchedReadLatencyInMS = DeltaSchedLatencyDiskReadIoBucketMaxLatency / 1000.0,
         MaxSchedWriteLatencyInMS = DeltaSchedLatencyDiskWriteIoBucketMaxLatency / 1000.0
//| parse blobPath with "XDISK:" blobPathStr "/" * // dd blobpath parsing
//| where isempty(blobPath) or BlobPath contains blobPathStr or BlobPath contains blobPath
;
let asap_bqe_read = asap_max_counters 
    | extend counter = MaxBqeReadLatencyInMS
    | summarize
        Gt_500us = countif(counter >= 0.5),
        Gt_1ms = countif(counter >= 1),
        Lt_2ms = countif(counter < 2),
        Gt_2ms = countif(counter >= 2),
        Gt_5ms = countif(counter >= 5),
        Gt_10ms = countif(counter >= 10),
        Gt_20ms = countif(counter >= 20),
        Gt_50ms = countif(counter >= 50),
        Gt_100ms = countif(counter >= 100),
        Gt_200ms = countif(counter >= 200),
        Gt_500ms = countif(counter >= 500),
        Gt_1_Sec = countif(counter >= 1000),
        Gt_2_Sec = countif(counter >= 2000),
        Gt_5_Sec = countif(counter >= 5000),
        Gt_10_Sec = countif(counter >= 10000),
        Gt_15_Sec = countif(counter >= 15000),
        Gt_30_Sec = countif(counter >= 30000),
        Q100_InMS = max(counter) by HistogramTypeDesc = "ASAP Bqe Reads";
let asap_bqe_write = asap_max_counters | extend counter = MaxBqeWriteLatencyInMS
    | summarize
        Gt_500us = countif(counter >= 0.5),
        Gt_1ms = countif(counter >= 1),
        Lt_2ms = countif(counter < 2),
        Gt_2ms = countif(counter >= 2),
        Gt_5ms = countif(counter >= 5),
        Gt_10ms = countif(counter >= 10),
        Gt_20ms = countif(counter >= 20),
        Gt_50ms = countif(counter >= 50),
        Gt_100ms = countif(counter >= 100),
        Gt_200ms = countif(counter >= 200),
        Gt_500ms = countif(counter >= 500),
        Gt_1_Sec = countif(counter >= 1000),
        Gt_2_Sec = countif(counter >= 2000),
        Gt_5_Sec = countif(counter >= 5000),
        Gt_10_Sec = countif(counter >= 10000),
        Gt_15_Sec = countif(counter >= 15000),
        Gt_30_Sec = countif(counter >= 30000),
        Q100_InMS = max(counter) by HistogramTypeDesc = "ASAP Bqe Writes";
let asap_backend_read = asap_max_counters | extend counter = MaxFOBackendReadLatencyInMS
    | summarize
        Gt_500us = countif(counter >= 0.5),
        Gt_1ms = countif(counter >= 1),
        Lt_2ms = countif(counter < 2),
        Gt_2ms = countif(counter >= 2),
        Gt_5ms = countif(counter >= 5),
        Gt_10ms = countif(counter >= 10),
        Gt_20ms = countif(counter >= 20),
        Gt_50ms = countif(counter >= 50),
        Gt_100ms = countif(counter >= 100),
        Gt_200ms = countif(counter >= 200),
        Gt_500ms = countif(counter >= 500),
        Gt_1_Sec = countif(counter >= 1000),
        Gt_2_Sec = countif(counter >= 2000),
        Gt_5_Sec = countif(counter >= 5000),
        Gt_10_Sec = countif(counter >= 10000),
        Gt_15_Sec = countif(counter >= 15000),
        Gt_30_Sec = countif(counter >= 30000),
        Q100_InMS = max(counter) by HistogramTypeDesc = "ASAP FO Backend Reads";
let asap_backend_write = asap_max_counters | extend counter = MaxFOBackendWriteLatencyInMS
    | summarize
        Gt_500us = countif(counter >= 0.5),
        Gt_1ms = countif(counter >= 1),
        Lt_2ms = countif(counter < 2),
        Gt_2ms = countif(counter >= 2),
        Gt_5ms = countif(counter >= 5),
        Gt_10ms = countif(counter >= 10),
        Gt_20ms = countif(counter >= 20),
        Gt_50ms = countif(counter >= 50),
        Gt_100ms = countif(counter >= 100),
        Gt_200ms = countif(counter >= 200),
        Gt_500ms = countif(counter >= 500),
        Gt_1_Sec = countif(counter >= 1000),
        Gt_2_Sec = countif(counter >= 2000),
        Gt_5_Sec = countif(counter >= 5000),
        Gt_10_Sec = countif(counter >= 10000),
        Gt_15_Sec = countif(counter >= 15000),
        Gt_30_Sec = countif(counter >= 30000),
        Q100_InMS = max(counter) by HistogramTypeDesc = "ASAP FO Backend Writes";
let asap_sched_read = asap_max_counters | extend counter = MaxSchedReadLatencyInMS
    | summarize
        Gt_500us = countif(counter >= 0.5),
        Gt_1ms = countif(counter >= 1),
        Lt_2ms = countif(counter < 2),
        Gt_2ms = countif(counter >= 2),
        Gt_5ms = countif(counter >= 5),
        Gt_10ms = countif(counter >= 10),
        Gt_20ms = countif(counter >= 20),
        Gt_50ms = countif(counter >= 50),
        Gt_100ms = countif(counter >= 100),
        Gt_200ms = countif(counter >= 200),
        Gt_500ms = countif(counter >= 500),
        Gt_1_Sec = countif(counter >= 1000),
        Gt_2_Sec = countif(counter >= 2000),
        Gt_5_Sec = countif(counter >= 5000),
        Gt_10_Sec = countif(counter >= 10000),
        Gt_15_Sec = countif(counter >= 15000),
        Gt_30_Sec = countif(counter >= 30000),
        Q100_InMS = max(counter) by  HistogramTypeDesc = "ASAP Scheduler Reads";
let asap_sched_write = asap_max_counters | extend counter = MaxSchedWriteLatencyInMS
    | summarize
        Gt_500us = countif(counter >= 0.5),
        Gt_1ms = countif(counter >= 1),
        Lt_2ms = countif(counter < 2),
        Gt_2ms = countif(counter >= 2),
        Gt_5ms = countif(counter >= 5),
        Gt_10ms = countif(counter >= 10),
        Gt_20ms = countif(counter >= 20),
        Gt_50ms = countif(counter >= 50),
        Gt_100ms = countif(counter >= 100),
        Gt_200ms = countif(counter >= 200),
        Gt_500ms = countif(counter >= 500),
        Gt_1_Sec = countif(counter >= 1000),
        Gt_2_Sec = countif(counter >= 2000),
        Gt_5_Sec = countif(counter >= 5000),
        Gt_10_Sec = countif(counter >= 10000),
        Gt_15_Sec = countif(counter >= 15000),
        Gt_30_Sec = countif(counter >= 30000),
        Q100_InMS = max(counter) by  HistogramTypeDesc = "ASAP Scheduler Writes";
let asap_total_read = asap_max_counters | extend counter = DeltaIoLatencyDiskReadIoBucketMaxLatency / 1000.0
    | summarize
        Gt_500us = countif(counter >= 0.5),
        Gt_1ms = countif(counter >= 1),
        Lt_2ms = countif(counter < 2),
        Gt_2ms = countif(counter >= 2),
        Gt_5ms = countif(counter >= 5),
        Gt_10ms = countif(counter >= 10),
        Gt_20ms = countif(counter >= 20),
        Gt_50ms = countif(counter >= 50),
        Gt_100ms = countif(counter >= 100),
        Gt_200ms = countif(counter >= 200),
        Gt_500ms = countif(counter >= 500),
        Gt_1_Sec = countif(counter >= 1000),
        Gt_2_Sec = countif(counter >= 2000),
        Gt_5_Sec = countif(counter >= 5000),
        Gt_10_Sec = countif(counter >= 10000),
        Gt_15_Sec = countif(counter >= 15000),
        Gt_30_Sec = countif(counter >= 30000),
        Q100_InMS = max(counter) by  HistogramTypeDesc = "ASAP Reads";
let asap_total_write = asap_max_counters | extend counter = DeltaIoLatencyDiskWriteIoBucketMaxLatency / 1000.0
    | summarize
        Gt_500us = countif(counter >= 0.5),
        Gt_1ms = countif(counter >= 1),
        Lt_2ms = countif(counter < 2),
        Gt_2ms = countif(counter >= 2),
        Gt_5ms = countif(counter >= 5),
        Gt_10ms = countif(counter >= 10),
        Gt_20ms = countif(counter >= 20),
        Gt_50ms = countif(counter >= 50),
        Gt_100ms = countif(counter >= 100),
        Gt_200ms = countif(counter >= 200),
        Gt_500ms = countif(counter >= 500),
        Gt_1_Sec = countif(counter >= 1000),
        Gt_2_Sec = countif(counter >= 2000),
        Gt_5_Sec = countif(counter >= 5000),
        Gt_10_Sec = countif(counter >= 10000),
        Gt_15_Sec = countif(counter >= 15000),
        Gt_30_Sec = countif(counter >= 30000), 
        Q100_InMS = max(counter) 
        by  HistogramTypeDesc = "ASAP Writes";
union asap_bqe_read, asap_bqe_write, asap_backend_read, asap_backend_write, 
        asap_sched_read, asap_sched_write, asap_total_read, asap_total_write
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

## Hyper-V Layer Latency Bucket Summary

### Azure Host VM Hyperv Disk Stats

_Widget purpose:_ Hyper-V Layer Latency Bucket Summary

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Disk IO Latency Stats > Hyper-V Layer Latency Bucket Summary`

**Tables:** `HyperVStorageStackTable`
**Aggregations:** `summarize TotalIOsGt1s = sum(count_1s) + sum(count_5s) + sum(count_10s) + sum(count_20s) +`
**Output columns:** `MessageJson`

```kusto
let nodeStorageEvents = materialize(cluster("azcore.centralus.kusto.windows.net").database("Fa").HyperVStorageStackTable
                        | where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and Message contains containerId);
nodeStorageEvents
| where EventId == 300 or EventId == 301
| project PreciseTimeStamp, MessageJson = parse_json(Message)
| where MessageJson.DeviceName contains containerId
| extend VHDMPPath = MessageJson.DeviceName, IoType = tostring(MessageJson.IoTypeStr), 
        count_1s = toint(MessageJson.IoCount10), 
        count_5s = toint(MessageJson.IoCount11), 
        count_10s = toint(MessageJson.IoCount12), 
        count_20s = toint(MessageJson.IoCount13), 
        count_30s = toint(MessageJson.IoCount14), 
        count_gt30s = toint(MessageJson.IoCount15)
| project-away MessageJson
| summarize TotalIOsGt1s = sum(count_1s) + sum(count_5s) + sum(count_10s) + sum(count_20s) + sum(count_30s) + sum(count_30s),
            TotalIOsGt5s = sum(count_5s) + sum(count_10s) + sum(count_20s) + sum(count_30s) + sum(count_30s),
            TotalIOsGt10s = sum(count_10s) + sum(count_20s) + sum(count_30s) + sum(count_30s),
            TotalIOsGt20s = sum(count_20s) + sum(count_30s) + sum(count_30s),
            TotalIOsGt30s = sum(count_30s)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

## IO Latency Analysis

### AzureHost VM Disk IO Latency Analysis

_Widget purpose:_ IO Latency Analysis

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Disk IO Latency Stats > IO Latency Analysis`

**Aggregations:** `summarize R_XSTORE_RDMA_Q95 = max(column_ifexists("Reads as seen by XSTORE (for STCP + RDM`

```kusto
CalculateLatencyHistogramForContainer(containerId, startTime, endTime)
| evaluate pivot(HistogramTypeDesc, max(All_Q95))
| summarize R_XSTORE_RDMA_Q95 = max(column_ifexists("Reads as seen by XSTORE (for STCP + RDMA)", 0)),
            R_XSTORE_RDMA_T = max(column_ifexists("Reads as seen by XSTORE (for STCP + RDMA)", 0)),
            R_VHDDISK_STCP_Q95 = max(column_ifexists("Reads using STCP (Vhddisk)", 0)),
            R_VHDDISK_RDMA_Q95 = max(column_ifexists("Reads using RDMA (Vhddisk)", 0)),
            R_BLOBCACHE_Q95 = max(column_ifexists("Reads from BackingStore (BlobCache)", 0)),
            W_XSTORE_RDMA_Q95 = max(column_ifexists("Writes as seen by XSTORE (for STCP + RDMA)", 0)),
            W_VHDDISK_STCP_Q95 = max(column_ifexists("Writes using STCP (Vhddisk)", 0)),
            W_VHDDISK_RDMA_Q95 = max(column_ifexists("Writes using RDMA (Vhddisk)", 0)),
            W_BLOBCACHE_Q95 = max(column_ifexists("Write Through (BlobCache)", 0))
| project 
          Read_Q95_Latency_Analysis = case(R_XSTORE_RDMA_Q95 * 1.25 > R_VHDDISK_RDMA_Q95 or R_XSTORE_RDMA_Q95 * 1.25 > R_VHDDISK_STCP_Q95, "Reads: XSTORE Server Latencies seems higher. Please escalate to XStore\\Triage.", ""),
          Write_Q95_Latency_Analysis = case(W_XSTORE_RDMA_Q95 * 1.25 > W_VHDDISK_RDMA_Q95 or W_XSTORE_RDMA_Q95 * 1.25 > W_VHDDISK_STCP_Q95, "Writes: XSTORE Server Latencies seems higher. Please escalate to XStore\\Triage.", "")
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

## StorageClient IO Stats

### Azure Host VM StorageClient IO Latency Stats

_Widget purpose:_ StorageClient IO Stats

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Disk IO Latency Stats > StorageClient IO Stats`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize hint.strategy=shuffle Bin_Count = sum(Bin_Count), Bin_01 = sum(Bin_01), Bin_02 = by HistogramTypeEnum, HistogramTypeDesc, HistogramVersion, IOSizeBucket` · `summarize hint.strategy=shuffle Gt_500us = sum(Bin_21) + sum(Bin_22) + sum(Bin_23) + sum(B by HistogramTypeEnum, HistogramTypeDesc, HistogramVersion`

> ⚠️ Verbose machine-generated KQL (73 KB, e.g. histogram aggregations expanded across many bins). Full body extracted to [`20-vm-disk-io-latency-stats--azure-host-vm-storageclient-io-latency-stats.kql`](20-vm-disk-io-latency-stats--azure-host-vm-storageclient-io-latency-stats.kql); the opening lines are shown below for context. Nothing is truncated — the full query is preserved verbatim in the `.kql` file.

```kusto
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and SurfaceName contains containerId
| where HistogramTypeEnum != 4 // Removing Flush, since Flush and Flush with throttling are the same.
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and SurfaceName contains containerId
)
| extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and ContainerId == containerId
    | extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    //
    // For UltraDisk, we have more granular IO Size Buckets
    // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
    //
    | extend IOSizeBucket = case(IOSizeBucket in (0, 1) and TelemetryVersion >= 2, 0, // 0 - 8k
                                IOSizeBucket == 2 and TelemetryVersion >= 2, 1, // 8 - 64k
                                IOSizeBucket == 3 and TelemetryVersion >= 2, 2, // 64+
                                IOSizeBucket == 4 and TelemetryVersion >= 2, 3, // all IO Sizes
                                IOSizeBucket)
    | where SurfaceName contains containerId
)
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
                Bin_137 = sum(Bin_137), Bin_138 = sum(Bin_138), Bin_139 = sum(Bin_139), Bin_140 = sum(Bin_140), Bin_141 = sum(Bin_141), Bin_142 = sum(Bin_142), Bin_143 = sum(Bin_143), Bin_144 = sum(Bin_144),
                Bin_145 = sum(Bin_145), Bin_146 = sum(Bin_146), Bin_147 = sum(Bin_147), Bin_148 = sum(Bin_148), Bin_149 = sum(Bin_149), Bin_150 = sum(Bin_150), Bin_151 = sum(Bin_151), Bin_152 = sum(Bin_152),
                Bin_153 = sum(Bin_153), Bin_154 = sum(Bin_154), Bin_155 = sum(Bin_155), Bin_156 = sum(Bin_156), Bin_157 = sum(Bin_157), Bin_158 = sum(Bin_158), Bin_159 = sum(Bin_159), Bin_160 = sum(Bin_160),
                Bin_161 = sum(Bin_161), Bin_162 = sum(Bin_162), Bin_163 = sum(Bin_163), Bin_164 = sum(Bin_164), Bin_165 = sum(Bin_165), Bin_166 = sum(Bin_166), Bin_167 = sum(Bin_167), Bin_168 = sum(Bin_168),
                Bin_169 = sum(Bin_169), Bin_170 = sum(Bin_170), Bin_171 = sum(Bin_171), Bin_172 = sum(Bin_172), Bin_173 = sum(Bin_173), Bin_174 = sum(Bin_174), Bin_175 = sum(Bin_175), Bin_176 = sum(Bin_176),
                Bin_177 = sum(Bin_177), Bin_178 = sum(Bin_178), Bin_179 = sum(Bin_179), Bin_180 = sum(Bin_180), Bin_181 = sum(Bin_181), Bin_182 = sum(Bin_182), Bin_183 = sum(Bin_183), Bin_184 = sum(Bin_184),
                Bin_185 = sum(Bin_185), Bin_186 = sum(Bin_186), Bin_187 = sum(Bin_187), Bin_188 = sum(Bin_188), Bin_189 = sum(Bin_189), Bin_190 = sum(Bin_190), Bin_191 = sum(Bin_191), Bin_192 = sum(Bin_192),
                Bin_193 = sum(Bin_193), Bin_194 = sum(Bin_194), Bin_195 = sum(Bin_195), Bin_196 = sum(Bin_196), Bin_197 = sum(Bin_197), Bin_198 = sum(Bin_198), Bin_199 = sum(Bin_199), Bin_200 = sum(Bin_200),
                Bin_201 = sum(Bin_201), Bin_202 = sum(Bin_202), Bin_203 = sum(Bin_203), Bin_204 = sum(Bin_204), Bin_205 = sum(Bin_205), Bin_206 = sum(Bin_206), Bin_207 = sum(Bin_207), Bin_208 = sum(Bin_208),
                Bin_209 = sum(Bin_209), Bin_210 = sum(Bin_210), Bin_211 = sum(Bin_211), Bin_212 = sum(Bin_212), Bin_213 = sum(Bin_213), Bin_214 = sum(Bin_214), Bin_215 = sum(Bin_215), Bin_216 = sum(Bin_216),
                Bin_217 = sum(Bin_217), Bin_218 = sum(Bin_218), Bin_219 = sum(Bin_219), Bin_220 = sum(Bin_220), Bin_221 = sum(Bin_221), Bin_222 = sum(Bin_222), Bin_223 = sum(Bin_223), Bin_224 = sum(Bin_224),
                Bin_225 = sum(Bin_225), Bin_226 = sum(Bin_226), Bin_227 = sum(Bin_227), Bin_228 = sum(Bin_228), Bin_229 = sum(Bin_229), Bin_230 = sum(Bin_230), Bin_231 = sum(Bin_231), Bin_232 = sum(Bin_232),
                Bin_233 = sum(Bin_233), Bin_234 = sum(Bin_234), Bin_235 = sum(Bin_235), Bin_236 = sum(Bin_236), Bin_237 = sum(Bin_237), Bin_238 = sum(Bin_238), Bin_239 = sum(Bin_239), Bin_240 = sum(Bin_240),
// ... [truncated — see 20-vm-disk-io-latency-stats--azure-host-vm-storageclient-io-latency-stats.kql for full body]
```

**Params:** `{containerId}`, `{startTime}`, `{endTime}`, `{blobPath}`, `{nodeId}`, `{Cloud}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ StorageClient IO Stats

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `Table`
Source panel: `VM Disk IO Latency Stats > StorageClient IO Stats`

**Tables:** `OsXIOHealthSignalEvent`, `OsRDSSDHealthSignalEvent`, `OsUltraSSDHealthSignalEvent`

```kusto
let xioDisks = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let rdssdDisks = OsRDSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct BlobPath, SurfaceName;
let ddDisks = OsUltraSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId
| distinct BlobPath, SurfaceName = SurfaceGUID;
union xioDisks, rdssdDisks, ddDisks
| extend BlobPath = case(isempty(BlobPath), SurfaceName, BlobPath)
| parse BlobPath with NewValue "?" *
| extend Value = case(isempty(NewValue), BlobPath, NewValue)
| distinct Value
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---
