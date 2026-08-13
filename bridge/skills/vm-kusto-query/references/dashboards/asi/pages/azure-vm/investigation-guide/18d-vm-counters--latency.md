# VM Counters — Latency

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Counters** (49 queries, part 4 of 7).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## Latency

### Azure Host VM HyperV Latency Query

_Widget purpose:_ IO Latencies

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > Latency > Latency > HyperV > IO Latencies`

**Tables:** `HyperVStorageStackTable`
**Output columns:** `PreciseTimeStamp`, `Level`, `EventId`, `TaskName`, `EventMessage`, `TimeInMs`, `Message`

```kusto
HyperVStorageStackTable 
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where Message has_any (containerId) and EventId == 9
| parse EventMessage with * " took " TimeInMs " milliseconds" *
| project PreciseTimeStamp, Level, EventId, TaskName, EventMessage, TimeInMs, Message
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host Node Mellanox QoS counters

_Widget purpose:_ Mellanox QoS Counters

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > Networking > Mellanox QoS Counters`

**Tables:** `Mlx5QoSCounters`
**Aggregations:** `summarize Host_to_Tor_Pause_Duration_Sec = max(Sent_Pause_Duration)/1e6,Tor_to_Host = max( by bin(PreciseTimeStamp, 1m), Priority`

```kusto
cluster("Netperf").database("NetPerfKustoDB").Mlx5QoSCounters 
| where Priority in~ ("Priority 3","Priority 4") and TIMESTAMP between (startTime .. endTime) and NodeId in~ (nodeId)
| summarize Host_to_Tor_Pause_Duration_Sec = max(Sent_Pause_Duration)/1e6,Tor_to_Host = max(Rcv_Pause_Duration)/1e6 by bin(PreciseTimeStamp, 1m), Priority
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### RDMA Client Latency from local to peers

_Widget purpose:_ RDMA Client Latency (in microseconds) from local to peers

Cluster: `azurehn.kusto.windows.net` · Database: `Azurehn` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > Networking > RDMA Client Latency (in microseconds) from local to peers`

**Tables:** `f_getNodeIdFromContainerId`, `EStatsClientLatencyPerApp`
**Aggregations:** `summarize avg(P50), avg(P90), avg(P99), avg(P99_9), avg(P99_99) //, max(Max) by bin(PreciseTimeStamp, 1m)`

```kusto
let impactedContainerId = ["containerId"];
let impactStartTime =["startTime"];
let impactEndTime = ["endTime"];
let latestNodeId = materialize(cluster('azurehn.kusto.windows.net').database('Azurehn').f_getNodeIdFromContainerId(impactedContainerId, impactStartTime - 2h, impactEndTime + 2h));
let impactedNodeId = iff(isnotempty(["nodeId"]), ["nodeId"], toscalar(latestNodeId));
// how long does each NDK operation take (send, read, write) from when posted by SW to when completion received
cluster('netperf.kusto.windows.net').database('NetPerfKustoDB').EStatsClientLatencyPerApp
| where NodeId =~ impactedNodeId
| where PreciseTimeStamp >= impactStartTime and PreciseTimeStamp <= impactEndTime
//| where OperationStatus == 'SUCCESS'
| summarize avg(P50), avg(P90), avg(P99), avg(P99_9), avg(P99_99)
    //, max(Max) 
    by bin(PreciseTimeStamp, 1m)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

**Signal filters seen in KQL:** `OperationStatus == "SUCCESS"`

---

### RDMA Client Latency from peers to local

_Widget purpose:_ RDMA Client Latency (in microseconds) from peers to local

Cluster: `azurehn.kusto.windows.net` · Database: `Azurehn` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > Networking > RDMA Client Latency (in microseconds) from peers to local`

**Tables:** `f_getNodeIdFromContainerId`, `dcmInventoryGenerationMappingV3`, `f_getRDMAPeers`, `EStatsClientLatencyPerApp`
**Aggregations:** `summarize avg(P50), avg(P90), avg(P99), avg(P99_9), avg(P99_99) //, max(Max) by bin(PreciseTimeStamp, 1m)`

```kusto
let peers = dynamic(null);
let impactedContainerId = ["containerId"];
let impactStartTime =["startTime"];
let impactEndTime = ["endTime"];
let latestNodeId = materialize(cluster('azurehn.kusto.windows.net').database('Azurehn').f_getNodeIdFromContainerId(impactedContainerId, impactStartTime - 2h, impactEndTime + 2h));
let impactedNodeId = iff(isnotempty(["nodeId"]), ["nodeId"], toscalar(latestNodeId));
let localIP = toscalar(cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').dcmInventoryGenerationMappingV3
| where NodeId =~ impactedNodeId
| project IpAddress);
let selectedPeerNodeIDs = ["peers"];
let peerNodeIDs = materialize(cluster('azurehn.kusto.windows.net').database('Azurehn').f_getRDMAPeers(impactedNodeId, impactStartTime, impactEndTime));
// how long does each NDK operation take (send, read, write) from when posted by SW to when completion received
cluster('netperf.kusto.windows.net').database('NetPerfKustoDB').EStatsClientLatencyPerApp
| where ((isempty(selectedPeerNodeIDs) and NodeId in (peerNodeIDs)) or NodeId in (selectedPeerNodeIDs)) and DestIp == localIP
| where PreciseTimeStamp >= impactStartTime and PreciseTimeStamp <= impactEndTime
//| where OperationStatus == 'SUCCESS'
| summarize avg(P50), avg(P90), avg(P99), avg(P99_9), avg(P99_99) 
 //, max(Max)
 by bin(PreciseTimeStamp, 1m)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

**Signal filters seen in KQL:** `OperationStatus == "SUCCESS"`

---

### Azure Host Node RDMA Estats HW Latency Local to Peers

_Widget purpose:_ RDMA Hardware Latency (in microseconds) from local to peers

Cluster: `netperf` · Database: `NetPerfKustoDB` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > Networking > RDMA Hardware Latency (in microseconds) from local to peers`

**Tables:** `EStatsHardwareLatencyPerApp`
**Aggregations:** `summarize avg(P50), avg(P90), avg(P99), avg(P99_9), avg(P99_99) by bin(PreciseTimeStamp, 1m)`

```kusto
cluster('netperf.kusto.windows.net').database('NetPerfKustoDB').EStatsHardwareLatencyPerApp
| where NodeId =~ nodeId
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| summarize avg(P50), avg(P90), avg(P99), avg(P99_9), avg(P99_99)
    by bin(PreciseTimeStamp, 1m)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host RDMA Estats Hardware Peers to local

_Widget purpose:_ RDMA Hardware Latency (in microseconds) from peers to local

Cluster: `netperf` · Database: `NetPerfKustoDB` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > Networking > RDMA Hardware Latency (in microseconds) from peers to local`

**Tables:** `dcmInventoryGenerationMappingV3`, `f_getRDMAPeers`, `EStatsHardwareLatencyPerApp`
**Aggregations:** `summarize avg(P50), avg(P90), avg(P99), avg(P99_9), avg(P99_99) // , max(Max) by bin(PreciseTimeStamp, 1m)`

```kusto
let localIP = toscalar(cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').dcmInventoryGenerationMappingV3
| where NodeId =~ nodeId
            | project IpAddress);
let peers = dynamic(null);
let selectedPeerNodeIDs = ["peers"];
let peerNodeIDs = materialize(cluster('azurehn.kusto.windows.net').database('Azurehn').f_getRDMAPeers(nodeId, queryFrom, queryTo));
// how long does each NDK operation take (send, read, write) from when posted by SW to when completion received
cluster('netperf.kusto.windows.net').database('NetPerfKustoDB').EStatsHardwareLatencyPerApp
| where ((isempty(selectedPeerNodeIDs) and NodeId in (peerNodeIDs)) or NodeId in (selectedPeerNodeIDs)) and DestIp == localIP
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
//| where OperationStatus == 'SUCCESS'
| summarize 
    avg(P50), avg(P90), avg(P99), avg(P99_9), avg(P99_99)
    // , max(Max) 
    by bin(PreciseTimeStamp, 1m)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

**Signal filters seen in KQL:** `OperationStatus == "SUCCESS"`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ IO Stats by TimeTaken (select the Histogram Layer)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > IO Stats > IO Stats > IO Stats by TimeTaken (select the Histogram Layer)`

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

### Azure Host VM IO Stats Ex by HistogramType

_Widget purpose:_ IO Stats by TimeTaken (select the Histogram Layer)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > IO Stats > IO Stats > IO Stats by TimeTaken (select the Histogram Layer)`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize Gt_500us = sum(Bin_21) + sum(Bin_22) + sum(Bin_23) + sum(Bin_24) + sum(Bin_25) + by bin(PreciseTimeStamp, 5s)`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
)
| where isempty(histogramDesc) or HistogramDesc == histogramDesc
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| where isempty(blobPath) or BlobPath == blobPath
| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
| summarize Gt_500us = sum(Bin_21) + sum(Bin_22) + sum(Bin_23) + sum(Bin_24) + sum(Bin_25) + sum(Bin_26) + sum(Bin_27) + sum(Bin_28) + sum(Bin_29) + sum(Bin_30) + sum(Bin_31) + sum(Bin_32) + sum(Bin_33) + sum(Bin_34) + sum(Bin_35) + sum(Bin_36) + sum(Bin_37) + sum(Bin_38) + sum(Bin_39) + sum(Bin_40) + sum(Bin_41) + sum(Bin_42) + sum(Bin_43) + sum(Bin_44) + sum(Bin_45) + sum(Bin_46) + sum(Bin_47) + sum(Bin_48) + sum(Bin_49) + sum(Bin_50) + sum(Bin_51) + sum(Bin_52) + sum(Bin_53) + sum(Bin_54) + sum(Bin_55) + sum(Bin_56) + sum(Bin_57) + sum(Bin_58) + sum(Bin_59) + sum(Bin_60) + sum(Bin_61) + sum(Bin_62) + sum(Bin_63) + sum(Bin_64) + sum(Bin_65) + sum(Bin_66) + sum(Bin_67) + sum(Bin_68) + sum(Bin_69) + sum(Bin_70) + sum(Bin_71) + sum(Bin_72) + sum(Bin_73) + sum(Bin_74) + sum(Bin_75) + sum(Bin_76) + sum(Bin_77) + sum(Bin_78) + sum(Bin_79) + sum(Bin_80) + sum(Bin_81) + sum(Bin_82) + sum(Bin_83) + sum(Bin_84) + sum(Bin_85) + sum(Bin_86) + sum(Bin_87) + sum(Bin_88) + sum(Bin_89) + sum(Bin_90) + sum(Bin_91) + sum(Bin_92) + sum(Bin_93) + sum(Bin_94) + sum(Bin_95) + sum(Bin_96) + sum(Bin_97) + sum(Bin_98) + sum(Bin_99) + sum(Bin_100) + sum(Bin_101) + sum(Bin_102) + sum(Bin_103) + sum(Bin_104) + sum(Bin_105) + sum(Bin_106) + sum(Bin_107) + sum(Bin_108) + sum(Bin_109) + sum(Bin_110) + sum(Bin_111) + sum(Bin_112) + sum(Bin_113) + sum(Bin_114) + sum(Bin_115) + sum(Bin_116) + sum(Bin_117) + sum(Bin_118) + sum(Bin_119) + sum(Bin_120) + sum(Bin_121) + sum(Bin_122) + sum(Bin_123) + sum(Bin_124) + sum(Bin_125) + sum(Bin_126) + sum(Bin_127) + sum(Bin_128) + sum(Bin_129) + sum(Bin_130) + sum(Bin_131) + sum(Bin_132) + sum(Bin_133) + sum(Bin_134) + sum(Bin_135) + sum(Bin_136) + sum(Bin_137) + sum(Bin_138) + sum(Bin_139) + sum(Bin_140) + sum(Bin_141) + sum(Bin_142) + sum(Bin_143) + sum(Bin_144) + sum(Bin_145) + sum(Bin_146) + sum(Bin_147) + sum(Bin_148) + sum(Bin_149) + sum(Bin_150) + sum(Bin_151) + sum(Bin_152) + sum(Bin_153) + sum(Bin_154) + sum(Bin_155) + sum(Bin_156) + sum(Bin_157) + sum(Bin_158) + sum(Bin_159) + sum(Bin_160) + sum(Bin_161) + sum(Bin_162) + sum(Bin_163) + sum(Bin_164) + sum(Bin_165) + sum(Bin_166) + sum(Bin_167) + sum(Bin_168) + sum(Bin_169) + sum(Bin_170) + sum(Bin_171) + sum(Bin_172) + sum(Bin_173) + sum(Bin_174) + sum(Bin_175) + sum(Bin_176) + sum(Bin_177) + sum(Bin_178) + sum(Bin_179) + sum(Bin_180) + sum(Bin_181) + sum(Bin_182) + sum(Bin_183) + sum(Bin_184) + sum(Bin_185) + sum(Bin_186) + sum(Bin_187) + sum(Bin_188) + sum(Bin_189) + sum(Bin_190) + sum(Bin_191) + sum(Bin_192) + sum(Bin_193) + sum(Bin_194) + sum(Bin_195) + sum(Bin_196) + sum(Bin_197) + sum(Bin_198) + sum(Bin_199) + sum(Bin_200) + sum(Bin_201) + sum(Bin_202) + sum(Bin_203) + sum(Bin_204) + sum(Bin_205) + sum(Bin_206) + sum(Bin_207) + sum(Bin_208) + sum(Bin_209) + sum(Bin_210) + sum(Bin_211) + sum(Bin_212) + sum(Bin_213) + sum(Bin_214) + sum(Bin_215) + sum(Bin_216) + sum(Bin_217) + sum(Bin_218) + sum(Bin_219) + sum(Bin_220) + sum(Bin_221) + sum(Bin_222) + sum(Bin_223) + sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_1ms = sum(Bin_41) + sum(Bin_42) + sum(Bin_43) + sum(Bin_44) + sum(Bin_45) + sum(Bin_46) + sum(Bin_47) + sum(Bin_48) + sum(Bin_49) + sum(Bin_50) + sum(Bin_51) + sum(Bin_52) + sum(Bin_53) + sum(Bin_54) + sum(Bin_55) + sum(Bin_56) + sum(Bin_57) + sum(Bin_58) + sum(Bin_59) + sum(Bin_60) + sum(Bin_61) + sum(Bin_62) + sum(Bin_63) + sum(Bin_64) + sum(Bin_65) + sum(Bin_66) + sum(Bin_67) + sum(Bin_68) + sum(Bin_69) + sum(Bin_70) + sum(Bin_71) + sum(Bin_72) + sum(Bin_73) + sum(Bin_74) + sum(Bin_75) + sum(Bin_76) + sum(Bin_77) + sum(Bin_78) + sum(Bin_79) + sum(Bin_80) + sum(Bin_81) + sum(Bin_82) + sum(Bin_83) + sum(Bin_84) + sum(Bin_85) + sum(Bin_86) + sum(Bin_87) + sum(Bin_88) + sum(Bin_89) + sum(Bin_90) + sum(Bin_91) + sum(Bin_92) + sum(Bin_93) + sum(Bin_94) + sum(Bin_95) + sum(Bin_96) + sum(Bin_97) + sum(Bin_98) + sum(Bin_99) + sum(Bin_100) + sum(Bin_101) + sum(Bin_102) + sum(Bin_103) + sum(Bin_104) + sum(Bin_105) + sum(Bin_106) + sum(Bin_107) + sum(Bin_108) + sum(Bin_109) + sum(Bin_110) + sum(Bin_111) + sum(Bin_112) + sum(Bin_113) + sum(Bin_114) + sum(Bin_115) + sum(Bin_116) + sum(Bin_117) + sum(Bin_118) + sum(Bin_119) + sum(Bin_120) + sum(Bin_121) + sum(Bin_122) + sum(Bin_123) + sum(Bin_124) + sum(Bin_125) + sum(Bin_126) + sum(Bin_127) + sum(Bin_128) + sum(Bin_129) + sum(Bin_130) + sum(Bin_131) + sum(Bin_132) + sum(Bin_133) + sum(Bin_134) + sum(Bin_135) + sum(Bin_136) + sum(Bin_137) + sum(Bin_138) + sum(Bin_139) + sum(Bin_140) + sum(Bin_141) + sum(Bin_142) + sum(Bin_143) + sum(Bin_144) + sum(Bin_145) + sum(Bin_146) + sum(Bin_147) + sum(Bin_148) + sum(Bin_149) + sum(Bin_150) + sum(Bin_151) + sum(Bin_152) + sum(Bin_153) + sum(Bin_154) + sum(Bin_155) + sum(Bin_156) + sum(Bin_157) + sum(Bin_158) + sum(Bin_159) + sum(Bin_160) + sum(Bin_161) + sum(Bin_162) + sum(Bin_163) + sum(Bin_164) + sum(Bin_165) + sum(Bin_166) + sum(Bin_167) + sum(Bin_168) + sum(Bin_169) + sum(Bin_170) + sum(Bin_171) + sum(Bin_172) + sum(Bin_173) + sum(Bin_174) + sum(Bin_175) + sum(Bin_176) + sum(Bin_177) + sum(Bin_178) + sum(Bin_179) + sum(Bin_180) + sum(Bin_181) + sum(Bin_182) + sum(Bin_183) + sum(Bin_184) + sum(Bin_185) + sum(Bin_186) + sum(Bin_187) + sum(Bin_188) + sum(Bin_189) + sum(Bin_190) + sum(Bin_191) + sum(Bin_192) + sum(Bin_193) + sum(Bin_194) + sum(Bin_195) + sum(Bin_196) + sum(Bin_197) + sum(Bin_198) + sum(Bin_199) + sum(Bin_200) + sum(Bin_201) + sum(Bin_202) + sum(Bin_203) + sum(Bin_204) + sum(Bin_205) + sum(Bin_206) + sum(Bin_207) + sum(Bin_208) + sum(Bin_209) + sum(Bin_210) + sum(Bin_211) + sum(Bin_212) + sum(Bin_213) + sum(Bin_214) + sum(Bin_215) + sum(Bin_216) + sum(Bin_217) + sum(Bin_218) + sum(Bin_219) + sum(Bin_220) + sum(Bin_221) + sum(Bin_222) + sum(Bin_223) + sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Lt_2ms = sum(Bin_01) + sum(Bin_02) + sum(Bin_03) + sum(Bin_04) + sum(Bin_05) + sum(Bin_06) + sum(Bin_07) + sum(Bin_08) + sum(Bin_09) + sum(Bin_10) + sum(Bin_11) + sum(Bin_12) + sum(Bin_13) + sum(Bin_14) + sum(Bin_15) + sum(Bin_16) + sum(Bin_17) + sum(Bin_18) + sum(Bin_19) + sum(Bin_20) + sum(Bin_21) + sum(Bin_22) + sum(Bin_23) + sum(Bin_24) + sum(Bin_25) + sum(Bin_26) + sum(Bin_27) + sum(Bin_28) + sum(Bin_29) + sum(Bin_30) + sum(Bin_31) + sum(Bin_32) + sum(Bin_33) + sum(Bin_34) + sum(Bin_35) + sum(Bin_36) + sum(Bin_37) + sum(Bin_38) + sum(Bin_39) + sum(Bin_40) + sum(Bin_41) + sum(Bin_42) + sum(Bin_43) + sum(Bin_44) + sum(Bin_45) + sum(Bin_46) + sum(Bin_47) + sum(Bin_48) + sum(Bin_49) + sum(Bin_50) + sum(Bin_51) + sum(Bin_52) + sum(Bin_53) + sum(Bin_54) + sum(Bin_55) + sum(Bin_56) + sum(Bin_57) + sum(Bin_58) + sum(Bin_59) + sum(Bin_60) + sum(Bin_61) + sum(Bin_62) + sum(Bin_63) + sum(Bin_64) + sum(Bin_65) + sum(Bin_66) + sum(Bin_67) + sum(Bin_68) + sum(Bin_69) + sum(Bin_70) + sum(Bin_71) + sum(Bin_72) + sum(Bin_73) + sum(Bin_74) + sum(Bin_75) + sum(Bin_76) + sum(Bin_77) + sum(Bin_78) + sum(Bin_79) + sum(Bin_80),
            Gt_2ms = sum(Bin_81) + sum(Bin_82) + sum(Bin_83) + sum(Bin_84) + sum(Bin_85) + sum(Bin_86) + sum(Bin_87) + sum(Bin_88) + sum(Bin_89) + sum(Bin_90) + sum(Bin_91) + sum(Bin_92) + sum(Bin_93) + sum(Bin_94) + sum(Bin_95) + sum(Bin_96) + sum(Bin_97) + sum(Bin_98) + sum(Bin_99) + sum(Bin_100) + sum(Bin_101) + sum(Bin_102) + sum(Bin_103) + sum(Bin_104) + sum(Bin_105) + sum(Bin_106) + sum(Bin_107) + sum(Bin_108) + sum(Bin_109) + sum(Bin_110) + sum(Bin_111) + sum(Bin_112) + sum(Bin_113) + sum(Bin_114) + sum(Bin_115) + sum(Bin_116) + sum(Bin_117) + sum(Bin_118) + sum(Bin_119) + sum(Bin_120) + sum(Bin_121) + sum(Bin_122) + sum(Bin_123) + sum(Bin_124) + sum(Bin_125) + sum(Bin_126) + sum(Bin_127) + sum(Bin_128) + sum(Bin_129) + sum(Bin_130) + sum(Bin_131) + sum(Bin_132) + sum(Bin_133) + sum(Bin_134) + sum(Bin_135) + sum(Bin_136) + sum(Bin_137) + sum(Bin_138) + sum(Bin_139) + sum(Bin_140) + sum(Bin_141) + sum(Bin_142) + sum(Bin_143) + sum(Bin_144) + sum(Bin_145) + sum(Bin_146) + sum(Bin_147) + sum(Bin_148) + sum(Bin_149) + sum(Bin_150) + sum(Bin_151) + sum(Bin_152) + sum(Bin_153) + sum(Bin_154) + sum(Bin_155) + sum(Bin_156) + sum(Bin_157) + sum(Bin_158) + sum(Bin_159) + sum(Bin_160) + sum(Bin_161) + sum(Bin_162) + sum(Bin_163) + sum(Bin_164) + sum(Bin_165) + sum(Bin_166) + sum(Bin_167) + sum(Bin_168) + sum(Bin_169) + sum(Bin_170) + sum(Bin_171) + sum(Bin_172) + sum(Bin_173) + sum(Bin_174) + sum(Bin_175) + sum(Bin_176) + sum(Bin_177) + sum(Bin_178) + sum(Bin_179) + sum(Bin_180) + sum(Bin_181) + sum(Bin_182) + sum(Bin_183) + sum(Bin_184) + sum(Bin_185) + sum(Bin_186) + sum(Bin_187) + sum(Bin_188) + sum(Bin_189) + sum(Bin_190) + sum(Bin_191) + sum(Bin_192) + sum(Bin_193) + sum(Bin_194) + sum(Bin_195) + sum(Bin_196) + sum(Bin_197) + sum(Bin_198) + sum(Bin_199) + sum(Bin_200) + sum(Bin_201) + sum(Bin_202) + sum(Bin_203) + sum(Bin_204) + sum(Bin_205) + sum(Bin_206) + sum(Bin_207) + sum(Bin_208) + sum(Bin_209) + sum(Bin_210) + sum(Bin_211) + sum(Bin_212) + sum(Bin_213) + sum(Bin_214) + sum(Bin_215) + sum(Bin_216) + sum(Bin_217) + sum(Bin_218) + sum(Bin_219) + sum(Bin_220) + sum(Bin_221) + sum(Bin_222) + sum(Bin_223) + sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_5ms = sum(Bin_201) + sum(Bin_202) + sum(Bin_203) + sum(Bin_204) + sum(Bin_205) + sum(Bin_206) + sum(Bin_207) + sum(Bin_208) + sum(Bin_209) + sum(Bin_210) + sum(Bin_211) + sum(Bin_212) + sum(Bin_213) + sum(Bin_214) + sum(Bin_215) + sum(Bin_216) + sum(Bin_217) + sum(Bin_218) + sum(Bin_219) + sum(Bin_220) + sum(Bin_221) + sum(Bin_222) + sum(Bin_223) + sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_10ms = sum(Bin_206) + sum(Bin_207) + sum(Bin_208) + sum(Bin_209) + sum(Bin_210) + sum(Bin_211) + sum(Bin_212) + sum(Bin_213) + sum(Bin_214) + sum(Bin_215) + sum(Bin_216) + sum(Bin_217) + sum(Bin_218) + sum(Bin_219) + sum(Bin_220) + sum(Bin_221) + sum(Bin_222) + sum(Bin_223) + sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_20ms = sum(Bin_207) + sum(Bin_208) + sum(Bin_209) + sum(Bin_210) + sum(Bin_211) + sum(Bin_212) + sum(Bin_213) + sum(Bin_214) + sum(Bin_215) + sum(Bin_216) + sum(Bin_217) + sum(Bin_218) + sum(Bin_219) + sum(Bin_220) + sum(Bin_221) + sum(Bin_222) + sum(Bin_223) + sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_50ms = sum(Bin_210) + sum(Bin_211) + sum(Bin_212) + sum(Bin_213) + sum(Bin_214) + sum(Bin_215) + sum(Bin_216) + sum(Bin_217) + sum(Bin_218) + sum(Bin_219) + sum(Bin_220) + sum(Bin_221) + sum(Bin_222) + sum(Bin_223) + sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_100ms = sum(Bin_215) + sum(Bin_216) + sum(Bin_217) + sum(Bin_218) + sum(Bin_219) + sum(Bin_220) + sum(Bin_221) + sum(Bin_222) + sum(Bin_223) + sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_200ms = sum(Bin_216) + sum(Bin_217) + sum(Bin_218) + sum(Bin_219) + sum(Bin_220) + sum(Bin_221) + sum(Bin_222) + sum(Bin_223) + sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_500ms = sum(Bin_219) + sum(Bin_220) + sum(Bin_221) + sum(Bin_222) + sum(Bin_223) + sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_1_Sec = sum(Bin_224) + sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_2_Sec = sum(Bin_225) + sum(Bin_226) + sum(Bin_227) + sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_5_Sec = sum(Bin_228) + sum(Bin_229) + sum(Bin_230) + sum(Bin_231) + sum(Bin_232) + sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256), 
            Gt_10_Sec = sum(Bin_233) + sum(Bin_234) + sum(Bin_235) + sum(Bin_236) + sum(Bin_237) + sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_15_Sec = sum(Bin_238) + sum(Bin_239) + sum(Bin_240) + sum(Bin_241) + sum(Bin_242) + sum(Bin_243) + sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256),
            Gt_30_Sec = sum(Bin_244) + sum(Bin_245) + sum(Bin_246) + sum(Bin_247) + sum(Bin_248) + sum(Bin_249) + sum(Bin_250) + sum(Bin_251) + sum(Bin_252) + sum(Bin_253) + sum(Bin_254) + sum(Bin_255) + sum(Bin_256)
