# Host Charts

> Source: **Azure Host — Azure Host Node** dashboard, chapter **Host Charts** (28 queries across 9 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ASAP

### Azure Host VM ASAP 2.0 IO Stats

_Widget purpose:_ Node ASAP IO Stats

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > ASAP > Node ASAP IO Stats`

```kusto
OsAsapCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and ContainerId contains containerId and NodeId == nodeId
| parse blobPath with "XDISK:" ddBlobPath "/" *
| extend BlobPath = case(BlobPath contains "?", split(BlobPath, "?")[0], BlobPath)
| where isempty(blobPath) or BlobPath contains blobPath or (BlobPath contains ddBlobPath and BlobPath contains "md-dd-")
| extend AvgReadIOSizeInBytes = ReadMBPS * 1024 * 1024 / ReadIOPS,
         AvgWriteIOSizeInBytes = WriteMBPS * 1024 * 1024 / WriteIOPS
| extend AvgBqeReadLatencyInMS = DeltaBqeLatencyDiskReadIoBucketLatencySum / DeltaBqeLatencyDiskReadIoBucketSampleCount / 1000.0,
         AvgBqeWriteLatencyInMS = DeltaBqeLatencyDiskWriteIoBucketLatencySum / DeltaBqeLatencyDiskWriteIoBucketSampleCount / 1000.0,
         AvgFOBackendReadLatencyInMS = DeltaBackendLatencyDiskReadIoBucketLatencySum / DeltaBackendLatencyDiskReadIoBucketSampleCount / 1000.0,
         AvgFOBackendWriteLatencyInMS = DeltaBackendLatencyDiskWriteIoBucketLatencySum / DeltaBackendLatencyDiskWriteIoBucketSampleCount / 1000.0,
         AvgSchedReadLatencyInMS = DeltaSchedLatencyDiskReadIoBucketLatencySum / DeltaSchedLatencyDiskReadIoBucketSampleCount / 1000.0,
         AvgSchedWriteLatencyInMS = DeltaSchedLatencyDiskWriteIoBucketLatencySum / DeltaSchedLatencyDiskWriteIoBucketSampleCount / 1000.0
| summarize 
            FO_IOPS = sum(DeltaFoCompleted) / max(OsDiagDurationInSec),
            FO_MBPS = sum(DeltaFoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
            PO_IOPS = sum(DeltaPoCompleted) / max(OsDiagDurationInSec), 
            PO_MBPS = sum(DeltaPoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
            IOPS = sum(IOPS), MBPS = sum(MBPS), 
            ReadIOPS = sum(ReadIOPS), WriteIOPS = sum(WriteIOPS), MaxReadIOPS = max(MaxReadIOPS), MaxReadMBPS = max(MaxReadMBPS),
            MaxWriteIOPS = max(MaxWriteIOPS), MaxWriteMBPS = max(MaxWriteMBPS),
            QD = sum(QD),
            AvgReadIOSizeInBytes = avg(AvgReadIOSizeInBytes),
            AvgWriteIOSizeInBytes = avg(AvgWriteIOSizeInBytes),
            DeltaFoCompleted = sum(DeltaFoCompleted), DeltaPoCompleted = sum(DeltaPoCompleted), DeltaIOCompleted = sum(DeltaIOCompleted),
            AvgReadLatencyInMS = avg(AverageReadLatency), AvgWriteLatencyInMS = avg(AverageWriteLatency),
            AvgBqeReadLatencyInMS = avg(AvgBqeReadLatencyInMS), AvgBqeWriteLatencyInMS = avg(AvgBqeWriteLatencyInMS),
            AvgFOBackendReadLatencyInMS = avg(AvgFOBackendReadLatencyInMS), AvgFOBackendWriteLatencyInMS = avg(AvgFOBackendWriteLatencyInMS),
            AvgSchedReadLatencyInMS = avg(AvgSchedReadLatencyInMS), AvgSchedWriteLatencyInMS = avg(AvgSchedWriteLatencyInMS),
            MaxReadLatencyInMS = max(DeltaIoLatencyDiskReadIoBucketMaxLatency / 1000.0), 
            MaxWriteLatencyInMS = max(DeltaIoLatencyDiskWriteIoBucketMaxLatency / 1000.0),
            MaxSchedReadLatencyInMS = max(DeltaSchedLatencyDiskReadIoBucketMaxLatency / 1000.0), 
            MaxSchedWriteLatencyInMS = max(DeltaSchedLatencyDiskWriteIoBucketMaxLatency / 1000.0),
            MaxBqeReadLatencyInMS = max(DeltaBqeLatencyDiskReadIoBucketMaxLatency / 1000.0), 
            MaxBqeWriteLatencyInMS = max(DeltaBqeLatencyDiskWriteIoBucketMaxLatency / 1000.0),
            MaxBackendReadLatencyInMS = max(DeltaBackendLatencyDiskReadIoBucketMaxLatency / 1000.0), 
            MaxBackendWriteLatencyInMS = max(DeltaBackendLatencyDiskWriteIoBucketMaxLatency / 1000.0),
            BqeExceptions = sum(DeltaBqeExceptions), 
            BqeTimeoutExceptions = sum(DeltaBqeTimeoutExceptions),
            XioTimeoutExceptions = sum(DeltaXioTimeoutExceptions), SwingTimeoutExceptions = sum(DeltaSwingTimeoutExceptions), 
            CrcMismatchExceptions = sum(DeltaCrcMismatchExceptions), XioInvalidSessionExceptions = sum(DeltaXioInvalidSessionExceptions),
            XioHttpStatusNotOkExceptions = sum(DeltaXioHttpStatusNotOkExceptions)
            by bin(todatetime(OsDiagHostTimeStamp), 5s)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`, `{blobPath}`

---

## Host Memory

### HostResourceManager High Level Memory Usage Breakdown

_Widget purpose:_ HostResourceManager High Level Memory Usage (by MaxCommitUsageBytesTotal)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `TimeSeries`
Source panel: `Host Charts > Host Memory > HostResourceManager High Level Memory Usage (by MaxCommitUsageBytesTotal)`

```kusto
//HostResourceManager High Level Memory Usage Breakdown
HostResourceManagerResourceSnapshotEntries
| where TIMESTAMP between (startTime .. endTime) and NodeId == nodeId
| where (IdentifierLevel1 == 'System' and (IdentifierLevel2 != 'Pool' or IdentifierLevel3 == 'TotalPoolUsage'))
    or (IdentifierLevel1 == 'Process' and IdentifierLevel2 == 'Process' and IdentifierLevel3 in ('TotalProcessUsage', 'TotalSharedCommit'))
| project TIMESTAMP, NodeId, SnapshotId, CommitUsageBytes_Total_Max, IdentifierLevel = strcat(IdentifierLevel0,'_',IdentifierLevel1,'_',IdentifierLevel2,'_',IdentifierLevel3)
| summarize CommitUsageBytes_Total_Max = max(CommitUsageBytes_Total_Max) by SnapshotId, IdentifierLevel, bin(TIMESTAMP, 1m)
//| evaluate pivot(IdentifierLevel, max(max_CommitUsageBytes_Total_Max), TIMESTAMP)
//| extend drawChart = 1 //meant to workaround validation in ASI
| project TIMESTAMP, IdentifierLevel, CommitUsageBytes_Total_Max
| order by TIMESTAMP asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### HostResourceManager Top Pool Tags

_Widget purpose:_ HostResourceManager Top Pool Tags (by MaxCommitUsageBytesTotal)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `TimeSeries`
Source panel: `Host Charts > Host Memory > HostResourceManager Top Pool Tags (by MaxCommitUsageBytesTotal)`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('KernelAgent').HostResourceManagerResourceSnapshotEntries
| where TIMESTAMP between (startTime .. endTime) and NodeId == nodeId
| where IdentifierLevel1 == 'System' and IdentifierLevel2 == 'Pool' and IdentifierLevel3 != 'TotalPoolUsage'
| project TIMESTAMP, NodeId, SnapshotId, CommitUsageBytes_Total_Max, IdentifierLevel3
| summarize CommitUsageBytes_Total_Max = max(CommitUsageBytes_Total_Max)
    //, max(PhysicalUsageBytes_Total_Max)
    by NodeId, SnapshotId, PoolTag = IdentifierLevel3, bin(TIMESTAMP, 1m)
//| evaluate pivot(PoolTag, max(max_CommitUsageBytes_Total_Max), NodeId, TIMESTAMP)
| project TIMESTAMP, PoolTag, CommitUsageBytes_Total_Max
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `IdentifierLevel1 == "System"`

---

### HostResourceManager Top Processes

_Widget purpose:_ HostResourceManager Top Processes (by MaxCommitUsageBytesTotal)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `TimeSeries`
Source panel: `Host Charts > Host Memory > HostResourceManager Top Processes (by MaxCommitUsageBytesTotal)`

```kusto
HostResourceManagerResourceSnapshotEntries
| where TIMESTAMP between (startTime .. endTime) and NodeId == nodeId
| where IdentifierLevel1 == 'Process' and IdentifierLevel2 != 'Process'
| project TIMESTAMP, NodeId, SnapshotId, CommitUsageBytes_Total_Max, IdentifierLevel2, IdentifierLevel3
| summarize CommitUsageBytes_Total_Max = sum(CommitUsageBytes_Total_Max)
    //, max(PhysicalUsageBytes_Total_Max)
    by NodeId, SnapshotId, ProcessName=IdentifierLevel2, bin(TIMESTAMP, 1m) 
//| evaluate pivot(ProcessName, max(sum_CommitUsageBytes_Total_Max), NodeId, TIMESTAMP)
| project TIMESTAMP, ProcessName, CommitUsageBytes_Total_Max
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `IdentifierLevel1 == "Process"`

---

### Hypervisor Metadata Memory Partition

_Widget purpose:_ Hypervisor Metadata Memory Partition MBytes

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `TimeSeries`
Source panel: `Host Charts > Host Memory > Hypervisor Metadata Memory Partition MBytes`

```kusto
//Hypervisor Metadata Memory Partition
KaHostSummary
| where TIMESTAMP between (startTime .. endTime) and NodeId == nodeId
| project TIMESTAMP, VmMetadataPartitionTotalMB, VmMetadataPartitionTotalMB_Min, VmMetadataPartitionAvailableMB, VmMetadataPartitionAvailableMB_Min
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Host System Partition Memory

_Widget purpose:_ System Partition MBytes (Host OS)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `TimeSeries`
Source panel: `Host Charts > Host Memory > System Partition MBytes (Host OS)`

```kusto
//Host System Partition
KaHostSummary
| where TIMESTAMP between (startTime .. endTime) and NodeId == nodeId
| project TIMESTAMP, SystemTotalMB, SystemTotalMB_Min, AvailableMB, AvailableMB_Min, ResidentAvailableMB, ResidentAvailableMB_Min
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### VM Memory Partition All Pages

_Widget purpose:_ VM Memory Partition MBytes (including IO Space and metadata)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `TimeSeries`
Source panel: `Host Charts > Host Memory > VM Memory Partition MBytes (including IO Space and metadata)`

```kusto
//VM Memory Partition - All Pages
KaHostSummary
| where TIMESTAMP between (startTime .. endTime) and NodeId == nodeId
| project TIMESTAMP, VmMemoryPartitionTotalMB = VmPartitionTotalMB + VmPartitionIOSpaceTotalMB, VmMemoryPartitionAvailableMB = VmPartitionAvailableMB + VmPartitionIOSpaceAvailableMB
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### VM Memory Partition IO Space Pages

_Widget purpose:_ VM Memory Partition MBytes (IO Space only)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `TimeSeries`
Source panel: `Host Charts > Host Memory > VM Memory Partition MBytes (IO Space only)`

```kusto
//VM Memory Partition - IO Space Pages
KaHostSummary
| where TIMESTAMP between (startTime .. endTime) and NodeId == nodeId
| project TIMESTAMP, VmPartitionIOSpaceTotalMB, VmPartitionIOSpaceTotalMB_Min, VmPartitionIOSpaceAvailableMB, VmPartitionIOSpaceAvailableMB_Min
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Host System

### Azure Host Drive Free Space

_Widget purpose:_ C Drive Free Space %

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Host System > System > C Drive Free Space %`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\LogicalDisk(", driveLetter, @":)\\% Free Space').dimensions('NodeID').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{driveLetter}`, `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

### Azure Host Drive Free Space

_Widget purpose:_ D Drive Free Space %

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Host System > System > D Drive Free Space %`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\LogicalDisk(", driveLetter, @":)\\% Free Space').dimensions('NodeID').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{driveLetter}`, `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

### Azure Host Node Available Memory

_Widget purpose:_ Host Available Memory (MBytes)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Host System > System > Host Available Memory (MBytes)`

```kusto
let query = strcat(@"metricNamespace('HostAgent.Counters').metric('\\Memory\\Available MBytes').dimensions('NodeID','Cluster').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

### Azure Host CPU 5 seconds

_Widget purpose:_ Host CPU (5 seconds)

Cluster: `intmgmtshared.centralus.kusto.windows.net` · Database: `Fleet` · Type: `TimeSeries`
Source panel: `Host Charts > Host System > System > Host CPU (5 seconds)`

```kusto
MetricsPerNode
| where PreciseTimestamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimestamp, RootVirtualProcessorTotalRunTimePercent
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host VP CPU

_Widget purpose:_ Host CPU Usage Graph (1 min avg)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Host System > System > Host CPU Usage Graph (1 min avg)`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\Hyper-V Hypervisor Root Virtual Processor(_Total)\\% Total Run Time').dimensions('NodeID').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

### Azure Host Node NPP Bytes

_Widget purpose:_ Host Nonpaged Pool Bytes

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Host System > System > Host Nonpaged Pool Bytes`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\Memory\\Pool Nonpaged Bytes').dimensions('NodeID','Cluster').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

### Azure Host Node Process Handle Count

_Widget purpose:_ Host Process Total Handle Count

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Host System > System > Host Process Total Handle Count`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\Process(_Total)\\Handle Count').dimensions('NodeID','Cluster').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

## Local Disks

### HostStorage Avg IO Latency

_Widget purpose:_ Local Disk Avg Latencies (microseconds)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `Host Charts > Local Disks > Local Disks > Local Disk Avg Latencies (microseconds)`

```kusto
WindowsStorageEvents
| where PreciseTimeStamp between ((startTime - 1h)..(endTime + 1h))
| where NodeId == nodeId
| where ProviderName == "Microsoft-Windows-StorPort"
| where EventId == 505 and toint(Version) > 3
| where Lun == 0 and Target == 0 // Only Physical drives
| invoke GenericDecodeEventData()
| extend TotalIoCount = tolong(EventDataJson.TotalIoCount)
| extend TotalReadWriteLatency = tolong(iff(isempty(EventDataJson.BucketIoLatency1_100ns), 0, EventDataJson.BucketIoLatency1_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency2_100ns), 0, EventDataJson.BucketIoLatency2_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency3_100ns), 0, EventDataJson.BucketIoLatency3_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency4_100ns), 0, EventDataJson.BucketIoLatency4_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency5_100ns), 0, EventDataJson.BucketIoLatency5_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency6_100ns), 0, EventDataJson.BucketIoLatency6_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency7_100ns), 0, EventDataJson.BucketIoLatency7_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency8_100ns), 0, EventDataJson.BucketIoLatency8_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency9_100ns), 0, EventDataJson.BucketIoLatency9_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency10_100ns), 0, EventDataJson.BucketIoLatency10_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency11_100ns), 0, EventDataJson.BucketIoLatency11_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency12_100ns), 0, EventDataJson.BucketIoLatency12_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency13_100ns), 0, EventDataJson.BucketIoLatency13_100ns)) +
                                 tolong(iff(isempty(EventDataJson.BucketIoLatency14_100ns), 0, EventDataJson.BucketIoLatency14_100ns))
