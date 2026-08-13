# StorageClient Tables (part 3/3)

> Source: **Azure Host — Azure Host Node** dashboard, chapter **StorageClient Tables** (21 queries, part 3 of 3).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## Updates

### Storage Client VM Brownout for all VMs

_Widget purpose:_ StorageClientVmBrownout for All VMs

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Sc` · Type: `Table`
Source panel: `StorageClient Tables > Updates > DPHP Update Logs > Brownout > StorageClientVmBrownout for All VMs`

```kusto
StorageClientVmBrownout
| where PreciseTimeStamp between (_startTime.._endTime)
| where NodeId == _nodeId
| summarize arg_max(PreciseTimeStamp, NodeType, Updated, Brownout, BrownoutEnd, BrownoutStart) by ContainerId
| project PreciseTimeStamp, ContainerId, NodeType, Updated, Brownout, BrownoutStart, BrownoutEnd
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

---

### ListOfExecutions

_Widget purpose:_ DPP Executions

Cluster: `storageclient.eastus` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `StorageClient Tables > Updates > DPHP Update Logs > DPP Update Graph > DPP Executions`

```kusto
ListExecutionsOnNodes(queryFrom, queryTo, Node_Id)
| where DPHP has "Datapath"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{Node_Id}`

**Signal filters seen in KQL:** `DPHP has "Datapath"`

---

### Update_Node_Logs

_Widget purpose:_ DPP Update Graph

Cluster: `rdosdata` · Database: `rdosdatapath` · Type: `CoBeTimeline`
Source panel: `StorageClient Tables > Updates > DPHP Update Logs > DPP Update Graph > DPP Executions > DPP Update Graph`