by bin(PreciseTimeStamp, 5s)
```

**Params:** `{blobPath}`, `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{histogramDesc}`

---

### Azure Host VM Histogram Layers

_Widget purpose:_ IO Stats by TimeTaken (select the Histogram Layer)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > IO Stats > IO Stats > IO Stats by TimeTaken (select the Histogram Layer)`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu` · `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
        | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId 
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    //| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
    )
| distinct Value = HistogramDesc
| sort by Value
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ Total IOs per Histogram Layer

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > IO Stats > IO Stats > Total IOs per Histogram Layer`

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

### Azure Host VM Latency IO Stats per Histogram

_Widget purpose:_ Total IOs per Histogram Layer

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > IO Stats > IO Stats > Total IOs per Histogram Layer`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize TotalIOs = sum(Bin_Count) by bin(PreciseTimeStamp, 5s), HistogramDesc`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    //
    // For UltraDisk, we have more granular IO Size Buckets
    // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
    //
    | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                 IOSizeBucket == 2, 1, // 8 - 64k
                                 IOSizeBucket == 3, 2, // 64+
                                 IOSizeBucket == 4, 3, // All IO Sizes
                                 IOSizeBucket)
)
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| where isempty(blobPath) or BlobPath == blobPath
| summarize TotalIOs = sum(Bin_Count) by bin(PreciseTimeStamp, 5s), HistogramDesc
| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
```