| extend AvgReadWriteLatency_100ns = TotalReadWriteLatency / TotalIoCount
| extend AvgReadWriteLatency_us = AvgReadWriteLatency_100ns / 10
| project PreciseTimeStamp, DeviceGuid, AvgReadWriteLatency_us //, Version
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `ProviderName == "Microsoft-Windows-StorPort"`

---

### Azure Host Disk Status

_Widget purpose:_ Local Disk Health Status

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Local Disks > Local Disks > Local Disk Health Status`

```kusto
NodeDiskHealthStatusEtwTable  
| where PreciseTimeStamp between ( (startTime - 1h) .. (endTime + 1h))
| where NodeId == nodeId
| summarize 
    TotalDisks = max(TotalDisks), 
    HealthyDisks = min(HealthyDisks), 
    OnlineDisks = min(OnlineDisks), 
    TotalNonVhdDisks = max(TotalNonVhdDisks), 
    HealthyNonVhdDisks = min(HealthyNonVhdDisks), 
    OnlineNonVhdDisks = min(OnlineNonVhdDisks)
    by bin(PreciseTimeStamp, 30m)
| order by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### HostStorage High Latency IO Counts

_Widget purpose:_ Local Disk High Latency IO Count

Cluster: `azcore.centralus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `Host Charts > Local Disks > Local Disks > Local Disk High Latency IO Count`

```kusto
WindowsStorageEvents
| where PreciseTimeStamp between ((startTime - 1h)..(endTime + 1h))
| where NodeId == nodeId
| where ProviderName == "Microsoft-Windows-StorPort"
| where EventId == 505 and toint(Version) > 3
| where Lun == 0 and Target == 0 // Only Physical drives
| invoke GenericDecodeEventData()
| extend HighLatencyIoCount = tolong(EventDataJson.HighLatencyIoCount)
| project PreciseTimeStamp, DeviceGuid, HighLatencyIoCount
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `ProviderName == "Microsoft-Windows-StorPort"`