```kusto
let RawPfResults = cluster("AzureCM").database("AzureCM").OsUpdateManagerEvents
| where ExecutionId == Execution_Id;
let PfResults = RawPfResults
| order by StartTime asc
| where Description has "NET_START_BARBERA"
    or Description has "BLOBCACHE_PAUSE"
    or Description has "BLOBCACHE_UNLOAD"
    or Description has "DEVCON_RESTART_VHDDISK"
    or Description contains "BLOBCACHE_LOAD"
    or Description has "BLOBCACHE_UNPAUSE"
    or Description has "NET_STOP_BARBERA"
    or Description has "hostupdate.py started"
    or Description has "hostupdate.py exiting"
| extend EventId = case(Description has "BLOBCACHE_PAUSE", "Blobcache_Pause",
                        Description contains "BLOBCACHE_LOAD","Blobcache_Load",
                        Description has "BLOBCACHE_UNLOAD","Blobcache_Unload",
                        Description has "BLOBCACHE_UNPAUSE","Blobcache_Unpause",
                        Description has "DEVCON_RESTART_VHDDISK","Restart_VHDdisk",
                        Description has "NET_START_BARBERA","Start_Barbera",
                        Description has "NET_STOP_BARBERA","Stop_Barbera",
                        Description has "hostupdate.py started","Starting",
                        Description has "hostupdate.py exiting","Exiting", Description)
| project-rename  TimeStamp = StartTime
| extend StartTime = iff(Description has_any ("BLOBCACHE_PAUSE", "BLOBCACHE_LOAD", "BLOBCACHE_UNLOAD",
                    "BLOBCACHE_UNPAUSE", "DEVCON_RESTART_VHDDISK", "NET_START_BARBERA", "NET_STOP_BARBERA") or Description contains "BLOBCACHE_LOAD",
                    extract("START: ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+)", 1, Description, typeof(string)), TimeStamp)
//
| extend EndTime = iff(Description has_any ("BLOBCACHE_PAUSE", "BLOBCACHE_LOAD", "BLOBCACHE_UNLOAD",
                    "BLOBCACHE_UNPAUSE", "DEVCON_RESTART_VHDDISK", "NET_START_BARBERA", "NET_STOP_BARBERA")  or Description contains "BLOBCACHE_LOAD",
                    extract("END: ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+)", 1, Description, typeof(string)), next(TimeStamp))
| project EventId, todatetime(StartTime), todatetime(EndTime), Description;
//
//
//
let DppErrors = PfResults
| order by StartTime asc
| where Description has "hostupdate.py exiting:"
| parse Description with * "hostupdate.py exiting:" * ";" * ";" Error_String "." *
//
| extend EventId = case(Error_String has "ERROR_HP_INVALID_ARG", "Starting", 
                    Error_String has "ERROR_HP_UNEXPECTED_PF_DATAPATH_BUILD_NAME", "Starting", 
                    Error_String has "ERROR_HP_UNKNOWN_DPHOSTPLUGIN_BUILD_NAME", "Starting", 
                    Error_String has "ERROR_HP_VHDDISKPRT_REG_KEY_PRE_UPDATE", "Restart_VHDdisk",
                    Error_String has "ERROR_HP_EMPTY_INPUT_FILE", "Starting",
                    Error_String has "ERROR_HP_PARSING_INPUT_FILE", "Starting",
                    Error_String has "ERROR_HP_FAILED_ENUM_VMS_VHDS", "Restart_VHDdisk",
                    Error_String has "ERROR_HP_VDC_CLOSE", "Starting",
                    Error_String has "ERROR_HP_STOPPING_BARBERA_NO_LLDS", "Stop_Barbera",
                    Error_String has "ERROR_HP_START_COPYING_PAYLOAD", "Starting",
                    Error_String has "ERROR_HP_COPYING_PAYLOAD", "Starting",
                    Error_String has "ERROR_HP_DISABLE_RDMA", "Starting",
                    Error_String has "ERROR_HP_STARTING_VHD_PRE_START", "Restart_VHDdisk",
                    Error_String has "ERROR_HP_VHD_PRE_START", "Restart_VHDdisk",
                    Error_String has "ERROR_HP_START_PAUSING_VHDS", "Restart_VHDdisk",
                    Error_String has "ERROR_HP_PAUSING_DISKS", "Restart_VHDdisk",
                    Error_String has "ERROR_HP_START_RESTARTING_VHDDISK", "Restart_VHDdisk",
                    Error_String has "ERROR_HP_VHD_RESTART", "Restart_VHDdisk",
                    Error_String has "ERROR_HP_STARTING_BARBERA_WITH_LLDS", "Start_Barbera",
                    Error_String has "ERROR_HP_VDC_OPEN", "Exiting",
                    Error_String has "ERROR_HP_START_ENABLING_RDMA", "Exiting",
                    Error_String has "ERROR_HP_BLOBCACHE_CONTAINER_RECOVERY", "Exiting",
                    Error_String has "ERROR_HP_START_RESUMING_VHDS", "Restart_VHDdisk",
                    Error_String has "ERROR_HP_START_ENABLING_RDMA", "Exiting",
                    Error_String has "ERROR_HP_STARTING_BARBERA_NO_LLDS", "Start_Barbera",
                    Error_String has "ERROR_HP_BLOBCACHE_STATE_UNKNOWN", "Blobcache_Pause",
                    Error_String has "ERROR_HP_START_LOADING_BLOBCACHE", "Blobcache_Load",
                    Error_String has "ERROR_HP_BLOBCACHE_EVENT1", "Blobcache_Load",
                    Error_String has "ERROR_HP_LOADING_BLOBCACHE", "Blobcache_Load",
                    Error_String has "ERROR_HP_START_STARTING_BLOBCACHE", "Blobcache_Unpause",
                    Error_String has "ERROR_HP_START_RESTORING_BLOBCACHE_CONFIG", "Blobcache_Unpause",
                    Error_String has "ERROR_HP_RESTORING_BLOBCACHE_CONFIGURATION", "Blobcache_Unpause",
                    Error_String has "ERROR_HP_START_UNPAUSING_BLOBCACHE", "Blobcache_Unpause",
                    Error_String has "ERROR_HP_UNPAUSING_BLOBCACHE", "Blobcache_Unpause",
                    Error_String has "ERROR_HP_FLUSH", "Blobcache_Unpause",
                    Error_String has "ERROR_HP_START_STOPPING_BLOBCACHE", "Blobcache_Unload",
                    Error_String has "ERROR_HP_STOPPING_BLOBCACHE", "Blobcache_Unload",
                    Error_String has "ERROR_HP_START_PAUSING_BLOBCACHE", "Blobcache_Pause", 
                    Error_String has "ERROR_HP_PAUSING_BLOBCACHE", "Blobcache_Pause",
                    Error_String has "ERROR_HP_START_UNLOADING_BLOBCACHE", "Blobcache_Unload",
                    Error_String has "ERROR_HP_UNLOADING_BLOBCACHE", "Blobcache_Unload",
                    Error_String has "ERROR_NONE", "", 
                    "Exiting")
//
| extend Health = "unhealthy"
| project EventId, Health, Error_String;
//
//
//
let PfResults1 = PfResults
| lookup kind=leftouter DppErrors on EventId
| project EventId, StartTime, EndTime, Description, Error_String, Health = case(isempty(Health), "healthy", Health);
//
//
//
let DriverLogs = cluster("azcore.centralus").database("Fa").OsDriverLogTable
| where NodeId == Node_Id
| where todatetime(EventTime) between (DphpStartTime..DphpEndTime)
//| project EventTime, Cluster, NodeId, Component, Message
| where Component == "blobcache"
| where //Message startswith "DriverUnload"
     Message startswith "BcConfigStoreType"
    //or Message startswith "Backing store index"
    or Message has "BcpConfigSave"
    or Message has "DriverCleanup:"
    //or Message startswith "Disconnected backingStore"
    or Message has "Free MDL based pool"
    or Message has "Logfile close"
    or Message has "Logfile open"
    or Message has "DriverEntry:"
    or Message startswith "BcConfigRestore"
    or Message has "BcCreateCacheStoreInternal()"
    //or Message startswith "BcConfiguration finished"
//| where Message !startswith "BcCreateBackingStore"
| project-rename Description = Message
| extend EventId = Description
| extend EventTimeTimeStamp = todatetime(EventTime)
| order by EventTimeTimeStamp asc 
| extend StartTime = iff(Description startswith "BcConfig", EventTimeTimeStamp, prev(EventTimeTimeStamp))
, EndTime = iff(Description startswith "BcConfig", next(EventTimeTimeStamp), EventTimeTimeStamp)
//| project EventTime, Duration = EndTime - StartTime, 
| project EventId, StartTime, EndTime, Description;
//
//
//
let DppStages = PfResults1
| union kind=outer DriverLogs
//
| extend ParentId = case(Description has "BLOBCACHE_PAUSE", "",
                        Description contains "BLOBCACHE_LOAD","",
                        Description has "BLOBCACHE_UNLOAD","",
                        Description has "BLOBCACHE_UNPAUSE","",
                        Description has "DEVCON_RESTART_VHDDISK","",
                        Description has "NET_START_BARBERA","",
                        Description has "NET_STOP_BARBERA","",
                        Description matches regex strcat("^(", strcat_array(pack_array("BcConfigStore", "BcpConfigSave", "DriverCleanup"), ")|("), ")"), "Blobcache_Unload",
                        Description has "Free MDL based pool","DriverCleanup: Cleanup module BcCacheReadModule",
                        Description matches regex strcat("^(", strcat_array(pack_array("DriverEntry:", "BcConfigRestore"), ")|("), ")"), "Blobcache_Load",
                        Description has "BcCreateCacheStoreInternal()","BcConfigRestoreType(CacheStores)",
                        Description has_any ("Logfile open", "Logfile close"), "Restart_VHDdisk",
                        "")
//
| project-rename Content = Description
| project EventId, ParentId, StartTime, EndTime, Content, Error_String, Health = case(isempty(Health), "healthy", Health);
DppStages
```