**Params:** `{blobPath}`, `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{ioSizeBucket}`

---

### Azure Host VM IO Block Sizes

_Widget purpose:_ Total IOs per Histogram Layer

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > IO Stats > IO Stats > Total IOs per Histogram Layer`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ Average in Milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Average in Milliseconds`

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

### Azure Host VM UltraSSD Average Latency Per Blob

_Widget purpose:_ Average in Milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Average in Milliseconds`

**Tables:** `OsAsapCounterTable`, `OsUltraSSDLatencyHistogramTableV2`, `Latency_Histograms`
**Aggregations:** `summarize AvgBqeReadLatencyInMS = avg(AvgBqeReadLatencyInMS), AvgBqeWriteLatencyInMS = avg by bin(PreciseTimeStamp, 5s)` · `summarize //hint.strategy=shuffle Bin_AverageLatency = avg(Bin_AverageLatency) by bin(todatetime(PreciseTimeStamp), 5s), HistogramDesc = database('SharedWorkspace`

```kusto
let asap_avg_counters = OsAsapCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId contains containerId 
| extend AvgBqeReadLatencyInMS = DeltaBqeLatencyDiskReadIoBucketLatencySum / DeltaBqeLatencyDiskReadIoBucketSampleCount / 1000.0,
         AvgBqeWriteLatencyInMS = DeltaBqeLatencyDiskWriteIoBucketLatencySum / DeltaBqeLatencyDiskWriteIoBucketSampleCount / 1000.0,
         AvgFOBackendReadLatencyInMS = DeltaBackendLatencyDiskReadIoBucketLatencySum / DeltaBackendLatencyDiskReadIoBucketSampleCount / 1000.0,
         AvgFOBackendWriteLatencyInMS = DeltaBackendLatencyDiskWriteIoBucketLatencySum / DeltaBackendLatencyDiskWriteIoBucketSampleCount / 1000.0,
         AvgSchedReadLatencyInMS = DeltaSchedLatencyDiskReadIoBucketLatencySum / DeltaSchedLatencyDiskReadIoBucketSampleCount / 1000.0,
         AvgSchedWriteLatencyInMS = DeltaSchedLatencyDiskWriteIoBucketLatencySum / DeltaSchedLatencyDiskWriteIoBucketSampleCount / 1000.0
| parse blobPath with "XDISK:" blobPathStr "/" * // dd blobpath parsing
| where isempty(blobPath) or (BlobPath contains blobPathStr and blobPathStr !startswith "0.0.0.0") or BlobPath contains blobPath
| summarize AvgBqeReadLatencyInMS = avg(AvgBqeReadLatencyInMS),
            AvgBqeWriteLatencyInMS = avg(AvgBqeWriteLatencyInMS),
            AvgFOBackendReadLatencyInMS = avg(AvgFOBackendReadLatencyInMS),
            AvgFOBackendWriteLatencyInMS = avg(AvgFOBackendWriteLatencyInMS),
            AvgSchedReadLatencyInMS = avg(AvgSchedReadLatencyInMS),
            AvgSchedWriteLatencyInMS = avg(AvgSchedWriteLatencyInMS),
            AverageReadLatency = avg(AverageReadLatency),
            AverageWriteLatency = avg(AverageWriteLatency) by bin(PreciseTimeStamp, 5s);
let asap_bqe_read = asap_avg_counters | project PreciseTimeStamp, HistogramDesc = "ASAP Bqe Reads", Latency = AvgBqeReadLatencyInMS;
let asap_bqe_write = asap_avg_counters | project PreciseTimeStamp, HistogramDesc = "ASAP Bqe Writes", Latency = AvgBqeWriteLatencyInMS;
let asap_backend_read = asap_avg_counters | project PreciseTimeStamp, HistogramDesc = "ASAP FO Backend Reads", Latency = AvgFOBackendReadLatencyInMS;
let asap_backend_write = asap_avg_counters | project PreciseTimeStamp, HistogramDesc = "ASAP FO Backend Writes", Latency = AvgFOBackendWriteLatencyInMS;
let asap_sched_read = asap_avg_counters | project PreciseTimeStamp, HistogramDesc = "ASAP Scheduler Reads", Latency = AvgSchedReadLatencyInMS;
let asap_sched_write = asap_avg_counters | project PreciseTimeStamp, HistogramDesc = "ASAP Scheduler Writes", Latency = AvgSchedWriteLatencyInMS;
let asap_total_read = asap_avg_counters | project PreciseTimeStamp, HistogramDesc = "ASAP Reads", Latency = AverageReadLatency;
let asap_total_write = asap_avg_counters | project PreciseTimeStamp, HistogramDesc = "ASAP Writes", Latency = AverageWriteLatency;
let Latency_Histograms = OsUltraSSDLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId contains containerId 
        and IOSizeBucket != 4
| parse BlobPath with NewBlobPath "?" *
| extend BlobPath = case(isempty(NewBlobPath), BlobPath, NewBlobPath)
| where isempty(blobPath) or BlobPath == blobPath
| summarize //hint.strategy=shuffle 
        Bin_AverageLatency = avg(Bin_AverageLatency)
    by bin(todatetime(PreciseTimeStamp), 5s), HistogramDesc =  database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum), HistogramVersion
| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
| project PreciseTimeStamp, HistogramDesc, Latency = Bin_AverageLatency
// convert to milliseconds
| extend Latency = Latency / 1000.0;
let DD_Read_RDMA_Network = Latency_Histograms | summarize HistogramDesc = "DirectDrive RDMA Reads (Network)",  Latency = take_anyif(Latency, HistogramDesc =~ "DirectDrive RDMA Reads")  - take_anyif(Latency, HistogramDesc =~ "DirectDrive Server RDMA Reads")  by PreciseTimeStamp;
let DD_Write_RDMA_Network = Latency_Histograms | summarize HistogramDesc = "DirectDrive RDMA Writes (Network)", Latency = take_anyif(Latency, HistogramDesc =~ "DirectDrive RDMA Writes") - take_anyif(Latency, HistogramDesc =~ "DirectDrive Server RDMA Writes") by PreciseTimeStamp;
let DD_Read_TCP_Network = Latency_Histograms | summarize HistogramDesc = "DirectDrive TCP Reads (Network)",   Latency = take_anyif(Latency, HistogramDesc =~ "DirectDrive TCP Reads")   - take_anyif(Latency, HistogramDesc =~ "DirectDrive Server TCP Reads")   by PreciseTimeStamp;
let DD_Write_TCP_Network = Latency_Histograms | summarize HistogramDesc = "DirectDrive TCP Writes (Network)",  Latency = take_anyif(Latency, HistogramDesc =~ "DirectDrive TCP Writes")  - take_anyif(Latency, HistogramDesc =~ "DirectDrive Server TCP Writes")  by PreciseTimeStamp;
union Latency_Histograms, DD_Read_RDMA_Network, DD_Write_RDMA_Network, DD_Read_TCP_Network, DD_Write_TCP_Network,
        asap_bqe_read, asap_bqe_write, asap_backend_read, asap_backend_write, 
        asap_sched_read, asap_sched_write, asap_total_read, asap_total_write
| sort by HistogramDesc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`, `{blobPath}`