---

### HostStorage Max IO Latency

_Widget purpose:_ Local Disk Max Latencies (microseconds)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `Host Charts > Local Disks > Local Disks > Local Disk Max Latencies (microseconds)`

```kusto
WindowsStorageEvents
| where PreciseTimeStamp between ((startTime - 1h)..(endTime + 1h))
| where NodeId == nodeId
| where ProviderName == "Microsoft-Windows-StorPort"
| where EventId == 505 and toint(Version) > 3
| where Lun == 0 and Target == 0 // Only Physical drives
| invoke GenericDecodeEventData()
| extend MaxReadWriteLatency_100ns = tolong(EventDataJson.MaxReadWriteLatency_100ns)
| extend MaxReadWriteLatency_us = MaxReadWriteLatency_100ns / 10
| project PreciseTimeStamp, DeviceGuid, MaxReadWriteLatency_us
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `ProviderName == "Microsoft-Windows-StorPort"`

---

### Azure Host StorPort IO Telemetry Stats

_Widget purpose:_ StorPort IO Telemetry (per hour)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Local Disks > Local Disks > StorPort IO Telemetry (per hour)`

```kusto
WindowsEventTable
| where PreciseTimeStamp between ((startTime - 12h) .. (endTime + 12h)) and NodeId == nodeId
| where Description contains "storport" and ProviderName == "Microsoft-Windows-StorPort" and EventId == 505
| parse Description with * "Disk Device Guid is {" DiskGuid "}" * "Total IO:" TotalIOs " " * "Total Bytes Read:" BytesRead " " * "Total Bytes Written:" BytesWritten
| project PreciseTimeStamp, EventId, todouble(TotalIOs), todouble(BytesRead), todouble(BytesWritten)
| summarize TotalIOs = sum(TotalIOs), TotalBytesRead = sum(BytesRead), TotalBytesWritten = sum(BytesWritten) by PreciseTimeStamp = bin(PreciseTimeStamp, 5m)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `Description contains "storport"`

---

## MPF

### Azure Host VM MPF Stats

_Widget purpose:_ Node MPF IO Stats 

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > MPF > Node MPF IO Stats `