**Params:** `{queryFrom}`, `{queryTo}`, `{Execution_Id}`, `{DphpStartTime}`, `{DphpEndTime}`, `{Node_Id}`

**Signal filters seen in KQL:** `Description has "NET_START_BARBERA"` · `Description has "hostupdate.py exiting:"` · `Component == "blobcache"`

---

### XIO_Condition_Query

_Widget purpose:_ DPP Update Graph

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `CoBeTimeline`
Source panel: `StorageClient Tables > Updates > DPHP Update Logs > DPP Update Graph > DPP Executions > DPP Update Graph`

```kusto
let PfResults = cluster("AzureCM").database("AzureCM").OsUpdateManagerEvents
| where ExecutionId == Execution_ID
| project StartTime, MessageType, TimeTaken, Description;
//let DphpResults = cluster("rdosdata").database("rdosdatapath").DPUpdateManagerEvents
//| where ExecutionId == Execution_ID
//| project StartTime, MessageType, TimeTaken, Description;
//DphpResults
//| union 
PfResults
| order by StartTime asc
| where Description has "Node is XIO"
    or Description has "Node is not XIO"
| extend Show_XIO_Table = iff(Description has "Node is XIO", "true", "false");
```

**Params:** `{queryFrom}`, `{queryTo}`, `{Execution_ID}`

**Signal filters seen in KQL:** `Description has "Node is XIO"`

---

### Azure Host DPHP Update Events

_Widget purpose:_ StorageClient Drivers Update Logs

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `StorageClient Tables > Updates > DPHP Update Logs > DPP Verbose Logs > StorageClient Drivers Update Logs`

```kusto
GetDppPfUpdateEvents(nodeId, startTime, endTime)
| extend StartTime = todatetime(StartTime)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Azure Host Node OsAnalyzerLogTable

_Widget purpose:_ OsAnalyzerLogTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Updates > DPHP Update Logs > PF Services Update Logs > OsAnalyzerLogTable`

```kusto
OsAnalyzerLogTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, Level, Message
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## User Mode Processes

### Azure Host Storage Client User Mode Processes Usage Stats

_Widget purpose:_ Host Storage Team's Usermode Processes

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `AutopilotDeployment` · Type: `TimeSeries`
Source panel: `StorageClient Tables > User Mode Processes > Host Storage Team's Usermode Processes`

```kusto
ProcessesPerfCounter
| where PreciseTimeStamp between ((queryFrom - 4h) .. (queryTo + 4h)) and NodeId == nodeId 
    and ImageName in~ ("XDiskSvc.exe", "osdiag.exe", "OsAnalyzer.exe", "BarberaSvc.exe", "blobcache.exe", "vhdctrl.exe", "asapdiag.exe")
| project PreciseTimeStamp, ImageName, PrivateUsage
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

## Vdc (UltraDisk Client)

### VDC_Diskpacing_Events

Cluster: `https://azcore.centralus.kusto.windows.net/` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Vdc (UltraDisk Client) > Vdc > Disk Pacing Events`