---

### Azure Host VM Latency Q100

_Widget purpose:_ Q100 in milliseconds - Max Latency

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q100 in milliseconds - Max Latency`

**Tables:** `OsAsapCounterTable`, `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`, `Latency_Histogram_Quantiles`
**Aggregations:** `summarize MaxBqeReadLatencyInMS = max(MaxBqeReadLatencyInMS), MaxBqeWriteLatencyInMS = max by bin(PreciseTimeStamp, 5s)` · `summarize //hint.strategy=shuffle Q100 = max(Bin_Q100) by bin(todatetime(PreciseTimeStamp), 5s), HistogramTypeEnum, HistogramTypeDesc, His`

```kusto
let asap_avg_counters = OsAsapCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId contains containerId 
| extend MaxBqeReadLatencyInMS = DeltaBqeLatencyDiskReadIoBucketMaxLatency / 1000.0,
         MaxBqeWriteLatencyInMS = DeltaBqeLatencyDiskWriteIoBucketMaxLatency / 1000.0,
         MaxFOBackendReadLatencyInMS = DeltaBackendLatencyDiskReadIoBucketMaxLatency / 1000.0,
         MaxFOBackendWriteLatencyInMS = DeltaBackendLatencyDiskWriteIoBucketMaxLatency / 1000.0,
         MaxSchedReadLatencyInMS = DeltaSchedLatencyDiskReadIoBucketMaxLatency / 1000.0,
         MaxSchedWriteLatencyInMS = DeltaSchedLatencyDiskWriteIoBucketMaxLatency / 1000.0
| parse blobPath with "XDISK:" blobPathStr "/" * // dd blobpath parsing
| where isempty(blobPath) or (BlobPath contains blobPathStr and blobPathStr !startswith "0.0.0.0") or BlobPath contains blobPath
| summarize MaxBqeReadLatencyInMS = max(MaxBqeReadLatencyInMS),
            MaxBqeWriteLatencyInMS = max(MaxBqeWriteLatencyInMS),
            MaxFOBackendReadLatencyInMS = max(MaxFOBackendReadLatencyInMS),
            MaxFOBackendWriteLatencyInMS = max(MaxFOBackendWriteLatencyInMS),
            MaxSchedReadLatencyInMS = max(MaxSchedReadLatencyInMS),
            MaxSchedWriteLatencyInMS = max(MaxSchedWriteLatencyInMS),
            MaxReadLatency = max(DeltaIoLatencyDiskReadIoBucketMaxLatency / 1000.0),
            MaxWriteLatency = max(DeltaIoLatencyDiskWriteIoBucketMaxLatency / 1000.0) by bin(PreciseTimeStamp, 5s);
let asap_bqe_read = asap_avg_counters | project PreciseTimeStamp, HistogramTypeDesc = "ASAP Bqe Reads", LatencyQuantile = MaxBqeReadLatencyInMS;
let asap_bqe_write = asap_avg_counters | project PreciseTimeStamp, HistogramTypeDesc = "ASAP Bqe Writes", LatencyQuantile = MaxBqeWriteLatencyInMS;
let asap_backend_read = asap_avg_counters | project PreciseTimeStamp, HistogramTypeDesc = "ASAP FO Backend Reads", LatencyQuantile = MaxFOBackendReadLatencyInMS;
let asap_backend_write = asap_avg_counters | project PreciseTimeStamp, HistogramTypeDesc = "ASAP FO Backend Writes", LatencyQuantile = MaxFOBackendWriteLatencyInMS;
let asap_sched_read = asap_avg_counters | project PreciseTimeStamp, HistogramTypeDesc = "ASAP Scheduler Reads", LatencyQuantile = MaxSchedReadLatencyInMS;
let asap_sched_write = asap_avg_counters | project PreciseTimeStamp, HistogramTypeDesc = "ASAP Scheduler Writes", LatencyQuantile = MaxSchedWriteLatencyInMS;
let asap_total_read = asap_avg_counters | project PreciseTimeStamp, HistogramTypeDesc = "ASAP Reads", LatencyQuantile = MaxReadLatency;
let asap_total_write = asap_avg_counters | project PreciseTimeStamp, HistogramTypeDesc = "ASAP Writes", LatencyQuantile = MaxWriteLatency;
let Latency_Histogram_Quantiles = OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
)
| extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
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
)
| extend HistogramTypeEnum = case(HistogramTypeDesc contains "Ultra", strcat("Ultra_", HistogramTypeEnum), tostring(HistogramTypeEnum))
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with ParsedBlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| where isempty(blobPath) or ParsedBlobPath == blobPath or BlobPath contains blobPath
| summarize //hint.strategy=shuffle
            Q100 = max(Bin_Q100)
           by bin(todatetime(PreciseTimeStamp), 5s), HistogramTypeEnum, HistogramTypeDesc, HistogramVersion
| extend Q100 = Q100 / 1000.0
| extend HistogramTypeDesc = replace_string(HistogramTypeDesc, "UltraSSD", "DirectDrive")
| project PreciseTimeStamp, HistogramTypeDesc, LatencyQuantile = Q100;
let Read_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Reads using RDMA (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads using RDMA (Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads as seen by XSTORE (for STCP + RDMA)")  by PreciseTimeStamp;
let Write_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Writes using RDMA (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes using RDMA (Vhddisk)") - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes as seen by XSTORE (for STCP + RDMA)") by PreciseTimeStamp;
let Read_STCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Reads using STCP (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads using STCP (Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads as seen by XSTORE (for STCP + RDMA)")  by PreciseTimeStamp;
let Write_STCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Writes using STCP (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes using STCP(Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes as seen by XSTORE (for STCP + RDMA)") by PreciseTimeStamp;
let DD_Read_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive RDMA Reads (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive RDMA Reads")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server RDMA Reads")  by PreciseTimeStamp;
let DD_Write_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive RDMA Writes (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive RDMA Writes") - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server RDMA Writes") by PreciseTimeStamp;
let DD_Read_TCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive TCP Reads (Network)",   LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive TCP Reads")   - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server TCP Reads")   by PreciseTimeStamp;
let DD_Write_TCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive TCP Writes (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive TCP Writes")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server TCP Writes")  by PreciseTimeStamp;
union Latency_Histogram_Quantiles, Read_RDMA_Network, Write_RDMA_Network, Read_STCP_Network, Write_STCP_Network, DD_Read_RDMA_Network, DD_Write_RDMA_Network, DD_Read_TCP_Network, DD_Write_TCP_Network,
        asap_bqe_read, asap_bqe_write, asap_backend_read, asap_backend_write, 
        asap_sched_read, asap_sched_write, asap_total_read, asap_total_write
| order by HistogramTypeDesc asc, PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{blobPath}`, `{ioSizeBucket}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ Q100 in milliseconds - Max Latency

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q100 in milliseconds - Max Latency`

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