```kusto
OsMpfCounterTable | union OsMpfLogicalDiskCounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| where ContainerId == containerId or isempty(containerId)
//| where IsNewDisk == 0
| extend MBPS = column_ifexists("MBPS", BPS/1024/1024),
         ReadMBPS = column_ifexists("ReadMBPS", ReadBPS/1024/1024),
         WriteMBPS = column_ifexists("WriteMBPS", WriteBPS/1024/1024),
         ReadIOSizeInBytes = DeltaReadByteCount * 1.0 / DeltaReadIOCount,
         WriteIOSizeInBytes = DeltaWriteByteCount * 1.0 / DeltaWriteIOCount
| summarize IOPS = sum(IOPS), 
            WriteIOPS = sum(WriteIOPS), ReadIOPS = sum(ReadIOPS), 
            MBPS = sum(MBPS), ReadMBPS = sum(ReadMBPS), WriteMBPS = sum(WriteMBPS), ReadIOSizeInBytes = avg(ReadIOSizeInBytes), WriteIOSizeInBytes = avg(WriteIOSizeInBytes),
            TotalDisks = dcount(ChildControllerSerialNumber)
             by bin(PreciseTimeStamp, 5s)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

## Networking

### Azure Host Networking PortQuotaRundown

_Widget purpose:_ Port Count by Process

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Networking > Networking > Port Count by Process`

