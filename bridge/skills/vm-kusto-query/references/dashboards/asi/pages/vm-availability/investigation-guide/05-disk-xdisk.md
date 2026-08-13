# Disk & XDisk

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Disk & XDisk** (7 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Disk

### SCSI Disk Perf

_Widget purpose:_ Local SCSI Disk Perf (Average IO Latency) on Node

Cluster: `azcore.centralus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `Disk & XDisk > Disk > 505 SCSI Disk Perf > 505 SCSI Disk Perf > Local SCSI Disk Perf (Average IO Latency) on Node`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('SharedWorkspace').GetStorportIoPerfForDisk(nodeid=nodeid, scsi="")
| where PreciseTimeStamp between (starttime .. endtime)
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, SCSIAddress, TotalIo, TotalReadBytes, TotalWriteBytes, HighLatIos, AvgIoLatency
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### Disk Event in Node Windows Event

_Widget purpose:_ Disk Event

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Disk & XDisk > Disk > Disk Windows Event > Disk Windows Event > Disk Event`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
| where EventId !in (505, 504, 146, 145, 142)
| where ProviderName in ("BlobCache", "Disk", "Barbera", "disk", "stornvme", "VhdDiskPrt", "Microsoft-Windows-Ntfs", "Microsoft-Windows-StorPort", "Vdc", "Microsoft-Windows-Hyper-V-SynthStor")
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by TimeCreated asc 
| extend level = case (Level == 1, "critical", Level == 2, "error", Level == 3, "warning", "info")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### BlobCache

_Widget purpose:_ Disk Event Timeline

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Disk & XDisk > Disk > Disk Windows Event > Disk Windows Event > Disk Event Timeline`

```kusto
let event504 = (cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
| where EventId == 504 and ProviderName == "Microsoft-Windows-StorPort"
| parse Description with * "There were " ErrorHint:long "total errors" *
| where ErrorHint > 0
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId, ErrorHint, Description, NodeId, Cluster 
| extend StartTime = TimeCreated, EndTime = TimeCreated + 1m, GroupBy = strcat("Errors in StorPort 504" ), Content = tostring(ErrorHint));
let event504unqiue = (cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
| where EventId == 504 and ProviderName == "Microsoft-Windows-StorPort"
| where Description contains "few unique errors"
| extend ErrorHint = 1
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId, ErrorHint, Description, NodeId, Cluster 
| extend StartTime = TimeCreated, EndTime = TimeCreated + 1m, GroupBy = strcat("Unique Error in StorPort 504" ), Content = tostring(ErrorHint));
let event505 = (cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
| where EventId == 505 and ProviderName == "Microsoft-Windows-StorPort"
| parse Description with * "Corresponding Class Disk Device Guid is {" DiskDeviceGuid:string "}" * "The IO failed counts are" bucket1:long "," bucket2:long "," bucket3:long "," bucket4:long "," bucket5:long 
    "," bucket6:long "," bucket7:long "," bucket8:long "," bucket9:long "," bucket10:long 
    "," bucket11:long "," bucket12:long "," bucket13:long "," bucket14:long *
| extend  ErrorHint =   bucket1 + bucket2 + bucket3 + bucket3 + bucket4 + bucket5 + bucket6 + bucket7 + bucket8 + bucket9 + bucket10 + bucket11 + bucket12  +  bucket13  +  bucket14
| where ErrorHint > 0
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId, DiskDeviceGuid, ErrorHint, Description, NodeId, Cluster 
| extend StartTime = TimeCreated, EndTime = TimeCreated + 1m, GroupBy = strcat("Errors in StorPort 505" ), Content = tostring(ErrorHint));
let diskEvents = (cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
| where EventId !in (505, 504, 146, 145, 142)
| where ProviderName in ("BlobCache", "Disk", "Barbera", "disk", "stornvme", "VhdDiskPrt", "Microsoft-Windows-Ntfs", "Microsoft-Windows-StorPort", "Vdc", "Microsoft-Windows-Hyper-V-SynthStor")
// | where Description !contains "RDMA Session Init Failed."
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| extend StartTime = TimeCreated, EndTime = TimeCreated + 1m, GroupBy = strcat(ProviderName, " : ", EventId), Content = EventId);
union event504, event505, event504unqiue, diskEvents
| order by GroupBy asc, TimeCreated asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `Description contains "few unique errors"`

---

### Query Storeport Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Disk & XDisk > Disk > Storport Device`

```kusto
let event504 = WindowsEventTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventId == 504 and ProviderName == "Microsoft-Windows-StorPort"
| parse Description with * "Corresponding Class Disk Device Guid is {" DiskDeviceGuid:string "}" * "There were " Errors:long "total errors" *
| where Errors > 0
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId,DiskDeviceGuid, Errors, Description;
let event504unqiue = WindowsEventTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventId == 504 and ProviderName == "Microsoft-Windows-StorPort"
| where Description contains "few unique errors"
| parse Description with * "Corresponding Class Disk Device Guid is {" DiskDeviceGuid:string "}" *
| extend Errors = 1
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId,DiskDeviceGuid, Errors, Description; 
let event505 = WindowsEventTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventId == 505 and ProviderName == "Microsoft-Windows-StorPort"
| parse Description with * "Corresponding Class Disk Device Guid is {" DiskDeviceGuid:string "}" * "The IO failed counts are" bucket1:long "," bucket2:long "," bucket3:long "," bucket4:long "," bucket5:long 
    "," bucket6:long "," bucket7:long "," bucket8:long "," bucket9:long "," bucket10:long 
    "," bucket11:long "," bucket12:long "," bucket13:long "," bucket14:long *
| extend  Errors =   bucket1 + bucket2 + bucket3 + bucket3 + bucket4 + bucket5 + bucket6 + bucket7 + bucket8 + bucket9 + bucket10 + bucket11 + bucket12  +  bucket13  +  bucket14
| where Errors > 0
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId, DiskDeviceGuid, Errors, Description;
union event504, event505, event504unqiue
| order by TimeCreated asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Description contains "few unique errors"`

---

### Query Storport Event Timeline

_Widget purpose:_ Storport Event Timeline

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Disk & XDisk > Disk > Storport Device > Storport Event Timeline`

```kusto
let event504 = WindowsEventTable()
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventId == 504 and ProviderName == "Microsoft-Windows-StorPort"
| parse Description with * "There were " ErrorHint:long "total errors" *
| where ErrorHint > 0
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId, ErrorHint, Description, NodeId, Cluster 
| extend StartTime = TimeCreated, EndTime = TimeCreated + 1m, GroupBy = strcat("StorPort: 504 Errors" ), Content = tostring(ErrorHint);
let event504unqiue = WindowsEventTable()
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventId == 504 and ProviderName == "Microsoft-Windows-StorPort"
| where Description contains "few unique errors"
| extend ErrorHint = 1
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId, ErrorHint, Description, NodeId, Cluster 
| extend StartTime = TimeCreated, EndTime = TimeCreated + 1m, GroupBy = strcat("StorPort: 504 Unqiue Error" ), Content = tostring(ErrorHint);
let event505 = WindowsEventTable()
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventId == 505 and ProviderName == "Microsoft-Windows-StorPort"
| parse Description with * "Corresponding Class Disk Device Guid is {" DiskDeviceGuid:string "}" * "The IO failed counts are" bucket1:long "," bucket2:long "," bucket3:long "," bucket4:long "," bucket5:long 
    "," bucket6:long "," bucket7:long "," bucket8:long "," bucket9:long "," bucket10:long 
    "," bucket11:long "," bucket12:long "," bucket13:long "," bucket14:long *
| extend  ErrorHint =   bucket1 + bucket2 + bucket3 + bucket3 + bucket4 + bucket5 + bucket6 + bucket7 + bucket8 + bucket9 + bucket10 + bucket11 + bucket12  +  bucket13  +  bucket14
| where ErrorHint > 0
| project PreciseTimeStamp, TimeCreated = todatetime(TimeCreated),  ProviderName, Channel, EventId, DiskDeviceGuid, ErrorHint, Description, NodeId, Cluster 
| extend StartTime = TimeCreated, EndTime = TimeCreated + 1m, GroupBy = strcat("StorPort: 505 Errors" ), Content = tostring(ErrorHint);
union event504, event505, event504unqiue
| order by GroupBy asc, TimeCreated asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Description contains "few unique errors"`

---

### Query OsVhddiskEventTable

Cluster: `Azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Disk & XDisk > Disk > VhdDisk > OsVhddiskEventTable`

```kusto
cluster('Azcore.centralus').database('Fa').OsVhddiskEventTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| extend ErrorCode = strcat(substring(ParamBinary1, 46, 2), substring(ParamBinary1, 44, 2), substring(ParamBinary1, 42, 2), substring(ParamBinary1, 40, 2)) , 
  RawClientRequestId = strcat(substring(ParamBinary1, 94, 2), substring(ParamBinary1, 92, 2), substring(ParamBinary1, 90, 2), substring(ParamBinary1, 88, 2), substring(ParamBinary1, 86, 2), substring(ParamBinary1, 84, 2), substring(ParamBinary1, 82, 2), substring(ParamBinary1, 80, 2)),
  Time = strcat(substring(ParamBinary1, 102, 2), substring(ParamBinary1, 100, 2), substring(ParamBinary1, 98, 2), substring(ParamBinary1, 96, 2)),
  LocalPort = strcat(substring(ParamBinary1, 106, 2), substring(ParamBinary1, 104, 2)),
  PendingRequest = substring(ParamBinary1, 108, 2),
  RxCxnTimeoutFactor =  substring(ParamBinary1, 110, 2),
  LastStatus = strcat(substring(ParamBinary1, 150, 2), substring(ParamBinary1, 148, 2), substring(ParamBinary1, 146, 2), substring(ParamBinary1, 144, 2)) ,
  SequenceNumber = strcat(substring(ParamBinary1, 158, 2), substring(ParamBinary1, 156, 2), substring(ParamBinary1, 154, 2), substring(ParamBinary1, 152, 2)),
  Offset = strcat(substring(ParamBinary1, 174, 2), substring(ParamBinary1, 172, 2), substring(ParamBinary1, 170, 2), substring(ParamBinary1, 168, 2), substring(ParamBinary1, 166, 2), substring(ParamBinary1, 164, 2), substring(ParamBinary1, 162, 2), substring(ParamBinary1, 160, 2)),
  IoLength = strcat(substring(ParamBinary1, 182, 2), substring(ParamBinary1, 180, 2), substring(ParamBinary1, 178, 2), substring(ParamBinary1, 176, 2)),
  RecvStatus = strcat(substring(ParamBinary1, 190, 2), substring(ParamBinary1, 188, 2), substring(ParamBinary1, 186, 2), substring(ParamBinary1, 184, 2)),
  RawHttpCode = strcat(substring(ParamBinary1, 198, 2), substring(ParamBinary1, 196, 2), substring(ParamBinary1, 194, 2), substring(ParamBinary1, 192, 2)),
  Retries = substring(ParamBinary1, 200, 2),
  Flags = substring(ParamBinary1, 202, 2), 
  ResubmitCount = substring(ParamBinary1, 204, 2),
  TxCxnTimeoutFactor = substring(ParamBinary1, 206, 2)
| extend HttpStatusCode = tolong(strcat("0x", RawHttpCode))
| extend ClientRequestId = tolong(strcat("0x", RawClientRequestId))
| project PreciseTimeStamp, RawClientRequestId, EventId, ClientRequestId, Time, ParamStr1, LocalPort, PendingRequest , RxCxnTimeoutFactor , LastStatus , SequenceNumber, Offset, IoLength, RecvStatus, RawHttpCode, HttpStatusCode, Retries, Flags, ResubmitCount , TxCxnTimeoutFactor, ParamBinary1
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query VhdDiskEtwEventTable

Cluster: `Azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Disk & XDisk > Disk > VhdDisk > VhdDiskEtwEventTable`

```kusto
cluster('Azcore.centralus').database('Fa').VhdDiskEtwEventTable()
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, EventId, ProviderName, OpcodeName, KeywordName, TaskName, EventMessage
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---