### Azure Host VM IO Block Sizes

_Widget purpose:_ Q100 in milliseconds - Max Latency

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q100 in milliseconds - Max Latency`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ Q50 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q50 in milliseconds`

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

### Azure Host VM Surface Latency Stats Q50

_Widget purpose:_ Q50 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q50 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`, `Latency_Histogram_Quantiles`
**Aggregations:** `summarize //hint.strategy=shuffle Bin_Count = sum(Bin_Count), Bin_01 = sum(Bin_01), Bin_02 by bin(todatetime(PreciseTimeStamp), 5s), HistogramTypeEnum, HistogramTypeDesc, His` · `summarize HistogramTypeDesc = "Reads using RDMA (Network)", LatencyQuantile = take_anyif(L by XSTORE (for STCP + RDMA)") by PreciseTimeStamp`

```kusto
let Latency_Histogram_Quantiles = OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
)
| extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
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
)
| extend HistogramTypeEnum = case(HistogramTypeDesc contains "Ultra", strcat("Ultra_", HistogramTypeEnum), tostring(HistogramTypeEnum))
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| where isempty(blobPath) or BlobPath == blobPath
| summarize //hint.strategy=shuffle
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
                Bin_241 = sum(Bin_241), Bin_242 = sum(Bin_242), Bin_243 = sum(Bin_243), Bin_244 = sum(Bin_244), Bin_245 = sum(Bin_245), Bin_246 = sum(Bin_246), Bin_247 = sum(Bin_247), Bin_248 = sum(Bin_248),
                Bin_249 = sum(Bin_249), Bin_250 = sum(Bin_250), Bin_251 = sum(Bin_251), Bin_252 = sum(Bin_252), Bin_253 = sum(Bin_253), Bin_254 = sum(Bin_254), Bin_255 = sum(Bin_255), Bin_256 = sum(Bin_256)
           by bin(todatetime(PreciseTimeStamp), 5s), HistogramTypeEnum, HistogramTypeDesc, HistogramVersion
| extend //Q25 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.25),
         Q50 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.5)//,
         //Q75 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.75),
         //Q90 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.90),
         //Q95 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.95),
         //Q99 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.99),
         //Q999 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.999),
         //Q100 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 1.0)
// Convert latency quantiles to milliseconds
//| extend Q25 = Q25 / 1000.0, Q50 = Q50 / 1000.0, Q75 = Q75 / 1000.0, Q90 = Q90 / 1000.0, Q95 = Q95 / 1000.0, Q99 = Q99 / 1000.0, Q999 = Q999 / 1000.0, Q100 = Q100 / 1000.0
| extend Q50 = Q50 / 1000.0
| extend HistogramTypeDesc = replace_string(HistogramTypeDesc, "UltraSSD", "DirectDrive")
| project PreciseTimeStamp, HistogramTypeDesc, LatencyQuantile = Q50;
let Read_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Reads using RDMA (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads using RDMA (Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads as seen by XSTORE (for STCP + RDMA)")  by PreciseTimeStamp;
let Write_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Writes using RDMA (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes using RDMA (Vhddisk)") - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes as seen by XSTORE (for STCP + RDMA)") by PreciseTimeStamp;
let Read_STCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Reads using STCP (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads using STCP (Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads as seen by XSTORE (for STCP + RDMA)")  by PreciseTimeStamp;
let Write_STCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Writes using STCP (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes using STCP(Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes as seen by XSTORE (for STCP + RDMA)") by PreciseTimeStamp;
let DD_Read_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive RDMA Reads (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive RDMA Reads")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server RDMA Reads")  by PreciseTimeStamp;
let DD_Write_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive RDMA Writes (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive RDMA Writes") - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server RDMA Writes") by PreciseTimeStamp;
let DD_Read_TCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive TCP Reads (Network)",   LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive TCP Reads")   - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server TCP Reads")   by PreciseTimeStamp;
let DD_Write_TCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive TCP Writes (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive TCP Writes")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server TCP Writes")  by PreciseTimeStamp;
union Latency_Histogram_Quantiles, Read_RDMA_Network, Write_RDMA_Network, Read_STCP_Network, Write_STCP_Network, DD_Read_RDMA_Network, DD_Write_RDMA_Network, DD_Read_TCP_Network, DD_Write_TCP_Network
| sort by HistogramTypeDesc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{blobPath}`, `{ioSizeBucket}`

---

### Azure Host VM IO Block Sizes

_Widget purpose:_ Q50 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q50 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ Q75 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q75 in milliseconds`

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

### Azure Host VM Surface Latency Stats Q75

_Widget purpose:_ Q75 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q75 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`, `Latency_Histogram_Quantiles`
**Aggregations:** `summarize hint.strategy=shuffle Bin_Count = sum(Bin_Count), Bin_01 = sum(Bin_01), Bin_02 = by bin(todatetime(PreciseTimeStamp), 5m), HistogramTypeEnum, HistogramTypeDesc, His` · `summarize HistogramTypeDesc = "Reads using RDMA (Network)", LatencyQuantile = take_anyif(L by XSTORE (for STCP + RDMA)") by PreciseTimeStamp`