```kusto
CloudNetworkingTriageTable
| where PreciseTimeStamp between (startTime .. endTime) and TaskName == 'PortQuotaRundown' and NodeId == nodeId
| extend Message = extract_all(@'Port_Usage_(?P<Id>\d+)_Is_Service="(?P<IsService>0|1)" Port_Usage_(?P<Id>\d+)_Process_Name="(?P<ProcessName>[^\"]+)" Port_Usage_(?P<Id>\d+)_Port_Count="(?P<PortCount>\d+)"', dynamic(['Id', 'IsService', 'ProcessName', 'PortCount']), Message)
| mv-expand Message
| project PreciseTimeStamp, NodeId, Cluster, Id = toint(Message[0]), IsService = tobool(Message[1]), ProcessName = tostring(Message[2]), PortCount = toint(Message[3])
| project PreciseTimeStamp, ProcessName, PortCount
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### TCPIP Connection Counters

Cluster: `wdgeventstore.kusto.windows.net` · Database: `HostOSCoreNet` · Type: `TimeSeries`
Source panel: `Host Charts > Networking > Networking > TCPIP Connection Counters`

```kusto
//Networking - TCPIP Connection Counters - TCPIPConnectionFailures.kql
let specificNodeId = nodeId;
let counterName = dynamic([
	"TCPv4\\Connection Failures",
	"TCPv4\\Connections Active",
	"TCPv4\\Connections Established",
	"TCPv4\\Connections Passive",
	"TCPv4\\Connections Reset",
	"TCPv4\\Segments Retransmitted/sec",
	"TCPv6\\Connection Failures",
	"TCPv6\\Connections Active",
	"TCPv6\\Connections Established",
	"TCPv6\\Connections Passive",
	"TCPv6\\Connections Reset"
	"TCPv6\\Segments Retransmitted/sec"
]);
cluster('wdgeventstore.kusto.windows.net').database('HostOSCoreNet').CoreNetPerfTable
| where Counter in (counterName)
| where PreciseTimeStamp between (startTime..endTime)
| where NodeId == specificNodeId
| project TIMESTAMP, CounterName, CounterValue
| render timechart
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### TCPIP Performance Counters