```kusto
cluster("azcore.centralus").database('Fa').VdcEtwEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == nodeId
| where EventId == 52
| sort by PreciseTimeStamp asc
| extend MessageStr = tostring(parse_csv(replace_string(replace_string(Message, '" ', '", '), '"', '')))
| extend DiskUri = extract(@"DiskUri=([^"",\]]+)", 1, MessageStr)
| extend IsDiskPacingActive = extract(@"IsDiskPacingActive=(\w+)", 1, MessageStr)
| extend DiskPacingEpochId = extract(@"DiskPacingEpochId=(\d+)", 1, MessageStr)
| extend IopsThrottle = extract(@"IopsThrottle=(\d+)", 1, MessageStr)
| extend BpsThrottle = extract(@"BpsThrottle=(\d+)", 1, MessageStr)
| project PreciseTimeStamp, DiskUri, IsDiskPacingActive, DiskPacingEpochId, IopsThrottle, BpsThrottle
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host StorageAgent ETW Table

_Widget purpose:_ StorageAgent ETW Table

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Vdc (UltraDisk Client) > Vdc > StorageAgent (updates) > StorageAgent > StorageAgent ETW Table`

```kusto
StorageAgentEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, EventMessage
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### SAListOfExecutions

_Widget purpose:_ Storage Agent Executions

Cluster: `storageclient.eastus` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Vdc (UltraDisk Client) > Vdc > StorageAgent Update Graph > Storage Agent Executions`

```kusto
let startTime = datetime("2023-09-20T11:30:00.000Z");
let endTime = datetime("2023-09-20T12:40:26.000Z");
cluster('storageclient.eastus').database('Fa').StorageAgentEtwEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId =~ node_Id
| parse EventMessage with * " " * "ActivityId " ActivityId " " *
| parse EventMessage with * " " * "ActivityId " ActivityId1
| extend ExecutionId = case(ActivityId1 contains " ", ActivityId, ActivityId1)
| summarize min(PreciseTimeStamp) by ExecutionId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{node_Id}`

---

### SA_Node_Update_Logs

Cluster: `storageclient.eastus` · Database: `Fa` · Type: `CoBeTimeline`
Source panel: `StorageClient Tables > Vdc (UltraDisk Client) > Vdc > StorageAgent Update Graph > Storage Agent Executions`

```kusto
let selectedExecution = cluster("storageclient.eastus.kusto.windows.net").database("Fa").StorageAgentEtwEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId =~ node_Id
| where EventMessage contains toscalar(execution_Id);
let stages = selectedExecution
| extend EventId = case(EventMessage contains "Storage Agent Failure", "EventMessage",
                        EventMessage contains "Started", "Start",
                        (EventMessage contains "Driver: afsmbdirect" or EventMessage contains "StorageAgent updated driver: afsmbdirect"), "AFSMBDirect",
                        ((EventMessage contains "Ddx" or EventMessage contains "StorageAgent updated driver: Ddx") and EventMessage !contains "DdxBrownoutTimeInMs"), "DDX",
                        ((EventMessage contains "Vdc" or EventMessage contains "StorageAgent updated driver: Vdc") and EventMessage !contains "VdcProxy" and EventMessage !contains "VdcService" and EventMessage !contains "VdcBrownoutTimeInMs"), "VDC",
                        (EventMessage contains "VdcService" or EventMessage contains "StorageAgent updated driver: VdcService"), "VDCService",
                        (EventMessage contains "VdcProxy" or EventMessage contains "StorageAgent updated driver: VdcProxy"), "VDCProxy",
                        EventMessage contains "Storage Agent Completed.", "End",
                        //EventMessage contains "Storage Agent Failure", "Failure" 
                        EventMessage)
| project-rename Description = EventMessage
| order by PreciseTimeStamp asc
| extend endTime = next(PreciseTimeStamp, 1)  
| serialize //;
| project StartTime = PreciseTimeStamp, EndTime = iff(isempty(endTime),PreciseTimeStamp, endTime), EventId, Content = Description;
let failures = cluster("storageclient.eastus.kusto.windows.net").database("Fa").StorageAgentEtwEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId =~ node_Id
| where EventMessage contains "Storage Agent failure"
| extend EventId = case((EventMessage contains "Vdc" and EventMessage !contains "VdcService" and EventMessage !contains "VdcProxy"), "VDC",
                        EventMessage contains "VdcService", "VDCService", 
                        EventMessage contains "VdcProxy", "VDCProxy",
                        EventMessage contains "Ddx", "DDX", 
                        EventMessage contains "afsmbdirect", "AFSMBDirect","End")
| extend Health = "unhealthy"
| project-rename ErrorString = EventMessage
| project PreciseTimeStamp, EventId, Health, ErrorString;
let finalStages = stages
| lookup kind=leftouter failures on EventId
| project EventId, StartTime, EndTime, Content, ErrorString, Health = case(isempty(Health), "healthy", Health);
finalStages
```