```kusto
let Latency_Histogram_Quantiles = OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
)
| extend HistogramTypeDesc = GetHistogramDesc(HistogramTypeEnum)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
    | extend HistogramTypeDesc = GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    //
    // For UltraDisk, we have more granular IO Size Buckets
    // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
    //
    | extend IOSizeBucket = case(IOSizeBucket in (0, 1) and TelemetryVersion >= 2, 0, // 0 - 8k
                                 IOSizeBucket == 2 and TelemetryVersion >= 2, 1, // 8 - 64k
                                 IOSizeBucket == 3 and TelemetryVersion >= 2, 2, // 64+
                                 IOSizeBucket == 4 and TelemetryVersion >= 2, 3, // all IO Sizes
                                 IOSizeBucket)
)
| extend HistogramTypeEnum = case(HistogramTypeDesc contains "Ultra", strcat("Ultra_", HistogramTypeEnum), tostring(HistogramTypeEnum))
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
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
                Bin_241 = sum(Bin_241), Bin_242 = sum(Bin_242), Bin_243 = sum(Bin_243), Bin_244 = sum(Bin_244), Bin_245 = sum(Bin_245), Bin_246 = sum(Bin_246), Bin_247 = sum(Bin_247), Bin_248 = sum(Bin_248),
                Bin_249 = sum(Bin_249), Bin_250 = sum(Bin_250), Bin_251 = sum(Bin_251), Bin_252 = sum(Bin_252), Bin_253 = sum(Bin_253), Bin_254 = sum(Bin_254), Bin_255 = sum(Bin_255), Bin_256 = sum(Bin_256)
           by bin(todatetime(PreciseTimeStamp), 5m), HistogramTypeEnum, HistogramTypeDesc, HistogramVersion
| extend Q25 = CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.25),
         Q50 = CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.5),
         Q75 = CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.75),
         Q90 = CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.90),
         Q95 = CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.95),
         Q99 = CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.99),
         Q999 = CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.999),
         Q100 = CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 1.0)
// Convert latency quantiles to milliseconds
| extend Q25 = Q25 / 1000.0, Q50 = Q50 / 1000.0, Q75 = Q75 / 1000.0, Q90 = Q90 / 1000.0, Q95 = Q95 / 1000.0, Q99 = Q99 / 1000.0, Q999 = Q999 / 1000.0, Q100 = Q100 / 1000.0
| extend HistogramTypeDesc = replace_string(HistogramTypeDesc, "UltraSSD", "DirectDrive")
| project PreciseTimeStamp, HistogramTypeDesc, LatencyQuantile = Q75;
let Read_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Reads using RDMA (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads using RDMA (Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads as seen by XSTORE (for STCP + RDMA)")  by PreciseTimeStamp;
let Write_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Writes using RDMA (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes using RDMA (Vhddisk)") - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes as seen by XSTORE (for STCP + RDMA)") by PreciseTimeStamp;
let Read_STCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Reads using STCP (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads using STCP (Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads as seen by XSTORE (for STCP + RDMA)")  by PreciseTimeStamp;
let Write_STCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Writes using STCP (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes using STCP(Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes as seen by XSTORE (for STCP + RDMA)") by PreciseTimeStamp;
let DD_Read_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive RDMA Reads (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive RDMA Reads")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server RDMA Reads")  by PreciseTimeStamp;
let DD_Write_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive RDMA Writes (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive RDMA Writes") - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server RDMA Writes") by PreciseTimeStamp;
let DD_Read_TCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive TCP Reads (Network)",   LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive TCP Reads")   - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server TCP Reads")   by PreciseTimeStamp;
let DD_Write_TCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive TCP Writes (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive TCP Writes")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server TCP Writes")  by PreciseTimeStamp;
union Latency_Histogram_Quantiles, Read_RDMA_Network, Write_RDMA_Network, Read_STCP_Network, Write_STCP_Network, DD_Read_RDMA_Network, DD_Write_RDMA_Network, DD_Read_TCP_Network, DD_Write_TCP_Network
| sort by HistogramTypeDesc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{blobPath}`, `{ioSizeBucket}`

---

### Azure Host VM IO Block Sizes

_Widget purpose:_ Q75 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q75 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ Q95 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q95 in milliseconds`

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

### Azure Host VM Latency Q95

_Widget purpose:_ Q95 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q95 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`, `Latency_Histogram_Quantiles`
**Aggregations:** `summarize //hint.strategy=shuffle Bin_Count = sum(Bin_Count), Bin_01 = sum(Bin_01), Bin_02 by bin(todatetime(PreciseTimeStamp), 5s), HistogramTypeEnum, HistogramTypeDesc, His` · `summarize HistogramTypeDesc = "Reads using RDMA (Network)", LatencyQuantile = take_anyif(L by XSTORE (for STCP + RDMA)") by PreciseTimeStamp`

```kusto
let Latency_Histogram_Quantiles = OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
)
| extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
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
)
| extend HistogramTypeEnum = case(HistogramTypeDesc contains "Ultra", strcat("Ultra_", HistogramTypeEnum), tostring(HistogramTypeEnum))
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| where isempty(blobPath) or BlobPath == blobPath
| summarize //hint.strategy=shuffle
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
                Bin_241 = sum(Bin_241), Bin_242 = sum(Bin_242), Bin_243 = sum(Bin_243), Bin_244 = sum(Bin_244), Bin_245 = sum(Bin_245), Bin_246 = sum(Bin_246), Bin_247 = sum(Bin_247), Bin_248 = sum(Bin_248),
                Bin_249 = sum(Bin_249), Bin_250 = sum(Bin_250), Bin_251 = sum(Bin_251), Bin_252 = sum(Bin_252), Bin_253 = sum(Bin_253), Bin_254 = sum(Bin_254), Bin_255 = sum(Bin_255), Bin_256 = sum(Bin_256)
           by bin(todatetime(PreciseTimeStamp), 5s), HistogramTypeEnum, HistogramTypeDesc, HistogramVersion
| extend //Q25 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.25),
         //Q50 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.5),
         //Q75 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.75),
         //Q90 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.90),
         Q95 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.95)//,
         //Q99 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.99),
         //Q999 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.999),
         //Q100 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 1.0)
// Convert latency quantiles to milliseconds
//| extend Q25 = Q25 / 1000.0, Q50 = Q50 / 1000.0, Q75 = Q75 / 1000.0, Q90 = Q90 / 1000.0, Q95 = Q95 / 1000.0, Q99 = Q99 / 1000.0, Q999 = Q999 / 1000.0, Q100 = Q100 / 1000.0
| extend Q95 = Q95 / 1000.0
| extend HistogramTypeDesc = replace_string(HistogramTypeDesc, "UltraSSD", "DirectDrive")
| project PreciseTimeStamp, HistogramTypeDesc, LatencyQuantile = Q95;
let Read_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Reads using RDMA (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads using RDMA (Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads as seen by XSTORE (for STCP + RDMA)")  by PreciseTimeStamp;
let Write_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Writes using RDMA (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes using RDMA (Vhddisk)") - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes as seen by XSTORE (for STCP + RDMA)") by PreciseTimeStamp;
let Read_STCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Reads using STCP (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads using STCP (Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads as seen by XSTORE (for STCP + RDMA)")  by PreciseTimeStamp;
let Write_STCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Writes using STCP (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes using STCP(Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes as seen by XSTORE (for STCP + RDMA)") by PreciseTimeStamp;
let DD_Read_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive RDMA Reads (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive RDMA Reads")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server RDMA Reads")  by PreciseTimeStamp;
let DD_Write_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive RDMA Writes (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive RDMA Writes") - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server RDMA Writes") by PreciseTimeStamp;
let DD_Read_TCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive TCP Reads (Network)",   LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive TCP Reads")   - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server TCP Reads")   by PreciseTimeStamp;
let DD_Write_TCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive TCP Writes (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive TCP Writes")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server TCP Writes")  by PreciseTimeStamp;
union Latency_Histogram_Quantiles, Read_RDMA_Network, Write_RDMA_Network, Read_STCP_Network, Write_STCP_Network, DD_Read_RDMA_Network, DD_Write_RDMA_Network, DD_Read_TCP_Network, DD_Write_TCP_Network
| sort by HistogramTypeDesc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{blobPath}`, `{ioSizeBucket}`

---

### Azure Host VM IO Block Sizes

_Widget purpose:_ Q95 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q95 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Latency Q99

_Widget purpose:_ Q99 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q99 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`, `Latency_Histogram_Quantiles`
**Aggregations:** `summarize //hint.strategy=shuffle Bin_Count = sum(Bin_Count), Bin_01 = sum(Bin_01), Bin_02 by bin(todatetime(PreciseTimeStamp), 5s), HistogramTypeEnum, HistogramTypeDesc, His` · `summarize HistogramTypeDesc = "Reads using RDMA (Network)", LatencyQuantile = take_anyif(L by XSTORE (for STCP + RDMA)") by PreciseTimeStamp`