Cluster: `wdgeventstore.kusto.windows.net` · Database: `HostOSCoreNet` · Type: `TimeSeries`
Source panel: `Host Charts > Networking > Networking > TCPIP Performance Counters`

```kusto
//HostCharts - Networking - TCPIP Performance Counters - TCPIPPerformance.kql
let specificNodeId = nodeId;
let counterName = dynamic([
    "TCPIP Performance Diagnostics\\TCP timeouts",
    "TCPIP Performance Diagnostics\\IPv4 NBLs indicated with low-resource flag",
    "TCPIP Performance Diagnostics\\IPv6 NBLs indicated with low-resource flag",
    "TCPIP Performance Diagnostics\\IPv4 NBLs/sec indicated with low-resource flag"
    "TCPIP Performance Diagnostics\\IPv6 NBLs/sec indicated with low-resource flag"
    "TCPIP Performance Diagnostics\\IPv4 NBLs indicated without prevalidation",
    "TCPIP Performance Diagnostics\\IPv6 NBLs/sec indicated without prevalidation",
    "TCPIP Performance Diagnostics\\TCP checksum errors"
]);
cluster('wdgeventstore.kusto.windows.net').database('HostOSCoreNet').CoreNetPerfTable
| where Counter in (counterName)
| where PreciseTimeStamp between (startTime..endTime)
| where NodeId == specificNodeId
| project TIMESTAMP, CounterName, CounterValue
| render timechart
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## VMs CPU

### Azure Host VMs CPU Usage

_Widget purpose:_ VM CPU Percentage

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > VMs CPU > VMs CPU > VM CPU Percentage`