**Params:** `{queryFrom}`, `{queryTo}`, `{node_Id}`, `{execution_Id}`

**Signal filters seen in KQL:** `EventMessage contains "Storage Agent failure"`

---

### Azure Host Vdc Etw Events

_Widget purpose:_ Vdc (UltraDisk Client) ETW Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Vdc (UltraDisk Client) > Vdc > VdcEtwEvents > VdcEtwEvents > Vdc (UltraDisk Client) ETW Events`

```kusto
VdcEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, ProviderName, EventId, KeywordName, ChannelName, Message = tostring(parse_csv(replace_string(replace_string(Message, '" ', '", '), '"', '')))
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## Vhddisk

### Azure Host VM Vhddisk MaxTime Summary

_Widget purpose:_ Max/Min Response time at Vhddisk Layer (including retries)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Vhddisk > Vhddisk > Debug > Max/Min Response time at Vhddisk Layer (including retries)`

```kusto
let blobs = OsXIOHealthSignalEvent | union OsXIOSurfaceCounterTable | union OsXIOXdiskCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and (SurfaceName contains containerId or SurfaceName contains vmId)
| parse BlobPath with * "/" BlobPath "?" *
| distinct BlobPath;
VhdDiskEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == nodeId
| where EventId == 13
| project PreciseTimeStamp, EventMessage
| parse EventMessage with * 'blobpath:/' BlobPath '.' * 'TransportType:' TransportType '.' * 'RequestOpCode:' RequestOpCode '.' * 'RequestElapsedTimeMs:' RequestElapsedTimeMs '.' * "ResubmitCount:" ResubmitCount "." *
| where BlobPath in (blobs)
| extend RequestElapsedTimeMs = tolong(RequestElapsedTimeMs)
| extend IoType = iff(RequestOpCode == 6, "Read", "Write")
| extend Transport = case(TransportType == 1, "RDMA", TransportType == 2, "HTTP", "STCP")
| summarize count(), MaxRequestElapsedTimeMs = max(RequestElapsedTimeMs), AvgRequestElapsedTimeMs = round(avg(RequestElapsedTimeMs), 2), 
            MinRequestElapsedTimeMs = min(RequestElapsedTimeMs),
            MaxResubmitCount = max(tolong(ResubmitCount)), AvgResubmitCount = round(avg(tolong(ResubmitCount)), 2)
            by bin(PreciseTimeStamp, 1m), IoType_Transport = strcat(IoType,'-',Transport), BlobPath
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{vmId}`

---

### Azure Host Vhddisk ETW Events

_Widget purpose:_ Vhddisk ETW Events

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Vhddisk > Vhddisk > ETW > ETW > Vhddisk ETW Events`

```kusto
VhdDiskEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, EventId, EventMessage
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Vhddisk Events

_Widget purpose:_ Vhddisk Events

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Vhddisk > Vhddisk > Events > Events > Vhddisk Events`

