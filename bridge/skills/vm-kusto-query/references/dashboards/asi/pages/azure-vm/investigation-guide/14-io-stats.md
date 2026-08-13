# IO Stats

> Source: **Azure Host - Azure VM** dashboard, chapter **IO Stats** (6 queries across 5 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## IO Charts

### Azure Host VM TDPR IO timechart

_Widget purpose:_ IO Charts

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `IO Stats > IO Charts`

**Tables:** `OsXIOXdiskCounterTable`, `OsXIOSurfaceCounterTable`
**Aggregations:** `summarize WriteMBPS = sum(WriteMBPS), ReadMBPS = sum(ReadMBPS), MaxQD = max(MaxQD), ReadIO by bin(todatetime(OsDiagHostTimeStamp), 5s)`

```kusto
OsXIOXdiskCounterTable
| where PreciseTimeStamp between ((startTime - 5s) .. endTime) and NodeId == nodeId and SurfaceName contains containerId
| union (
    OsXIOSurfaceCounterTable
    | where PreciseTimeStamp between ((startTime - 5s) .. endTime) and NodeId == nodeId and SurfaceName contains containerId
)
| parse BlobPath with BlobPath "?" *
| where isempty(blobPath) or BlobPath == blobPath
| summarize 
            WriteMBPS = sum(WriteMBPS),
            ReadMBPS = sum(ReadMBPS),
            MaxQD = max(MaxQD), 
            ReadIOPS = sum(ReadIOPS),
            CacheReadIOPS = sum(DeltaCacheReads) / 5,
            WriteIOPS = sum(WriteIOPS),
            DeltaReads = sum(DeltaReads),
            DeltaWrites = sum(DeltaWrites),
            DeltaFlush = sum(DeltaFlush),
            DeltaThrottled = sum(DeltaThrottled),
            AvgThrottleTimeInMs = sum(DeltaThrottleTimeInSec) * 1000.0 / sum(DeltaThrottled),
            NWREADIOPS = sum(NWReadIOPS), 
            NWWRITEIOPS = sum(NWWriteIOPS), 
            NWQD = sum(XQD), 
            Del503Cnt = sum(Del503Cnt)
            by bin(todatetime(OsDiagHostTimeStamp), 5s)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{blobPath}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ IO Charts

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `IO Stats > IO Charts`

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

## IO Latency Stats during Provisioning

### Azure Host VM TDPR IO Stats Provisioning

_Widget purpose:_ IO Latency Stats during Provisioning

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `IO Stats > IO Latency Stats during Provisioning`

**Tables:** `IaasVmOperations`, `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize arg_min(StartTime, *) by containerId` · `summarize arg_min(StartTime, *) by containerId`

> ⚠️ Verbose machine-generated KQL (78 KB, e.g. histogram aggregations expanded across many bins). Full body extracted to [`14-io-stats--azure-host-vm-tdpr-io-stats-provisioning.kql`](14-io-stats--azure-host-vm-tdpr-io-stats-provisioning.kql); the opening lines are shown below for context. Nothing is truncated — the full query is preserved verbatim in the `.kql` file.

```kusto
let provisioningStartTime = toscalar(cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
| where StartTime between (startTime .. endTime)
        and ContainerId == containerId
| summarize arg_min(StartTime, *) by containerId
| extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
| extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
         VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
         StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
| project VmBootEndTime);
let provisioningEndTime = toscalar(cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
| where StartTime between (startTime .. endTime)
        and ContainerId == containerId
| summarize arg_min(StartTime, *) by containerId
| extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
| extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
         VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
         StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
| project datetime_add('second', ProvisioningDurationInSeconds, VmBootEndTime));
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (provisioningStartTime .. provisioningEndTime) and NodeId == nodeId and SurfaceName contains containerId
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (provisioningStartTime .. provisioningEndTime) and NodeId == nodeId and SurfaceName contains containerId
)
| extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (provisioningStartTime .. provisioningEndTime) and NodeId == nodeId and ContainerId == containerId
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
| parse BlobPath with BlobPath "?" *
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
// ... [truncated — see 14-io-stats--azure-host-vm-tdpr-io-stats-provisioning.kql for full body]
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

## IO Stats during Prefetch

### Azure Host VM TDPR IO Stats Prefetch

_Widget purpose:_ IO Stats during Prefetch

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `IO Stats > IO Stats during Prefetch`

**Tables:** `IaasVmOperations`, `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize arg_min(StartTime, *) by containerId` · `summarize arg_min(StartTime, *) by containerId`

> ⚠️ Verbose machine-generated KQL (78 KB, e.g. histogram aggregations expanded across many bins). Full body extracted to [`14-io-stats--azure-host-vm-tdpr-io-stats-prefetch.kql`](14-io-stats--azure-host-vm-tdpr-io-stats-prefetch.kql); the opening lines are shown below for context. Nothing is truncated — the full query is preserved verbatim in the `.kql` file.