```kusto
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and CounterName == "Percentage CPU"
| project PreciseTimeStamp, RoleInstanceId, AverageCounterValue
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## VMs Disk IO Stats

### Azure Host StorageClient VMs Disk IOPS

_Widget purpose:_ VM Disk IOPS (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > VMs Disk IO Stats > VMs Disk IO Stats > VM Disk IOPS (StorageClient)`

```kusto
let containers = cluster("AzureCM.kusto.windows.net").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 1h)) and nodeId == nodeIdStr
| union (
    cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
    | where PreciseTimeStamp between ((startTime - 4h) .. (endTime + 2h)) and NodeId == nodeIdStr
    | extend containerId = ContainerId, creationTime = tostring(CreationTime), roleInstanceName = RoleInstanceName, 
         subscriptionId = SubscriptionId, containerType = PolicyName, virtualMachineUniqueId = VirtualMachineUniqueId,
         nodeId = NodeId, tipNodeSessionId = TipNodeSessionId, tenantName = TenantName, availabilitySetName = AvailabilitySetName,
         billingType = "", roleType = RoleType, additionalContainerProperties = AdditionalContainerProperties, Tenant = ClusterName
    | summarize arg_max(PreciseTimeStamp, roleInstanceName) by containerId         
)
| summarize arg_min(PreciseTimeStamp, roleInstanceName) by containerId
| distinct roleInstanceName, containerId
| extend metric = strcat(roleInstanceName, " (", substring(containerId, 0, 13), ")")
;
let containerview = OsXIOSurfaceCounterTable | union (OsRDSSDSurfaceCounterTable)
| union (OsUltraSSDCounterTable | extend SurfaceName = ContainerId | where IsNewDisk == 0 and IsRFR == 0)
| union (OsAsapCounterTable | extend SurfaceName = ContainerId | where IsNewDisk == 0)
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeIdStr and IsNewDisk == 0
| extend containerId = tostring(case(indexof(SurfaceName, "~") > 0, split(SurfaceName, "~")[0], split(SurfaceName, "_")[0]))
| summarize IOPS = sum(IOPS) by bin(PreciseTimeStamp, 5m), containerId
| join kind=leftouter(
    containers
) on containerId
| project-away containerId, containerId1;
let nodeview = containerview | summarize IOPS = sum(IOPS) by bin(PreciseTimeStamp, 5m), metric = "Total_Node", roleInstanceName = "Total_Node";
containerview
| union nodeview
| where isnotempty(roleInstanceName)
| project-away roleInstanceName
```