```kusto
let Latency_Histogram_Quantiles = OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
)
| extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
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
)
| extend HistogramTypeEnum = case(HistogramTypeDesc contains "Ultra", strcat("Ultra_", HistogramTypeEnum), tostring(HistogramTypeEnum))
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| where isempty(blobPath) or BlobPath == blobPath
| summarize //hint.strategy=shuffle
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
                Bin_241 = sum(Bin_241), Bin_242 = sum(Bin_242), Bin_243 = sum(Bin_243), Bin_244 = sum(Bin_244), Bin_245 = sum(Bin_245), Bin_246 = sum(Bin_246), Bin_247 = sum(Bin_247), Bin_248 = sum(Bin_248),
                Bin_249 = sum(Bin_249), Bin_250 = sum(Bin_250), Bin_251 = sum(Bin_251), Bin_252 = sum(Bin_252), Bin_253 = sum(Bin_253), Bin_254 = sum(Bin_254), Bin_255 = sum(Bin_255), Bin_256 = sum(Bin_256)
           by bin(todatetime(PreciseTimeStamp), 5s), HistogramTypeEnum, HistogramTypeDesc, HistogramVersion
| extend //Q25 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.25),
         //Q50 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.5),
         //Q75 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.75),
         //Q90 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.90),
         //Q95 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.95),
         Q99 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.99)//,
         //Q999 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 0.999),
         //Q100 = database('SharedWorkspace').CalculateQuantilesV4(HistogramVersion, Bin_01, Bin_02, Bin_03, Bin_04, Bin_05, Bin_06, Bin_07, Bin_08, Bin_09, Bin_10, Bin_11, Bin_12, Bin_13, Bin_14, Bin_15, Bin_16, Bin_17, Bin_18, Bin_19, Bin_20, Bin_21, Bin_22, Bin_23, Bin_24, Bin_25, Bin_26, Bin_27, Bin_28, Bin_29, Bin_30, Bin_31, Bin_32, Bin_33, Bin_34, Bin_35, Bin_36, Bin_37, Bin_38, Bin_39, Bin_40, Bin_41, Bin_42, Bin_43, Bin_44, Bin_45, Bin_46, Bin_47, Bin_48, Bin_49, Bin_50, Bin_51, Bin_52, Bin_53, Bin_54, Bin_55, Bin_56, Bin_57, Bin_58, Bin_59, Bin_60, Bin_61, Bin_62, Bin_63, Bin_64, Bin_65, Bin_66, Bin_67, Bin_68, Bin_69, Bin_70, Bin_71, Bin_72, Bin_73, Bin_74, Bin_75, Bin_76, Bin_77, Bin_78, Bin_79, Bin_80, Bin_81, Bin_82, Bin_83, Bin_84, Bin_85, Bin_86, Bin_87, Bin_88, Bin_89, Bin_90, Bin_91, Bin_92, Bin_93, Bin_94, Bin_95, Bin_96, Bin_97, Bin_98, Bin_99, Bin_100, Bin_101, Bin_102, Bin_103, Bin_104, Bin_105, Bin_106, Bin_107, Bin_108, Bin_109, Bin_110, Bin_111, Bin_112, Bin_113, Bin_114, Bin_115, Bin_116, Bin_117, Bin_118, Bin_119, Bin_120, Bin_121, Bin_122, Bin_123, Bin_124, Bin_125, Bin_126, Bin_127, Bin_128, Bin_129, Bin_130, Bin_131, Bin_132, Bin_133, Bin_134, Bin_135, Bin_136, Bin_137, Bin_138, Bin_139, Bin_140, Bin_141, Bin_142, Bin_143, Bin_144, Bin_145, Bin_146, Bin_147, Bin_148, Bin_149, Bin_150, Bin_151, Bin_152, Bin_153, Bin_154, Bin_155, Bin_156, Bin_157, Bin_158, Bin_159, Bin_160, Bin_161, Bin_162, Bin_163, Bin_164, Bin_165, Bin_166, Bin_167, Bin_168, Bin_169, Bin_170, Bin_171, Bin_172, Bin_173, Bin_174, Bin_175, Bin_176, Bin_177, Bin_178, Bin_179, Bin_180, Bin_181, Bin_182, Bin_183, Bin_184, Bin_185, Bin_186, Bin_187, Bin_188, Bin_189, Bin_190, Bin_191, Bin_192, Bin_193, Bin_194, Bin_195, Bin_196, Bin_197, Bin_198, Bin_199, Bin_200, Bin_201, Bin_202, Bin_203, Bin_204, Bin_205, Bin_206, Bin_207, Bin_208, Bin_209, Bin_210, Bin_211, Bin_212, Bin_213, Bin_214, Bin_215, Bin_216, Bin_217, Bin_218, Bin_219, Bin_220, Bin_221, Bin_222, Bin_223, Bin_224, Bin_225, Bin_226, Bin_227, Bin_228, Bin_229, Bin_230, Bin_231, Bin_232, Bin_233, Bin_234, Bin_235, Bin_236, Bin_237, Bin_238, Bin_239, Bin_240, Bin_241, Bin_242, Bin_243, Bin_244, Bin_245, Bin_246, Bin_247, Bin_248, Bin_249, Bin_250, Bin_251, Bin_252, Bin_253, Bin_254, Bin_255, Bin_256, 1.0)
// Convert latency quantiles to milliseconds
//| extend Q25 = Q25 / 1000.0, Q50 = Q50 / 1000.0, Q75 = Q75 / 1000.0, Q90 = Q90 / 1000.0, Q95 = Q95 / 1000.0, Q99 = Q99 / 1000.0, Q999 = Q999 / 1000.0, Q100 = Q100 / 1000.0
| extend Q99 = Q99 / 1000.0
| extend HistogramTypeDesc = replace_string(HistogramTypeDesc, "UltraSSD", "DirectDrive")
| project PreciseTimeStamp, HistogramTypeDesc, LatencyQuantile = Q99;
let Read_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Reads using RDMA (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads using RDMA (Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads as seen by XSTORE (for STCP + RDMA)")  by PreciseTimeStamp;
let Write_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Writes using RDMA (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes using RDMA (Vhddisk)") - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes as seen by XSTORE (for STCP + RDMA)") by PreciseTimeStamp;
let Read_STCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Reads using STCP (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads using STCP (Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Reads as seen by XSTORE (for STCP + RDMA)")  by PreciseTimeStamp;
let Write_STCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "Writes using STCP (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes using STCP(Vhddisk)")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "Writes as seen by XSTORE (for STCP + RDMA)") by PreciseTimeStamp;
let DD_Read_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive RDMA Reads (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive RDMA Reads")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server RDMA Reads")  by PreciseTimeStamp;
let DD_Write_RDMA_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive RDMA Writes (Network)", LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive RDMA Writes") - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server RDMA Writes") by PreciseTimeStamp;
let DD_Read_TCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive TCP Reads (Network)",   LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive TCP Reads")   - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server TCP Reads")   by PreciseTimeStamp;
let DD_Write_TCP_Network = Latency_Histogram_Quantiles | summarize HistogramTypeDesc = "DirectDrive TCP Writes (Network)",  LatencyQuantile = take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive TCP Writes")  - take_anyif(LatencyQuantile, HistogramTypeDesc =~ "DirectDrive Server TCP Writes")  by PreciseTimeStamp;
union Latency_Histogram_Quantiles, Read_RDMA_Network, Write_RDMA_Network, Read_STCP_Network, Write_STCP_Network, DD_Read_RDMA_Network, DD_Write_RDMA_Network, DD_Read_TCP_Network, DD_Write_TCP_Network
| sort by HistogramTypeDesc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{blobPath}`, `{ioSizeBucket}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ Q99 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q99 in milliseconds`

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

### Azure Host VM IO Block Sizes

_Widget purpose:_ Q99 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Blob > Per-Blob > Q99 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Histogram Layers

_Widget purpose:_ Q100 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q100 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu` · `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
        | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId 
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    //| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
    )
| distinct Value = HistogramDesc
| sort by Value
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Per Histogram Q100

_Widget purpose:_ Q100 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q100 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize Q100 = max(Bin_Q100) by bin(todatetime(PreciseTimeStamp), 5s), BlobPath // conve`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| where isempty(histogramDesc) or HistogramDesc == histogramDesc
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | where isempty(histogramDesc) or HistogramDesc == histogramDesc
)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    | where isempty(histogramDesc) or HistogramDesc == histogramDesc
    //
    // For UltraDisk, we have more granular IO Size Buckets
    // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
    //
    | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                 IOSizeBucket == 2, 1, // 8 - 64k
                                 IOSizeBucket == 3, 2, // 64+
                                 IOSizeBucket == 4, 3, // All IO Sizes
                                 IOSizeBucket)
)
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with BlobPath "?" *
| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
| summarize Q100 = max(Bin_Q100) by bin(todatetime(PreciseTimeStamp), 5s), BlobPath
// convert to milliseconds
| extend Q100 = Q100 / 1000.0
```

**Params:** `{histogramDesc}`, `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{ioSizeBucket}`

---

### Azure Host VM IO Block Sizes

_Widget purpose:_ Q100 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q100 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Histogram Layers

_Widget purpose:_ Q50 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q50 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu` · `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
        | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId 
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    //| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
    )
| distinct Value = HistogramDesc
| sort by Value
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Per Histogram Q50

_Widget purpose:_ Q50 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q50 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize Q50 = max(Bin_Q50) by bin(todatetime(PreciseTimeStamp), 5s), BlobPath // convert`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| where isempty(histogramDesc) or HistogramDesc == histogramDesc
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | where isempty(histogramDesc) or HistogramDesc == histogramDesc
)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    | where isempty(histogramDesc) or HistogramDesc == histogramDesc
    //
    // For UltraDisk, we have more granular IO Size Buckets
    // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
    //
    | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                 IOSizeBucket == 2, 1, // 8 - 64k
                                 IOSizeBucket == 3, 2, // 64+
                                 IOSizeBucket == 4, 3, // All IO Sizes
                                 IOSizeBucket)
)
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
| summarize Q50 = max(Bin_Q50) by bin(todatetime(PreciseTimeStamp), 5s), BlobPath
// convert to milliseconds
| extend Q50 = Q50 / 1000.0
```

**Params:** `{histogramDesc}`, `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{ioSizeBucket}`

---

### Azure Host VM IO Block Sizes

_Widget purpose:_ Q50 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q50 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Per Histogram Q75

_Widget purpose:_ Q75 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q75 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize Q75 = max(Bin_Q75) by bin(todatetime(PreciseTimeStamp), 5s), BlobPath // convert`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| where isempty(histogramDesc) or HistogramDesc == histogramDesc
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | where isempty(histogramDesc) or HistogramDesc == histogramDesc
)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    | where isempty(histogramDesc) or HistogramDesc == histogramDesc
    //
    // For UltraDisk, we have more granular IO Size Buckets
    // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
    //
    | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                 IOSizeBucket == 2, 1, // 8 - 64k
                                 IOSizeBucket == 3, 2, // 64+
                                 IOSizeBucket == 4, 3, // All IO Sizes
                                 IOSizeBucket)
)
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
| summarize Q75 = max(Bin_Q75) by bin(todatetime(PreciseTimeStamp), 5s), BlobPath
// convert to milliseconds
| extend Q75 = Q75 / 1000.0
```

**Params:** `{histogramDesc}`, `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{ioSizeBucket}`

---

### Azure Host VM Histogram Layers

_Widget purpose:_ Q75 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q75 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu` · `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
        | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId 
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    //| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
    )
| distinct Value = HistogramDesc
| sort by Value
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM IO Block Sizes

_Widget purpose:_ Q75 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q75 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Histogram Layers

_Widget purpose:_ Q95 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q95 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu` · `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
        | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId 
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    //| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
    )
| distinct Value = HistogramDesc
| sort by Value
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Per Histogram Layer Q95

_Widget purpose:_ Q95 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q95 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize Q95 = max(Bin_Q95) by bin(todatetime(PreciseTimeStamp), 5s), BlobPath // convert`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| where isempty(histogramDesc) or HistogramDesc == histogramDesc
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | where isempty(histogramDesc) or HistogramDesc == histogramDesc
)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    | where isempty(histogramDesc) or HistogramDesc == histogramDesc
    //
    // For UltraDisk, we have more granular IO Size Buckets
    // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
    //
    | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                 IOSizeBucket == 2, 1, // 8 - 64k
                                 IOSizeBucket == 3, 2, // 64+
                                 IOSizeBucket == 4, 3, // All IO Sizes
                                 IOSizeBucket)
)
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
| summarize Q95 = max(Bin_Q95) by bin(todatetime(PreciseTimeStamp), 5s), BlobPath
// convert to milliseconds
| extend Q95 = Q95 / 1000.0
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{histogramDesc}`, `{ioSizeBucket}`

---

### Azure Host VM IO Block Sizes

_Widget purpose:_ Q95 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q95 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Histogram Layers

_Widget purpose:_ Q99 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q99 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu` · `summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnu`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId
        | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and ContainerId == containerId 
    | summarize by HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    //| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
    )
