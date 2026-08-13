# VM Counters — MPF Stats (v6 VMs Temp Disk) 

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Counters** (2 queries, part 5 of 7).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## MPF Stats (v6 VMs Temp Disk) 

### Azure VM MFND ControllerSettings

_Widget purpose:_ MFND Controller Settings

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > MPF Stats (v6 VMs Temp Disk)  > MFND Controller Settings`

**Tables:** `DirectAccessEvent`
**Output columns:** `TIMESTAMP`, `ContainerId`, `Operation`, `ResultCode`, `SerialNumber`, `LocationPath`, `MfndControllerSettings`

```kusto
cluster('azcore.centralus').database('Fa').DirectAccessEvent
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and ContainerId  == containerId
| project TIMESTAMP, ContainerId, Operation, ResultCode, SerialNumber, LocationPath, MfndControllerSettings
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### Azure Host VM MPF Stats

_Widget purpose:_ MPF Telemetry

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > MPF Stats (v6 VMs Temp Disk)  > MPF Telemetry`

**Tables:** `OsMpfCounterTable`
**Aggregations:** `summarize IOPS = sum(IOPS), WriteIOPS = sum(WriteIOPS), ReadIOPS = sum(ReadIOPS), MBPS = s by bin(PreciseTimeStamp, 5s)`

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