**Params:** `{nodeIdStr}`, `{startTime}`, `{endTime}`

---

### Azure Host VM StorageClient Disk MBPS

_Widget purpose:_ VM Disk MBPS (StorageClient)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > VMs Disk IO Stats > VMs Disk IO Stats > VM Disk MBPS (StorageClient)`

```kusto
let containers = cluster("AzureCM.kusto.windows.net").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 1h)) and nodeId == nodeIdStr
| union (
    cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
    | where PreciseTimeStamp between ((startTime - 4h) .. (endTime + 4h)) and NodeId == nodeIdStr and isnotempty(RoleInstanceName)
    | extend containerId = ContainerId, creationTime = tostring(CreationTime), roleInstanceName = RoleInstanceName, 
         subscriptionId = SubscriptionId, containerType = PolicyName, virtualMachineUniqueId = VirtualMachineUniqueId,
         nodeId = NodeId, tipNodeSessionId = TipNodeSessionId, tenantName = TenantName, availabilitySetName = AvailabilitySetName,
         billingType = "", roleType = RoleType, additionalContainerProperties = AdditionalContainerProperties, Tenant = ClusterName
)
| summarize arg_min(PreciseTimeStamp, roleInstanceName) by containerId
| distinct containerId, roleInstanceName
| extend metric = strcat(roleInstanceName, " (", substring(containerId, 0, 13), ")")
;
let containerview = OsXIOSurfaceCounterTable | union (OsRDSSDSurfaceCounterTable)
| union (OsUltraSSDCounterTable | extend SurfaceName = ContainerId | where IsNewDisk == 0 and IsRFR == 0)
| union (OsAsapCounterTable | extend SurfaceName = ContainerId | where IsNewDisk == 0)
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeIdStr and IsNewDisk == 0
| extend containerId = tostring(case(indexof(SurfaceName, "~") > 0, split(SurfaceName, "~")[0], split(SurfaceName, "_")[0]))
| summarize MBPS = sum(MBPS) by bin(PreciseTimeStamp, 5m), containerId
| join kind=leftouter(
    containers
) on containerId
| project-away containerId, containerId1;
let nodeview = containerview | summarize MBPS = sum(MBPS) by bin(PreciseTimeStamp, 5m), metric = "Total_Node", roleInstanceName = "Total_Node";
containerview
| union nodeview
| where isnotempty(roleInstanceName)
| project-away roleInstanceName
```

**Params:** `{nodeIdStr}`, `{startTime}`, `{endTime}`

---

## VMs Memory

### Azure Host VMs Memory Usage

_Widget purpose:_ Average Memory Pressure on VMs

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > VMs Memory > VMs Memory > Average Memory Pressure on VMs`

```kusto
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId // and CounterName contains @"\Hyper-V Dynamic Memory VM" and CounterName contains "Current Pressure"
        and CounterName contains "Guest Available Memory"
| project PreciseTimeStamp, RoleInstanceId, AverageCounterValue
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---