| distinct Value = HistogramDesc
| sort by Value
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Per Histogram Layer Q99

_Widget purpose:_ Q99 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q99 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize Q99 = max(Bin_Q95) by bin(todatetime(PreciseTimeStamp), 5s), BlobPath // convert`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| where isempty(histogramDesc) or HistogramDesc == histogramDesc
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
    | where isempty(histogramDesc) or HistogramDesc == histogramDesc
)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
    | extend HistogramDesc = database('SharedWorkspace').GetHistogramDescV2("UltraSSD", HistogramTypeEnum)
    | where isempty(histogramDesc) or HistogramDesc == histogramDesc
    //
    // For UltraDisk, we have more granular IO Size Buckets
    // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
    //
    | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                 IOSizeBucket == 2, 1, // 8 - 64k
                                 IOSizeBucket == 3, 2, // 64+
                                 IOSizeBucket == 4, 3, // All IO Sizes
                                 IOSizeBucket)
)
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| where isempty(ioSizeBucket) or IOSizeBucket =~ ioSizeBucket
| parse BlobPath with BlobPath "?" *
| extend BlobPath = iff(isempty(BlobPath), SurfaceName, BlobPath)
| extend HistogramDesc = replace_string(HistogramDesc, 'UltraSSD', 'DirectDrive')
| summarize Q99 = max(Bin_Q95) by bin(todatetime(PreciseTimeStamp), 5s), BlobPath
// convert to milliseconds
| extend Q99 = Q99 / 1000.0
```

**Params:** `{histogramDesc}`, `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{ioSizeBucket}`

---

### Azure Host VM IO Block Sizes

_Widget purpose:_ Q99 in milliseconds

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageClient > Per-Layer > Per-Layer > Q99 in milliseconds`

**Tables:** `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`

```kusto
OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
    | distinct IOSizeBucket
    | union (
        OsRDSSDSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
        | distinct IOSizeBucket
    )
    | union (
        OsUltraSSDLatencyHistogramTableV2
        | where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId
        | distinct IOSizeBucket
        //
        // For UltraDisk, we have more granular IO Size Buckets
        // Below query summarizes them to just 3 sizes, as BlobCache telemetry 0-8k, 8-64k, 64k+
        //
        | extend IOSizeBucket = case(IOSizeBucket in (0, 1), 0, // 0 - 8k
                                     IOSizeBucket == 2, 1, // 8 - 64k
                                     IOSizeBucket == 3, 2, // 64+
                                     IOSizeBucket == 4, 3, // All IO Sizes
                                     IOSizeBucket)
    )
| extend IOSizeBucket = case(IOSizeBucket == 0, "0-8k", 
                            IOSizeBucket == 1, "8k-64k", 
                            IOSizeBucket == 2, "64k+", 
                            IOSizeBucket == 3, "All",
                            "Unknown")
| distinct Value = IOSizeBucket
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Xstore e2e Latency Top Summary

_Widget purpose:_ Average E2E Latency (in ms) Stats

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > Latency > Latency > StorageServer (Xstore) > Average E2E Latency (in ms) Stats`

**Tables:** `OsXIOHealthSignalEvent`
**Aggregations:** `summarize arg_max(AverageE2ELatency, *) by RequestType`
**Output columns:** `PreciseTimeStamp`, `RequestType`, `AverageE2ELatency`

```kusto
let accounts = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and SurfaceName contains containerId and Type in (0, 4)
| parse BlobPath with * "/" AccountName "/" *
| distinct AccountName;
database('Xstore').AccountTransactionOneMinuteEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| parse AccountName with AccountName ";" *
| where AccountName in (accounts)
| project PreciseTimeStamp, RequestType = strcat(AccountName, "-", RequestType), AverageE2ELatency, AverageServerLatency
| summarize arg_max(AverageE2ELatency, *) by RequestType
| project PreciseTimeStamp, RequestType, AverageE2ELatency
| sort by AverageE2ELatency desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{cluster}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Xstore Latency Stats

_Widget purpose:_ Average E2E Latency (includes Server/Network/Client) (in ms)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageServer (Xstore) > Average E2E Latency (includes Server/Network/Client) (in ms)`

**Tables:** `OsXIOHealthSignalEvent`
**Output columns:** `PreciseTimeStamp`, `RequestType`, `AverageE2ELatency`, `AverageServerLatency`

```kusto
let accounts = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and SurfaceName contains containerId and Type in (0, 4)
| parse BlobPath with * "/" AccountName "/" *
| distinct AccountName;
database('Xstore').AccountTransactionOneMinuteEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| parse AccountName with AccountName ";" *
| where AccountName in (accounts)
| project PreciseTimeStamp, RequestType = tostring(strcat(AccountName, "-", RequestType)), AverageE2ELatency, AverageServerLatency
```

**Params:** `{queryFrom}`, `{queryTo}`, `{cluster}`, `{nodeId}`, `{containerId}`

---

### Azure Host VM Xstore Latency Stats

_Widget purpose:_ Average Server Latency (in ms)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageServer (Xstore) > Average Server Latency (in ms)`

**Tables:** `OsXIOHealthSignalEvent`
**Output columns:** `PreciseTimeStamp`, `RequestType`, `AverageE2ELatency`, `AverageServerLatency`

```kusto
let accounts = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and SurfaceName contains containerId and Type in (0, 4)
| parse BlobPath with * "/" AccountName "/" *
| distinct AccountName;
database('Xstore').AccountTransactionOneMinuteEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| parse AccountName with AccountName ";" *
| where AccountName in (accounts)
| project PreciseTimeStamp, RequestType = tostring(strcat(AccountName, "-", RequestType)), AverageE2ELatency, AverageServerLatency
```

**Params:** `{queryFrom}`, `{queryTo}`, `{cluster}`, `{nodeId}`, `{containerId}`

---

### Azure Host VM Xstore Latency Top Summary

_Widget purpose:_ Average Server Latency (in ms) Stats

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > Latency > Latency > StorageServer (Xstore) > Average Server Latency (in ms) Stats`

**Tables:** `OsXIOHealthSignalEvent`
**Aggregations:** `summarize arg_max(AverageServerLatency, *) by RequestType`
**Output columns:** `PreciseTimeStamp`, `RequestType`, `AverageServerLatency`

```kusto
let accounts = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and SurfaceName contains containerId and Type in (0, 4)
| parse BlobPath with * "/" AccountName "/" *
| distinct AccountName;
database('Xstore').AccountTransactionOneMinuteEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| parse AccountName with AccountName ";" *
| where AccountName in (accounts)
| project PreciseTimeStamp, RequestType = strcat(AccountName, "-", RequestType), AverageE2ELatency, AverageServerLatency
| summarize arg_max(AverageServerLatency, *) by RequestType
| project PreciseTimeStamp, RequestType, AverageServerLatency
| sort by AverageServerLatency desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{cluster}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM Xstore Server Lat per Blob

_Widget purpose:_ Per-Blob Average Server Latency (in ms) 

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Latency > Latency > StorageServer (Xstore) > Per-Blob Average Server Latency (in ms) `

**Tables:** `OsXIOHealthSignalEvent`
**Aggregations:** `summarize AvgServerTimeInMs = avg(AvgServerTimeInMs) by Time = bin(IntervalStartTime, 1m), BlobPath = strcat(RequestType, "-", BlobPath)`

```kusto
let blobs = OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId and Type in (0, 4)
| parse BlobPath with * "/" BlobPathStr "?" *
| distinct BlobPathStr;
database('Xstore').XStoreAccountRealtimeTransaction
| where PreciseTimeStamp between (startTime .. endTime)
| extend BlobPath = strcat(split(Account, ";")[0], "/", Container, "/abcd")
| where BlobPath in (blobs)
| summarize AvgServerTimeInMs = avg(AvgServerTimeInMs) by Time = bin(IntervalStartTime, 1m), BlobPath = strcat(RequestType, "-", BlobPath)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---