```kusto
let Extract16Char=(ParamBinary1:string, Offset:long)
{
    strcat(substring(ParamBinary1, Offset + 14, 2),
           substring(ParamBinary1, Offset + 12, 2),
           substring(ParamBinary1, Offset + 10, 2),
           substring(ParamBinary1, Offset + 8, 2),
           substring(ParamBinary1, Offset + 6, 2),
           substring(ParamBinary1, Offset + 4, 2),
           substring(ParamBinary1, Offset + 2, 2),
           substring(ParamBinary1, Offset, 2)
          )
};
let Extract8Char=(ParamBinary1:string, Offset:long)
{
    strcat(substring(ParamBinary1, Offset + 6, 2),
           substring(ParamBinary1, Offset + 4, 2),
           substring(ParamBinary1, Offset + 2, 2),
           substring(ParamBinary1, Offset, 2)
          )
};
let Extract4Char=(ParamBinary1:string, Offset:long)
{
    strcat(substring(ParamBinary1, Offset + 2, 2), 
           substring(ParamBinary1, Offset, 2)
          )
};
let Extract2Char=(ParamBinary1:string, Offset:long)
{
    strcat(substring(ParamBinary1, Offset, 2)
          )
};
OsVhddiskEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| extend DumpDataSize = Extract4Char(ParamBinary1, 4),
         NumberOfStrings = Extract4Char(ParamBinary1, 8),
         StringOffset = Extract4Char(ParamBinary1, 12),
         ErrorCode = Extract8Char(ParamBinary1, 24),
         FinalStatus = Extract8Char(ParamBinary1, 40),
         ClientRequestId = Extract16Char(ParamBinary1, 80),
         Time = Extract8Char(ParamBinary1, 96),
         LocalPort = Extract4Char(ParamBinary1, 104),
         PendingRequest = Extract2Char(ParamBinary1, 108),
         RxCxnTimeoutFactor = Extract2Char(ParamBinary1, 110),
         Id1 = Extract8Char(ParamBinary1, 112),
         Id2 = Extract8Char(ParamBinary1, 120),
         Id3 = Extract8Char(ParamBinary1, 128),
         Id4 = Extract8Char(ParamBinary1, 136),
         LastStatus = Extract8Char(ParamBinary1, 144),
         SequenceNumber = Extract8Char(ParamBinary1, 152),
         Offset = Extract16Char(ParamBinary1, 160),
         IoLength = Extract8Char(ParamBinary1, 176),
         RecvStatus = Extract8Char(ParamBinary1, 184),
         HttpCode = Extract8Char(ParamBinary1, 192),
         Retries = Extract2Char(ParamBinary1, 200),
         Flags = Extract2Char(ParamBinary1, 202),
         ResubmitCount = Extract2Char(ParamBinary1, 204),
         TxCxnTimeoutFactor = Extract2Char(ParamBinary1, 206),
         ServerRequestId = iff(strlen(ParamBinary1) == 240, substring(ParamBinary1, 208, 32), "")
| extend OriginalClientdRequestId = substring(ClientRequestId, 8, 8),
         FastPathRetries = substring(ClientRequestId, 0, 8)
| extend Details = case(EventId == 2, pack("ParamBinary1", ParamBinary1,
                		 "DumpDataSize", DumpDataSize,
                         "NumberOfStrings", NumberOfStrings,
                         "StringOffset", StringOffset,
                         "ErrorCode", ErrorCode,
                         "FinalStatus", FinalStatus,
                         "ClientRequestId", ClientRequestId,
                         "Time", Time,
                         "LocalPort", LocalPort,
                         "PendingRequest", PendingRequest,
                         "RxCxnTimeoutFactor", RxCxnTimeoutFactor,
                         "Id1", Id1,
                         "Id2", Id2,
                         "Id3", Id3,
                         "Id4", Id4,
                         "LastStatus", LastStatus,
                         "SequenceNumber", SequenceNumber,
                         "Offset", Offset,
                         "IoLength", IoLength,
                         "RecvStatus", RecvStatus,
                         "HttpCode", HttpCode,
                         "Retries", Retries,
                         "Flags", Flags,
                         "ResubmitCount", ResubmitCount,
                         "TxCxnTimeoutFactor", TxCxnTimeoutFactor,
                         "ServerRequestId", ServerRequestId,
                		 "OriginalClientdRequestId", OriginalClientdRequestId,
                         "FastPathRetries", FastPathRetries), pack("ParamBinary1", ParamBinary1))
| project PreciseTimeStamp, EventId, ParamStr1, Details
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Node Transport Percentage Query

_Widget purpose:_ IO percentage by Transport

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > Vhddisk > Vhddisk > IO Transport Stats > IO percentage by Transport`

```kusto
OsXIOXdiskCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and SurfaceName contains containerId
| distinct *
| summarize TotalHttpIoCount = sum(DelXIOCnt) - sum(DelXTrimCnt), TotalStcpIoCount = sum(DelStcpIOCnt), TotalRdmaIoCount = sum(DelRdmaIOCnt), 
            XIOPS = sum(XIOPS), RdmaIOPS = sum(RdmaIOPS), StcpIOPS = sum(StcpIOPS),
            Del503Cnt = sum(Del503Cnt), 
            Del500Cnt = sum(Del500Cnt)
             by 
            PreciseTimeStamp = bin(PreciseTimeStamp, 5s)
| extend TotalIoCount = TotalHttpIoCount + TotalStcpIoCount + TotalRdmaIoCount
| project PreciseTimeStamp, XIOPS, RdmaIOPS, StcpIOPS, PercentRdmaIOPS = tolong((TotalRdmaIoCount * 100.0) / TotalIoCount), PercentStcpIOPS = tolong((TotalStcpIoCount * 100.0) / TotalIoCount), PercentHTTPIOPS = tolong((TotalHttpIoCount * 100.0) / TotalIoCount), Del500Cnt, Del503Cnt
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### OsVhddiskEventTable

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Vhddisk > Vhddisk > OsVhddiskEventTable`