```kusto
let prefetchStartTime = toscalar(cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
| where StartTime between (startTime .. endTime)
        and ContainerId == containerId
| summarize arg_min(StartTime, *) by containerId
| extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
| extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
         VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
         StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
| project datetime_add('second', -PrefetchDurationInSeconds, PrefetchEndTime));
let prefetchEndTime = toscalar(cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
| where StartTime between (startTime .. endTime)
        and ContainerId == containerId
| summarize arg_min(StartTime, *) by containerId
| extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
| extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
         VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
         StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
| project PrefetchEndTime);
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between ((prefetchStartTime - 10s) .. (prefetchEndTime + 5s)) and NodeId == nodeId and SurfaceName contains containerId
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between ((prefetchStartTime - 10s) .. (prefetchEndTime + 5s)) and NodeId == nodeId and SurfaceName contains containerId
)
| extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (prefetchStartTime .. (prefetchEndTime + 5s)) and NodeId == nodeId and ContainerId == containerId
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
| parse BlobPath with BlobPath "?" *
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
// ... [truncated — see 14-io-stats--azure-host-vm-tdpr-io-stats-prefetch.kql for full body]
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

## IO Stats during Provisioning 

### Azure Host VM TDPR Surface Stats Provisioning

_Widget purpose:_ IO Stats during Provisioning 

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `IO Stats > IO Stats during Provisioning `

**Tables:** `IaasVmOperations`, `OsXIOXdiskCounterTable`, `OsXIOSurfaceCounterTable`
**Aggregations:** `summarize arg_min(StartTime, *) by containerId` · `summarize arg_min(StartTime, *) by containerId`

```kusto
let provisioningStartTime = toscalar(cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
| where StartTime between (startTime .. endTime)
        and ContainerId == containerId
| summarize arg_min(StartTime, *) by containerId
| extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
| extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
         VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
         StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
| project VmBootEndTime);
let provisioningEndTime = toscalar(cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
| where StartTime between (startTime .. endTime)
        and ContainerId == containerId
| summarize arg_min(StartTime, *) by containerId
| extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
| extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
         VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
         StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
| project datetime_add('second', ProvisioningDurationInSeconds, VmBootEndTime));
OsXIOXdiskCounterTable
| where PreciseTimeStamp between (provisioningStartTime .. provisioningEndTime) and NodeId == nodeId and SurfaceName contains containerId and IsNewDisk == 1
| union (
    OsXIOSurfaceCounterTable
    | where PreciseTimeStamp between (provisioningStartTime .. provisioningEndTime) and NodeId == nodeId and SurfaceName contains containerId and IsNewDisk == 1
)
| parse BlobPath with BlobPath "?" *
| summarize 
            DeltaReads = sum(DeltaReads),
            DeltaWrites = sum(DeltaWrites),
            DeltaFlush = sum(DeltaFlush),
            DeltaThrottled = sum(DeltaThrottled),
            AvgThrottleTimeInMs = sum(DeltaThrottleTimeInSec) * 1000.0 / sum(DeltaThrottled),
            MaxQD = max(MaxQD), 
            Del503Cnt = sum(Del503Cnt)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

## IO Stats during VmBoot

### Azure Host VM TDPR IO Stats Boot

_Widget purpose:_ IO Stats during VmBoot

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `IO Stats > IO Stats during VmBoot`

**Tables:** `IaasVmOperations`, `OsXIOSurfaceLatencyHistogramTableV2`, `OsRDSSDSurfaceLatencyHistogramTableV2`, `OsUltraSSDLatencyHistogramTableV2`
**Aggregations:** `summarize arg_min(StartTime, *) by containerId` · `summarize arg_min(StartTime, *) by containerId`

> ⚠️ Verbose machine-generated KQL (75 KB, e.g. histogram aggregations expanded across many bins). Full body extracted to [`14-io-stats--azure-host-vm-tdpr-io-stats-boot.kql`](14-io-stats--azure-host-vm-tdpr-io-stats-boot.kql); the opening lines are shown below for context. Nothing is truncated — the full query is preserved verbatim in the `.kql` file.

```kusto
let vmBootStartTime = toscalar(cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
| where StartTime between (startTime .. endTime)
        and ContainerId == containerId
| summarize arg_min(StartTime, *) by containerId
| extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
| extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
         VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
         StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
| project datetime_add('second', -VmBootDurationInSeconds, VmBootEndTime));
let vmBootEndTime = toscalar(cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
| where StartTime between (startTime .. endTime)
        and ContainerId == containerId
| summarize arg_min(StartTime, *) by containerId
| extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
| extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
         VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
         StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
| project VmBootEndTime);
OsXIOSurfaceLatencyHistogramTableV2
| where PreciseTimeStamp between (vmBootStartTime .. vmBootEndTime) and NodeId == nodeId and SurfaceName contains containerId
| union (
    OsRDSSDSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (vmBootStartTime .. vmBootEndTime) and NodeId == nodeId and SurfaceName contains containerId
)
| extend HistogramTypeDesc = database('SharedWorkspace').GetHistogramDesc(HistogramTypeEnum)
| union (
    OsUltraSSDLatencyHistogramTableV2
    | where PreciseTimeStamp between (vmBootStartTime .. vmBootEndTime) and NodeId == nodeId and ContainerId == containerId
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
| parse BlobPath with BlobPath "?" *
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
// ... [truncated — see 14-io-stats--azure-host-vm-tdpr-io-stats-boot.kql for full body]
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---