```kusto
OsVhddiskEventTable
| where  NodeId  == nodeId
| where PreciseTimeStamp >= startTime
| where PreciseTimeStamp <= endTime
| extend ErrorCode = strcat(substring(ParamBinary1, 46, 2), substring(ParamBinary1, 44, 2), substring(ParamBinary1, 42, 2), substring(ParamBinary1, 40, 2)) , 
    ClientRequestId = strcat(substring(ParamBinary1, 94, 2), substring(ParamBinary1, 92, 2), substring(ParamBinary1, 90, 2), substring(ParamBinary1, 88, 2), substring(ParamBinary1, 86, 2), substring(ParamBinary1, 84, 2), substring(ParamBinary1, 82, 2), substring(ParamBinary1, 80, 2)),
    Time = strcat(substring(ParamBinary1, 102, 2), substring(ParamBinary1, 100, 2), substring(ParamBinary1, 98, 2), substring(ParamBinary1, 96, 2)),
    LocalPort = strcat(substring(ParamBinary1, 106, 2), substring(ParamBinary1, 104, 2)),
    PendingRequest = substring(ParamBinary1, 108, 2),
    RxCxnTimeoutFactor =  substring(ParamBinary1, 110, 2),
    LastStatus = strcat(substring(ParamBinary1, 150, 2), substring(ParamBinary1, 148, 2), substring(ParamBinary1, 146, 2), substring(ParamBinary1, 144, 2)) ,
    SequenceNumber = strcat(substring(ParamBinary1, 158, 2), substring(ParamBinary1, 156, 2), substring(ParamBinary1, 154, 2), substring(ParamBinary1, 152, 2)),
    Offset = strcat(substring(ParamBinary1, 174, 2), substring(ParamBinary1, 172, 2), substring(ParamBinary1, 170, 2), substring(ParamBinary1, 168, 2), substring(ParamBinary1, 166, 2), substring(ParamBinary1, 164, 2), substring(ParamBinary1, 162, 2), substring(ParamBinary1, 160, 2)),
    IoLength = strcat(substring(ParamBinary1, 182, 2), substring(ParamBinary1, 180, 2), substring(ParamBinary1, 178, 2), substring(ParamBinary1, 176, 2)),
    RecvStatus = strcat(substring(ParamBinary1, 190, 2), substring(ParamBinary1, 188, 2), substring(ParamBinary1, 186, 2), substring(ParamBinary1, 184, 2)),
    HttpCode = strcat(substring(ParamBinary1, 198, 2), substring(ParamBinary1, 196, 2), substring(ParamBinary1, 194, 2), substring(ParamBinary1, 192, 2)),
    Retries = substring(ParamBinary1, 200, 2),
    Flags = substring(ParamBinary1, 202, 2), 
    ResubmitCount = substring(ParamBinary1, 204, 2),
    TxCxnTimeoutFactor = substring(ParamBinary1, 206, 2)
  | project PreciseTimeStamp, EventId, ParamStr1, ParamBinary1, ClientRequestId, Time, LocalPort, PendingRequest , RxCxnTimeoutFactor , LastStatus , SequenceNumber, Offset, IoLength, RecvStatus, HttpCode, Retries, Flags, ResubmitCount , TxCxnTimeoutFactor, ErrorCode
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Node vhdum logs

_Widget purpose:_ Vhdum Events (user-mode calls)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > Vhddisk > Vhddisk > Vhdum > Vhdum > Vhdum Events (user-mode calls)`

```kusto
VhdumEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, EventId, EventMessage
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## VM Disks

### Azure Host Node VM Disks

_Widget purpose:_ Disks attached to VMs running in this node

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `fa` · Type: `Table`
Source panel: `StorageClient Tables > VM Disks > Disks attached to VMs running in this node`

```kusto
let ClusterInfo = cluster('azurecm.kusto.windows.net').database('AzureCM').LogClusterSnapshot
    | where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 1h)) //and Tenant == cluster
    | distinct Tenant, AvailabilityZone;
cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and Cluster == cluster
| extend ContainerId = tostring(split(split(SurfaceName, "_")[0], "~")[0])
| union (cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsUltraSSDCounterTable | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and Cluster == cluster)
| parse ArmId with * "/disks/" DiskName
//| parse BlobPath with NewBlobPath "?" *
| parse BlobPath with * "/" NewBlobPath "?" *
| extend BlobPath = case(isnotempty(NewBlobPath), NewBlobPath, BlobPath)
| extend StorageAccount = tostring(split(BlobPath, "/")[0])
| extend SurfaceName = case(isempty(SurfaceName), SurfaceGUID, SurfaceName)
| extend ThrottleIndices = replace_string(ThrottleCountersListString, ";", "")
| extend DiskSkuType = case(IsXIOdisk == 1, "Premium SSD", 
                            BlobPath contains "md-ssd-", "Standard SSD", 
                            IsXIOdisk == 0 and BlobPath !contains "md-ssd-" and Type == 0, "Standard HDD",
                            DiskSkuType == 0, "UltraSSD",
                            DiskSkuType == 1, "Premium SSD V2","")
| summarize arg_max(PreciseTimeStamp, CachePolicy, BlobPath, ContainerId, StorageAccount, EncryptionFlags, Type, StorageTenant, SDFTenant, Cluster, DiskType, SlotId, DiskName, DiskSkuType, ArmId, BSId, WSId, ThrottleIndices) by SurfaceName
| distinct CachePolicy, SurfaceName, BlobPath, ContainerId, StorageAccount, EncryptionFlags, Type, StorageTenant, SDFTenant, Cluster, DiskType, SlotId, DiskName, DiskSkuType, ArmId, BSId, WSId, ThrottleIndices
| extend StorageTenant = case(isempty(StorageTenant), tolower(tostring(split(SDFTenant, "-")[1])), StorageTenant)
| join kind = leftouter (
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsConfigTable
    | where PreciseTimeStamp between ((startTime - 6h)  .. (endTime + 6h))
            and NodeId == nodeId and Component == "blobprop" and Cluster == cluster
    | extend BlobProperties = parse_json(ConfigValue)
    | extend 
             DiskAccessTier = tostring(BlobProperties.blobproperties['x-ms-access-tier']),
             EnhancedConnectionVersion = BlobProperties.blobproperties["x-ms-enhancedconnectionversion"],
             StorageTenant = tostring(BlobProperties.storagecluster)
    | extend BlobProperties = BlobProperties.blobproperties
    | summarize hint.strategy=shuffle arg_max(PreciseTimeStamp, *) by ConfigName
    | project BlobPath = ConfigName, DiskAccessTier, EnhancedConnectionVersion, BlobProperties, StorageTenant
    | parse BlobPath with * "/" BlobPath
) on BlobPath
| extend StorageTenant = case(isnotempty(StorageTenant), StorageTenant, StorageTenant1)
| extend EnhancedConnectionVersion = case(isempty(BlobProperties), "Unknown", EnhancedConnectionVersion)
| project-away BlobPath1
// Stitch Compute Cluster Properties for Availability Zone
| join kind=leftouter (
    ClusterInfo
) on $left.Cluster == $right.Tenant
| extend StorageCluster = substring(tolower(StorageTenant), 0, strlen(StorageTenant) - 1)
| join kind=leftouter (
    ClusterInfo | project Tenant = tolower(Tenant), StorageClusterAvailabilityZone = AvailabilityZone
) on $left.StorageCluster == $right.Tenant
//
// Stitch T2 Colocation
//
| extend compute_cluster = tolower(Cluster)
// | join kind=leftouter (
//     cluster("azdhrdma.centralus.kusto.windows.net").database("azdhrdma").AppStpUnderSameT2Mapping()
//     | where compute_cluster contains cluster
//     | extend compute_cluster = tolower(compute_cluster)
// ) on compute_cluster
| extend DiskType = case(DiskType == 1, "OS Disk", DiskType == 2, "Temp Disk", DiskType == 3 or BlobPath contains "md-dd", "Data Disk", SurfaceName startswith "BASE_", "Ephemeral OS Disk Base", "")
| extend DiskType = case(Type == 4, strcat(DiskType, " (WriteAccelerator)"), DiskType)
| extend AZColocation = case(CachePolicy == 5, "", AvailabilityZone  == StorageClusterAvailabilityZone, "Yes", isnotempty(AvailabilityZone) or isnotempty(StorageClusterAvailabilityZone), "No", "Unknown")
| extend LUN = case(DiskType == "OS Disk" or DiskType == "Temp Disk", "NA", tostring(SlotId))
| project ContainerId, CachePolicy, EncryptionFlags, DiskType, DiskSkuType, DiskName, SurfaceName, BlobPath, StorageTenant, DiskAccessTier, FastPathEnabled = case(DiskType == "Temp Disk", "", EnhancedConnectionVersion == "Unknown", "Unknown", tostring(isnotempty(EnhancedConnectionVersion))), LUN, BSId, WSId, ThrottleIndices, BlobProperties, StorageAccount, AZColocation, ArmId //, xio_clusters, AvailabilityZone, StorageCluster, StorageClusterAvailabilityZone
| extend CachePolicy = case(CachePolicy == 0, "None", CachePolicy == 1, "ReadOnly", CachePolicy == 2, "ReadWrite", CachePolicy == 5, "LocalDisk", BlobPath contains "md-dd", "None", tostring(CachePolicy))
| sort by ContainerId desc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{cluster}`

---

## XDiskSvc

### Azure Host XdiskEncEvent

_Widget purpose:_ XdiskEncEvent

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > XDiskSvc > XDiskSvc > XDiskEncEvent > XDiskEncEvent > XdiskEncEvent`

```kusto
XdiskEncEvent
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == nodeId
| project PreciseTimeStamp, errorCode, message, messageType
| sort by PreciseTimeStamp
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host XDiskSvcEvent Query

_Widget purpose:_ XdiskSvcEvent

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > XDiskSvc > XDiskSvc > XDiskSvcEvent > XDiskSvcEvent > XdiskSvcEvent`

```kusto
XdiskSvcEvent
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, eventType, entityType, errorCode, message, messageType
| sort by PreciseTimeStamp
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---
