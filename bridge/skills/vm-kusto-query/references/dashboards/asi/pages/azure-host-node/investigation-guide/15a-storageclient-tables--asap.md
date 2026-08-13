# StorageClient Tables — ASAP

> Source: **Azure Host — Azure Host Node** dashboard, chapter **StorageClient Tables** (85 queries, part 1 of 3).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## ASAP

### Azure Host ASFO Features Values

_Widget purpose:_ ASAP and ASFO features

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASAP and ASFO features`

```kusto
OsConfigTable
| where  PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where ConfigType == "registry" and Component == "asap"
| where ConfigName in ("AllowFullOffloadDd", "AllowFullOffloadXio", "SharedDisk", "HwCapabilityXioHBESupport", "HwCapabilityDdHBESupport", "NodeQosHwOffloadEnabled", "DiskResizeStatus", "AbcDirectFlags")
| project PreciseTimeStamp, Component, ConfigName, ConfigValue
| summarize arg_max(PreciseTimeStamp, *) by ConfigName
| project-away PreciseTimeStamp, Component
| order by ConfigName asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `ConfigType == "registry"`

---

### Azure Host ASFO Components Versions

_Widget purpose:_ ASAP Components Versions from Events

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASAP Components Versions from Events`

```kusto
let pfVersion = AsapPfEtwTraceLogEventView
| where PreciseTimeStamp between (_startTime .. _endTime)
| where NodeId == _nodeId
| where Message has "ProductVersion"
| extend json = parse_json(Message)
| extend ProductVersion = tostring(json.ProductVersion)
| summarize arg_max(PreciseTimeStamp, *) by ProductVersion
| project Source = "PF", PreciseTimeStamp, ProductVersion
;
let kmsVersion = AsapKmsEtwTraceLogEventView
| where PreciseTimeStamp between (_startTime .. _endTime)
| where NodeId == _nodeId
| where EventId !in (4198,4199) and EventName !has "AsapDiag"
| where Message has "ProductVersion" and Message !has "fallback_software"
| extend json = parse_json(Message)
| extend ProductVersion = tostring(json.ProductVersion)
| summarize arg_max(PreciseTimeStamp, *) by ProductVersion
| project Source = "KMS", PreciseTimeStamp, ProductVersion
;
let umedVersion = AsapNvmeEtwTraceLogEventView
| where PreciseTimeStamp between (_startTime .. _endTime)
| where NodeId == _nodeId
| where Message has "ProductVersion"
| extend json = parse_json(Message)
| extend ProductVersion = tostring(json.ProductVersion)
| summarize arg_max(PreciseTimeStamp, *) by ProductVersion
| project Source = "UMED", PreciseTimeStamp, ProductVersion
;
let adpaVersion = AsapDpaEtwTraceLogEventView
| where PreciseTimeStamp between (_startTime .. _endTime)
| where NodeId == _nodeId
| where Message has "ProductVersion"
| extend json = parse_json(Message)
| extend ProductVersion = tostring(json.ProductVersion)
| summarize arg_max(PreciseTimeStamp, *) by ProductVersion
| project Source = "ADPA", PreciseTimeStamp, ProductVersion
;
let nullVersion = AsapNullEtwTraceLogEventView
| where PreciseTimeStamp between (_startTime .. _endTime)
| where NodeId == _nodeId
| where Message has "ProductVersion"
| extend json = parse_json(Message)
| extend ProductVersion = tostring(json.ProductVersion)
| summarize arg_max(PreciseTimeStamp, *) by ProductVersion
| project Source = "Null", PreciseTimeStamp, ProductVersion
;
union pfVersion, kmsVersion, umedVersion, adpaVersion, nullVersion
| project-rename LastEvent = PreciseTimeStamp
| order by LastEvent asc
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

**Signal filters seen in KQL:** `Message has "ProductVersion"`

---

### Azure Host ASFO Features

_Widget purpose:_ ASFO Node Details

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `FeatureList` · Widget: `Card`
Source panel: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASFO Node Details`

```kusto
OsConfigTable
| where  PreciseTimeStamp between ((startTime-2d) .. endTime) and NodeId == nodeId
| where ConfigType == "registry" and Component == "asap"
| where ConfigName in ("AllowFullOffloadDd", "AllowFullOffloadXio", "SharedDisk", "HwCapabilityXioHBESupport", "HwCapabilityDdHBESupport", "NodeQosHwOffloadEnabled", "DiskResizeStatus", "AbcDirectFlags")
| project PreciseTimeStamp, Component, ConfigName, ConfigValue
| summarize arg_max(PreciseTimeStamp, *) by ConfigName
| extend State = iff(tolong(ConfigValue) != 0, "enabled", "disabled")
| extend FeatureName = case(
    ConfigName == "AllowFullOffloadDd", "FO on DD",
    ConfigName == "AllowFullOffloadXio", "FO on XIO",
    ConfigName == "SharedDisk", "Shared Disk",
    ConfigName == "HwCapabilityDdHBESupport", "HBE FO on DD",
    ConfigName == "HwCapabilityXioHBESupport", "HBE FO on XIO",
    ConfigName == "NodeQosHwOffloadEnabled", "HW QoS",
    ConfigName == "DiskResizeStatus", "Disk Resize",
    ConfigName == "AbcDirectFlags", "VHDMP bypass",
    "Unknown")
| project-away PreciseTimeStamp
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `ConfigType == "registry"`

---

### Azure Host Node Info ASAP

_Widget purpose:_ ASFO Node Details

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Card`
Source panel: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASFO Node Details`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where  PreciseTimeStamp between ((_startTime-2d) .. _endTime) and nodeId == _nodeId
| summarize arg_max(PreciseTimeStamp, *) by nodeId
| extend hostEnv = parse_json(hostingEnvironment)
| extend HostOsVHD = tostring(hostEnv.OSBaseImageName)
| extend Host_OS = case(
    HostOsVHD has "22621.2576", "AH2023 SP1",
    HostOsVHD has "22621.1177", "AH2023",
    HostOsVHD has "26100." or HostOsVHD has "26080.", "AH2024",
    HostOsVHD has "26101.", "AH2024.1",
    HostOsVHD has "26102.", "AH2025",
    HostOsVHD has "20348.", "AH2021",
    "Unknown")
| project NodeId = nodeId, Cluster = Tenant, Host_OS, HostOsVHD
| join kind=innerunique (GetAllAsapClustersExtendedOverlakeDCM) on Cluster
| project-away Cluster1
```

**Params:** `{_nodeId}`, `{_startTime}`, `{_endTime}`

---

### ASFO_PO_FO_Transitions

_Widget purpose:_ ASFO PO <-> FO transitions

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > ASFO PO <-> FO transitions`

```kusto
AsapPfEtwTraceLogEventViewExtended
| where PreciseTimeStamp between (_startTime .. _endTime)
    and NodeId == _nodeId
    and EventId == 7111
| extend
    FullOffload = tobool(json.FullOffload),
    Command = toint(json.Command)
| extend
    CommandText = case(
        Command == 0, "Single",
        Command == 1, "All",
        Command == 2, "XIO",
        Command == 3, "DD",
        "Unknown")
| project PreciseTimeStamp, VfId, NsId, NsIndex, FullOffload, Command, CommandText
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

---

### AsapMapVfIdToContainerIdOvl2Node

_Widget purpose:_ Mapping for ASAP VF ID to Container ID

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > ASFO Host Details > Mapping for ASAP VF ID to Container ID`

```kusto
AsapMapVfIdToContainerIdOvl2(_nodeId, _startTime, _endTime)
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

---

### Azure Host ASAP Full Offload PF and UMED details

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Details`

```kusto
union  AsapPfEtwTraceLogEventTable, AsapNvmeEtwTraceLogEventTable
| where PreciseTimeStamp  between (queryFrom..queryTo)
and NodeId == nodeId
| parse TaskName with StrEVID ' - ' *
| extend EVID=toint(StrEVID)
//| where EVID in (1,2,72,44, 5400, 8001, 4244)//, 6028, 6029, 8001, 6032)
| where EVID < 9000 or EVID > 9500
| extend t = parse_json(Message)
| extend SubCode = case(EVID == 6029 and
                            t.HttpSubCode == "2198536472","XFE_E_ACCOUNT_REQUEST_THROTTLED",
                            t.HttpSubCode == "2198536473","XFE_E_OVERALL_REQUEST_THROTTLED",
                            t.HttpSubCode == "2198540548","XFE_E_RDMA_SESSION_NOT_FOUND",
                            t.HttpSubCode == "2198536474","XFE_E_EXPECTED_PROVIDER_REQUEST_THROTTLED",
                            t.HttpSubCode == "2198537743","XFE_E_BLOB_SEQUENCE_NUMBER_CONDITION_NOT_MET",
                            t.HttpSubCode == "2198540553","XFE_E_RDMA_OUTOFBAND_METADATA_NOT_SUPPORTED",
                            t.HttpSubCode == "2198471990","XS_STATUS_BLOB_SESSION_NOT_FOUND",
                            t.HttpSubCode == "2198540554","XFE_E_FASTPATH_PARTITION_RELATED_ERROR",
                            t.HttpSubCode == "2198471991","XS_STATUS_BLOB_SESSION_EXPIRED",
                            t.HttpSubCode == "2198537738","XFE_E_BLOB_LEASE_LOST",
                            t.HttpSubCode)
//| where EVID !in (8002,5001,5007,8003,4000,1051,1070)
//| where EVID in (1,2,72,1006)
| extend SessIdx = case(EVID in (5200,5201, 5202,5203,5204,5207,5208,5209,5210,6033,6028,6029,6031,5211,5212), toint(t.SessionIndex), -1)
| extend WriteSess = SessIdx % 2
//| summarize excpcount=count() by ProviderName,  EVID, SubCode, WriteSess, bin (PreciseTimeStamp,10m)
| extend AsapQpn = case(EVID in (20037,20038,20039,20000,20004,20100,20043,1076,6028,20014,5200,5201,5209,5210,5300,5302,6029,6031,5211,5212,20044,8002), toint(t.AsapQpn),
                        EVID in(1075),toint(t.ASAPQPN),
                        EVID == 30001,toint(t.ResponderRqVqId)/2,-1)
| extend reinj = case(EVID == 1075, t.NumberOfCancelledBqes, "0")
| extend NSID = case(isnotempty(t.NsId), toint(t.NsId),-1)
// | extend NSID = case(EVID in (6031,6029,6028,5001,5007,4244,5209,5210,5211), (1024-(t.NsIndex)),
//                      EVID in (5200,5201, 5202,5203,5204,5207,5208,6033), toint(t.NsId),-1)
| extend NewState = case(EVID == 5201, t.NewState,"")
| extend QPF = case(EVID == 6028, t.QpHadFatalError,"-1")
| extend TSess = case (EVID in (5212), toint(t.TimePeriodMs),0)
| extend TQpn = case (EVID in (20044), toint(t.TimespanMs),0)
| extend OldState = case(EVID == 5201, t.OldState,"")
| extend BSIndex = case(EVID == 3003, toint(t.BackingStoreIndex), -1)
| extend BqeIdx = case(EVID in (6028,6029,5007,5001), toint(t.BqeIdx),
                    EVID in (8002), toint(t.BqeIndex),
                    EVID in (9031), toint(t.Gen_reinject_bqe_idx), -1)
| extend AsapQpn = case(EVID in (20037,20038,20039,20000,20004,20100,20043,1076,6028,20014,5200,5201,5209,5210,5300,5302,6029,6031,5211,5212,20044,8002), toint(t.AsapQpn),
                        EVID in(1075),toint(t.ASAPQPN),
                        EVID == 30001,toint(t.ResponderRqVqId)/2,-1)
| extend Excp = case(EVID == 1051, toint(t.ExceptionCode),-1)
| extend IPAdd = case(EVID in (5300),t.IpString,"")
| extend bseq = case(EVID in(9031), toint(t.Gen_bqe_nqe_seq_id),-1)
| extend nseq = case(EVID in(9031), toint(t.Gen_nqe_nqe_seq_id),1)
| extend bqenqestatus = case(EVID in(9031), toint(t.Gen_status),-1)
//| where ((EVID == 9031 and bqenqestatus == 1 and bseq != nseq) or (EVID in(1,2,44,5400,5401,10213,8001,10215,10218,10219,6032,8002,6029,6028,5302,1075,20037,20038,20039,20044)))
| extend Source = case (
    ProviderName == "MicrosoftXAccelAsapUmedTraceLogging", "UMED",
    ProviderName == "MicrosoftXAccelAsapPfTraceLogging", "PF",
    "Unknown")
| project PreciseTimeStamp, Source, Level, reinj, EVID, BSIndex,NSID, SessIdx, AsapQpn, Excp, QPF,SubCode,BqeIdx,TSess, TQpn,  IPAdd, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host ASFO Node Events Stats Table

_Widget purpose:_ ASAP events count by provider and event Id (every 5 min)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Details > ASAP events count by provider and event Id (every 5 min)`

```kusto
union AsapKmsEtwTraceLogEventView, AsapNvmeEtwTraceLogEventView, AsapPfEtwTraceLogEventView
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == nodeId
| extend Provider = case(
    ProviderName == "MicrosoftXAccelAsapKmsTraceLogging", "KMS",
    ProviderName == "MicrosoftXAccelAsapPfTraceLogging", "PF",
    ProviderName == "MicrosoftXAccelAsapUmedTraceLogging", "UMED",
    "Unknown")
| summarize count() by bin(PreciseTimeStamp, 5m), Provider, EventId, EventName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### FullOffloadExceptionsQuery

_Widget purpose:_ ASFO Exceptions Total Counts

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CategoryChart`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > ASFO Exceptions Total Counts`

```kusto
AsapPfEtwTraceLogEventViewExtended // Need to scale solution to work w kbarde: "Extended and ExetendedDD" functions using union opr
    | where NodeId == nodeId
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where EventId between (6000..6500) or EventId == 6504
    | extend t = parse_json(Message)
    // Extend helper columns
    | extend Code = tostring(json.HttpSubCode), PfVer = tostring(json.ProductVersion), 
             dd_fo_throttle = tolong(json.dd_fo_throttle),
             dd_report_error = coalesce( tolong(json.DD_Report_Error), tolong(json.dd_report_error))
    | project  PreciseTimeStamp, NodeId, EventId, EventName, Code, dd_fo_throttle, dd_report_error, Message, json
    //
    | lookup (cluster('storageclient.eastus.kusto.windows.net').database('Sc').Asap_FOExceptions_HttpTranscodeTable) on Code
    | extend SubCode = iff(isnotempty(Description), Description, EventName)
    // DD special cases:
    | extend Exception_qp_id = toint(json.Exception_qp_id), qp_id = toint(json.qp_id), Ready = toint(json.Ready)
    | extend Analyze_SliceBqeTimeoutChannelNotReady = case(Ready == 0, "RdmaQpReady0BecauseAlreadyDone", Exception_qp_id != qp_id, "RdmaQpNotReadyBecauseRecycled", "")
    | project-away Exception_qp_id, qp_id, Ready
    //
    | extend SubCode = case // Triage notes from past triage experiences specific to DD
                       ( EventId == 6050, 'AsapBqeTimeoutReadExceptionDD', 
                         EventId == 6504 and dd_report_error == 1, "AsapBqeTimeoutWriteExceptionDD",  
                         EventId == 6504 and dd_fo_throttle == 1, "AsapMaxTaskLimitHitExceptionDD",  
                         EventId == 6057, Analyze_SliceBqeTimeoutChannelNotReady,
                         SubCode
                       )                   
| summarize count_ = count() by SubCode 
| order by count_
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### MinLatencyFloorDelayPv2Query

_Widget purpose:_ Avg & Max New Min Latency floor delays PV2: (PS: Unit is in terms of FPGA cycles, MaxDeltaCycles = NewMinLatencyFloor - CurrentMinLatencyFloor)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Avg & Max New Min Latency floor delays PV2: (PS: Unit is in terms of FPGA cycles, MaxDeltaCycles = NewMinLatencyFloor - CurrentMinLatencyFloor)`

```kusto
let duration = queryFrom - queryTo;
let stepSize = case(
    duration < 24h, 30s,        // Fine detail for short-term debugging
    duration < 3d,  5m,         // Slight aggregation
    duration < 7d,  15m,        // Up to ~7 days, still captures trends
    duration < 14d, 30m,        // Mid-range
    duration < 30d, 1h,         // Long range
    3h                          // 30–60 days summary view
);
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapPfEtwTraceLogEventViewExtended
| where PreciseTimeStamp between (queryFrom .. queryTo) and EventId == 7118
        and  NodeId == nodeId //and (VfId in (_getVFNSInfo | distinct VfId) or NsIndex in (_getVFNSInfo | distinct NsIndex))
| project PreciseTimeStamp, NodeId, EventId, EventName, json
| extend CurrentMinLatencyFloorDelay = todouble(json.CurrentMinLatencyFloorDelay), 
         NewMinLatencyFloorDelay = todouble(json.NewMinLatencyFloorDelay)
// Values are shown in FPGA cycles. For OVL2 running at 220 MHz, 1 cycle ≈ 4.5 ns.
| summarize
    MaxNewMinLatFloorDelayCycles = max(NewMinLatencyFloorDelay), // Worst-case applied latency floor
    AvgNewMinLatFloorDelayCycles = avg(NewMinLatencyFloorDelay), // Typical applied latency floor
    MaxDeltaCycles    = max(NewMinLatencyFloorDelay - CurrentMinLatencyFloorDelay) 
    by bin(PreciseTimeStamp, stepSize)
//
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project
    PreciseTimeStamp = ts,
    MaxNewMinLatencyFloorDelayCycles = coalesce(MaxNewMinLatFloorDelayCycles, 0.0),
    AvgNewMinLatencyFloorDelayCycles = coalesce(AvgNewMinLatFloorDelayCycles, 0.0),
    MaxDeltaCycles    = coalesce(MaxDeltaCycles, 0.0)


// let duration = queryFrom - queryTo;
// let stepSize = case(
//     duration < 24h, 30s,        // Fine detail for short-term debugging
//     duration < 3d,  5m,         // Slight aggregation
//     duration < 7d,  15m,        // Up to ~7 days, still captures trends
//     duration < 14d, 30m,        // Mid-range
//     duration < 30d, 1h,         // Long range
//     3h                          // 30–60 days summary view
// );
// let alignedStart = bin(queryFrom, stepSize);
// let alignedEnd   = bin(queryTo, stepSize);
// let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
// //let _getVFNSInfo = AsapMapVmToDiskOVL2(nodeId, _containerId, queryFrom, queryTo);
// //_getVFNSInfo | as _getVFNSInfo;
// AsapPfEtwTraceLogEventViewExtended
// | where PreciseTimeStamp between (queryFrom .. queryTo) and EventId in (7118)
//         and  NodeId == nodeId //and (VfId in (_getVFNSInfo | distinct VfId) or NsIndex in (_getVFNSInfo | distinct NsIndex))
// | project PreciseTimeStamp, NodeId, EventId, EventName, json
// | summarize count() by bin(PreciseTimeStamp, stepSize)
// | order by count_ 
// | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
// | project PreciseTimeStamp=ts, count_ = coalesce(count_, 0)
// | order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_asapPf_AllDisks

_Widget purpose:_ IOPS: FO vs PO (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > IOPS: FO vs PO (All Disks, includes boot disk)`

```kusto
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
    );
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapNodeFOStatsAsapPf(nodeId, queryFrom, queryTo) 
    //
    | project PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs , MaxWriteLatencyMs,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs, 
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs,
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
              FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
              PO_Read_IOPS = coalesce(PO_Read_IOPS, 0.0),
              PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
              FO_Read_MBPS  = coalesce(FO_Read_Mbps, 0.0),
              FO_Write_MBPS = coalesce(FO_Write_Mbps, 0.0),
              PO_Read_MBPS  = coalesce(PO_Read_Mbps, 0.0),
              PO_Write_MBPS = coalesce(PO_Write_Mbps, 0.0),
               //
              AverageReadLatencyInMS = coalesce(AvgReadLatencyMs, 0.0),
              AverageWriteLatencyMS = coalesce(AvgWriteLatencyMs, 0.0),
              //
              AvgBackendReadLatencyMs  = coalesce(AvgBackendReadLatencyMs, 0.0),
              AvgBackendWriteLatencyMs = coalesce(AvgBackendWriteLatencyMs, 0.0),
              AvgBqeReadLatencyMs      = coalesce(AvgBqeReadLatencyMs, 0.0),
              AvgBqeWriteLatencyMs     = coalesce(AvgBqeWriteLatencyMs, 0.0),
              AvgSchedReadLatencyMs   = coalesce(AvgSchedReadLatencyMs, 0.0),
              AvgSchedWriteLatencyMs  = coalesce(AvgSchedWriteLatencyMs, 0.0),
              //
              MaxReadLatencyInMS = coalesce(MaxReadLatencyMs, 0.0),
              MaxWriteLatencyInMS = coalesce(MaxWriteLatencyMs, 0.0),
              //
              BqeMaxReadLatencyMs = coalesce(BqeMaxReadLatencyMs, 0.0),
              BqeMaxWriteLatencyMs = coalesce(BqeMaxWriteLatencyMs, 0.0),
              //
              BackendMaxReadLatencyMs = coalesce(BackendMaxReadLatencyMs, 0.0),
              BackendMaxWriteLatencyMs = coalesce(BackendMaxWriteLatencyMs, 0.0),
              //
              SchedulerMaxReadLatencyMs = coalesce(SchedulerMaxReadLatencyMs, 0.0),
              SchedulerMaxWriteLatencyMs = coalesce(SchedulerMaxWriteLatencyMs, 0.0)
              //
    | order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_asapPf_UseSwpe0

_Widget purpose:_ IOPS: FO vs PO (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > IOPS: FO vs PO (FO enabled Disks)`

```kusto
//
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
);
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapNodeFOStatsAsapPf(nodeId, queryFrom, queryTo, _useSwpe="0") 
    //
    | project PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs , MaxWriteLatencyMs,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs, 
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs, 
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
              FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
              PO_Read_IOPS = coalesce(PO_Read_IOPS, 0.0),
              PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
              FO_Read_MBPS  = coalesce(FO_Read_Mbps, 0.0),
              FO_Write_MBPS = coalesce(FO_Write_Mbps, 0.0),
              PO_Read_MBPS  = coalesce(PO_Read_Mbps, 0.0),
              PO_Write_MBPS = coalesce(PO_Write_Mbps, 0.0),
               //
              AverageReadLatencyInMS = coalesce(AvgReadLatencyMs, 0.0),
              AverageWriteLatencyMS = coalesce(AvgWriteLatencyMs, 0.0),
              //
              AvgBackendReadLatencyMs  = coalesce(AvgBackendReadLatencyMs, 0.0),
              AvgBackendWriteLatencyMs = coalesce(AvgBackendWriteLatencyMs, 0.0),
              AvgBqeReadLatencyMs      = coalesce(AvgBqeReadLatencyMs, 0.0),
              AvgBqeWriteLatencyMs     = coalesce(AvgBqeWriteLatencyMs, 0.0),
              AvgSchedReadLatencyMs   = coalesce(AvgSchedReadLatencyMs, 0.0),
              AvgSchedWriteLatencyMs  = coalesce(AvgSchedWriteLatencyMs, 0.0),
              //
              MaxReadLatencyInMS = coalesce(MaxReadLatencyMs, 0.0),
              MaxWriteLatencyInMS = coalesce(MaxWriteLatencyMs, 0.0),
              //
              BqeMaxReadLatencyMs = coalesce(BqeMaxReadLatencyMs, 0.0),
              BqeMaxWriteLatencyMs = coalesce(BqeMaxWriteLatencyMs, 0.0),
              //
              BackendMaxReadLatencyMs = coalesce(BackendMaxReadLatencyMs, 0.0),
              BackendMaxWriteLatencyMs = coalesce(BackendMaxWriteLatencyMs, 0.0),
              //
              SchedulerMaxReadLatencyMs = coalesce(SchedulerMaxReadLatencyMs, 0.0),
              SchedulerMaxWriteLatencyMs = coalesce(SchedulerMaxWriteLatencyMs, 0.0)
              //
    | order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_asapPf_AllDisks

_Widget purpose:_ Latency: Average & Max in Ms (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (All Disks, includes boot disk)`

```kusto
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
    );
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapNodeFOStatsAsapPf(nodeId, queryFrom, queryTo) 
    //
    | project PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs , MaxWriteLatencyMs,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs, 
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs,
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
              FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
              PO_Read_IOPS = coalesce(PO_Read_IOPS, 0.0),
              PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
              FO_Read_MBPS  = coalesce(FO_Read_Mbps, 0.0),
              FO_Write_MBPS = coalesce(FO_Write_Mbps, 0.0),
              PO_Read_MBPS  = coalesce(PO_Read_Mbps, 0.0),
              PO_Write_MBPS = coalesce(PO_Write_Mbps, 0.0),
               //
              AverageReadLatencyInMS = coalesce(AvgReadLatencyMs, 0.0),
              AverageWriteLatencyMS = coalesce(AvgWriteLatencyMs, 0.0),
              //
              AvgBackendReadLatencyMs  = coalesce(AvgBackendReadLatencyMs, 0.0),
              AvgBackendWriteLatencyMs = coalesce(AvgBackendWriteLatencyMs, 0.0),
              AvgBqeReadLatencyMs      = coalesce(AvgBqeReadLatencyMs, 0.0),
              AvgBqeWriteLatencyMs     = coalesce(AvgBqeWriteLatencyMs, 0.0),
              AvgSchedReadLatencyMs   = coalesce(AvgSchedReadLatencyMs, 0.0),
              AvgSchedWriteLatencyMs  = coalesce(AvgSchedWriteLatencyMs, 0.0),
              //
              MaxReadLatencyInMS = coalesce(MaxReadLatencyMs, 0.0),
              MaxWriteLatencyInMS = coalesce(MaxWriteLatencyMs, 0.0),
              //
              BqeMaxReadLatencyMs = coalesce(BqeMaxReadLatencyMs, 0.0),
              BqeMaxWriteLatencyMs = coalesce(BqeMaxWriteLatencyMs, 0.0),
              //
              BackendMaxReadLatencyMs = coalesce(BackendMaxReadLatencyMs, 0.0),
              BackendMaxWriteLatencyMs = coalesce(BackendMaxWriteLatencyMs, 0.0),
              //
              SchedulerMaxReadLatencyMs = coalesce(SchedulerMaxReadLatencyMs, 0.0),
              SchedulerMaxWriteLatencyMs = coalesce(SchedulerMaxWriteLatencyMs, 0.0)
              //
    | order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_asapPf_UseSwpe0

_Widget purpose:_ Latency: Average & Max in Ms (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (FO enabled Disks)`

```kusto
//
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
);
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapNodeFOStatsAsapPf(nodeId, queryFrom, queryTo, _useSwpe="0") 
    //
    | project PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs , MaxWriteLatencyMs,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs, 
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs, 
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
              FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
              PO_Read_IOPS = coalesce(PO_Read_IOPS, 0.0),
              PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
              FO_Read_MBPS  = coalesce(FO_Read_Mbps, 0.0),
              FO_Write_MBPS = coalesce(FO_Write_Mbps, 0.0),
              PO_Read_MBPS  = coalesce(PO_Read_Mbps, 0.0),
              PO_Write_MBPS = coalesce(PO_Write_Mbps, 0.0),
               //
              AverageReadLatencyInMS = coalesce(AvgReadLatencyMs, 0.0),
              AverageWriteLatencyMS = coalesce(AvgWriteLatencyMs, 0.0),
              //
              AvgBackendReadLatencyMs  = coalesce(AvgBackendReadLatencyMs, 0.0),
              AvgBackendWriteLatencyMs = coalesce(AvgBackendWriteLatencyMs, 0.0),
              AvgBqeReadLatencyMs      = coalesce(AvgBqeReadLatencyMs, 0.0),
              AvgBqeWriteLatencyMs     = coalesce(AvgBqeWriteLatencyMs, 0.0),
              AvgSchedReadLatencyMs   = coalesce(AvgSchedReadLatencyMs, 0.0),
              AvgSchedWriteLatencyMs  = coalesce(AvgSchedWriteLatencyMs, 0.0),
              //
              MaxReadLatencyInMS = coalesce(MaxReadLatencyMs, 0.0),
              MaxWriteLatencyInMS = coalesce(MaxWriteLatencyMs, 0.0),
              //
              BqeMaxReadLatencyMs = coalesce(BqeMaxReadLatencyMs, 0.0),
              BqeMaxWriteLatencyMs = coalesce(BqeMaxWriteLatencyMs, 0.0),
              //
              BackendMaxReadLatencyMs = coalesce(BackendMaxReadLatencyMs, 0.0),
              BackendMaxWriteLatencyMs = coalesce(BackendMaxWriteLatencyMs, 0.0),
              //
              SchedulerMaxReadLatencyMs = coalesce(SchedulerMaxReadLatencyMs, 0.0),
              SchedulerMaxWriteLatencyMs = coalesce(SchedulerMaxWriteLatencyMs, 0.0)
              //
    | order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_asapPf_AllDisks

_Widget purpose:_ MBPS: FO vs PO (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > MBPS: FO vs PO (All Disks, includes boot disk)`

```kusto
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
    );
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapNodeFOStatsAsapPf(nodeId, queryFrom, queryTo) 
    //
    | project PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs , MaxWriteLatencyMs,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs, 
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs,
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
              FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
              PO_Read_IOPS = coalesce(PO_Read_IOPS, 0.0),
              PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
              FO_Read_MBPS  = coalesce(FO_Read_Mbps, 0.0),
              FO_Write_MBPS = coalesce(FO_Write_Mbps, 0.0),
              PO_Read_MBPS  = coalesce(PO_Read_Mbps, 0.0),
              PO_Write_MBPS = coalesce(PO_Write_Mbps, 0.0),
               //
              AverageReadLatencyInMS = coalesce(AvgReadLatencyMs, 0.0),
              AverageWriteLatencyMS = coalesce(AvgWriteLatencyMs, 0.0),
              //
              AvgBackendReadLatencyMs  = coalesce(AvgBackendReadLatencyMs, 0.0),
              AvgBackendWriteLatencyMs = coalesce(AvgBackendWriteLatencyMs, 0.0),
              AvgBqeReadLatencyMs      = coalesce(AvgBqeReadLatencyMs, 0.0),
              AvgBqeWriteLatencyMs     = coalesce(AvgBqeWriteLatencyMs, 0.0),
              AvgSchedReadLatencyMs   = coalesce(AvgSchedReadLatencyMs, 0.0),
              AvgSchedWriteLatencyMs  = coalesce(AvgSchedWriteLatencyMs, 0.0),
              //
              MaxReadLatencyInMS = coalesce(MaxReadLatencyMs, 0.0),
              MaxWriteLatencyInMS = coalesce(MaxWriteLatencyMs, 0.0),
              //
              BqeMaxReadLatencyMs = coalesce(BqeMaxReadLatencyMs, 0.0),
              BqeMaxWriteLatencyMs = coalesce(BqeMaxWriteLatencyMs, 0.0),
              //
              BackendMaxReadLatencyMs = coalesce(BackendMaxReadLatencyMs, 0.0),
              BackendMaxWriteLatencyMs = coalesce(BackendMaxWriteLatencyMs, 0.0),
              //
              SchedulerMaxReadLatencyMs = coalesce(SchedulerMaxReadLatencyMs, 0.0),
              SchedulerMaxWriteLatencyMs = coalesce(SchedulerMaxWriteLatencyMs, 0.0)
              //
    | order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_asapPf_UseSwpe0

_Widget purpose:_ MBPS: FO vs PO (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > MBPS: FO vs PO (FO enabled Disks)`

```kusto
//
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
);
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapNodeFOStatsAsapPf(nodeId, queryFrom, queryTo, _useSwpe="0") 
    //
    | project PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs , MaxWriteLatencyMs,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs, 
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs, 
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
              FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
              PO_Read_IOPS = coalesce(PO_Read_IOPS, 0.0),
              PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
              FO_Read_MBPS  = coalesce(FO_Read_Mbps, 0.0),
              FO_Write_MBPS = coalesce(FO_Write_Mbps, 0.0),
              PO_Read_MBPS  = coalesce(PO_Read_Mbps, 0.0),
              PO_Write_MBPS = coalesce(PO_Write_Mbps, 0.0),
               //
              AverageReadLatencyInMS = coalesce(AvgReadLatencyMs, 0.0),
              AverageWriteLatencyMS = coalesce(AvgWriteLatencyMs, 0.0),
              //
              AvgBackendReadLatencyMs  = coalesce(AvgBackendReadLatencyMs, 0.0),
              AvgBackendWriteLatencyMs = coalesce(AvgBackendWriteLatencyMs, 0.0),
              AvgBqeReadLatencyMs      = coalesce(AvgBqeReadLatencyMs, 0.0),
              AvgBqeWriteLatencyMs     = coalesce(AvgBqeWriteLatencyMs, 0.0),
              AvgSchedReadLatencyMs   = coalesce(AvgSchedReadLatencyMs, 0.0),
              AvgSchedWriteLatencyMs  = coalesce(AvgSchedWriteLatencyMs, 0.0),
              //
              MaxReadLatencyInMS = coalesce(MaxReadLatencyMs, 0.0),
              MaxWriteLatencyInMS = coalesce(MaxWriteLatencyMs, 0.0),
              //
              BqeMaxReadLatencyMs = coalesce(BqeMaxReadLatencyMs, 0.0),
              BqeMaxWriteLatencyMs = coalesce(BqeMaxWriteLatencyMs, 0.0),
              //
              BackendMaxReadLatencyMs = coalesce(BackendMaxReadLatencyMs, 0.0),
              BackendMaxWriteLatencyMs = coalesce(BackendMaxWriteLatencyMs, 0.0),
              //
              SchedulerMaxReadLatencyMs = coalesce(SchedulerMaxReadLatencyMs, 0.0),
              SchedulerMaxWriteLatencyMs = coalesce(SchedulerMaxWriteLatencyMs, 0.0)
              //
    | order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### AsapQpHealthCheckFailed_Spread

_Widget purpose:_ Spread of 'AsapQpHealthCheckFailed' Event (Only in PF Version 6.70.2.32+)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Spread of 'AsapQpHealthCheckFailed' Event (Only in PF Version 6.70.2.32+)`

```kusto
// try your new bin sizes w more granularity
//
let duration = queryFrom - queryTo;
let stepSize = case(
    duration < 24h, 30s,        // Fine detail for short-term debugging
    duration < 3d,  5m,         // Slight aggregation
    duration < 7d,  15m,        // Up to ~7 days, still captures trends
    duration < 14d, 30m,        // Mid-range
    duration < 30d, 1h,         // Long range
    3h                          // 30–60 days summary view
);
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//let _getVFNSInfo = AsapMapVmToDiskOVL2(nodeId, _containerId, queryFrom, queryTo);
//_getVFNSInfo | as _getVFNSInfo;
// This Event 5903 Does NOT carry VF or NS info in its Messag column, so this is only shown Node level 
AsapPfEtwTraceLogEventViewExtended
| where PreciseTimeStamp between (queryFrom .. queryTo) and EventId in (5903)
and  NodeId == nodeId //and (VfId in (_getVFNSInfo | distinct VfId) or NsIndex in (_getVFNSInfo | distinct NsIndex))
| project PreciseTimeStamp, NodeId, EventId, EventName, json
| summarize count() by bin(PreciseTimeStamp, stepSize)
| order by count_ 
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project PreciseTimeStamp=ts, count_ = coalesce(count_, 0)
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Full Offload Exceptions

_Widget purpose:_ Spread of ASFO FO Exceptions

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 30s DiskMetrics for ASAP > Spread of ASFO FO Exceptions`

```kusto
// REVISED SCAFOLD Logic for matching time axis to match search window 
//
// Scafold logic
// Compute duration and choose step size dynamically
//
let duration = endTime - startTime;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
    );
let alignedStart = bin(startTime, stepSize);
let alignedEnd   = bin(endTime, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapPfEtwTraceLogEventViewExtended // Need to scale solution to work w kbarde: "Extended and ExetendedDD" functions using union opr
    | where NodeId == nodeId
    | where PreciseTimeStamp between (startTime .. endTime)
    | where EventId between (6000..6500) or EventId == 6504
    | extend t = parse_json(Message)
    // Extend helper columns
    | extend Code = tostring(json.HttpSubCode), PfVer = tostring(json.ProductVersion), 
             dd_fo_throttle = tolong(json.dd_fo_throttle),
             dd_report_error = coalesce( tolong(json.DD_Report_Error), tolong(json.dd_report_error))
    | project  PreciseTimeStamp, NodeId, EventId, EventName, Code, dd_fo_throttle, dd_report_error, Message, json
    //
    | lookup (cluster('storageclient.eastus.kusto.windows.net').database('Sc').Asap_FOExceptions_HttpTranscodeTable) on Code
    | extend SubCode = iff(isnotempty(Description), Description, EventName)
    // DD special cases:
    | extend Exception_qp_id = toint(json.Exception_qp_id), qp_id = toint(json.qp_id), Ready = toint(json.Ready)
    | extend Analyze_SliceBqeTimeoutChannelNotReady = case(Ready == 0, "RdmaQpReady0BecauseAlreadyDone", Exception_qp_id != qp_id, "RdmaQpNotReadyBecauseRecycled", "")
    | project-away Exception_qp_id, qp_id, Ready
    //
    | extend SubCode = case // Triage notes from past triage experiences specific to DD
                       ( EventId == 6050, 'AsapBqeTimeoutReadExceptionDD', 
                         EventId == 6504 and dd_report_error == 1, "AsapBqeTimeoutWriteExceptionDD",  
                         EventId == 6504 and dd_fo_throttle == 1, "AsapMaxTaskLimitHitExceptionDD",  
                         EventId == 6057, Analyze_SliceBqeTimeoutChannelNotReady,
                         SubCode
                       )                   
| summarize count_ = count() by SubCode, bin(PreciseTimeStamp, stepSize)
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project PreciseTimeStamp=ts, SubCode, count_ = coalesce(count_, 0)
| order by PreciseTimeStamp asc


// AsapPfEtwTraceLogEventView
// | where NodeId == nodeId
// | where PreciseTimeStamp between (startTime .. endTime)
// | where EventId between (6000..6500)
// | extend t = parse_json(Message)
// | extend Code = tostring(t.HttpSubCode) //,  MetadataStatus = tostring(t.check_metadata_status)
// | lookup (cluster('storageclient.eastus.kusto.windows.net').database('Sc').Asap_FOExceptions_HttpTranscodeTable) on Code
// | extend SubCode = iff(isnotempty(Description),Description, EventName)
// | project PreciseTimeStamp, Level, EventId, Message, EventName, SubCode
// | summarize count() by EventName, SubCode, bin(PreciseTimeStamp, 1m)
// | project PreciseTimeStamp, SubCode, count_
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### asapNodeFOStats_OsCounters_AllDisks

_Widget purpose:_ FO Average & Max Latencies, (Milliseconds), All disks

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO Average & Max Latencies, (Milliseconds), All disks`

```kusto
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
    duration < 3d, 5m,          // 
    duration < 14d, 15m,        // Slight aggregation
    duration < 30d, 30m,        // Smooth trend?
    1h                          // For 30–60 days
);               
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
// Main query
AsapNodeFOStatsOsCounters(nodeId, queryFrom, queryTo)
// Join with scaffold to enforce full time range
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project PreciseTimeStamp=ts,
          FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
          FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
          PO_Read_IOPS  = coalesce(PO_Read_IOPS, 0.0),
          PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
          //
          FO_Read_Mbps  = coalesce(FO_Read_Mbps, 0.0),
          FO_Write_Mbps = coalesce(FO_Write_Mbps, 0.0),
          PO_Read_Mbps  = coalesce(PO_Read_Mbps, 0.0),
          PO_Write_Mbps = coalesce(PO_Write_Mbps, 0.0),
          //
          AvgReadLatencyInMS = coalesce(AvgReadLatencyInMS, 0.0),
          AverageWriteLatencyMS = coalesce(AvgWriteLatencyInMS, 0.0),
          //
          MaxReadLatencyInMS = coalesce(MaxReadLatencyInMS, 0.0),
          MaxWriteLatencyInMS = coalesce(MaxWriteLatencyInMS, 0.0),
          //
          BqeMaxReadLatencyInMS = coalesce(BqeMaxReadLatencyInMS, 0.0),
          BqeMaxWriteLatencyInMS = coalesce(BqeMaxWriteLatencyInMS, 0.0),
          //
          BackendMaxReadLatencyInMS = coalesce(BackendMaxReadLatencyInMS, 0.0),
          BackendMaxWriteLatencyInMS = coalesce(BackendMaxWriteLatencyInMS, 0.0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_OsCounters_UseSwpe0

_Widget purpose:_ FO Average & Max Latencies, (Milliseconds), FO disks i.e UseSwpe = 0

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO Average & Max Latencies, (Milliseconds), FO disks i.e UseSwpe = 0`

```kusto
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
    duration < 3d, 5m,          // 
    duration < 14d, 15m,        // Slight aggregation
    duration < 30d, 30m,        // Smooth trend?
    1h                          // For 30–60 days
);
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
// Main query
AsapNodeFOStatsOsCounters(nodeId, queryFrom, queryTo, _useSwpe = "0")
// Join with scaffold to enforce full time range
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project PreciseTimeStamp=ts,
          FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
          FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
          PO_Read_IOPS  = coalesce(PO_Read_IOPS, 0.0),
          PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
          //
          FO_Read_Mbps  = coalesce(FO_Read_Mbps, 0.0),
          FO_Write_Mbps = coalesce(FO_Write_Mbps, 0.0),
          PO_Read_Mbps  = coalesce(PO_Read_Mbps, 0.0),
          PO_Write_Mbps = coalesce(PO_Write_Mbps, 0.0),
          //
          AvgReadLatencyInMS = coalesce(AvgReadLatencyInMS, 0.0),
          AverageWriteLatencyMS = coalesce(AvgWriteLatencyInMS, 0.0),
          MaxReadLatencyInMS = coalesce(MaxReadLatencyInMS, 0.0),
          MaxWriteLatencyInMS = coalesce(MaxWriteLatencyInMS, 0.0),
          //
          BqeMaxReadLatencyInMS = coalesce(BqeMaxReadLatencyInMS, 0.0),
          BqeMaxWriteLatencyInMS = coalesce(BqeMaxWriteLatencyInMS, 0.0),
          //
          BackendMaxReadLatencyInMS = coalesce(BackendMaxReadLatencyInMS, 0.0),
          BackendMaxWriteLatencyInMS = coalesce(BackendMaxWriteLatencyInMS, 0.0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_OsCounters_AllDisks

_Widget purpose:_ FO vs PO: IOPS All disks (includes bootdisk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: IOPS All disks (includes bootdisk)`

```kusto
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
    duration < 3d, 5m,          // 
    duration < 14d, 15m,        // Slight aggregation
    duration < 30d, 30m,        // Smooth trend?
    1h                          // For 30–60 days
);               
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
// Main query
AsapNodeFOStatsOsCounters(nodeId, queryFrom, queryTo)
// Join with scaffold to enforce full time range
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project PreciseTimeStamp=ts,
          FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
          FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
          PO_Read_IOPS  = coalesce(PO_Read_IOPS, 0.0),
          PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
          //
          FO_Read_Mbps  = coalesce(FO_Read_Mbps, 0.0),
          FO_Write_Mbps = coalesce(FO_Write_Mbps, 0.0),
          PO_Read_Mbps  = coalesce(PO_Read_Mbps, 0.0),
          PO_Write_Mbps = coalesce(PO_Write_Mbps, 0.0),
          //
          AvgReadLatencyInMS = coalesce(AvgReadLatencyInMS, 0.0),
          AverageWriteLatencyMS = coalesce(AvgWriteLatencyInMS, 0.0),
          //
          MaxReadLatencyInMS = coalesce(MaxReadLatencyInMS, 0.0),
          MaxWriteLatencyInMS = coalesce(MaxWriteLatencyInMS, 0.0),
          //
          BqeMaxReadLatencyInMS = coalesce(BqeMaxReadLatencyInMS, 0.0),
          BqeMaxWriteLatencyInMS = coalesce(BqeMaxWriteLatencyInMS, 0.0),
          //
          BackendMaxReadLatencyInMS = coalesce(BackendMaxReadLatencyInMS, 0.0),
          BackendMaxWriteLatencyInMS = coalesce(BackendMaxWriteLatencyInMS, 0.0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_OsCounters_UseSwpe0

_Widget purpose:_ FO vs PO: IOPS, FO disks i.e UseSwpe = 0

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: IOPS, FO disks i.e UseSwpe = 0`

```kusto
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
    duration < 3d, 5m,          // 
    duration < 14d, 15m,        // Slight aggregation
    duration < 30d, 30m,        // Smooth trend?
    1h                          // For 30–60 days
);
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
// Main query
AsapNodeFOStatsOsCounters(nodeId, queryFrom, queryTo, _useSwpe = "0")
// Join with scaffold to enforce full time range
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project PreciseTimeStamp=ts,
          FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
          FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
          PO_Read_IOPS  = coalesce(PO_Read_IOPS, 0.0),
          PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
          //
          FO_Read_Mbps  = coalesce(FO_Read_Mbps, 0.0),
          FO_Write_Mbps = coalesce(FO_Write_Mbps, 0.0),
          PO_Read_Mbps  = coalesce(PO_Read_Mbps, 0.0),
          PO_Write_Mbps = coalesce(PO_Write_Mbps, 0.0),
          //
          AvgReadLatencyInMS = coalesce(AvgReadLatencyInMS, 0.0),
          AverageWriteLatencyMS = coalesce(AvgWriteLatencyInMS, 0.0),
          MaxReadLatencyInMS = coalesce(MaxReadLatencyInMS, 0.0),
          MaxWriteLatencyInMS = coalesce(MaxWriteLatencyInMS, 0.0),
          //
          BqeMaxReadLatencyInMS = coalesce(BqeMaxReadLatencyInMS, 0.0),
          BqeMaxWriteLatencyInMS = coalesce(BqeMaxWriteLatencyInMS, 0.0),
          //
          BackendMaxReadLatencyInMS = coalesce(BackendMaxReadLatencyInMS, 0.0),
          BackendMaxWriteLatencyInMS = coalesce(BackendMaxWriteLatencyInMS, 0.0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_OsCounters_AllDisks

_Widget purpose:_ FO vs PO: MBPS All disks (includes bootdisk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: MBPS All disks (includes bootdisk)`

```kusto
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
    duration < 3d, 5m,          // 
    duration < 14d, 15m,        // Slight aggregation
    duration < 30d, 30m,        // Smooth trend?
    1h                          // For 30–60 days
);               
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
// Main query
AsapNodeFOStatsOsCounters(nodeId, queryFrom, queryTo)
// Join with scaffold to enforce full time range
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project PreciseTimeStamp=ts,
          FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
          FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
          PO_Read_IOPS  = coalesce(PO_Read_IOPS, 0.0),
          PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
          //
          FO_Read_Mbps  = coalesce(FO_Read_Mbps, 0.0),
          FO_Write_Mbps = coalesce(FO_Write_Mbps, 0.0),
          PO_Read_Mbps  = coalesce(PO_Read_Mbps, 0.0),
          PO_Write_Mbps = coalesce(PO_Write_Mbps, 0.0),
          //
          AvgReadLatencyInMS = coalesce(AvgReadLatencyInMS, 0.0),
          AverageWriteLatencyMS = coalesce(AvgWriteLatencyInMS, 0.0),
          //
          MaxReadLatencyInMS = coalesce(MaxReadLatencyInMS, 0.0),
          MaxWriteLatencyInMS = coalesce(MaxWriteLatencyInMS, 0.0),
          //
          BqeMaxReadLatencyInMS = coalesce(BqeMaxReadLatencyInMS, 0.0),
          BqeMaxWriteLatencyInMS = coalesce(BqeMaxWriteLatencyInMS, 0.0),
          //
          BackendMaxReadLatencyInMS = coalesce(BackendMaxReadLatencyInMS, 0.0),
          BackendMaxWriteLatencyInMS = coalesce(BackendMaxWriteLatencyInMS, 0.0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### asapNodeFOStats_OsCounters_UseSwpe0

_Widget purpose:_ FO vs PO: MBPS, FO disks i.e UseSwpe = 0

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > 5m OsAsapCounters > FO vs PO: MBPS, FO disks i.e UseSwpe = 0`

```kusto
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
    duration < 3d, 5m,          // 
    duration < 14d, 15m,        // Slight aggregation
    duration < 30d, 30m,        // Smooth trend?
    1h                          // For 30–60 days
);
// Align scaffold to bin boundaries
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
// Main query
AsapNodeFOStatsOsCounters(nodeId, queryFrom, queryTo, _useSwpe = "0")
// Join with scaffold to enforce full time range
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project PreciseTimeStamp=ts,
          FO_Read_IOPS  = coalesce(FO_Read_IOPS, 0.0),
          FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
          PO_Read_IOPS  = coalesce(PO_Read_IOPS, 0.0),
          PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
          //
          FO_Read_Mbps  = coalesce(FO_Read_Mbps, 0.0),
          FO_Write_Mbps = coalesce(FO_Write_Mbps, 0.0),
          PO_Read_Mbps  = coalesce(PO_Read_Mbps, 0.0),
          PO_Write_Mbps = coalesce(PO_Write_Mbps, 0.0),
          //
          AvgReadLatencyInMS = coalesce(AvgReadLatencyInMS, 0.0),
          AverageWriteLatencyMS = coalesce(AvgWriteLatencyInMS, 0.0),
          MaxReadLatencyInMS = coalesce(MaxReadLatencyInMS, 0.0),
          MaxWriteLatencyInMS = coalesce(MaxWriteLatencyInMS, 0.0),
          //
          BqeMaxReadLatencyInMS = coalesce(BqeMaxReadLatencyInMS, 0.0),
          BqeMaxWriteLatencyInMS = coalesce(BqeMaxWriteLatencyInMS, 0.0),
          //
          BackendMaxReadLatencyInMS = coalesce(BackendMaxReadLatencyInMS, 0.0),
          BackendMaxWriteLatencyInMS = coalesce(BackendMaxWriteLatencyInMS, 0.0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Full Offload Exceptions

_Widget purpose:_ ASFO Exceptions

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > ASFO Exceptions`

```kusto
// REVISED SCAFOLD Logic for matching time axis to match search window 
//
// Scafold logic
// Compute duration and choose step size dynamically
//
let duration = endTime - startTime;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
    );
let alignedStart = bin(startTime, stepSize);
let alignedEnd   = bin(endTime, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapPfEtwTraceLogEventViewExtended // Need to scale solution to work w kbarde: "Extended and ExetendedDD" functions using union opr
    | where NodeId == nodeId
    | where PreciseTimeStamp between (startTime .. endTime)
    | where EventId between (6000..6500) or EventId == 6504
    | extend t = parse_json(Message)
    // Extend helper columns
    | extend Code = tostring(json.HttpSubCode), PfVer = tostring(json.ProductVersion), 
             dd_fo_throttle = tolong(json.dd_fo_throttle),
             dd_report_error = coalesce( tolong(json.DD_Report_Error), tolong(json.dd_report_error))
    | project  PreciseTimeStamp, NodeId, EventId, EventName, Code, dd_fo_throttle, dd_report_error, Message, json
    //
    | lookup (cluster('storageclient.eastus.kusto.windows.net').database('Sc').Asap_FOExceptions_HttpTranscodeTable) on Code
    | extend SubCode = iff(isnotempty(Description), Description, EventName)
    // DD special cases:
    | extend Exception_qp_id = toint(json.Exception_qp_id), qp_id = toint(json.qp_id), Ready = toint(json.Ready)
    | extend Analyze_SliceBqeTimeoutChannelNotReady = case(Ready == 0, "RdmaQpReady0BecauseAlreadyDone", Exception_qp_id != qp_id, "RdmaQpNotReadyBecauseRecycled", "")
    | project-away Exception_qp_id, qp_id, Ready
    //
    | extend SubCode = case // Triage notes from past triage experiences specific to DD
                       ( EventId == 6050, 'AsapBqeTimeoutReadExceptionDD', 
                         EventId == 6504 and dd_report_error == 1, "AsapBqeTimeoutWriteExceptionDD",  
                         EventId == 6504 and dd_fo_throttle == 1, "AsapMaxTaskLimitHitExceptionDD",  
                         EventId == 6057, Analyze_SliceBqeTimeoutChannelNotReady,
                         SubCode
                       )                   
| summarize count_ = count() by SubCode, bin(PreciseTimeStamp, stepSize)
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project PreciseTimeStamp=ts, SubCode, count_ = coalesce(count_, 0)
| order by PreciseTimeStamp asc


// AsapPfEtwTraceLogEventView
// | where NodeId == nodeId
// | where PreciseTimeStamp between (startTime .. endTime)
// | where EventId between (6000..6500)
// | extend t = parse_json(Message)
// | extend Code = tostring(t.HttpSubCode) //,  MetadataStatus = tostring(t.check_metadata_status)
// | lookup (cluster('storageclient.eastus.kusto.windows.net').database('Sc').Asap_FOExceptions_HttpTranscodeTable) on Code
// | extend SubCode = iff(isnotempty(Description),Description, EventName)
// | project PreciseTimeStamp, Level, EventId, Message, EventName, SubCode
// | summarize count() by EventName, SubCode, bin(PreciseTimeStamp, 1m)
// | project PreciseTimeStamp, SubCode, count_
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### FOPercent_NodeQuery

_Widget purpose:_ FO% KPI : [ %FO = Ratio of FullOffload IO to Total IO]

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > FO% KPI : [ %FO = Ratio of FullOffload IO to Total IO]`

```kusto
// Compute duration and choose step size dynamically
//
let duration = queryTo - queryFrom;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
    );
// Scafold logic - Revised algo to handle search span time axes to match across all charts
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (queryFrom .. queryTo ) and NodeId  == nodeId and EventId == 1265
    | project Cluster, NodeId, PreciseTimeStamp, EventId, EventName, Message
    | extend json = parse_json(Message)
    | extend UseSwpe = toint(json.UseSwpe), VfId = tolong(json.VfId),  NsId = toint(json.NsId), NsIndex = toint(json.NsIndex),
             NamespaceType = toint(json.NamespaceType), CachePolicy = toint(json.CachePolicy), 
             TotalCompletedIO = todouble(json.TotalCompletedIO), 
             FOCompletedIO = todouble(json.FOCompletedIO),
             POCompletedIO = todouble(json.POCompletedIO),
             POCompletedReadIO = todouble(json.POCompletedReadIO),
             POCompletedWriteIO = todouble(json.POCompletedWriteIO)
    // Apply FO condition
    | where UseSwpe == 0 
    // Remove OS disk, include only uncached data disks, also eliminate IDLE VM case so total IO is always non zero
    | where NsId != 0 and NamespaceType in (1,2)
    | where (NamespaceType == 1 and CachePolicy == 1) or (NamespaceType == 2 and CachePolicy == 0)
    | where TotalCompletedIO != 0   
    | project-away Message, json   
    //
    // Summarize
    | summarize TotalIO = sum(TotalCompletedIO), 
                TotalFOIO = sum(FOCompletedIO),
                TotalPOIO = sum(POCompletedIO),
                TotalPOReads = sum (POCompletedReadIO) ,
                TotalPOWrites = sum (POCompletedWriteIO) 
                by Cluster, NodeId, bin(PreciseTimeStamp, stepSize)
    //            
    | extend PercentOfFOCompletedIO = round(100.0 * todouble(TotalFOIO) / todouble(TotalIO),2),
             PercentOfPOCompletedIO = round(100.0 * todouble(TotalPOIO) / todouble(TotalIO),2),
             PercentOfPOReads       = round(100.0 * todouble(TotalPOReads) / todouble(TotalIO),2),
             PercentOfPOWrites      = round(100.0 * todouble(TotalPOWrites) / todouble(TotalIO),2)
    | summarize AVG_FOPercent = round(avg(PercentOfFOCompletedIO),2) by bin(PreciseTimeStamp, stepSize)
    //
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts, AVG_FOPercent = coalesce(AVG_FOPercent, 0.0)
    | order by PreciseTimeStamp asc


// // Scafold logic - Revised algo to handle search span time axes to match across all charts
// // Compute duration and choose step size dynamically
// //
// let duration = queryTo - queryFrom;
// let stepSize = case(
//     duration < 12h, 5m,        // very short window
//     duration < 1d, 5m,          // up to 1 day
//     duration < 7d, 12h,         // 1–7 days
//     1d                          // >7 days
// );
// let alignedStart = bin(queryFrom, stepSize);
// let alignedEnd   = bin(queryTo, stepSize);
// let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
// //
// cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsAsapCounterTable
// | where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
// | project Cluster, PreciseTimeStamp, NodeId, ContainerId, UseSwpe, 
//           DeltaFoCompleted, DeltaPoCompleted, DeltaIOCompleted, 
//           DeltaReadIOCompleted, DeltaWriteIOCompleted, 
//           DeltaFoReadCompleted, DeltaFoWriteCompleted,
//           DeltaPoReadCompleted, DeltaPoWriteCompleted,
//           OsDiagDurationInSec, CachePolicy, DiskClass, DiskType, NamespaceName
// | where UseSwpe == 0 and DeltaIOCompleted != 0
// | summarize 
//     TotalFOCompletedIO = sum(DeltaFoCompleted),
//     TotalPOCompletedIO = sum(DeltaPoCompleted),  
//     TotalCompletedIO  = sum(DeltaIOCompleted),
//     TotalCompletedPOReads = sum(DeltaPoReadCompleted),
//     TotalCompletedPOWrites = sum(DeltaPoWriteCompleted)
//     by Cluster, NodeId, ContainerId, bin(PreciseTimeStamp, stepSize)
// | extend PercentOfFOCompletedIO = round(100.0 * todouble(TotalFOCompletedIO) / todouble(TotalCompletedIO),2),
//          PercentOfPOCompletedIO = round(100.0 * todouble(TotalPOCompletedIO) / todouble(TotalCompletedIO),2),
//          PercentOfPOReads       = round(100.0 * todouble(TotalCompletedPOReads) / todouble(TotalCompletedIO),2),
//          PercentOfPOWrites      = round(100.0 * todouble(TotalCompletedPOWrites) / todouble(TotalCompletedIO),2)
// | summarize AVG_FOPercent = round(avg(PercentOfFOCompletedIO),2) by bin(PreciseTimeStamp, stepSize)
// | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
// | project PreciseTimeStamp=ts, AVG_FOPercent = coalesce(AVG_FOPercent, 0.0)
// | order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### FullOffloadStats_AllDisksQuery

_Widget purpose:_ Full Offload (IOPS KPIs, All data disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (IOPS KPIs, All data disks)`

```kusto
//
// Compute duration and choose step size dynamically
//
let duration = endTime - startTime;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
    );
// Align scaffold to 30s bin boundaries
let alignedStart = bin(startTime, stepSize);
let alignedEnd   = bin(endTime, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
            and EventId == 1265
    | extend t = parse_json(Message)
    | extend
        CachePolicy = toint(t.CachePolicy),
        NsId = toint(t.NsId),
        VfId = tolong(t.VfId),
        UseSwpe = toint(t.UseSwpe),
        UseSpcNsSwpe = toint(t.UseSpcNsSwpe),
        NamespaceType = toint(t.NamespaceType),
        // raw_PO_IOPS = todouble(t.POCompletedIO)/30.0,
        // raw_FO_IOPS = todouble(t.FOCompletedIO)/30.0,
        raw_PO_Read_IO = todouble(t.POCompletedReadIO),
        raw_FO_Read_IO = todouble(t.FOCompletedReadIO),
        raw_PO_Write_IO = todouble(t.POCompletedWriteIO),
        raw_FO_Write_IO = todouble(t.FOCompletedWriteIO),
        //
        //
        // TPUT // Raw bytes dont rationalize here to get per 30s as we wanna use dynamic stepsize
        raw_PO_Read_Bytes = todouble(t.POCompletedReadBytes),
        raw_PO_Write_Bytes = todouble(t.POCompletedWriteBytes),
        raw_FO_Read_Bytes = todouble(t.FOCompletedReadBytes),
        raw_FO_Write_Bytes = todouble(t.FOCompletedWriteBytes),
        //
        raw_FO_Percentage_IOPS = todouble(t.FOCompletedIO) * 100.0 / (todouble(t.POCompletedIO) + todouble(t.FOCompletedIO)),
        raw_FO_Persentage_Mbps = todouble(t.FOCompletedBytes) * 100.0 / (todouble(t.POCompletedBytes) + todouble(t.FOCompletedBytes))
    // Filter Conndition to query ASAP disks and exclude OS disk
    | where NsId != 1 
    | where (NamespaceType in (1,2))
    //
    // Condition to do only FO disks
    //| where UseSwpe  == 0 
    //
    // Summarize
    | summarize
    FO_Read_IOPS  = sum(raw_FO_Read_IO)  / todouble(totimespan(stepSize)/1s),
    FO_Write_IOPS = sum(raw_FO_Write_IO) / todouble(totimespan(stepSize)/1s),
    PO_Read_IOPS  = sum(raw_PO_Read_IO)  / todouble(totimespan(stepSize)/1s),
    PO_Write_IOPS = sum(raw_PO_Write_IO) / todouble(totimespan(stepSize)/1s),
    //kbarde
    // Total MB transferred in bin / bin duration to get MB/s
            // These are converted to binary mega bytes MBps (not mega bits)
            // compute total MB/s over a binned interval.
        FO_Read_Mbps = sum(raw_FO_Read_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        FO_Write_Mbps = sum(raw_FO_Write_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        PO_Read_Mbps = sum(raw_PO_Read_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        PO_Write_Mbps = sum(raw_PO_Write_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s)
    by bin(PreciseTimeStamp, stepSize)
    //
    // Now scaffold join matches correctly.Join with scaffold to enforce full time range
    //
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              FO_Read_IOPS = coalesce(FO_Read_IOPS, 0.0),
              FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
              PO_Read_IOPS = coalesce(PO_Read_IOPS, 0.0),
              PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
              FO_Read_Mbps = coalesce(FO_Read_Mbps, 0.0),
              FO_Write_Mbps = coalesce(FO_Write_Mbps, 0.0),
              PO_Read_Mbps = coalesce(PO_Read_Mbps, 0.0),
              PO_Write_Mbps = coalesce(PO_Write_Mbps, 0.0)
    | order by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Fulloffload Statistics

_Widget purpose:_ Full Offload (IOPS KPIs, FO data disks i.e UseSwpe = 0)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (IOPS KPIs, FO data disks i.e UseSwpe = 0)`

```kusto
//
// Compute duration and choose step size dynamically
//
let duration = endTime - startTime;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
    );
// Align scaffold to 30s bin boundaries
let alignedStart = bin(startTime, stepSize);
let alignedEnd   = bin(endTime, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
            and EventId == 1265
    | extend t = parse_json(Message)
    | extend
        CachePolicy = toint(t.CachePolicy),
        NsId = toint(t.NsId),
        VfId = tolong(t.VfId),
        UseSwpe = toint(t.UseSwpe),
        UseSpcNsSwpe = toint(t.UseSpcNsSwpe),
        NamespaceType = toint(t.NamespaceType),
        raw_PO_Read_IO = todouble(t.POCompletedReadIO),
        raw_FO_Read_IO = todouble(t.FOCompletedReadIO),
        raw_PO_Write_IO = todouble(t.POCompletedWriteIO),
        raw_FO_Write_IO = todouble(t.FOCompletedWriteIO),
        //
        raw_PO_Mbps = todouble(t.POCompletedBytes)/30000000.0,
        raw_FO_Mbps = todouble(t.FOCompletedBytes)/30000000.0,
        //
        // TPUT // Raw bytes dont rationalize here to get per 30s as we wanna use dynamic stepsize
        raw_PO_Read_Bytes = todouble(t.POCompletedReadBytes),
        raw_PO_Write_Bytes = todouble(t.POCompletedWriteBytes),
        raw_FO_Read_Bytes = todouble(t.FOCompletedReadBytes),
        raw_FO_Write_Bytes = todouble(t.FOCompletedWriteBytes),
        //
        raw_FO_Percentage_IOPS = todouble(t.FOCompletedIO) * 100.0 / (todouble(t.POCompletedIO) + todouble(t.FOCompletedIO)),
        raw_FO_Persentage_Mbps = todouble(t.FOCompletedBytes) * 100.0 / (todouble(t.POCompletedBytes) + todouble(t.FOCompletedBytes))
    // Filter Conndition to query ASAP disks and exclude OS disk
    | where NsId != 1 
    | where (NamespaceType in (1,2))
    //
    // Condition to do only FO disks
    | where NsId != 1 and (UseSwpe == 0 or UseSpcNsSwpe == 0) // Remove OSDisk (NSID) and retain records where NS are supposed to use FO I.e UseSwpe = 0
    | where (NamespaceType == 1 and CachePolicy == 1) or (NamespaceType == 2 and CachePolicy == 0)
    //
    // Summarize
    | summarize
    FO_Read_IOPS  = sum(raw_FO_Read_IO)  / todouble(totimespan(stepSize)/1s),
    FO_Write_IOPS = sum(raw_FO_Write_IO) / todouble(totimespan(stepSize)/1s),
    PO_Read_IOPS  = sum(raw_PO_Read_IO)  / todouble(totimespan(stepSize)/1s),
    PO_Write_IOPS = sum(raw_PO_Write_IO) / todouble(totimespan(stepSize)/1s),
    //kbarde
    // Total MB transferred in bin / bin duration to get MB/s
            // These are converted to binary mega bytes MBps (not mega bits)
            // compute total MB/s over a binned interval.
        FO_Read_Mbps = sum(raw_FO_Read_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        FO_Write_Mbps = sum(raw_FO_Write_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        PO_Read_Mbps = sum(raw_PO_Read_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        PO_Write_Mbps = sum(raw_PO_Write_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s)
    by bin(PreciseTimeStamp, stepSize)
    //
    // Now scaffold join matches correctly.Join with scaffold to enforce full time range
    //
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              FO_Read_IOPS = coalesce(FO_Read_IOPS, 0.0),
              FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
              PO_Read_IOPS = coalesce(PO_Read_IOPS, 0.0),
              PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
              FO_Read_Mbps = coalesce(FO_Read_Mbps, 0.0),
              FO_Write_Mbps = coalesce(FO_Write_Mbps, 0.0),
              PO_Read_Mbps = coalesce(PO_Read_Mbps, 0.0),
              PO_Write_Mbps = coalesce(PO_Write_Mbps, 0.0)
    | order by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### FullOffloadStats_AllDisksQuery

_Widget purpose:_ Full Offload (throughput KPIs, All data disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (throughput KPIs, All data disks)`

```kusto
//
// Compute duration and choose step size dynamically
//
let duration = endTime - startTime;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
    );
// Align scaffold to 30s bin boundaries
let alignedStart = bin(startTime, stepSize);
let alignedEnd   = bin(endTime, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
            and EventId == 1265
    | extend t = parse_json(Message)
    | extend
        CachePolicy = toint(t.CachePolicy),
        NsId = toint(t.NsId),
        VfId = tolong(t.VfId),
        UseSwpe = toint(t.UseSwpe),
        UseSpcNsSwpe = toint(t.UseSpcNsSwpe),
        NamespaceType = toint(t.NamespaceType),
        // raw_PO_IOPS = todouble(t.POCompletedIO)/30.0,
        // raw_FO_IOPS = todouble(t.FOCompletedIO)/30.0,
        raw_PO_Read_IO = todouble(t.POCompletedReadIO),
        raw_FO_Read_IO = todouble(t.FOCompletedReadIO),
        raw_PO_Write_IO = todouble(t.POCompletedWriteIO),
        raw_FO_Write_IO = todouble(t.FOCompletedWriteIO),
        //
        //
        // TPUT // Raw bytes dont rationalize here to get per 30s as we wanna use dynamic stepsize
        raw_PO_Read_Bytes = todouble(t.POCompletedReadBytes),
        raw_PO_Write_Bytes = todouble(t.POCompletedWriteBytes),
        raw_FO_Read_Bytes = todouble(t.FOCompletedReadBytes),
        raw_FO_Write_Bytes = todouble(t.FOCompletedWriteBytes),
        //
        raw_FO_Percentage_IOPS = todouble(t.FOCompletedIO) * 100.0 / (todouble(t.POCompletedIO) + todouble(t.FOCompletedIO)),
        raw_FO_Persentage_Mbps = todouble(t.FOCompletedBytes) * 100.0 / (todouble(t.POCompletedBytes) + todouble(t.FOCompletedBytes))
    // Filter Conndition to query ASAP disks and exclude OS disk
    | where NsId != 1 
    | where (NamespaceType in (1,2))
    //
    // Condition to do only FO disks
    //| where UseSwpe  == 0 
    //
    // Summarize
    | summarize
    FO_Read_IOPS  = sum(raw_FO_Read_IO)  / todouble(totimespan(stepSize)/1s),
    FO_Write_IOPS = sum(raw_FO_Write_IO) / todouble(totimespan(stepSize)/1s),
    PO_Read_IOPS  = sum(raw_PO_Read_IO)  / todouble(totimespan(stepSize)/1s),
    PO_Write_IOPS = sum(raw_PO_Write_IO) / todouble(totimespan(stepSize)/1s),
    //kbarde
    // Total MB transferred in bin / bin duration to get MB/s
            // These are converted to binary mega bytes MBps (not mega bits)
            // compute total MB/s over a binned interval.
        FO_Read_Mbps = sum(raw_FO_Read_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        FO_Write_Mbps = sum(raw_FO_Write_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        PO_Read_Mbps = sum(raw_PO_Read_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        PO_Write_Mbps = sum(raw_PO_Write_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s)
    by bin(PreciseTimeStamp, stepSize)
    //
    // Now scaffold join matches correctly.Join with scaffold to enforce full time range
    //
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              FO_Read_IOPS = coalesce(FO_Read_IOPS, 0.0),
              FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
              PO_Read_IOPS = coalesce(PO_Read_IOPS, 0.0),
              PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
              FO_Read_Mbps = coalesce(FO_Read_Mbps, 0.0),
              FO_Write_Mbps = coalesce(FO_Write_Mbps, 0.0),
              PO_Read_Mbps = coalesce(PO_Read_Mbps, 0.0),
              PO_Write_Mbps = coalesce(PO_Write_Mbps, 0.0)
    | order by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Fulloffload Statistics

_Widget purpose:_ Full Offload (throughput KPIs, FO data disks)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload (throughput KPIs, FO data disks)`

```kusto
//
// Compute duration and choose step size dynamically
//
let duration = endTime - startTime;
let stepSize = case(
        duration < 24h, 30s,        // Fine detail for short-term debugging
        duration < 3d,  5m,         // Slight aggregation
        duration < 7d,  15m,        // Up to ~7 days, still captures trends
        duration < 14d, 30m,        // Mid-range
        duration < 30d, 1h,         // Long range
        3h                          // 30–60 days summary view
    );
// Align scaffold to 30s bin boundaries
let alignedStart = bin(startTime, stepSize);
let alignedEnd   = bin(endTime, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
            and EventId == 1265
    | extend t = parse_json(Message)
    | extend
        CachePolicy = toint(t.CachePolicy),
        NsId = toint(t.NsId),
        VfId = tolong(t.VfId),
        UseSwpe = toint(t.UseSwpe),
        UseSpcNsSwpe = toint(t.UseSpcNsSwpe),
        NamespaceType = toint(t.NamespaceType),
        raw_PO_Read_IO = todouble(t.POCompletedReadIO),
        raw_FO_Read_IO = todouble(t.FOCompletedReadIO),
        raw_PO_Write_IO = todouble(t.POCompletedWriteIO),
        raw_FO_Write_IO = todouble(t.FOCompletedWriteIO),
        //
        raw_PO_Mbps = todouble(t.POCompletedBytes)/30000000.0,
        raw_FO_Mbps = todouble(t.FOCompletedBytes)/30000000.0,
        //
        // TPUT // Raw bytes dont rationalize here to get per 30s as we wanna use dynamic stepsize
        raw_PO_Read_Bytes = todouble(t.POCompletedReadBytes),
        raw_PO_Write_Bytes = todouble(t.POCompletedWriteBytes),
        raw_FO_Read_Bytes = todouble(t.FOCompletedReadBytes),
        raw_FO_Write_Bytes = todouble(t.FOCompletedWriteBytes),
        //
        raw_FO_Percentage_IOPS = todouble(t.FOCompletedIO) * 100.0 / (todouble(t.POCompletedIO) + todouble(t.FOCompletedIO)),
        raw_FO_Persentage_Mbps = todouble(t.FOCompletedBytes) * 100.0 / (todouble(t.POCompletedBytes) + todouble(t.FOCompletedBytes))
    // Filter Conndition to query ASAP disks and exclude OS disk
    | where NsId != 1 
    | where (NamespaceType in (1,2))
    //
    // Condition to do only FO disks
    | where NsId != 1 and (UseSwpe == 0 or UseSpcNsSwpe == 0) // Remove OSDisk (NSID) and retain records where NS are supposed to use FO I.e UseSwpe = 0
    | where (NamespaceType == 1 and CachePolicy == 1) or (NamespaceType == 2 and CachePolicy == 0)
    //
    // Summarize
    | summarize
    FO_Read_IOPS  = sum(raw_FO_Read_IO)  / todouble(totimespan(stepSize)/1s),
    FO_Write_IOPS = sum(raw_FO_Write_IO) / todouble(totimespan(stepSize)/1s),
    PO_Read_IOPS  = sum(raw_PO_Read_IO)  / todouble(totimespan(stepSize)/1s),
    PO_Write_IOPS = sum(raw_PO_Write_IO) / todouble(totimespan(stepSize)/1s),
    //kbarde
    // Total MB transferred in bin / bin duration to get MB/s
            // These are converted to binary mega bytes MBps (not mega bits)
            // compute total MB/s over a binned interval.
        FO_Read_Mbps = sum(raw_FO_Read_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        FO_Write_Mbps = sum(raw_FO_Write_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        PO_Read_Mbps = sum(raw_PO_Read_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s),
        PO_Write_Mbps = sum(raw_PO_Write_Bytes)/(1024*1024)/ todouble(totimespan(stepSize)/1s)
    by bin(PreciseTimeStamp, stepSize)
    //
    // Now scaffold join matches correctly.Join with scaffold to enforce full time range
    //
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              FO_Read_IOPS = coalesce(FO_Read_IOPS, 0.0),
              FO_Write_IOPS = coalesce(FO_Write_IOPS, 0.0),
              PO_Read_IOPS = coalesce(PO_Read_IOPS, 0.0),
              PO_Write_IOPS = coalesce(PO_Write_IOPS, 0.0),
              FO_Read_Mbps = coalesce(FO_Read_Mbps, 0.0),
              FO_Write_Mbps = coalesce(FO_Write_Mbps, 0.0),
              PO_Read_Mbps = coalesce(PO_Read_Mbps, 0.0),
              PO_Write_Mbps = coalesce(PO_Write_Mbps, 0.0)
    | order by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### FullOffloadExceptionsQuery

_Widget purpose:_ Full Offload Exceptions Counts

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CategoryChart`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Full Offload Exceptions Counts`

```kusto
AsapPfEtwTraceLogEventViewExtended // Need to scale solution to work w kbarde: "Extended and ExetendedDD" functions using union opr
    | where NodeId == nodeId
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where EventId between (6000..6500) or EventId == 6504
    | extend t = parse_json(Message)
    // Extend helper columns
    | extend Code = tostring(json.HttpSubCode), PfVer = tostring(json.ProductVersion), 
             dd_fo_throttle = tolong(json.dd_fo_throttle),
             dd_report_error = coalesce( tolong(json.DD_Report_Error), tolong(json.dd_report_error))
    | project  PreciseTimeStamp, NodeId, EventId, EventName, Code, dd_fo_throttle, dd_report_error, Message, json
    //
    | lookup (cluster('storageclient.eastus.kusto.windows.net').database('Sc').Asap_FOExceptions_HttpTranscodeTable) on Code
    | extend SubCode = iff(isnotempty(Description), Description, EventName)
    // DD special cases:
    | extend Exception_qp_id = toint(json.Exception_qp_id), qp_id = toint(json.qp_id), Ready = toint(json.Ready)
    | extend Analyze_SliceBqeTimeoutChannelNotReady = case(Ready == 0, "RdmaQpReady0BecauseAlreadyDone", Exception_qp_id != qp_id, "RdmaQpNotReadyBecauseRecycled", "")
    | project-away Exception_qp_id, qp_id, Ready
    //
    | extend SubCode = case // Triage notes from past triage experiences specific to DD
                       ( EventId == 6050, 'AsapBqeTimeoutReadExceptionDD', 
                         EventId == 6504 and dd_report_error == 1, "AsapBqeTimeoutWriteExceptionDD",  
                         EventId == 6504 and dd_fo_throttle == 1, "AsapMaxTaskLimitHitExceptionDD",  
                         EventId == 6057, Analyze_SliceBqeTimeoutChannelNotReady,
                         SubCode
                       )                   
| summarize count_ = count() by SubCode 
| order by count_
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### VMCountsPerFOPercent

_Widget purpose:_ Total FO VMs running and their Average FO% (Source = OSCounters, asapPF does not currently have ConrtainerID in its payload)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CategoryChart`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > Total FO VMs running and their Average FO% (Source = OSCounters, asapPF does not currently have ConrtainerID in its payload)`

```kusto
// Revised Scafold logic to show All VMs all Buckets and populate 0 if no data

// Define FO buckets explicitly
let FO_Buckets = datatable(FOBucket:string)
[
    "0-1%",
    "1-10%",
    "10-20%",
    "20-30%",
    "30-40%",
    "40-50%",
    "50-60%",
    "60-70%",
    "70-80%",
    "80-90%",
    "90-99%",
    "99-99.5%",
    "99.5-100%"
] 
| sort by FOBucket asc;
//
// VM-level FO % calculation
let _VmFOPercents =
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsAsapCounterTable
    | where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
    | project Cluster, PreciseTimeStamp, NodeId, ContainerId, UseSwpe, 
              DeltaFoCompleted, DeltaPoCompleted, DeltaIOCompleted,
              DeltaPoReadCompleted, DeltaPoWriteCompleted,
              OsDiagDurationInSec, CachePolicy, DiskClass, DiskType, NamespaceName
    // Filter: must stay FO, workload running (remove OS disk / idle VMs)
    | where UseSwpe == 0 and DeltaIOCompleted != 0
    | summarize TotalFOCompletedIO = sum(DeltaFoCompleted),
                TotalPOCompletedIO = sum(DeltaPoCompleted),  
                TotalCompletedIO   = sum(DeltaIOCompleted)
                by ContainerId
    | extend FOPercent = round(100.0 * todouble(TotalFOCompletedIO) / todouble(TotalCompletedIO), 2)
    | extend FOBucket = case(
        FOPercent >= 0  and FOPercent < 1,   "0-1%",
        FOPercent >= 1  and FOPercent < 10,  "1-10%",
        FOPercent >= 10 and FOPercent < 20,  "10-20%",
        FOPercent >= 20 and FOPercent < 30,  "20-30%",
        FOPercent >= 30 and FOPercent < 40,  "30-40%",
        FOPercent >= 40 and FOPercent < 50,  "40-50%",
        FOPercent >= 50 and FOPercent < 60,  "50-60%",
        FOPercent >= 60 and FOPercent < 70,  "60-70%",
        FOPercent >= 70 and FOPercent < 80,  "70-80%",
        FOPercent >= 80 and FOPercent < 90,  "80-90%",
        FOPercent >= 90 and FOPercent < 99,  "90-99%",
        FOPercent >= 99 and FOPercent < 99.5,  "99-99.5%",
        FOPercent >= 99.5 and FOPercent <= 100, "99.5-100%",
        "Other"
    )
    | summarize VmCount = dcount(ContainerId) by FOBucket;
//
// Force all buckets to appear
_VmFOPercents
| join kind=rightouter FO_Buckets on FOBucket
| project-away FOBucket
| extend VmCount = coalesce(VmCount, 0), FOBucket = FOBucket1
| project FOBucket, VmCount
| sort by FOBucket asc



// cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsAsapCounterTable
//     | where PreciseTimeStamp between (queryFrom .. queryTo ) and NodeId  == nodeId
//     | project Cluster, PreciseTimeStamp, NodeId, ContainerId, UseSwpe, 
//               DeltaFoCompleted,
//               DeltaPoCompleted, 
//               DeltaIOCompleted, 
//               DeltaReadIOCompleted, 
//               DeltaWriteIOCompleted, 
//               DeltaFoReadCompleted,
//               DeltaFoWriteCompleted,
//               DeltaPoReadCompleted,
//               DeltaPoWriteCompleted,
//               OsDiagDurationInSec, 
//               CachePolicy, DiskClass, DiskType, NamespaceName
//     // Filter Condition to fetch disks which are suppose to stayFO (Removes OS disk and IDLE VM cases)
//     | where UseSwpe == 0 and DeltaIOCompleted != 0
//     | summarize TotalFOCompletedIO = sum(DeltaFoCompleted),
//                 TotalPOCompletedIO = sum(DeltaPoCompleted),  
//                 TotalCompletedIO  = sum(DeltaIOCompleted),
//                 TotalCompletedPOReads = sum(DeltaPoReadCompleted),
//                 TotalCompletedPOWrites = sum(DeltaPoWriteCompleted)
//                 by Cluster, NodeId, ContainerId , bin(PreciseTimeStamp, 5m)
//     // Note the max granularity using this OS ASAP counters is 5m. the PF disk metrics is 30s.
//     // 
//     | extend PercentOfFOCompletedIO = round(100.0 * todouble(TotalFOCompletedIO) / todouble(TotalCompletedIO),2),
//              PercentOfPOCompletedIO = round(100.0 * todouble(TotalPOCompletedIO) / todouble(TotalCompletedIO),2),
//              PercentOfPOReads = round(100.0 * todouble(TotalCompletedPOReads) / todouble(TotalCompletedIO),2),
//              PercentOfPOWrites = round(100.0 * todouble(TotalCompletedPOWrites) / todouble(TotalCompletedIO),2)
//     //
//     | summarize FOPercent= round(avg(PercentOfFOCompletedIO),2)
//                 by  ContainerId
//     | sort by FOPercent asc
//     | extend FOBucket = case
//     (
//         FOPercent >= 0 and FOPercent < 1, "0-1%",
//         FOPercent >= 1 and FOPercent < 10, "1-10%",
//         FOPercent >= 10 and FOPercent < 20, "10-20%",
//         FOPercent >= 20 and FOPercent < 30, "20-30%",
//         FOPercent >= 30 and FOPercent < 40, "30-40%",
//         FOPercent >= 40 and FOPercent < 50, "40-50%",
//         FOPercent >= 50 and FOPercent < 60, "50-60%",
//         FOPercent >= 60 and FOPercent < 70, "60-70%",
//         FOPercent >= 70 and FOPercent < 80, "70-80%",
//         FOPercent >= 80 and FOPercent < 90, "80-90%",
//         FOPercent >= 90 and FOPercent < 99, "90-99%",
//         FOPercent >= 99 and FOPercent <= 100, "99-100%",
//         "Other"
//     )
//     | summarize VmCount = dcount(ContainerId) by FOBucket
//     | sort by FOBucket asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### OutlierContainersListQuery

_Widget purpose:_ VM outliers list: where %FO was < 80% (OSDiagVer >= 0.58)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > VM outliers list: where %FO was < 80% (OSDiagVer >= 0.58)`

```kusto
//
let threshold = 80;
//
cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsAsapCounterTable
    | where PreciseTimeStamp between (queryFrom .. queryTo ) and NodeId  == nodeId
    | project Cluster, PreciseTimeStamp, NodeId, ContainerId, UseSwpe, 
              DeltaFoCompleted,
              DeltaPoCompleted, 
              DeltaIOCompleted, 
              DeltaReadIOCompleted, 
              DeltaWriteIOCompleted, 
              DeltaFoReadCompleted,
              DeltaFoWriteCompleted,
              DeltaPoReadCompleted,
              DeltaPoWriteCompleted,
              OsDiagDurationInSec, 
              CachePolicy, DiskClass, DiskType, NamespaceName
    // Filter Condition to fetch disks which are suppose to stayFO (Removes OS disk and IDLE VM cases)
    | where UseSwpe == 0 and DeltaIOCompleted != 0
    | summarize TotalFOCompletedIO = sum(DeltaFoCompleted),
                TotalPOCompletedIO = sum(DeltaPoCompleted),  
                TotalCompletedIO  = sum(DeltaIOCompleted),
                TotalCompletedPOReads = sum(DeltaPoReadCompleted),
                TotalCompletedPOWrites = sum(DeltaPoWriteCompleted)
                by Cluster, NodeId, ContainerId
    // 
    | extend PercentOfFOCompletedIO = round(100.0 * todouble(TotalFOCompletedIO) / todouble(TotalCompletedIO),2),
             PercentOfPOCompletedIO = round(100.0 * todouble(TotalPOCompletedIO) / todouble(TotalCompletedIO),2),
             PercentOfPOReads = round(100.0 * todouble(TotalCompletedPOReads) / todouble(TotalCompletedIO),2),
             PercentOfPOWrites = round(100.0 * todouble(TotalCompletedPOWrites) / todouble(TotalCompletedIO),2)
    //
    | summarize FOPercent= round(avg(PercentOfFOCompletedIO),2),
                POReadsPercent = round(avg(PercentOfPOReads),2),
                POWritesPercent = round(avg(PercentOfPOWrites),2)
                by  ContainerId, TotalCompletedIO
    | where FOPercent < threshold
    | sort by FOPercent asc
    //
    | extend FOBucket = case
    (
        FOPercent >= 0 and FOPercent < 1, "0-1%",
        FOPercent >= 1 and FOPercent < 10, "1-10%",
        FOPercent >= 10 and FOPercent < 20, "10-20%",
        FOPercent >= 20 and FOPercent < 30, "20-30%",
        FOPercent >= 30 and FOPercent < 40, "30-40%",
        FOPercent >= 40 and FOPercent < 50, "40-50%",
        FOPercent >= 50 and FOPercent < 60, "50-60%",
        FOPercent >= 60 and FOPercent < 70, "60-70%",
        FOPercent >= 70 and FOPercent < 80, "70-80%",
        FOPercent >= 80 and FOPercent < 90, "80-90%",
        FOPercent >= 90 and FOPercent < 99, "90-99%",
        FOPercent >= 99 and FOPercent <= 100, "99-100%",
        "Other"
    )
    // Add Direct Link
    | extend AsiVMView = strcat("http://aka.ms/azurehostvm?containerId=", ContainerId, "&globalFrom=", queryFrom, "&globalTo=", queryTo)
    // Add filter
    | where FOBucket ==  fobucket or isempty(fobucket)
    | project-rename VmFOPercent = FOPercent
    ;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{fobucket}`

---

### FoBucketFilterQuery

_Widget purpose:_ VM outliers list: where %FO was < 80% (OSDiagVer >= 0.58)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Full Offload Stats > VM outliers list: where %FO was < 80% (OSDiagVer >= 0.58)`

```kusto
// Define FO buckets explicitly
let FO_Buckets = datatable(FOBucket:string)
[
    "0-1%",
    "1-10%",
    "10-20%",
    "20-30%",
    "30-40%",
    "40-50%",
    "50-60%",
    "60-70%",
    "70-80%",
    "80-90%",
    "90-99%",
    "99-100%"
] 
| sort by FOBucket asc
    // Below is name convention that ASI Needs! Value == FOBucket
    | extend Value = FOBucket
    | distinct Value
    | sort by Value asc ;
FO_Buckets;


// //
// let threshold = 80;
// //
// cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsAsapCounterTable
//     | where PreciseTimeStamp between (queryFrom .. queryTo ) and NodeId  == nodeId
//     | project Cluster, PreciseTimeStamp, NodeId, ContainerId, UseSwpe, 
//               DeltaFoCompleted,
//               DeltaPoCompleted, 
//               DeltaIOCompleted, 
//               DeltaReadIOCompleted, 
//               DeltaWriteIOCompleted, 
//               DeltaFoReadCompleted,
//               DeltaFoWriteCompleted,
//               DeltaPoReadCompleted,
//               DeltaPoWriteCompleted,
//               OsDiagDurationInSec, 
//               CachePolicy, DiskClass, DiskType, NamespaceName
//     // Filter Condition to fetch disks which are suppose to stayFO (Removes OS disk and IDLE VM cases)
//     | where UseSwpe == 0 and DeltaIOCompleted != 0
//     | summarize TotalFOCompletedIO = sum(DeltaFoCompleted),
//                 TotalPOCompletedIO = sum(DeltaPoCompleted),  
//                 TotalCompletedIO  = sum(DeltaIOCompleted),
//                 TotalCompletedPOReads = sum(DeltaPoReadCompleted),
//                 TotalCompletedPOWrites = sum(DeltaPoWriteCompleted)
//                 by Cluster, NodeId, ContainerId , bin(PreciseTimeStamp, 5m)
//     // Note the max granularity using this OS ASAP counters is 5m. the PF disk metrics is 30s.
//     // 
//     | extend PercentOfFOCompletedIO = round(100.0 * todouble(TotalFOCompletedIO) / todouble(TotalCompletedIO),2),
//              PercentOfPOCompletedIO = round(100.0 * todouble(TotalPOCompletedIO) / todouble(TotalCompletedIO),2),
//              PercentOfPOReads = round(100.0 * todouble(TotalCompletedPOReads) / todouble(TotalCompletedIO),2),
//              PercentOfPOWrites = round(100.0 * todouble(TotalCompletedPOWrites) / todouble(TotalCompletedIO),2)
//     //
//     | summarize FOPercent= round(avg(PercentOfFOCompletedIO),2),
//                 POReadsPercent = round(avg(PercentOfPOReads),2),
//                 POWritesPercent = round(avg(PercentOfPOWrites),2)
//                 by  ContainerId
//     | where FOPercent < threshold
//     | sort by FOPercent asc
//     //
//     | extend FOBucket = case
//     (
//         FOPercent >= 0 and FOPercent < 1, "0-1%",
//         FOPercent >= 1 and FOPercent < 10, "1-10%",
//         FOPercent >= 10 and FOPercent < 20, "10-20%",
//         FOPercent >= 20 and FOPercent < 30, "20-30%",
//         FOPercent >= 30 and FOPercent < 40, "30-40%",
//         FOPercent >= 40 and FOPercent < 50, "40-50%",
//         FOPercent >= 50 and FOPercent < 60, "50-60%",
//         FOPercent >= 60 and FOPercent < 70, "60-70%",
//         FOPercent >= 70 and FOPercent < 80, "70-80%",
//         FOPercent >= 80 and FOPercent < 90, "80-90%",
//         FOPercent >= 90 and FOPercent < 99, "90-99%",
//         FOPercent >= 99 and FOPercent <= 100, "99-100%",
//         "Other"
//     )
//     | distinct FOBucket
//     // Below is name convention that ASI Needs! Value == FOBucket
//     | extend Value = FOBucket
//     | distinct Value
//     | sort by Value asc 
//     ;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Asap Heartbeats

_Widget purpose:_ ASAP Heartbeats for PF and KMS

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Heartbeats for PF and KMS`

```kusto
AsapKmsEtwTraceLogEventView
| where PreciseTimeStamp between (queryFrom .. queryTo)
    and NodeId == nodeId
    and EventId == 1004
| project PreciseTimeStamp, EventId
| summarize KMS_Heartbeats = count() by bin(PreciseTimeStamp, 15m)
| project TimestampUtc = PreciseTimeStamp, KMS_Heartbeats
| join kind=fullouter (
    AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (queryFrom .. queryTo)
        and NodeId == nodeId
        and EventId == 72
    | project PreciseTimeStamp, EventId
    | summarize PF_Heartbeats = count() by bin(PreciseTimeStamp, 15m)
    | project TimestampUtc = PreciseTimeStamp, PF_Heartbeats
) on TimestampUtc
| project-away TimestampUtc1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Node ASAP VMA Query

_Widget purpose:_ ASAP Node view

Cluster: `Vmakpi.kusto.windows.net` · Database: `vmadb` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
VMA
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| extend Health = case(
    RCAEngineCategory == "Planned", "Healthy",
    RCAEngineCategory == "CustomerInitiated", "Neutral",
    "Unhealthy")
| project StartTime, Content = strcat(RoleInstanceName, " - ", RCA), Health
| distinct *
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Node Events

_Widget purpose:_ ASAP Node view

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId
| where Level == 1 or EventId in (1001) or (EventId == (1014) and ProviderName == "Microsoft-Windows-DNS-Client")
| project StartTime = todatetime(TimeCreated), Content = strcat(ProviderName, "-", EventId), Health = case(Level == 1, "Unhealthy", "Degraded")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Node State (Fabric)

_Widget purpose:_ ASAP Node view

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
TMMgmtNodeStateChangedEtwTable
| where PreciseTimeStamp between ((startTime - 1d) .. (endTime + 1d)) and BladeID == nodeId
| project StartTime = PreciseTimeStamp, Content = OldState, T = 1
 | union (
     TMMgmtNodeStateChangedEtwTable
     | where PreciseTimeStamp between ((startTime - 1d) .. (endTime + 1d)) and BladeID == nodeId
     | project StartTime = PreciseTimeStamp, Content = NewState, T = 2
 )
| sort by StartTime, T asc
| extend Health = case(Content == "Ready", "Healthy", Content == "Unhealthy", "Degraded", Content in ("HumanInvestigate", "PoweringOn"), "Unhealthy",  "Neutral")
| serialize
| extend EndTime = StartTime // case(isnotempty(next(StartTime)), next(StartTime), now())
| sort by StartTime asc, T asc 
| extend StartTime = case(isnotempty(prev(StartTime)), prev(EndTime), startTime - 1h),
         FilterOut = Content == next(Content) and Content == prev(Content)
| where FilterOut != 1
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), now())
| extend StartTime = case(isnotempty(prev(StartTime)), prev(EndTime), startTime - 1h)
| sort by StartTime asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Azure Host XStore E17 AutoTriage

_Widget purpose:_ ASAP Node view

Cluster: `azcore.centralus.kusto.windows.net` · Database: `XHealth` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
DiskFailureXStoreTriage
| where TimeStamp between (startTime .. endTime) and NodeId == nodeId
| summarize arg_max(TriageTimestamp, *) by VhdAppCluster, NodeId, DiskPath, TimeStamp
//| where TriageReason !contains "Lease"
| project StartTime = TimeStamp, Content = strcat("E17 RCA: ", TriageCategory, ".", TriageReason), Health = "Unhealthy", Tooltip = DiskPath
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Node Updates

_Widget purpose:_ ASAP Node view

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
TMMgmtNodeEventsEtwTable  
| where TIMESTAMP between (startTime .. endTime) and NodeId =~ nodeId  and (Message contains 'CreatePluginComplete' or Message contains 'UpdatePluginCompleted')
| parse kind = regex Message with * ' = HostPluginName:' Component:string ', HostPluginSetupFile:' * 'HostPluginPackage:'package:string ', Action:'* 
| project StartTime = TIMESTAMP, Health = "Degraded", Content = Component, Tooltip = strcat(Component, " <i> updated </i> to ", package)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host PF Service Updates

_Widget purpose:_ ASAP Node view

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
ServiceVersionSwitch 
| where NodeId == nodeId and PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h))
| project StartTime = PreciseTimeStamp, Health = "Degraded", Content = strcat(ServiceName," <i>updated</i> "), Tooltip = strcat("<b>", ServiceName, "</b> updated from <i>", CurrentVersion, "</i> to <b>", NewVersion, "</b>")
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host OSHostPlugin Events

_Widget purpose:_ ASAP Node view

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (startTime .. endTime) and ProviderName in ('OSHostPlugin', 'NMAgent') and NodeId == nodeId
| project StartTime = todatetime(TimeCreated), Content = EventId, Tooltip = strcat(ProviderName, " - ", Description)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### ASAP UMED CE Events Timeline

_Widget purpose:_ ASAP Node view

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
let AsapEvents = GetAsapEventsExtended();   
AsapNvmeEtwEventTable
| where NodeId == nodeId and PreciseTimeStamp between (queryFrom .. queryTo)
| where Level < 3
| project PreciseTimeStamp, ProviderName, EventId, Level, EventMessage
| lookup kind=leftouter (AsapEvents) on ($left.EventId == $right.Id and $left.ProviderName == $right.Provider)
| extend info = coalesce(EventName, EventMessage)
| project StartTime = PreciseTimeStamp, Content = strcat(tostring(EventId), " - ", info), Health = "Unhealthy"
| order by StartTime asc
| take 20
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### ASAP KMS CE Events Timeline

_Widget purpose:_ ASAP Node view

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
let AsapEvents = GetAsapEventsExtended();
AsapKmsEtwEventTable
| where NodeId == nodeId and PreciseTimeStamp between (queryFrom .. queryTo)
| where Level < 3
| project PreciseTimeStamp, ProviderName, EventId, Level, EventMessage
| lookup kind=leftouter (AsapEvents) on ($left.EventId == $right.Id and $left.ProviderName == $right.Provider)
| extend info = coalesce(EventName, EventMessage)
| project StartTime = PreciseTimeStamp, Content = strcat(tostring(EventId), " - ", info), Health = "Unhealthy"
| order by StartTime asc
| take 20
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### ASAP PF CE Events Timeline

_Widget purpose:_ ASAP Node view

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
let AsapEvents = GetAsapEventsExtended();
AsapPfEtwEventTable
| where NodeId == nodeId and PreciseTimeStamp between (queryFrom .. queryTo)
| where Level < 3
| project PreciseTimeStamp, ProviderName, EventId, Level, EventMessage
| lookup kind=leftouter (AsapEvents) on ($left.EventId == $right.Id and $left.ProviderName == $right.Provider)
| extend info = coalesce(EventName, EventMessage)
| project StartTime = PreciseTimeStamp, Content = strcat(tostring(EventId), " - ", info), Health = "Unhealthy"
| order by StartTime asc
| take 20
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Node TIP sessions

_Widget purpose:_ ASAP Node view

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > ASAP Node view`

```kusto
// Check LogNodeSnapshot for current TIP session ID
let logNodeTipSessionId = toscalar(
    LogNodeSnapshot
    | where PreciseTimeStamp between ((queryFrom - 1d) .. (queryTo + 1d)) and nodeId == _nodeId
    | summarize arg_max(PreciseTimeStamp,*)
    | project tipNodeSessionId
);
let logTipNodeSessionId = toscalar(
    LogTipNodeSessionSnapShot
    | where PreciseTimeStamp between ((queryFrom - 1d) .. (queryTo + 1d)) and nodeList has _nodeId
    | project tipNodeSessionId
);
let tipSessionId = coalesce(logTipNodeSessionId, logNodeTipSessionId);
let stuck = iff(isnotempty(logTipNodeSessionId), false, true);
LogTipNodeSessionSnapShot
| where tipNodeSessionId == tipSessionId
| project PreciseTimeStamp, startTime, expirationTime, tipNodeSessionId, createdBy, reason, nodeList
| summarize StartTime = arg_min(PreciseTimeStamp, *), EndTime = arg_max(PreciseTimeStamp, *) by tipNodeSessionId
| extend Health = iff(stuck, "Unhealthy", "Neutral")
| project StartTime, Content = strcat("TIP Id: ", tipNodeSessionId, ", CreatedBy: ", createdBy), Health, EndTime = iff(isnotempty(logTipNodeSessionId),EndTime, now())
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_nodeId}`

---

### ControllerResetsAndIoLossQuery

_Widget purpose:_ Controller Resets and IO Loss events Query

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > Controller Resets and IO Loss events Query`

```kusto
GetAsapPfEventsPerNode(nodeId, queryFrom, queryTo)
    | where EventId in (5400, 5403) // 5402
    | sort by PreciseTimeStamp asc
    //| where EventId == 5400 or (EventId == 5403 and prev(EventId) == 5400) // Take 5403 that follows Reset 5400 event to check if its HW or SW Detceted
    | summarize Count5400 =  countif(EventId == 5400), CountIOLoss = countif(EventId  == 5403) by bin(PreciseTimeStamp, 15m)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### CriticalErrorsQuery 

_Widget purpose:_ Critical Errors Query 

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > Critical Errors Query `

```kusto
GetAsapPfEventsPerNode(nodeId, queryFrom, queryTo)
    | where EventId in (44, 1098)
    | sort by PreciseTimeStamp asc
    | extend 
        hw_detected_ce = coalesce(tostring(extract(@"hw_detected_ce=(\d+)", 1, Message)), tostring(parse_json(Message)["hw_detected_ce"])),
        sw_detected_ce = coalesce(tostring(extract(@"sw_detected_ce=(\d+)", 1, Message)), tostring(parse_json(Message)["sw_detected_ce"]))
    | sort by PreciseTimeStamp asc 
    | where EventId == 44 or (EventId == 1098 and prev(EventId) == 44) // Take 1098 that follows CE 44 event to check if its HW or SW Detceted
    | summarize Count44 =  countif(EventId == 44), CountHWDetected = countif(hw_detected_ce  == '1'), CountSWDetected = countif(sw_detected_ce  == '1') by bin(PreciseTimeStamp, 15m)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### VfStuckExtrPrejudiceQuery

_Widget purpose:_ Vf Stuck and Extreme Prejudice Events Count

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `StorageClient Tables > ASAP > ASAP > Heartbeats > Vf Stuck and Extreme Prejudice Events Count`

```kusto
GetAsapKmsEventsPerNode(nodeId, queryFrom, queryTo)
    | where EventId in (1006, 3000)
    | sort by PreciseTimeStamp asc
    | summarize CountVfStuck =  countif(EventId == 1006), CountExtremePrejuidice = countif(EventId  == 3000) by bin(PreciseTimeStamp, 15m)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Node ASAP Insights For Node

_Widget purpose:_ ASAP Insights for the OVL 1.1 Node (for the time selected)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Insights > Insights > ASAP Insights for the OVL 1.1 Node (for the time selected)`

```kusto
AsapInsightsPerNode(nodeId, startTime, endTime)
| project PreciseTimeStamp, EventName, Message, level = case(Level >= 3, "warning", "error"), Details
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### AsapInsightsOVL2Query

_Widget purpose:_ ASAP Insights OVL 2 Node (for selected time range)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Insights > Insights > ASAP Insights OVL 2 Node (for selected time range)`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapInsightsPerNodeOvl2(nodeId, queryFrom, queryTo)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### ManaVersion

_Widget purpose:_ MANA Versions

Cluster: `Azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > MANA Version > MANA Versions`

```kusto
let hostname = toscalar(cluster("Azcore.centralus").database('Fa').WindowsEventTable
| where PreciseTimeStamp > ago(1d) and NodeId == nodeid
| take 1
| summarize take_any (Computer));
cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').LinuxOverlakeSystemdView()
| where TIMESTAMP between (startTime .. endTime)
| where _HOSTNAME startswith hostname and  PORTABLE startswith "socmana"
| project TIMESTAMP, _HOSTNAME, SYSLOG_IDENTIFIER, MESSAGE
| where MESSAGE !contains  "0x28006"
| parse MESSAGE  with * "] [" ManaDriver " v=" ManaDriverVersion " h=" FPGAImageVersion "]" * 
| extend ManaDriver = case ( ManaDriver =~ 'gdma', 'mana_bus(gdma)',
ManaDriver =~ 'bnic', 'mana(bnic)',
ManaDriver =~ 'rnic', 'mana_ib(rnic)',
'n/a'
)
| project TIMESTAMP, _HOSTNAME, SYSLOG_IDENTIFIER, ManaDriver, ManaDriverVersion, FPGAImageVersion , MESSAGE
| where isnotempty( FPGAImageVersion)
| summarize min(TIMESTAMP), max(TIMESTAMP) by _HOSTNAME, ManaDriver, ManaDriverVersion, FPGAImageVersion
```

**Params:** `{startTime}`, `{endTime}`, `{nodeid}`

---

### Azure Host ASAP All Tables Union

_Widget purpose:_ Non-Informational Only

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > All Tables > All Tables > Non-Informational Only`

```kusto
union cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapDpaEtwEventTable,
      cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapKmsEtwEventTable,
      cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapNullEtwEventTable,
      cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapNvmeEtwEventTable,
      cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and Level < 4
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project TimeCreated = todatetime(PreciseTimeStamp), Id = tostring(EventId), ProviderName, Message = EventMessage, level
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Node ASAP FPGA DataLogger

Cluster: `xaccel` · Database: `xaccel` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > DataLogger`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
let lookbackTime = queryFrom - 15d;
//
// Looking back 2 hours for ASAP PF hearbeat event to get the most likely git_hash
let git_hash = tostring(toscalar(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwEventTable
    | where PreciseTimeStamp between (lookbackTime .. startTime)
        and NodeId == nodeId and EventId in (1, 2, 72, 73)
    | summarize arg_max(PreciseTimeStamp, *) by NodeId
    | project PreciseTimeStamp, NodeId, EventMessage, Message
    | extend hwCommit = tohex(extract('HwCommitHash="(.*?)"', 1, Message, typeof(long)))
    | project hwCommit
    | take 1
));
//
// Materialize the ASAP PF events for calling few functions later
let events = materialize(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwEventTable
    | where PreciseTimeStamp between (startTime .. endTime)
        and NodeId == nodeId and EventId in (44, 1112)
    | project PreciseTimeStamp, Cluster, NodeId, EventId, Message, EventMessage
);
//
// HW CE summary
let hwceOutput = cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_HwCe_ByGitHash_V1(events, git_hash);
// Geting the HW first HW event debug registers
let event_key = toscalar(hwceOutput
| order by PreciseTimeStamp asc
| project event_key
| take 1);
cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_DataLogger(events, git_hash, event_key);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### ASAP ASAP PF HWCE and Debug Registers Dump

_Widget purpose:_ HW Critical Errors from ASAP FPGA debug registers dump

Cluster: `xaccel.centralus.kusto.windows.net` · Database: `XAccel` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > Debug Registers Dump (Overlake 1.1) > HW Critical Errors from ASAP FPGA debug registers dump`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
let lookbackTime = queryFrom - 15d;
let lookforwardTime = queryTo + 30m;
//
// Looking back for ASAP PF hearbeat event to get the most likely git_hash
let git_hash = tostring(toscalar(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwEventTable
    | where PreciseTimeStamp between (lookbackTime .. lookforwardTime)
        and NodeId == nodeId and EventId in (1, 2, 72, 73)
        and isnotempty(EventMessage)
    | extend hwCommit = extract('HwCommitHash="(.*?)"', 1, Message, typeof(long))
    | where hwCommit > 0
    | summarize arg_max(PreciseTimeStamp, *) by NodeId
    | project PreciseTimeStamp, NodeId, EventMessage, Message, hwCommit
    | project tohex(hwCommit)
    | take 1
));
//
// Materialize the ASAP PF events for calling few functions later
let events = materialize(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwEventTable
    | where PreciseTimeStamp between (startTime .. endTime)
        and NodeId == nodeId and EventId in (44, 1112)
    | project PreciseTimeStamp, Cluster, NodeId, EventId, Message, EventMessage
);
//
// HW CE summary
let hwceOutput = cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_HwCe_ByGitHash_V1(events, git_hash);
// Geting the HW first HW event debug registers
let event_key = toscalar(hwceOutput
| order by PreciseTimeStamp asc
| project event_key
| take 1);
cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_RegDump(events, git_hash, event_key)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Edit Query Azure Host ASAP Debug Registers HW CE

Cluster: `xaccel` · Database: `XAccel` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > HW CE from DR (Overlake 1.1)`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
let lookbackTime = queryFrom - 60d;
let lookforwardTime = queryTo + 30m;
//
// Looking back up to 60 days for ASAP PF hearbeat event to get the most likely git_hash
let git_hash = tostring(toscalar(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwEventTable
    | where PreciseTimeStamp between (lookbackTime .. lookforwardTime)
        and NodeId == nodeId and EventId in (1, 2, 72, 73)
        and isnotempty(EventMessage)
    | extend hwCommit = extract('HwCommitHash="(.*?)"', 1, Message, typeof(long))
    | where hwCommit > 0
    | summarize arg_max(PreciseTimeStamp, *) by NodeId
    | project PreciseTimeStamp, NodeId, EventMessage, Message, hwCommit
    | project tohex(hwCommit)
    | take 1
));
//
// Materialize the ASAP PF events for calling few functions later
let events = materialize(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwEventTable
    | where PreciseTimeStamp between (startTime .. endTime)
        and NodeId == nodeId and EventId in (44, 1112)
    | project PreciseTimeStamp, Cluster, NodeId, EventId, Message, EventMessage
);
//
// HW CE summary
cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_HwCe_ByGitHash_V1(events, git_hash)
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host ASAP KMS Table

_Widget purpose:_ AsapKmsEtwEventTable

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > KMS ETW > KMS ETW > AsapKmsEtwEventTable`

```kusto
AsapKmsEtwEventTable
| where NodeId == nodeId and PreciseTimeStamp between (startTime .. endTime)
| extend State = extract('State="(.*?)"', 1, Message, typeof(string))
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, State, level, KeywordName, EventId, EventMessage
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host Node ASAP Node Story

_Widget purpose:_ Node story based on ASAP, Hyper-V and NDPA events

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > Node Story > Node story based on ASAP, Hyper-V and NDPA events`

```kusto
GetAsapHypNdpEventsShort(nodeId, queryFrom, queryTo)
| where Source != "NetDatapath"
| extend level = case(Level < 2, "critical",Level == 2, "error", Level == 3, "warning", "info")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

**Signal filters seen in KQL:** `Source != "NetDatapath"`

---

### Azure Host ASAP ETW Table

_Widget purpose:_ AsapNvmeEtwEventTable

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > NVME ETW > NVME ETW > AsapNvmeEtwEventTable`

```kusto
AsapNvmeEtwEventTable
| where NodeId == nodeId and PreciseTimeStamp between (startTime .. endTime)
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, level, KeywordName, EventId, EventMessage
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host PF ETW Table

_Widget purpose:_ AsapPfEtwEventTable

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > PF ETW > PF ETW > AsapPfEtwEventTable`

```kusto
AsapPfEtwEventTable
| where NodeId == nodeId and PreciseTimeStamp between (startTime .. endTime)
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, level, KeywordName, EventId, EventMessage
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host ASAP FPGA HW Shell Telemetry

_Widget purpose:_ Shell HW FPGA Telemetry

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 1.1 ETW > Shell HW FPGA > Shell HW FPGA Telemetry`

```kusto
OsConfigTable
| where PreciseTimeStamp between ((queryFrom - 5m) .. (queryTo + 5m))
| where Component == "FpgaHwTelemetryView"
| where NodeId == queryNodeId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Component == "FpgaHwTelemetryView"`

---

### Azure Host ASFO Critical and Error Events

_Widget purpose:_ ASAP Components Versions from Events

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Critical and Error Events > ASAP Components Versions from Events`

```kusto
GetAsapEventsOverlake2(nodeId, queryFrom, queryTo)
| where Source !in ("NetDatapath")
| where Level <= 3
|extend level = case(
    Level == 1, "critical",
    Level == 2, "error",
    Level == 3, "warning",
    Level == 4, "info",
    "verbose")
| project-away Level
| sort by PreciseTimeStamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### ASAP Hardware Debug Registers Output S0C0 to S3CX

_Widget purpose:_ Debug Registers for clients S0C0 to S3Cx

Cluster: `xaccel.centralus.kusto.windows.net` · Database: `XAccel` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > S0C0 - S3Cx (Overlake 2) > Debug Registers for clients S0C0 to S3Cx`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
let lookbackTime = queryFrom - 15d;
//
// Looking back for ASAP PF hearbeat event to get the most likely git_hash
let git_hash = tostring(toscalar(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (lookbackTime .. startTime)
        and NodeId == nodeId and EventId in (1, 2, 72, 73)
    | summarize arg_max(PreciseTimeStamp, *) by NodeId
    | project PreciseTimeStamp, NodeId, Message
    | extend hwCommit = tohex(extract('"HwCommitHash":(.*?),', 1, Message, typeof(long)))
    | project hwCommit
| take 1
));
//
// Materialize the ASAP PF events for calling few functions later
let events = materialize(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (startTime .. endTime)
        and NodeId == nodeId and EventId in (44, 1112)
    | project PreciseTimeStamp, Cluster, NodeId, EventId, Message
);
//
// HW CE summary
let hwceOutput = cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_HwCe_ByGitHash_Ovl2_V1(events, git_hash);
// Geting the HW first HW event debug registers
let event_key = toscalar(
hwceOutput
| order by PreciseTimeStamp asc
| project event_key
| take 1);
//
cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_RegDump_Ovl2(events, git_hash, event_key)
| where client_name startswith "S0C"
    or client_name startswith "S1C"
    or client_name startswith "S2C"
    or client_name startswith "S3C"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

**Signal filters seen in KQL:** `client_name startswith "S0C"`

---

### ASAP Hardware Debug Registers Output S4C0 to S7CX

_Widget purpose:_ Debug Registers for clients S4C0 to S7Cx

Cluster: `xaccel.centralus.kusto.windows.net` · Database: `XAccel` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > S4C0 - S7Cx (Overlake 2) > Debug Registers for clients S4C0 to S7Cx`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
let lookbackTime = queryFrom - 15d;
//
// Looking back for ASAP PF hearbeat event to get the most likely git_hash
let git_hash = tostring(toscalar(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (lookbackTime .. startTime)
        and NodeId == nodeId and EventId in (1, 2, 72, 73)
    | summarize arg_max(PreciseTimeStamp, *) by NodeId
    | project PreciseTimeStamp, NodeId, Message
    | extend hwCommit = tohex(extract('"HwCommitHash":(.*?),', 1, Message, typeof(long)))
    | project hwCommit
| take 1
));
//
// Materialize the ASAP PF events for calling few functions later
let events = materialize(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (startTime .. endTime)
        and NodeId == nodeId and EventId in (44, 1112)
    | project PreciseTimeStamp, Cluster, NodeId, EventId, Message
);
//
// HW CE summary
let hwceOutput = cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_HwCe_ByGitHash_Ovl2_V1(events, git_hash);
// Geting the HW first HW event debug registers
let event_key = toscalar(
hwceOutput
| order by PreciseTimeStamp asc
| project event_key
| take 1);
//
cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_RegDump_Ovl2(events, git_hash, event_key)
| where client_name startswith "S4C"
    or client_name startswith "S5C"
    or client_name startswith "S6C"
    or client_name startswith "S7C"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

**Signal filters seen in KQL:** `client_name startswith "S4C"`

---

### ASAP Hardware Debug Registers Output S8C0 to SBCX

_Widget purpose:_ Debug Registers for clients S8C0 to SBCx

Cluster: `xaccel.centralus.kusto.windows.net` · Database: `XAccel` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > S8C0 - SBCx (Overlake 2) > Debug Registers for clients S8C0 to SBCx`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
let lookbackTime = queryFrom - 15d;
//
// Looking back for ASAP PF hearbeat event to get the most likely git_hash
let git_hash = tostring(toscalar(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (lookbackTime .. startTime)
        and NodeId == nodeId and EventId in (1, 2, 72, 73)
    | summarize arg_max(PreciseTimeStamp, *) by NodeId
    | project PreciseTimeStamp, NodeId, Message
    | extend hwCommit = tohex(extract('"HwCommitHash":(.*?),', 1, Message, typeof(long)))
    | project hwCommit
| take 1
));
//
// Materialize the ASAP PF events for calling few functions later
let events = materialize(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (startTime .. endTime)
        and NodeId == nodeId and EventId in (44, 1112)
    | project PreciseTimeStamp, Cluster, NodeId, EventId, Message
);
//
// HW CE summary
let hwceOutput = cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_HwCe_ByGitHash_Ovl2_V1(events, git_hash);
// Geting the HW first HW event debug registers
let event_key = toscalar(
hwceOutput
| order by PreciseTimeStamp asc
| project event_key
| take 1);
//
cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_RegDump_Ovl2(events, git_hash, event_key)
| where client_name startswith "S8C"
    or client_name startswith "S9C"
    or client_name startswith "SAC"
    or client_name startswith "SBC"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

**Signal filters seen in KQL:** `client_name startswith "S8C"`

---

### ASAP Hardware Debug Registers Output SCC0 to SFCX

_Widget purpose:_ Debug Registers for clients SCC0 to SFCx

Cluster: `xaccel.centralus.kusto.windows.net` · Database: `XAccel` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Debug Regs Split (Overlake 2) > SCC0 - SFCx (Overlake 2) > Debug Registers for clients SCC0 to SFCx`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
let lookbackTime = queryFrom - 15d;
//
// Looking back for ASAP PF hearbeat event to get the most likely git_hash
let git_hash = tostring(toscalar(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (lookbackTime .. startTime)
        and NodeId == nodeId and EventId in (1, 2, 72, 73)
    | summarize arg_max(PreciseTimeStamp, *) by NodeId
    | project PreciseTimeStamp, NodeId, Message
    | extend hwCommit = tohex(extract('"HwCommitHash":(.*?),', 1, Message, typeof(long)))
    | project hwCommit
| take 1
));
//
// Materialize the ASAP PF events for calling few functions later
let events = materialize(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (startTime .. endTime)
        and NodeId == nodeId and EventId in (44, 1112)
    | project PreciseTimeStamp, Cluster, NodeId, EventId, Message
);
//
// HW CE summary
let hwceOutput = cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_HwCe_ByGitHash_Ovl2_V1(events, git_hash);
// Geting the HW first HW event debug registers
let event_key = toscalar(
hwceOutput
| order by PreciseTimeStamp asc
| project event_key
| take 1);
//
cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_RegDump_Ovl2(events, git_hash, event_key)
| where client_name startswith "SCC"
    or client_name startswith "SDC"
    or client_name startswith "SEC"
    or client_name startswith "SFC"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

**Signal filters seen in KQL:** `client_name startswith "SCC"`

---

### Azure Host ASAP Full Offload PF Investigations

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Full Offload Investigations`

```kusto
let HttpTranscode=(c_:string) {
 case(c_ == "2198536472","XFE_E_ACCOUNT_REQUEST_THROTTLED",
      c_ == "2198536473","XFE_E_OVERALL_REQUEST_THROTTLED",
      c_ == "2198540548","XFE_E_RDMA_SESSION_NOT_FOUND",
      c_ == "2198536474","XFE_E_EXPECTED_PROVIDER_REQUEST_THROTTLED",
      c_ == "2198537743","XFE_E_BLOB_SEQUENCE_NUMBER_CONDITION_NOT_MET",
      c_ == "2198540553","XFE_E_RDMA_OUTOFBAND_METADATA_NOT_SUPPORTED",
      c_ == "2198471990","XS_STATUS_BLOB_SESSION_NOT_FOUND",
      c_ == "2198540554","XFE_E_FASTPATH_PARTITION_RELATED_ERROR",
      c_ == "2198471991","XS_STATUS_BLOB_SESSION_EXPIRED",
      c_ == "2198537738","XFE_E_BLOB_LEASE_LOST",
      c_ == "2198536517","XFE_E_BLOB_BANDWIDTH_THROTTLED",
      c_ == "2198536454","XFE_E_TIMEOUT",
      c_ == "2198471692","XS_STATUS_CRC_MISMATCH",
      c_)
};
AsapPfEtwTraceLogEventView
| where PreciseTimeStamp  between (startTime..endTime) 
    and NodeId == nodeId
| where EventId !between(9000..9500) 
| where EventId in (1,2,4243,4244,4503,44,5400,1117,7111,4250,7116,4237, 3003, 6029)
| where EventId !in (6502,9558,4500,4501,4610,4611)
| extend t = parse_json(Message)
| extend SubCode = case(EventId == 6029,HttpTranscode(t.HttpSubCode),t.HttpSubCode)
| extend ESWPE = case(EventId in (4501),t.ForceEnhancedSwpe,
                        (case (EventId == 4243,t.UseSpcNsSwpe,0)))
| extend SessIdx = case(EventId in (5200,5201,5202,5203,5206,5207,5208,5209,5210,5212,5213,5214,6028,6029,6030,6031,6033,6035,6037,7115), toint(t.SessionIndex), -1)
| extend NsName = case(EventId in (4244), t.NsName, "")
| extend WriteSess = SessIdx % 2
| extend AsapQpn = case(EventId in (5200,5201, 5202,5203,5204,5209,5210,5207,5208,5209,5210,5212,5300,5301,5900,5901,5902,5912,5913,5914,6028,6029,20000,20004,20005,20006,20007,20009,20011,20015,20037,20039,20100,20101,20102), toint(t.AsapQpn),
                        EventId in(1075),toint(t.ASAPQPN),
                        EventId in (30001,30002,30004),toint(t.ResponderRqVqId)/2,-1)
| extend reinj = case(EventId in(1075,1077,1078), t.NumberOfCancelledBqes, "0")
| extend NSID = case(EventId in (1067,4233,4234,4236,4237,4238,4239,4240,4243,4244,5200,5201,5202,5203,5206,5207,5208,5209,5210,5212,5213,5214,6028,6029,6030,6031,6035,6500,6501,6502,6503,7111,7115,7116), (1024-(t.NsIndex)), 
                     EventId in (4230,4236,4243,4244,5200,5201, 5202,5203,5204,5207,5208,5212,6020,6033,6037,6038), toint(t.NsId),-1)
| extend NewState = case(EventId == 5201, t.NewState,""), OldState = case(EventId == 5201, t.OldState,"")
| extend TimeSpan = case (EventId in (1111,4151,4243,4244,5212,10220,10221), toint(t.TimespanMs),0)
| extend BSIndex = case(EventId in (3003,4244,6038), toint(t.BackingStoreIndex), -1)
| extend BqeIdx = case(EventId in (6028,6035,6047), toint(t.BqeIdx),
                    EventId in (1075,1077,8002,8004), toint(t.BqeIndex),-1)
| extend Excp = case(EventId in (6000,6025),toint(t.ExceptionCode),-1)
| extend IPAdd = case(EventId in (5300,5301,5302),t.IpString,"")
| project PreciseTimeStamp, EventId, EventName, ESWPE, NsName, BSIndex,NSID, SessIdx, AsapQpn, Excp, SubCode, BqeIdx, IPAdd, Message
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host ASAP Debug Registers HW CE Overlake 2

Cluster: `xaccel.centralus.kusto.windows.net` · Database: `XAccel` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > HW CE from DR (Overlake 2)`

```kusto
//
let startTime = queryFrom;
let endTime = queryTo;
let lookbackTime = queryFrom - 7d;
//
// Looking back for ASAP PF hearbeat event to get the most likely git_hash
let git_hash = tostring(toscalar(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (lookbackTime .. startTime)
        and NodeId == nodeId and EventId in (1, 2, 72, 73)
    | summarize arg_max(PreciseTimeStamp, *) by NodeId
    | project PreciseTimeStamp, NodeId, Message
    | extend hwCommit = tohex(extract('"HwCommitHash":(.*?),', 1, Message, typeof(long)))
    | project hwCommit
| take 1
));
//
// Materialize the ASAP PF events for calling few functions later
let events = materialize(
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapPfEtwTraceLogEventView
    | where PreciseTimeStamp between (startTime .. endTime)
        and NodeId == nodeId and EventId in (44, 1112)
    | project PreciseTimeStamp, Cluster, NodeId, EventId, Message
);
//
// HW CE summary
cluster('xaccel.kusto.windows.net').database('XAccel').AsapPfEtw1112_HwCe_ByGitHash_Ovl2_V1(events, git_hash)
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Azure Host Node ASAP Insights for Overlake 2 Node

_Widget purpose:_ ASAP Insights for Overlake 2 node

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > Insights > ASAP Insights for Overlake 2 node`

```kusto
AsapInsightsPerNodeOvl2(nodeId, startTime, endTime)
| project PreciseTimeStamp, EventName, Message, level = case(
    Level == 1, "critical",
    Level == 2, "error",
    "warning"), Details
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host ASAP KMS Trace Logging

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > KMS Trace Logging`

```kusto
AsapKmsEtwTraceLogEventView
| where NodeId == nodeId and PreciseTimeStamp between (startTime .. endTime)
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, EventId, EventName, Message, level
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host ASAP NVME Trace Logging

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > NVME (UMED) Trace Logging`

```kusto
AsapNvmeEtwTraceLogEventView
| where NodeId == nodeId and PreciseTimeStamp between (startTime .. endTime)
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, EventId, EventName, Message, level
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host PF Trace Logging

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Overlake 2 Trace Logging > PF Trace Logging`

```kusto
AsapPfEtwTraceLogEventView
| where NodeId == nodeId and PreciseTimeStamp between (startTime .. endTime)
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, EventId, EventName, Message, level
| sort by PreciseTimeStamp
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Show_Cobe_Condition_OSHP 

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Column`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing`

```kusto
let  filteredEvents= materialize (union AsapKmsEtwEventTable , AsapNvmeEtwEventTable 
| where NodeId == _NodeId and PreciseTimeStamp between (_StartTime .. _EndTime )
| project PreciseTimeStamp, Cluster, DataCenter, Region, Provider = ProviderName, EventId, EventMessage, Level
| lookup kind=leftouter (
    GetAsapEventsExtended
    ) on $left.EventId == $right.Id, Provider
| where EventId in (107,22,23,9,2118,2120,1004) and EventMessage !contains ("Reason: 1") 
| where EventMessage !contains "ASAP Kernel-Mode Services DID receive bypass vhdmp handle for NSID 0" // because this is KMS 2118 event which we dont want
| order by PreciseTimeStamp asc 
| extend Note = iff( EventId == 23 and prev(EventId) == 22 and prev(EventMessage) contains "Transition: 0", "Ignore", "Keep") //flag out 23 event which mmatches with Tranition 0 22 event
| where (EventMessage !contains "Transition: 0") and Note!= "Ignore" //Filter out 22/23 pairs with NoOp
| project PreciseTimeStamp, Provider, EventId, EventName, Level,  EventMessage
| order by PreciseTimeStamp asc );
//filteredEvents; debug
let HardwareAccelerateEvents =
    filteredEvents
    | where EventId in (107,22) and EventMessage !contains ("Reason: 1")
    | order by PreciseTimeStamp asc
    | summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 107), EndTimestamp = minif(PreciseTimeStamp, EventId == 22)
    | extend Phase = "Hardware Accelerated Mode Pre-Servicing"
;
let ComputeBlackoutEvents =
    filteredEvents
    | where EventId in (22,23) 
    | order by PreciseTimeStamp asc
    | summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 22), EndTimestamp = minif(PreciseTimeStamp, EventId == 23)
    | extend Phase = "Compute Blackout (MMIO RangeChange)"
;
let StorageBrownoutEvents =
    filteredEvents
    | where EventId in (23,9) 
    | order by PreciseTimeStamp asc
    | summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 23), EndTimestamp = minif(PreciseTimeStamp, EventId == 9)
    | extend Phase = "Storage Brownout (Software Emulated Mode)"
;
let VmphuServiceEvents =
    filteredEvents
    | where EventId in( 9,2118) 
    | order by PreciseTimeStamp asc
    | summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 9), EndTimestamp = minif(PreciseTimeStamp, EventId == 2118)
    | extend Phase = "Compute Blackout (Vmphu FastSaveRestore)"
;
let HardwareAccelerateReturnEvents =
    filteredEvents
    | where EventId in(2118) 
    | order by PreciseTimeStamp asc
    | summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 2118)
    | extend EndTimestamp = _EndTime +  5m
    | extend Phase = "Hardware Accelerated Mode Post-Servicing"
;
union HardwareAccelerateEvents, ComputeBlackoutEvents, StorageBrownoutEvents,VmphuServiceEvents,HardwareAccelerateReturnEvents
| order by StartTimestamp asc
//Ignore ParentID for now.
| extend ParentId = case(Phase == "Hardware Accelerated", "", 
                         Phase == "Compute Blackout", "Hardware Accelerated",
                         Phase == "Storage Brownout", "Compute Blackout",
                         Phase == "Vmphu Fast Save and Restore","Storage Brownout",
                         Phase == "ServiceEndHardwareAccelerated","Vmphu Fast Save and Restore", "")
| extend Health = ""
| extend Content = case (Phase == "Storage Brownout (Software Emulated Mode)", "Software Emulated mode",
                        Phase == "Compute Blackout (MMIO RangeChange)", "MMIO Range Change",
                        Phase == "Hardware Accelerated Mode Pre-Servicing" , "Hardware Accelerated Mode (Prepare for Servicing)",
                        Phase == "Hardware Accelerated Mode Post-Servicing", "Hardware Accelerated Mode (Servicing End)",
                        Phase == "Compute Blackout (Vmphu FastSaveRestore)", "Vmphu Fast Save and Restore", "")
| project EventId = Phase,  StartTime = StartTimestamp, EndTime = EndTimestamp,Health = case(isempty(Health), "healthy", Health)  //, Content
| extend to_display = case(isempty(StartTime) or isempty( EndTime)
                      or StartTime >= EndTime, "false", "true")
| summarize dont_display_count = countif(to_display == "false")
| extend show_chart = iff(dont_display_count > 0, false, true)
```

**Params:** `{_NodeId}`, `{_EndTime}`, `{_StartTime}`

---

### MaxVM_ComputeBlackout1_ADPA

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Column`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing`

```kusto
let filteredEvents = materialize(union AsapKmsEtwEventTable , AsapNvmeEtwEventTable,AsapPfEtwEventTable, AsapDpaEtwEventTable
| where NodeId == _NodeId and PreciseTimeStamp between (_StartTime .. _EndTime )
| where EventMessage !contains ("Reason: 1") and EventMessage !contains  "RequestMask: 1"
| where EventMessage !contains "ASAP Kernel-Mode Services DID receive bypass vhdmp handle for NSID 0" // because this is KMS 2118 event which we dont want
| where  EventId in (107,22,23,9,2118,2120,1,2,1004)  or (EventId == 1007 and (ProviderName contains "DPA" or ProviderName !contains "KMS")) 
| order by PreciseTimeStamp asc 
| extend ContainerId = coalesce( (extract('ContainerID="(.*?)"', 1, Message, typeof(string))), extract(@"ContainerId\s+([a-f\d-]+)", 1, EventMessage, typeof(string)),
                                      (extract('ContainerID="(.*?)"', 1, EventMessage, typeof(string))))
| extend ComputeBlackoutVmPhu =  toint(extract(@"\(BlackoutInMs (\d+)\)", 1, EventMessage))
| extend ComputeBlackoutMMIO =  iff(EventId == 2120 , extract('TimespanMs="(.*?)"', 1, Message, typeof(int)),0)
| where EventMessage !has "ASAP PF is associating an MSI-X entry" // exclude pf 1004 events
| where EventMessage !has "ASAP Version Info - PF/NULL" //Filter eventID ==1004 WHERE PROVIDER WAS PF . We want KMS 1004
| project PreciseTimeStamp, Cluster, DataCenter, Region, ContainerId, Provider = ProviderName, Pid, Tid, EventId, EventMessage, Level, ComputeBlackoutVmPhu, ComputeBlackoutMMIO
| lookup kind=leftouter (
    GetAsapEventsExtended
    ) on $left.EventId == $right.Id, Provider
| order by PreciseTimeStamp asc, Pid asc, Tid asc 
);
//filteredEvents; //debug
let StartTimestamp107  = filteredEvents | where EventId == 107 | project PreciseTimeStamp; 
//StartTimestamp107;
let EndTimestamp1004  = filteredEvents | where EventId == 1004 | project PreciseTimeStamp;
let ComputeBlackoutHardwareUnload =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 22), EndTimestamp = minif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Unload"
    )
);
ComputeBlackoutHardwareUnload
| project Content = Phase, StartTime = StartTimestamp, EndTime = EndTimestamp, ContainerId
| as ComputeBlackoutHardwareUnload;
```

**Params:** `{_NodeId}`, `{_EndTime}`, `{_StartTime}`

---

### MaxVM_ComputeBlackout2_ADPA

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Column`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing`

```kusto
let filteredEvents = materialize(union AsapKmsEtwEventTable , AsapNvmeEtwEventTable,AsapPfEtwEventTable, AsapDpaEtwEventTable
| where NodeId == _NodeId and PreciseTimeStamp between (_StartTime .. _EndTime )
| where EventMessage !contains ("Reason: 1") and EventMessage !contains  "RequestMask: 1"
| where EventMessage !contains "ASAP Kernel-Mode Services DID receive bypass vhdmp handle for NSID 0" // because this is KMS 2118 event which we dont want
| where  EventId in (107,22,23,9,2118,2120,1,2,1004)  or (EventId == 1007 and (ProviderName contains "DPA" or ProviderName !contains "KMS")) 
| order by PreciseTimeStamp asc 
| extend ContainerId = coalesce( (extract('ContainerID="(.*?)"', 1, Message, typeof(string))), extract(@"ContainerId\s+([a-f\d-]+)", 1, EventMessage, typeof(string)),
                                      (extract('ContainerID="(.*?)"', 1, EventMessage, typeof(string))))
| extend ComputeBlackoutVmPhu =  toint(extract(@"\(BlackoutInMs (\d+)\)", 1, EventMessage))
| extend ComputeBlackoutMMIO =  iff(EventId == 2120 , extract('TimespanMs="(.*?)"', 1, Message, typeof(int)),0)
| where EventMessage !has "ASAP PF is associating an MSI-X entry" // exclude pf 1004 events
| where EventMessage !has "ASAP Version Info - PF/NULL" //Filter eventID ==1004 WHERE PROVIDER WAS PF . We want KMS 1004
| project PreciseTimeStamp, Cluster, DataCenter, Region, ContainerId, Provider = ProviderName, Pid, Tid, EventId, EventMessage, Level, ComputeBlackoutVmPhu, ComputeBlackoutMMIO
| lookup kind=leftouter (
    GetAsapEventsExtended
    ) on $left.EventId == $right.Id, Provider
| order by PreciseTimeStamp asc, Pid asc, Tid asc 
);
//filteredEvents; //debug
let StartTimestamp107  = filteredEvents | where EventId == 107 | project PreciseTimeStamp; 
//StartTimestamp107;
let EndTimestamp1004  = filteredEvents | where EventId == 1004 | project PreciseTimeStamp;
let ComputeBlackoutHardwareUnload =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 22), EndTimestamp = minif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Unload"
    )
);
// ComputeBlackoutHardwareUnload
// | project Content = Phase, StartTime = StartTimestamp, EndTime = EndTimestamp, ContainerId
// | as ComputeBlackoutHardwareUnload;
let StorageBrownoutEvents =
    materialize(filteredEvents
    | where EventId in (23,22) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 23), EndTimestamp = maxif(PreciseTimeStamp, EventId == 22) by ContainerId
    | extend Phase = "Storage Brownout"
    )
    //for every container we should have 4 events - 2 sets of (22,23)
 );
//StorageBrownoutEvents | as StorageBrownoutEvents;
let ComputeBlackoutHardwareLoad =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 22), EndTimestamp = maxif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Load"
    )
);
let PfServiceEvents =
    materialize(filteredEvents
    | where EventId in (2,1) 
    | order by PreciseTimeStamp asc
    | summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 2), EndTimestamp = minif(PreciseTimeStamp, EventId == 1)
    | extend Phase = "Pf Unload Load Servicing"
);
//PfServiceEvents | as PfServiceEvents;
ComputeBlackoutHardwareLoad 
| project Content = Phase, StartTime = StartTimestamp, EndTime = EndTimestamp, ContainerId
| as ComputeBlackoutHardwareLoad;
```

**Params:** `{_NodeId}`, `{_EndTime}`, `{_StartTime}`

---

### Display_ContainerIds_Query

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Service_V2`

```kusto
let filteredEvents = materialize(union AsapKmsEtwEventTable , AsapNvmeEtwEventTable,AsapPfEtwEventTable, AsapDpaEtwEventTable
| where NodeId == _NodeId and PreciseTimeStamp between (_StartTime .. _EndTime )
| where EventMessage !contains ("Reason: 1") and EventMessage !contains  "RequestMask: 1"
| where EventMessage !contains "ASAP Kernel-Mode Services DID receive bypass vhdmp handle for NSID 0" // because this is KMS 2118 event which we dont want
| where  EventId in (107,22,23,1,2, 2118,2120,1004)  or (EventId == 1007 and (ProviderName contains "DPA" or ProviderName !contains "KMS")) 
| order by PreciseTimeStamp asc 
| extend ContainerId = coalesce( (extract('ContainerID="(.*?)"', 1, Message, typeof(string))), extract(@"ContainerId\s+([a-f\d-]+)", 1, EventMessage, typeof(string)),
                                      (extract('ContainerID="(.*?)"', 1, EventMessage, typeof(string))))
| where EventMessage !has "ASAP PF is associating an MSI-X entry" // exclude pf 1004 events
| where EventMessage !has "ASAP Version Info - PF/NULL" //Filter eventID ==1004 WHERE PROVIDER WAS PF . We want KMS 1004
| project PreciseTimeStamp, Cluster, DataCenter, Region, ContainerId, Provider = ProviderName, EventId, EventMessage
| lookup kind=leftouter (
    GetAsapEventsExtended
    | project Id, Provider, EventName
    ) on $left.EventId == $right.Id, Provider
| order by PreciseTimeStamp asc
);
filteredEvents
| where isnotempty(ContainerId)
| distinct Cluster, DataCenter, Region, ContainerId, _NodeId; //debug
```

**Params:** `{_NodeId}`, `{_EndTime}`, `{_StartTime}`

---

### Check_ShowCobe_Condition_ADPA_MultiVm

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `MultiRow` · Widget: `Row`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Service_V2`

```kusto
let filteredEvents = materialize(GetAsapEventsOverlake2(_NodeId, _StartTime, _EndTime)
| extend json = parse_json(Message)
| extend ContainerId = tostring(json.ContainerId), PfVer = tostring(json.ProductVersion), Transition = tolong(json.Transition)
| where (Source == 'PF' and EventId in (1,2, 4237, 4244, 4243) ) 
        or (Source == 'UMED' and EventId in (2118,2120, 3031, 3032)) // NO need to include duration event 2120, we need Start/End fr Cobe
        or (Source == 'UMED' and EventId in (22,23) and Transition in (1,3)
        or (Source == 'KMS' and EventId in (107, 1004) ))
| sort by PreciseTimeStamp asc 
| project PreciseTimeStamp, Source, PfVer, ContainerId, EventId, EventName, Transition, EventMessage = Message
// Post Fill Container ID events:
| scan declare (Container_: string="") with 
        (
            step s1: true => Container_ = iff(isempty(ContainerId), s1.Container_, ContainerId);
        )
| extend  ContainerId = Container_
| project-away Container_
);
let StartTimestamp107  = filteredEvents | where EventId == 107 | project PreciseTimeStamp; //the pre service hardware accel time is constant for all containers
//StartTimestamp107;
let EndTimestamp1004  = filteredEvents | where EventId == 1004 | project PreciseTimeStamp;//the post service hardware accel time is constant for all containers
let HardwareAccelerateEvents =
    materialize(filteredEvents
    | where EventId in (107,22) and EventMessage !contains ("Reason: 1") //and EventMessage contains " Transition: 3"
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize EndTimestamp = minif(PreciseTimeStamp, EventId == 22) by ContainerId
     | extend Phase = "Hardware Accelerate Mode PreService" ,
       StartTimestamp = toscalar(StartTimestamp107) // how to add PreciseTimeStamp of event 107
    )
    | where isnotempty( ContainerId)
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    | project ContainerId, StartTimestamp, EndTimestamp, Phase, Duration
);
// HardwareAccelerateEvents | as HardwareAcceleratePreService;
let ComputeBlackoutHardwareUnload =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 22), EndTimestamp = minif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Unload"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
);
//ComputeBlackoutHardwareUnload | as ComputeBlackoutHardwareUnload;
let StorageBrownoutEvents =
    materialize(filteredEvents
    | where EventId in (23,22) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 23), EndTimestamp = maxif(PreciseTimeStamp, EventId == 22) by ContainerId
    | extend Phase = "Storage Brownout"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
    //for every container we should have 4 events - 2 sets of (22,23)
 );
//StorageBrownoutEvents | as StorageBrownoutEvents;
let PfServiceEvents =
    materialize(filteredEvents
    | where EventId in (2,1) 
    | order by PreciseTimeStamp asc
    | summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 2), EndTimestamp = minif(PreciseTimeStamp, EventId == 1)
    | extend Phase = "Pf Unload Load Servicing"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
);
//PfServiceEvents | as PfServiceEvents;
let ComputeBlackoutHardwareLoad =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 22), EndTimestamp = maxif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Load"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
);
//ComputeBlackoutHardwareLoad | as ComputeBlackoutHardwareLoad;
let HardwareAccelerateReturnEvents =
    materialize(filteredEvents
    | where EventId in(23,1007,1004) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 23) by ContainerId
     | extend EndTimestamp = toscalar(EndTimestamp1004) // how to add PreciseTimeStamp of event 107, 
     | extend Phase = "Hardware Accelerate Mode PostService"
     | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
    | where isnotempty( ContainerId)
);
//HardwareAccelerateReturnEvents | as HardwareAcceleratePostService;
union HardwareAccelerateEvents,ComputeBlackoutHardwareUnload, StorageBrownoutEvents, ComputeBlackoutHardwareLoad, HardwareAccelerateReturnEvents, PfServiceEvents
| order by StartTimestamp asc
//Ignore ParentID for now.
| extend ParentId = case(Phase == "Pf Unload Load Servicing","Storage Brownout",
                         "")
| extend ContainerId = iff (isempty(ContainerId), "All Containers", ContainerId)
| extend Health = ""
| project ContainerId, EventId = Phase,  StartTime = StartTimestamp, EndTime = EndTimestamp,ParentId,
          //Adding color codes using Health
          Health = case(Phase contains "Hardware Accelerate", "Healthy", Phase contains "Blackout","Unhealthy",Phase contains "Brownout", "Degraded", "Neutral"),
          Tooltip = strcat(Phase, " : " , _ContainerId, " : ", "\nDuration = ", strcat(tostring(Duration), " Ms"))
//Checking null conditions below 
| extend to_display = case(isempty(StartTime) or isempty( EndTime)
                      or StartTime > EndTime, "false", "true")
| summarize dont_display_count = countif(to_display == "false")
| extend show_chart = iff(dont_display_count > 0, false, true)
```

**Params:** `{_NodeId}`, `{_StartTime}`, `{_EndTime}`, `{_ContainerId}`

---

### AdpaServiceQueryPerContainer

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CoBeTimeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Service_V2`

```kusto
// let filteredEvents = materialize(union AsapKmsEtwEventTable , AsapNvmeEtwEventTable,AsapPfEtwEventTable, AsapDpaEtwEventTable
// | where NodeId == _NodeId and PreciseTimeStamp between (_StartTime .. _EndTime )
// | where EventMessage !contains ("Reason: 1") and EventMessage !contains  "RequestMask: 1"
// | where EventMessage !contains "ASAP Kernel-Mode Services DID receive bypass vhdmp handle for NSID 0" // because this is KMS 2118 event which we dont want
// | where  EventId in (107,22,23,9,2118,2120,1,2,1004)  or (EventId == 1007 and (ProviderName contains "DPA" or ProviderName !contains "KMS")) 
// | order by PreciseTimeStamp asc 
// | extend ContainerId = coalesce( (extract('ContainerID="(.*?)"', 1, Message, typeof(string))), extract(@"ContainerId\s+([a-f\d-]+)", 1, EventMessage, typeof(string)),
//                                       (extract('ContainerID="(.*?)"', 1, EventMessage, typeof(string))))
// | extend ComputeBlackoutVmPhu =  toint(extract(@"\(BlackoutInMs (\d+)\)", 1, EventMessage))
// | extend ComputeBlackoutMMIO =  iff(EventId == 2120 , extract('TimespanMs="(.*?)"', 1, Message, typeof(int)),0)
// | where EventMessage !has "ASAP PF is associating an MSI-X entry" // exclude pf 1004 events
// | where EventMessage !has "ASAP Version Info - PF/NULL" //Filter eventID ==1004 WHERE PROVIDER WAS PF . We want KMS 1004
// | project PreciseTimeStamp, Cluster, DataCenter, Region, ContainerId, Provider = ProviderName, Pid, Tid, EventId, EventMessage, Level, ComputeBlackoutVmPhu, ComputeBlackoutMMIO
// | lookup kind=leftouter (
//     cluster("xaccel.kusto.windows.net").database("asapdb").GetAsapEventsExtended
//     ) on $left.EventId == $right.Id, Provider
// | where ContainerId == _ContainerId or EventId in (107,1004,1,2)
// | order by PreciseTimeStamp asc, Pid asc, Tid asc 
// );
//filteredEvents; //debug
let filteredEvents = materialize(GetAsapEventsOverlake2(_NodeId, _StartTime, _EndTime)
| extend json = parse_json(Message)
| extend ContainerId = tostring(json.ContainerId), PfVer = tostring(json.ProductVersion), Transition = tolong(json.Transition)
| where (Source == 'PF' and EventId in (1,2, 4237, 4244, 4243) ) 
        or (Source == 'UMED' and EventId in (2120, 3031, 3032)) // NO need to include duration event 2120, we need Start/End fr Cobe
        or (Source == 'UMED' and EventId in (22,23) and Transition in (1,3)
        or (Source == 'KMS' and EventId in (107, 1004) ))
| sort by PreciseTimeStamp asc 
| project PreciseTimeStamp, Source, PfVer, ContainerId, EventId, EventName, Transition, EventMessage = Message
// Post Fill Container ID events:
| scan declare (Container_: string="") with 
        (
            step s1: true => Container_ = iff(isempty(ContainerId), s1.Container_, ContainerId);
        )
| extend  ContainerId = Container_
| project-away Container_
);
let StartTimestamp107  = filteredEvents | where EventId == 107 | project PreciseTimeStamp; //the pre service hardware accel time is constant for all containers
//StartTimestamp107;
let EndTimestamp1004  = filteredEvents | where EventId == 1004 | project PreciseTimeStamp;//the post service hardware accel time is constant for all containers
let HardwareAccelerateEvents =
    materialize(filteredEvents
    | where EventId in (107,22) and EventMessage !contains ("Reason: 1") //and EventMessage contains " Transition: 3"
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize EndTimestamp = minif(PreciseTimeStamp, EventId == 22) by ContainerId
     | extend Phase = "Hardware Accelerate Mode PreService" ,
       StartTimestamp = toscalar(StartTimestamp107) // how to add PreciseTimeStamp of event 107
    )
    | where isnotempty( ContainerId)
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    | project ContainerId, StartTimestamp, EndTimestamp, Phase, Duration
);
// HardwareAccelerateEvents | as HardwareAcceleratePreService;
let ComputeBlackoutHardwareUnload =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 22), EndTimestamp = minif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Unload"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
);
//ComputeBlackoutHardwareUnload | as ComputeBlackoutHardwareUnload;
let StorageBrownoutEvents =
    materialize(filteredEvents
    | where EventId in (23,22) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 23), EndTimestamp = maxif(PreciseTimeStamp, EventId == 22) by ContainerId
    | extend Phase = "Storage Brownout"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
    //for every container we should have 4 events - 2 sets of (22,23)
 );
//StorageBrownoutEvents | as StorageBrownoutEvents;
let PfServiceEvents =
    materialize(filteredEvents
    | where EventId in (2,1) 
    | order by PreciseTimeStamp asc
    | summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 2), EndTimestamp = minif(PreciseTimeStamp, EventId == 1)
    | extend Phase = "Pf Unload Load Servicing"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
);
//PfServiceEvents | as PfServiceEvents;
let ComputeBlackoutHardwareLoad =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 22), EndTimestamp = maxif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Load"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
);
//ComputeBlackoutHardwareLoad | as ComputeBlackoutHardwareLoad;
let HardwareAccelerateReturnEvents =
    materialize(filteredEvents
    | where EventId in(23,1007,1004) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 23) by ContainerId
     | extend EndTimestamp = toscalar(EndTimestamp1004) // how to add PreciseTimeStamp of event 107, 
     | extend Phase = "Hardware Accelerate Mode PostService"
     | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
    | where isnotempty( ContainerId)
);
//HardwareAccelerateReturnEvents | as HardwareAcceleratePostService;
union HardwareAccelerateEvents,ComputeBlackoutHardwareUnload, StorageBrownoutEvents, ComputeBlackoutHardwareLoad, HardwareAccelerateReturnEvents, PfServiceEvents
| order by StartTimestamp asc
//Ignore ParentID for now.
| extend ParentId = case(Phase == "Pf Unload Load Servicing","Storage Brownout",
                         "")
| extend ContainerId = iff (isempty(ContainerId), "All Containers", ContainerId)
| extend Health = ""
| project ContainerId, EventId = Phase,  StartTime = StartTimestamp, EndTime = EndTimestamp,ParentId,
          Health = case(Phase contains "Hardware Accelerate", "Healthy", Phase contains "Blackout","Unhealthy",Phase contains "Brownout", "Degraded", "Neutral"),
          Tooltip = strcat(Phase, " : " , _ContainerId, " : ", "\nDuration = ", strcat(tostring(Duration), " Ms"))
```

**Params:** `{_NodeId}`, `{_EndTime}`, `{_ContainerId}`, `{_StartTime}`

---

### ADPA_BlackoutBrownout_Test

_Widget purpose:_ OVL 1.1 Node Events (ADPA servicing) (Scroll down for OVL2+)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Summary > OVL 1.1 Node Events (ADPA servicing) (Scroll down for OVL2+)`

```kusto
let filteredEvents = materialize(union AsapKmsEtwEventTable , AsapNvmeEtwEventTable,AsapPfEtwEventTable, AsapDpaEtwEventTable
| where NodeId == _NodeId and PreciseTimeStamp between (_StartTime .. _EndTime )
| where EventMessage !contains ("Reason: 1") and EventMessage !contains  "RequestMask: 1"
| where EventMessage !contains "ASAP Kernel-Mode Services DID receive bypass vhdmp handle for NSID 0" // because this is KMS 2118 event which we dont want
| where  EventId in (107,22,23,9,2118,2120,1,2,1004)  or (EventId == 1007 and (ProviderName contains "DPA" or ProviderName !contains "KMS")) 
| order by PreciseTimeStamp asc 
| extend ContainerId = coalesce( (extract('ContainerID="(.*?)"', 1, Message, typeof(string))), extract(@"ContainerId\s+([a-f\d-]+)", 1, EventMessage, typeof(string)),
                                      (extract('ContainerID="(.*?)"', 1, EventMessage, typeof(string))))
| extend ComputeBlackoutVmPhu =  toint(extract(@"\(BlackoutInMs (\d+)\)", 1, EventMessage))
| extend ComputeBlackoutMMIO =  iff(EventId == 2120 , extract('TimespanMs="(.*?)"', 1, Message, typeof(int)),0)
| where EventMessage !has "ASAP PF is associating an MSI-X entry" // exclude pf 1004 events
| where EventMessage !has "ASAP Version Info - PF/NULL" //Filter eventID ==1004 WHERE PROVIDER WAS PF . We want KMS 1004
| project PreciseTimeStamp, Cluster, DataCenter, Region, ContainerId, Provider = ProviderName, Pid, Tid, EventId, EventMessage, Level, ComputeBlackoutVmPhu, ComputeBlackoutMMIO
| lookup kind=leftouter (
    GetAsapEventsExtended
    ) on $left.EventId == $right.Id, Provider
| order by PreciseTimeStamp asc, Pid asc, Tid asc 
);
//filteredEvents; //debug
let StartTimestamp107  = filteredEvents | where EventId == 107 | project PreciseTimeStamp; 
//StartTimestamp107;
let EndTimestamp1004  = filteredEvents | where EventId == 1004 | project PreciseTimeStamp;
let HardwareAccelerateEvents =
    materialize(filteredEvents
    | where EventId in (107,22) and EventMessage !contains ("Reason: 1") //and EventMessage contains " Transition: 3"
    | order by PreciseTimeStamp asc
    //| extend StartTimestamp = iff(EventId == 107, PreciseTimeStamp, todatetime(0))
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize EndTimestamp = minif(PreciseTimeStamp, EventId == 22) by ContainerId
     | extend Phase = "Hardware Accelerate Mode PreService" ,
       StartTimestamp = toscalar(StartTimestamp107) // how to add PreciseTimeStamp of event 107
    )
    | where isnotempty( ContainerId)
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    | project ContainerId, StartTimestamp, EndTimestamp, Phase, Duration
);
// HardwareAccelerateEvents | as HardwareAcceleratePreService;
let ComputeBlackoutHardwareUnload =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 22), EndTimestamp = minif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Unload"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
);
//ComputeBlackoutHardwareUnload | as ComputeBlackoutHardwareUnload;
let StorageBrownoutEvents =
    materialize(filteredEvents
    | where EventId in (23,22) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 23), EndTimestamp = maxif(PreciseTimeStamp, EventId == 22) by ContainerId
    | extend Phase = "Storage Brownout"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
    //for every container we should have 4 events - 2 sets of (22,23)
 );
//StorageBrownoutEvents | as StorageBrownoutEvents;
let PfServiceEvents =
    materialize(filteredEvents
    | where EventId in (2,1) 
    | order by PreciseTimeStamp asc
    | summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 2), EndTimestamp = minif(PreciseTimeStamp, EventId == 1)
    | extend Phase = "Pf Unload Load Servicing"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
);
//PfServiceEvents | as PfServiceEvents;
let ComputeBlackoutHardwareLoad =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 22), EndTimestamp = maxif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Load"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
);
//ComputeBlackoutHardwareLoad | as ComputeBlackoutHardwareLoad;
let HardwareAccelerateReturnEvents =
    materialize(filteredEvents
    | where EventId in(23,1007,1004) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 23) by ContainerId
     | extend EndTimestamp = toscalar(EndTimestamp1004) // how to add PreciseTimeStamp of event 107, 
     | extend Phase = "Hardware Accelerate Mode PostService"
     | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
    | where isnotempty( ContainerId)
);
//HardwareAccelerateReturnEvents | as HardwareAcceleratePostService;
union HardwareAccelerateEvents,ComputeBlackoutHardwareUnload, StorageBrownoutEvents, ComputeBlackoutHardwareLoad, HardwareAccelerateReturnEvents, PfServiceEvents
| extend ContainerId = iff (isempty( ContainerId), "All_Containers_PF_Servicing",ContainerId) 
| project Content = Phase, StartTime = StartTimestamp, EndTime = EndTimestamp, GroupBy = ContainerId, ToolTip = strcat("DurationInMs = ",Duration)
| order by StartTime asc, EndTime asc
```

**Params:** `{_NodeId}`, `{_EndTime}`, `{_StartTime}`

---

### AdpaServicingEventsAllVMsOVL2

_Widget purpose:_ OVL 2+ Node Events  (ADPA servicing)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CoBeTimeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing > ADPA_Summary > OVL 2+ Node Events  (ADPA servicing)`

```kusto
let FilterAdpaServiceEvents = materialize(GetAsapEventsOverlake2(_NodeId, _startTime, _endTime)
| extend json = parse_json(Message)
| extend ContainerId = tostring(json.ContainerId), PfVer = tostring(json.ProductVersion), Transition = tolong(json.Transition)
| where (Source == 'PF' and EventId in (1,2, 4237, 4244, 4243) ) 
        or (Source == 'UMED' and EventId in (3031, 3032)) // NO need to include duration event 2120, we need Start/End fr Cobe
        or (Source == 'UMED' and EventId in (22,23) and Transition in (1,3))
| sort by PreciseTimeStamp asc 
| project PreciseTimeStamp, Source, PfVer, ContainerId, EventId, EventName, Transition, Message
// Post Fill Container ID events:
| scan declare (Container_: string="") with 
        (
            step s1: true => Container_ = iff(isempty(ContainerId), s1.Container_, ContainerId);
        )
| extend  ContainerId = Container_
| project-away Container_
);
//FilterAdpaServiceEvents;
//
// if given time span ha smultiple PF Changes? Talk to Stan to clarify possible gandling. Make sure choose transation of interest or only consider move forward not rollback from repave
// Now find unload and load timestamps for PF Change transaction so we can narrow search window for additional surrounding events
let MaxTimeAllowedtoUpdatePFMin = 2;
let ValidPfTransations = materialize(FilterAdpaServiceEvents
| sort by PreciseTimeStamp asc 
| extend nextEventId = next(EventId), nextEventTime = next(PreciseTimeStamp), nextPFVersion = next(PfVer)
| extend PfChangeTimeMin = totimespan(nextEventTime- PreciseTimeStamp)/time(1m)
| project PreciseTimeStamp, nextEventTime, PfVer, nextPFVersion, EventId, nextEventId, PfChangeTimeMin
| where ( isnotempty( PfVer) and PfVer != nextPFVersion) and (EventId == 2 and nextEventId == 1) and PfChangeTimeMin  < MaxTimeAllowedtoUpdatePFMin
// MAYBE HAVE USER OF ASI CHOOSE WHICH TRANSACTION THEY WISH TO TRACK. OR INCLUDE ONLY FORWARD PF UPGRADE NOT ROLLBACK. OR USER SHOULD REDUCE SEARCH SPAN IN ASI PER HIS TRANSACTION
//| where TransactionID = _trascationId or isempty(_trascationId)
);
//ValidPfTransations| as ValidPfTransations;
let PfUnloadTime = toscalar(ValidPfTransations | project PreciseTimeStamp);
let PfLoadTime = toscalar(ValidPfTransations| project nextEventTime);
// print strcat("PfUnloadTime" ,PfUnloadTime);
// //
// NOW USE the relevant PF unload/Load times to further narrow down time range in sub events. See below queries Condition
let CB1_MmioBlackoutsHwDeparting = materialize(FilterAdpaServiceEvents
    | where EventId in (22,23) and Transition == 3 and totimespan(PreciseTimeStamp - PfUnloadTime) / time(1m) < MaxTimeAllowedtoUpdatePFMin //<--------------- Condition
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 22  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 23) by ContainerId
        | extend Phase = "ComputeBlackoutMmioHardwareDepart",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Unhealthy"
        )
);
//CB1_MmioBlackoutsHwDeparting | as CB1_MmioBlackoutsHwDeparting;
//
let CB1_ControllerPaused = materialize(FilterAdpaServiceEvents
    | where EventId in (3031, 3032) 
    // note these PAUSE EVENTS HAPPEN EARLIER THAN PF UNLOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( abs(PfUnloadTime - PreciseTimeStamp)) / time(1m) < MaxTimeAllowedtoUpdatePFMin) 
      and PreciseTimeStamp < PfLoadTime // WE NEED EVENTS PRIOR TO PF LOAD SO WE CAN GET COMPUTE BLACKOUT 1 DATA WHEN HW IS DEPARTING
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 3031  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 3032) by ContainerId
        | extend Phase = "ComputeBlackout1ControllerPaused",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackoutMmioHardwareDepart", Health = "Neutral"
        )
);
//CB1_ControllerPaused | as CB1_ControllerPaused;
let NS_Detach = materialize(FilterAdpaServiceEvents
    | where EventId in (4237) 
    // note these PAUSE EVENTS HAPPEN EARLIER THAN PF UNLOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( abs(PfUnloadTime - PreciseTimeStamp)) / time(1m) < MaxTimeAllowedtoUpdatePFMin) 
      and PreciseTimeStamp < PfLoadTime // WE NEED EVENTS PRIOR TO PF LOAD SO WE CAN GET COMPUTE BLACKOUT 1 DATA WHEN HW IS DEPARTING
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 4237  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 4237) by ContainerId
        | extend Phase = "NS_Detach",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackout1ControllerPaused", Health = "Degraded"
        )
);
//NS_Detach | as NS_Detach;
//
let StorageBrownouts = materialize(FilterAdpaServiceEvents
    | where EventId in (22,23) and Transition in (3, 1) and totimespan(PreciseTimeStamp - PfLoadTime) / time(1m) < MaxTimeAllowedtoUpdatePFMin //<--------------- Condition
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 23 and Transition == 3  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 22 and Transition == 1) by ContainerId
        | extend Phase = "StorageBrownouts",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Degraded"
        )
);
//StorageBrownouts | as StorageBrownouts;
let PfUpdate = materialize(FilterAdpaServiceEvents
    | where EventId in (2,1)  and totimespan(PreciseTimeStamp - PfLoadTime) / time(1m) < MaxTimeAllowedtoUpdatePFMin //<--------------- Condition
    | extend ContainerId = "AllContainers"// PF CHANGE EVENTS PAYLOAD DONT CARRY CONTAINER IDs and this driver update impacts all VMs on the node
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 2  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 1) by ContainerId
        | extend Phase = "PfUpdate",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "StorageBrownouts", Health = "Neutral"
        )
);
//PfUpdate | as PfUpdate;
//
let CB2_MmioBlackoutsHwArriving = materialize(FilterAdpaServiceEvents
    | where EventId in (22,23) and Transition == 1 and totimespan(PreciseTimeStamp - PfLoadTime) / time(1m) < MaxTimeAllowedtoUpdatePFMin //<--------------- Condition
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 22  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 23) by ContainerId
        | extend Phase = "ComputeBlackoutMmioHardwareArrive",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Unhealthy"
        )
);
//CB2_MmioBlackoutsHwArriving | as CB2_MmioBlackoutsHwArriving;
let NS_Attach = materialize(FilterAdpaServiceEvents
    | where EventId in (4244, 4243) 
    // note these PAUSE EVENTS HAPPEN EARLIER THAN PF UNLOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( abs(PreciseTimeStamp - PfLoadTime)) / time(1m) < MaxTimeAllowedtoUpdatePFMin) 
      and PreciseTimeStamp > PfLoadTime // WE NEED EVENTS PRIOR TO PF LOAD SO WE CAN GET COMPUTE BLACKOUT 1 DATA WHEN HW IS DEPARTING
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = minif(PreciseTimeStamp, EventId in (4244, 4243)  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId in(4244, 4243)) by ContainerId
        | extend Phase = "NS_Attach",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackout2ControllerResume", Health = "Degraded"
        )
);
//NS_Attach | as NS_Attach;
let CB2_ControllerResume = materialize(FilterAdpaServiceEvents
    | where EventId in (3031, 3032) 
    // note these PAUSE EVENTS HAPPEN AFTER  PF LOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( abs(PfLoadTime - PreciseTimeStamp)) / time(1m) < MaxTimeAllowedtoUpdatePFMin) 
      and PreciseTimeStamp > PfUnloadTime // WE NEED EVENTS LATER THAN PF UNLOADED SO WE CAN GET COMPUTE BLACKOUT 2 DATA WHEN HW IS ARRIVES
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 3031  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 3032) by ContainerId
        | extend Phase = "ComputeBlackout2ControllerResume",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackoutMmioHardwareArrive", Health = "Neutral"
        )
);
//CB2_ControllerResume | as CB2_ControllerResume;
//CB2_MmioBlackoutsHwArriving | as CB2_MmioBlackoutsHwArriving;
//
// Form your Cobe Timeline Meatadata SCHEMA
let FinalDataset = union CB1_MmioBlackoutsHwDeparting, 
                            CB1_ControllerPaused, 
                                NS_Detach, 
                         StorageBrownouts, 
                            PfUpdate, 
                         CB2_ControllerResume, 
                            NS_Attach, 
                            CB2_MmioBlackoutsHwArriving
| extend Step = case( Phase == "ComputeBlackoutMmioHardwareDepart", 1, 
                      Phase == "ComputeBlackout1ControllerPaused", 2, 
                      Phase ==  "NS_Detach", 3,
                      Phase ==  "StorageBrownouts", 4,
                      Phase == "PfUpdate", 5,
                      Phase == "ComputeBlackout2ControllerResume", 6,
                      Phase == "NS_Attach", 7, 
                      Phase == "ComputeBlackoutMmioHardwareArrive",8, 
                      999
                      )
| project ContainerId, EventId = Phase, StartTime = StartTimestamp, EndTime = EndTimestamp, ParentId, Health, Step
| order by StartTime, EndTime asc;
FinalDataset;
```

**Params:** `{_startTime}`, `{_endTime}`, `{_NodeId}`

---

### DisplayContainersQuery

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Service_V2`

```kusto
let filteredEvents = materialize(union AsapKmsEtwEventTable , AsapNvmeEtwEventTable,AsapPfEtwEventTable, AsapDpaEtwEventTable
| where NodeId == _NodeId and PreciseTimeStamp between (_StartTime .. _EndTime )
| where EventMessage !contains ("Reason: 1") and EventMessage !contains  "RequestMask: 1"
| where EventMessage !contains "ASAP Kernel-Mode Services DID receive bypass vhdmp handle for NSID 0" // because this is KMS 2118 event which we dont want
| where  EventId in (107,22,23,9,2118,2120,1,2,1004)  or (EventId == 1007 and (ProviderName contains "DPA" or ProviderName !contains "KMS")) 
| order by PreciseTimeStamp asc 
| extend ContainerId = coalesce( (extract('ContainerID="(.*?)"', 1, Message, typeof(string))), extract(@"ContainerId\s+([a-f\d-]+)", 1, EventMessage, typeof(string)),
                                      (extract('ContainerID="(.*?)"', 1, EventMessage, typeof(string))))
| where EventMessage !has "ASAP PF is associating an MSI-X entry" // exclude pf 1004 events
| where EventMessage !has "ASAP Version Info - PF/NULL" //Filter eventID ==1004 WHERE PROVIDER WAS PF . We want KMS 1004
| project PreciseTimeStamp, Cluster, DataCenter, Region, ContainerId, Provider = ProviderName,EventId, EventMessage
| lookup kind=leftouter (
    GetAsapEventsExtended
    | project Id, Provider, EventName
    ) on $left.EventId == $right.Id, Provider
| order by PreciseTimeStamp asc
);
filteredEvents
| where isnotempty(ContainerId)
| distinct Cluster, DataCenter, Region, ContainerId, _NodeId; //debug
```

**Params:** `{_NodeId}`, `{_EndTime}`, `{_StartTime}`

---

### OshpServiceQueryPerContainer

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CoBeTimeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Service_V2`

```kusto
let filteredEvents = materialize(GetAsapEventsOverlake2(_NodeId, _StartTime, _EndTime)
| extend json = parse_json(Message)
| extend ContainerId = tostring(json.ContainerId), PfVer = tostring(json.ProductVersion), Transition = tolong(json.Transition)
| where (Source == 'PF' and EventId in (1,2, 4237, 4244, 4243) ) 
        or (Source == 'UMED' and EventId in (2118,2120, 3031, 3032)) // NO need to include duration event 2120, we need Start/End fr Cobe
        or (Source == 'UMED' and EventId in (22,23) and Transition in (1,3)
        or (Source == 'KMS' and EventId in (107, 1004) ))
| sort by PreciseTimeStamp asc 
| project PreciseTimeStamp, Source, PfVer, ContainerId, EventId, EventName, Transition, EventMessage = Message
// Post Fill Container ID events:
| scan declare (Container_: string="") with 
        (
            step s1: true => Container_ = iff(isempty(ContainerId), s1.Container_, ContainerId);
        )
| extend  ContainerId = Container_
| project-away Container_
);
let StartTimestamp107  = filteredEvents | where EventId == 107 | project PreciseTimeStamp; //the pre service hardware accel time is constant for all containers
let EndTimestamp1004  = filteredEvents | where EventId == 1004 and prev(EventId) in (2118,19001) | project PreciseTimeStamp;//the post service hardware accel time is constant for all containers
let HardwareAccelerateEvents =
    materialize(filteredEvents
    | where EventId in (107,22) and EventMessage !contains ("Reason: 1") //and EventMessage contains " Transition: 3"
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize EndTimestamp = minif(PreciseTimeStamp, EventId == 22) by ContainerId
     | extend Phase = "Hardware Accelerate Mode PreService" ,
       StartTimestamp = toscalar(StartTimestamp107) 
    )
    | where isnotempty( ContainerId)
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    | project ContainerId, StartTimestamp, EndTimestamp, Phase, Duration
);
//HardwareAccelerateEvents | as HardwareAcceleratePreService; //debug
let ComputeBlackoutHardwareUnload =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 22), EndTimestamp = minif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Unload"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
);
//ComputeBlackoutHardwareUnload | as ComputeBlackoutHardwareUnload; //debug
let StorageBrownoutEvents =
    materialize(filteredEvents
    | where EventId in (23,19000) 
    | order by PreciseTimeStamp asc
    | project PreciseTimeStamp,ContainerId, EventId, EventMessage
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 23), EndTimestamp = minif(PreciseTimeStamp, EventId == 19000) by ContainerId
    | extend Phase = "Storage Brownout"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
);
//StorageBrownoutEvents | as StorageBrownoutEvents; //debug
let ComputeBlackoutVmPhuService =
    materialize(filteredEvents
    | where EventId in (19000,19001)
    | order by  PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 19000), EndTimestamp = minif(PreciseTimeStamp, EventId == 19001) by ContainerId
        | extend Phase = "Compute Blackout VMPHU Servicing"
        | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
        )
);
//ComputeBlackoutVmPhuService | as ComputeBlackoutVmPhuService; //debug
let HardwareAccelerateReturnEvents =
    materialize(filteredEvents
    | where EventId in(19001,1004) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 19001) by ContainerId
     | extend EndTimestamp = toscalar(EndTimestamp1004) 
     | extend Phase = "Hardware Accelerate Mode PostService"
     | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
    | where isnotempty( ContainerId)
);
//HardwareAccelerateReturnEvents | as HardwareAcceleratePostService; //debug
union HardwareAccelerateEvents,ComputeBlackoutHardwareUnload, StorageBrownoutEvents, ComputeBlackoutVmPhuService, HardwareAccelerateReturnEvents
| order by StartTimestamp asc
| extend ContainerId = iff (isempty(ContainerId), "All Containers", ContainerId)
| extend Health = ""
| project ContainerId, EventId = Phase,  StartTime = StartTimestamp, EndTime = EndTimestamp,
          //Adding color codes using Health
          Health = case(Phase contains "Hardware Accelerate", "Healthy", Phase contains "Blackout","Unhealthy",Phase contains "Brownout", "Degraded", "Neutral"),
          Tooltip = strcat(Phase, " : " , _ContainerId, " : ", "\nDuration = ", strcat(tostring(Duration), " Ms"))
//Checking null conditions below 
 | extend to_display = case(isempty(StartTime) or isempty( EndTime)
                       or StartTime > EndTime, "false", "true")
```

**Params:** `{_NodeId}`, `{_EndTime}`, `{_StartTime}`, `{_ContainerId}`

---

### OSHP_MaxVM_ScenarioQuery

_Widget purpose:_ OVL 1.1 Node Events (OSHP servicing) (Scroll down for OVL2+)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Summary > OVL 1.1 Node Events (OSHP servicing) (Scroll down for OVL2+)`

```kusto
let  filteredEvents= materialize (union AsapKmsEtwEventTable , AsapNvmeEtwEventTable, cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVWorkerTable 
| where NodeId == _NodeId and PreciseTimeStamp between (_StartTime .. _EndTime )
| where EventId in (107,22,23,2118,2120,1004,19000,19001) and EventMessage !contains ("Reason: 1") 
| extend ContainerId = coalesce( (extract('ContainerID="(.*?)"', 1, Message, typeof(string))), extract(@"ContainerId\s+([a-f\d-]+)", 1, EventMessage, typeof(string)),
                                      (extract('ContainerID="(.*?)"', 1, EventMessage, typeof(string))), (extract('ContainerID="(.*?)"', 1, EventMessage, typeof(string)))
                               )
| extend ContainerId = iff(isempty(ContainerId),extract(@"\'(.*?)\'", 1, EventMessage), ContainerId)
| extend VfId = tostring(extract( @"\[VfId:(\d+)\]", 1, EventMessage))
| extend ComputeBlackoutVmPhu =  toint(extract(@"\(BlackoutInMs (\d+)\)", 1, EventMessage))
| extend ComputeBlackoutMMIO =  iff(EventId == 2120 , extract('TimespanMs="(.*?)"', 1, Message, typeof(int)),0)
//| where EventMessage !has "ASAP PF is associating an MSI-X entry" // exclude pf 1004 events
//| where EventMessage !has "ASAP Version Info - PF/NULL" //Filter eventID ==1004 WHERE PROVIDER WAS PF . We want KMS 1004
| project PreciseTimeStamp,Cluster, DataCenter, Region, ContainerId, VfId, Provider = ProviderName, Pid, Tid, EventId, EventMessage, Message,Level, ComputeBlackoutVmPhu, ComputeBlackoutMMIO
| lookup kind=leftouter (
    GetAsapEventsExtended
    ) on $left.EventId == $right.Id, Provider
| where EventMessage !contains "ASAP Kernel-Mode Services DID receive bypass vhdmp handle for NSID 0" // because this is KMS 2118 event which we dont want
| order by PreciseTimeStamp asc 
//| order by VfId asc, PreciseTimeStamp asc, Pid asc, Tid asc //debug
| project PreciseTimeStamp, ContainerId, EventId, VfId,EventMessage, EventName
);
//filteredEvents; //debug
let StartTimestamp107  = filteredEvents | where EventId == 107 | project PreciseTimeStamp; //the pre service hardware accel time is constant for all containers
//StartTimestamp107;
let EndTimestamp1004  = filteredEvents | where EventId == 1004 and prev(EventId) in (2118,19001) | project PreciseTimeStamp;//the post service hardware accel time is constant for all containers
let HardwareAccelerateEvents =
    materialize(filteredEvents
    | where EventId in (107,22) and EventMessage !contains ("Reason: 1") //and EventMessage contains " Transition: 3"
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize EndTimestamp = minif(PreciseTimeStamp, EventId == 22) by ContainerId
     | extend Phase = "Hardware Accelerate Mode PreService" ,
       StartTimestamp = toscalar(StartTimestamp107) 
    )
    | where isnotempty( ContainerId)
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    | project ContainerId, StartTimestamp, EndTimestamp, Phase, Duration
);
//HardwareAccelerateEvents | as HardwareAcceleratePreService; //debug
let ComputeBlackoutHardwareUnload =
    materialize(filteredEvents
    | where EventId in (22,2120,23) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 22), EndTimestamp = minif(PreciseTimeStamp, EventId == 23) by ContainerId
    | extend Phase = "Compute Blackout Hardware Unload"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
);
//ComputeBlackoutHardwareUnload | as ComputeBlackoutHardwareUnload; //debug
let StorageBrownoutEvents =
    materialize(filteredEvents
    | where EventId in (23,19000) 
    | order by PreciseTimeStamp asc
    | project PreciseTimeStamp,ContainerId, VfId, EventId, EventMessage
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 23), EndTimestamp = minif(PreciseTimeStamp, EventId == 19000) by ContainerId
    | extend Phase = "Storage Brownout"
    | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
);
//StorageBrownoutEvents | as StorageBrownoutEvents; //debug
let ComputeBlackoutVmPhuService =
    materialize(filteredEvents
    | where EventId in (19000,19001)
    | order by  PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 19000), EndTimestamp = minif(PreciseTimeStamp, EventId == 19001) by ContainerId
        | extend Phase = "Compute Blackout VMPHU Servicing"
        | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
        )
);
//ComputeBlackoutVmPhuService | as ComputeBlackoutVmPhuService; //debug
let HardwareAccelerateReturnEvents =
    materialize(filteredEvents
    | where EventId in(19001,1004) 
    | order by PreciseTimeStamp asc
    | partition hint.strategy=shuffle by ContainerId
    (
     summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 19001) by ContainerId
     | extend EndTimestamp = toscalar(EndTimestamp1004) 
     | extend Phase = "Hardware Accelerate Mode PostService"
     | extend Duration = totimespan(EndTimestamp-StartTimestamp)/time(1ms)
    )
    | where isnotempty( ContainerId)
);
//HardwareAccelerateReturnEvents | as HardwareAcceleratePostService; //debug
union HardwareAccelerateEvents,ComputeBlackoutHardwareUnload, StorageBrownoutEvents, ComputeBlackoutVmPhuService, HardwareAccelerateReturnEvents
//| extend display_order = case (Phase contains "Hardware Accelerate", 3, Phase contains "Compute Blackout" , 0 , Phase contains "Storage Brownout", 2, 1)
| project Content = Phase, StartTime = StartTimestamp, EndTime = EndTimestamp, GroupBy = ContainerId, ToolTip = strcat("DurationInMs = ",Duration)//, display_order
| order by StartTime asc, EndTime asc
```

**Params:** `{_NodeId}`, `{_EndTime}`, `{_StartTime}`

---

### OshpServicingEventsAllVMsOVL2

_Widget purpose:_ OVL 2+ Node Events (OSHP servicing)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CoBeTimeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Summary > OVL 2+ Node Events (OSHP servicing)`

```kusto
let FilterOshpServiceEvents = materialize(GetAsapEventsOverlake2(_NodeId, _startTime, _endTime)
| extend json = parse_json(Message)
| extend ContainerId = tostring(json.ContainerId), 
         PfVer = iff (Source == 'PF', tostring(json.ProductVersion), ""), 
         KmsVer = iff (Source == 'KMS', tostring(json.ProductVersion), ""), 
         Transition = tolong(json.Transition)
| where (Source == 'PF' and EventId in (4237, 4244, 4243) ) 
        or (Source == 'KMS' and EventId  in (6,5) )
        or (Source == 'UMED' and EventId in (5,6, 2118, 3031, 3032))
        or (Source == 'UMED' and EventId in (22,23) and Transition in (1,3))
| sort by PreciseTimeStamp asc 
| project PreciseTimeStamp, Source, PfVer, KmsVer, ContainerId, EventId, EventName, Transition, Message
// Post Fill Container ID events:
| scan declare (Container_: string="") with 
        (
            step s1: true => Container_ = iff(isempty(ContainerId), s1.Container_, ContainerId);
        )
| extend  ContainerId = Container_
| project-away Container_
);
//FilterOshpServiceEvents;
//
// if given time span ha smultiple KMS Changes? Talk to Stan to clarify possible handling. Make sure choose transation of interest or only consider move forward not rollback from repave
// Now find unload and load timestamps for PF Change transaction so we can narrow search window for additional surrounding events
let MaxTimeAllowedtoUpdateKMSMin = 2;
let ValidKmsTransations = materialize(FilterOshpServiceEvents
| sort by PreciseTimeStamp asc 
| extend nextEventId = next(EventId), nextEventTime = next(PreciseTimeStamp), nextKMSVersion = next(KmsVer)
| extend KmsChangeTimeMin = totimespan(nextEventTime- PreciseTimeStamp)/time(1m)
| project PreciseTimeStamp, nextEventTime, KmsVer, nextKMSVersion, EventId, nextEventId, KmsChangeTimeMin
| where ( isnotempty(KmsVer) and KmsVer != nextKMSVersion) and (EventId == 6 and nextEventId == 5) and KmsChangeTimeMin  < MaxTimeAllowedtoUpdateKMSMin
// MAYBE HAVE USER OF ASI CHOOSE WHICH TRANSACTION THEY WISH TO TRACK. OR INCLUDE ONLY FORWARD PF UPGRADE NOT ROLLBACK. OR USER SHOULD REDUCE SEARCH SPAN IN ASI PER HIS TRANSACTION
//| where TransactionID = _trascationId or isempty(_trascationId)
);
//ValidKmsTransations| as ValidKmsTransations;
let KmsUnloadTime = toscalar(ValidKmsTransations | project PreciseTimeStamp);
let KmsLoadTime = toscalar(ValidKmsTransations| project nextEventTime);
// print strcat("KmsUnloadTime" ,KmsUnloadTime);
// 
// NOW USE the relevant PF unload/Load times to further narrow down time range in sub events. See below queries Condition
let CB1_MmioBlackoutsHwDeparting = materialize(FilterOshpServiceEvents
    | where EventId in (22,23) and Transition == 3 and abs(totimespan(PreciseTimeStamp - KmsUnloadTime)) / time(1m) < MaxTimeAllowedtoUpdateKMSMin //<--------------- Condition
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 22  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 23) by ContainerId
        | extend Phase = "ComputeBlackoutMmioHardwareDepart",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Unhealthy"
        )
);
//CB1_MmioBlackoutsHwDeparting | as CB1_MmioBlackoutsHwDeparting;
//
let CB1_ControllerPaused = materialize(FilterOshpServiceEvents
    | sort by PreciseTimeStamp  asc
    | where EventId in (4237, 3031, 3032) 
    // note these PAUSE EVENTS HAPPEN EARLIER THAN PF UNLOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( (KmsUnloadTime - PreciseTimeStamp)) / time(1m) < MaxTimeAllowedtoUpdateKMSMin) 
      and PreciseTimeStamp < KmsLoadTime 
    | where (EventId == 3031 and next(EventId) == 4237) or (EventId == 3032 and prev(EventId) in (4237) )
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 3031  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 3032) by ContainerId
        | extend Phase = "ComputeBlackout1ControllerPaused",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackoutMmioHardwareDepart", Health = "Neutral"
        )
);
//CB1_ControllerPaused | as CB1_ControllerPaused;
//
let NS_Detach = materialize(FilterOshpServiceEvents
    | where EventId in (4237) 
    // note these PAUSE EVENTS HAPPEN EARLIER THAN PF UNLOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( abs(KmsUnloadTime - PreciseTimeStamp)) / time(1m) < MaxTimeAllowedtoUpdateKMSMin) 
      and PreciseTimeStamp < KmsLoadTime // WE NEED EVENTS PRIOR TO PF LOAD SO WE CAN GET COMPUTE BLACKOUT 1 DATA WHEN HW IS DEPARTING
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 4237  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 4237) by ContainerId
        | extend Phase = "NS_Detach",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackout1ControllerPaused", Health = "Degraded"
        )
);
//NS_Detach | as NS_Detach;
//
let StorageBrownouts = materialize(FilterOshpServiceEvents
    | where ((EventId == 23 and Transition == 3) or (Source == 'UMED' and EventId == 5))  and totimespan(PreciseTimeStamp - KmsLoadTime) / time(1m) < MaxTimeAllowedtoUpdateKMSMin //<--------------- Condition
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 23),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 5) by ContainerId
        | extend Phase = "StorageBrownouts",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Degraded"
        )
);
//StorageBrownouts | as StorageBrownouts;
//
let VmphuBlackouts = materialize(FilterOshpServiceEvents
    | where (Source == 'UMED' and EventId in (5,6))  and totimespan(PreciseTimeStamp - KmsLoadTime) / time(1m) < MaxTimeAllowedtoUpdateKMSMin //<--------------- Condition
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 5),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 6) by ContainerId
        | extend Phase = "VmphuBlackouts",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Unhealthy"
        )
);
//VmphuBlackouts | as VmphuBlackouts;
let KmsUpdate = materialize(FilterOshpServiceEvents
    | where (Source == 'KMS' and EventId in (6,5))  and totimespan(PreciseTimeStamp - KmsLoadTime) / time(1m) < MaxTimeAllowedtoUpdateKMSMin //<--------------- Condition
    | extend ContainerId = "AllContainers"// PF CHANGE EVENTS PAYLOAD DONT CARRY CONTAINER IDs and this driver update impacts all VMs on the node
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 6  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 5) by ContainerId
        | extend Phase = "KmsUpdate",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "VmphuBlackouts", Health = "Neutral"
        )
);
//KmsUpdate | as KmsUpdate;
//
let CB2_ControllerResume = materialize(FilterOshpServiceEvents
    | sort by PreciseTimeStamp asc
    | where EventId in (4244, 4243, 3031, 3032) 
    // note these PAUSE EVENTS HAPPEN AFTER  PF LOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( abs(KmsLoadTime - PreciseTimeStamp)) / time(1m) < MaxTimeAllowedtoUpdateKMSMin) 
      and PreciseTimeStamp > KmsUnloadTime 
    | where (EventId == 3031 and next(EventId) in (4244, 4243) ) or (EventId == 3032 and prev(EventId) in (4244, 4243) )
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 3031  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 3032) by ContainerId
        | extend Phase = "ComputeBlackout2ControllerResume",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackoutMmioHardwareArrive", Health = "Neutral"
        )
);
//CB2_ControllerResume | as CB2_ControllerResume;
//
let CB2_MmioBlackoutsHwArriving = materialize(FilterOshpServiceEvents
    | where ( (Source == 'UMED' and EventId in (6)) or (EventId == 2118) ) 
              and totimespan(PreciseTimeStamp - KmsLoadTime) / time(1m) < MaxTimeAllowedtoUpdateKMSMin //<--------------- Condition: HW Arrive happens KMS Loaded.
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 6  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 2118) by ContainerId
        | extend Phase = "ComputeBlackoutMmioHardwareArrive",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Unhealthy"
        )
);
//CB2_MmioBlackoutsHwArriving | as CB2_MmioBlackoutsHwArriving;
//
let NS_Attach = materialize(FilterOshpServiceEvents
    | where EventId in (4244, 4243) 
    // note these PAUSE EVENTS HAPPEN EARLIER THAN PF UNLOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( abs(PreciseTimeStamp - KmsLoadTime)) / time(1m) < MaxTimeAllowedtoUpdateKMSMin) 
      and PreciseTimeStamp > KmsLoadTime // WE NEED EVENTS PRIOR TO PF LOAD SO WE CAN GET COMPUTE BLACKOUT 1 DATA WHEN HW IS DEPARTING
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = minif(PreciseTimeStamp, EventId in (4244, 4243)  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId in(4244, 4243)) by ContainerId
        | extend Phase = "NS_Attach",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackout2ControllerResume", Health = "Degraded"
        )
);
//NS_Attach | as NS_Attach;
union CB1_MmioBlackoutsHwDeparting, 
      CB1_ControllerPaused, 
      NS_Detach,
      StorageBrownouts, 
      VmphuBlackouts, 
      KmsUpdate,
      CB2_ControllerResume, 
      NS_Attach,
      CB2_MmioBlackoutsHwArriving
| extend Step = case( Phase == "ComputeBlackoutMmioHardwareDepart", 1, 
                      Phase == "ComputeBlackout1ControllerPaused", 2, 
                      Phase ==  "NS_Detach", 3,
                      Phase ==  "StorageBrownouts", 4,
                      Phase == "VmphuBlackouts", 5,
                      Phase == "KmsUpdate", 6,
                      Phase == "ComputeBlackout2ControllerResume", 7,
                      Phase == "NS_Attach", 8, 
                      Phase == "ComputeBlackoutMmioHardwareArrive",9, 
                      999
                      )
| project ContainerId, EventId = Phase, StartTime = StartTimestamp, EndTime = EndTimestamp, ParentId, Health, Step,  ToolTip = strcat("DurationInMs = ", Duration)
| order by StartTime, EndTime asc;
```

**Params:** `{_startTime}`, `{_endTime}`, `{_NodeId}`

---

### OshpServicingEventsAllVMsOVL2V2

_Widget purpose:_ OVL2+ Node Events (OSHP Servicing) View 2:

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `StorageClient Tables > ASAP > ASAP > Servicing > OSHP_Summary > OVL2+ Node Events (OSHP Servicing) View 2:`

```kusto
let FilterOshpServiceEvents = materialize(GetAsapEventsOverlake2(_NodeId, _startTime, _endTime)
| extend json = parse_json(Message)
| extend ContainerId = tostring(json.ContainerId), 
         PfVer = iff (Source == 'PF', tostring(json.ProductVersion), ""), 
         KmsVer = iff (Source == 'KMS', tostring(json.ProductVersion), ""), 
         Transition = tolong(json.Transition)
| where (Source == 'PF' and EventId in (4237, 4244, 4243) ) 
        or (Source == 'KMS' and EventId  in (6,5) )
        or (Source == 'UMED' and EventId in (5,6, 2118, 3031, 3032))
        or (Source == 'UMED' and EventId in (22,23) and Transition in (1,3))
| sort by PreciseTimeStamp asc 
| project PreciseTimeStamp, Source, PfVer, KmsVer, ContainerId, EventId, EventName, Transition, Message
// Post Fill Container ID events:
| scan declare (Container_: string="") with 
        (
            step s1: true => Container_ = iff(isempty(ContainerId), s1.Container_, ContainerId);
        )
| extend  ContainerId = Container_
| project-away Container_
);
//FilterOshpServiceEvents;
//
// if given time span ha smultiple KMS Changes? Talk to Stan to clarify possible handling. Make sure choose transation of interest or only consider move forward not rollback from repave
// Now find unload and load timestamps for PF Change transaction so we can narrow search window for additional surrounding events
let MaxTimeAllowedtoUpdateKMSMin = 2;
let ValidKmsTransations = materialize(FilterOshpServiceEvents
| sort by PreciseTimeStamp asc 
| extend nextEventId = next(EventId), nextEventTime = next(PreciseTimeStamp), nextKMSVersion = next(KmsVer)
| extend KmsChangeTimeMin = totimespan(nextEventTime- PreciseTimeStamp)/time(1m)
| project PreciseTimeStamp, nextEventTime, KmsVer, nextKMSVersion, EventId, nextEventId, KmsChangeTimeMin
| where ( isnotempty(KmsVer) and KmsVer != nextKMSVersion) and (EventId == 6 and nextEventId == 5) and KmsChangeTimeMin  < MaxTimeAllowedtoUpdateKMSMin
// MAYBE HAVE USER OF ASI CHOOSE WHICH TRANSACTION THEY WISH TO TRACK. OR INCLUDE ONLY FORWARD PF UPGRADE NOT ROLLBACK. OR USER SHOULD REDUCE SEARCH SPAN IN ASI PER HIS TRANSACTION
//| where TransactionID = _trascationId or isempty(_trascationId)
);
//ValidKmsTransations| as ValidKmsTransations;
let KmsUnloadTime = toscalar(ValidKmsTransations | project PreciseTimeStamp);
let KmsLoadTime = toscalar(ValidKmsTransations| project nextEventTime);
// print strcat("KmsUnloadTime" ,KmsUnloadTime);
// 
// NOW USE the relevant PF unload/Load times to further narrow down time range in sub events. See below queries Condition
let CB1_MmioBlackoutsHwDeparting = materialize(FilterOshpServiceEvents
    | where EventId in (22,23) and Transition == 3 and abs(totimespan(PreciseTimeStamp - KmsUnloadTime)) / time(1m) < MaxTimeAllowedtoUpdateKMSMin //<--------------- Condition
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 22  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 23) by ContainerId
        | extend Phase = "ComputeBlackoutMmioHardwareDepart",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Unhealthy"
        )
);
//CB1_MmioBlackoutsHwDeparting | as CB1_MmioBlackoutsHwDeparting;
//
let CB1_ControllerPaused = materialize(FilterOshpServiceEvents
    | sort by PreciseTimeStamp  asc
    | where EventId in (4237, 3031, 3032) 
    // note these PAUSE EVENTS HAPPEN EARLIER THAN PF UNLOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( (KmsUnloadTime - PreciseTimeStamp)) / time(1m) < MaxTimeAllowedtoUpdateKMSMin) 
      and PreciseTimeStamp < KmsLoadTime 
    | where (EventId == 3031 and next(EventId) == 4237) or (EventId == 3032 and prev(EventId) in (4237) )
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 3031  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 3032) by ContainerId
        | extend Phase = "ComputeBlackout1ControllerPaused",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackoutMmioHardwareDepart", Health = "Neutral"
        )
);
//CB1_ControllerPaused | as CB1_ControllerPaused;
//
let NS_Detach = materialize(FilterOshpServiceEvents
    | where EventId in (4237) 
    // note these PAUSE EVENTS HAPPEN EARLIER THAN PF UNLOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( abs(KmsUnloadTime - PreciseTimeStamp)) / time(1m) < MaxTimeAllowedtoUpdateKMSMin) 
      and PreciseTimeStamp < KmsLoadTime // WE NEED EVENTS PRIOR TO PF LOAD SO WE CAN GET COMPUTE BLACKOUT 1 DATA WHEN HW IS DEPARTING
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = minif(PreciseTimeStamp, EventId == 4237  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 4237) by ContainerId
        | extend Phase = "NS_Detach",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackout1ControllerPaused", Health = "Degraded"
        )
);
//NS_Detach | as NS_Detach;
//
let StorageBrownouts = materialize(FilterOshpServiceEvents
    | where ((EventId == 23 and Transition == 3) or (Source == 'UMED' and EventId == 5))  and totimespan(PreciseTimeStamp - KmsLoadTime) / time(1m) < MaxTimeAllowedtoUpdateKMSMin //<--------------- Condition
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 23),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 5) by ContainerId
        | extend Phase = "StorageBrownouts",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Degraded"
        )
);
//StorageBrownouts | as StorageBrownouts;
//
let VmphuBlackouts = materialize(FilterOshpServiceEvents
    | where (Source == 'UMED' and EventId in (5,6))  and totimespan(PreciseTimeStamp - KmsLoadTime) / time(1m) < MaxTimeAllowedtoUpdateKMSMin //<--------------- Condition
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 5),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 6) by ContainerId
        | extend Phase = "VmphuBlackouts",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Unhealthy"
        )
);
//VmphuBlackouts | as VmphuBlackouts;
let KmsUpdate = materialize(FilterOshpServiceEvents
    | where (Source == 'KMS' and EventId in (6,5))  and totimespan(PreciseTimeStamp - KmsLoadTime) / time(1m) < MaxTimeAllowedtoUpdateKMSMin //<--------------- Condition
    | extend ContainerId = "AllContainers"// PF CHANGE EVENTS PAYLOAD DONT CARRY CONTAINER IDs and this driver update impacts all VMs on the node
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 6  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 5) by ContainerId
        | extend Phase = "KmsUpdate",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "VmphuBlackouts", Health = "Neutral"
        )
);
//KmsUpdate | as KmsUpdate;
//
let CB2_ControllerResume = materialize(FilterOshpServiceEvents
    | sort by PreciseTimeStamp asc
    | where EventId in (4244, 4243, 3031, 3032) 
    // note these PAUSE EVENTS HAPPEN AFTER  PF LOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( abs(KmsLoadTime - PreciseTimeStamp)) / time(1m) < MaxTimeAllowedtoUpdateKMSMin) 
      and PreciseTimeStamp > KmsUnloadTime 
    | where (EventId == 3031 and next(EventId) in (4244, 4243) ) or (EventId == 3032 and prev(EventId) in (4244, 4243) )
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 3031  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 3032) by ContainerId
        | extend Phase = "ComputeBlackout2ControllerResume",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackoutMmioHardwareArrive", Health = "Neutral"
        )
);
//CB2_ControllerResume | as CB2_ControllerResume;
//
let CB2_MmioBlackoutsHwArriving = materialize(FilterOshpServiceEvents
    | where ( (Source == 'UMED' and EventId in (6)) or (EventId == 2118) ) 
              and totimespan(PreciseTimeStamp - KmsLoadTime) / time(1m) < MaxTimeAllowedtoUpdateKMSMin //<--------------- Condition: HW Arrive happens KMS Loaded.
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = maxif(PreciseTimeStamp, EventId == 6  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId == 2118) by ContainerId
        | extend Phase = "ComputeBlackoutMmioHardwareArrive",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "", Health = "Unhealthy"
        )
);
//CB2_MmioBlackoutsHwArriving | as CB2_MmioBlackoutsHwArriving;
//
let NS_Attach = materialize(FilterOshpServiceEvents
    | where EventId in (4244, 4243) 
    // note these PAUSE EVENTS HAPPEN EARLIER THAN PF UNLOADS, This is IMP so the below timespan is NON NEGATIVE. USE ABS() or use correct order 
      and (totimespan( abs(PreciseTimeStamp - KmsLoadTime)) / time(1m) < MaxTimeAllowedtoUpdateKMSMin) 
      and PreciseTimeStamp > KmsLoadTime // WE NEED EVENTS PRIOR TO PF LOAD SO WE CAN GET COMPUTE BLACKOUT 1 DATA WHEN HW IS DEPARTING
    | partition hint.strategy=shuffle by ContainerId
        (
         summarize StartTimestamp = minif(PreciseTimeStamp, EventId in (4244, 4243)  ),
                   EndTimestamp = maxif(PreciseTimeStamp,EventId in(4244, 4243)) by ContainerId
        | extend Phase = "NS_Attach",
                 Duration = round(totimespan(EndTimestamp-StartTimestamp)/time(1ms),2),
                 ParentId = "ComputeBlackout2ControllerResume", Health = "Degraded"
        )
);
//NS_Attach | as NS_Attach;
union CB1_MmioBlackoutsHwDeparting, 
      CB1_ControllerPaused, 
      NS_Detach,
      StorageBrownouts, 
      VmphuBlackouts, 
      KmsUpdate,
      CB2_ControllerResume, 
      NS_Attach,
      CB2_MmioBlackoutsHwArriving
| extend Step = case( Phase == "ComputeBlackoutMmioHardwareDepart", 1, 
                      Phase == "ComputeBlackout1ControllerPaused", 2, 
                      Phase ==  "NS_Detach", 3,
                      Phase ==  "StorageBrownouts", 4,
                      Phase == "VmphuBlackouts", 5,
                      Phase == "KmsUpdate", 6,
                      Phase == "ComputeBlackout2ControllerResume", 7,
                      Phase == "NS_Attach", 8, 
                      Phase == "ComputeBlackoutMmioHardwareArrive",9, 
                      999
                      )
| project GroupBy = ContainerId, Content = Phase, StartTime = StartTimestamp, EndTime = EndTimestamp, ParentId, Health, Step, ToolTip = strcat("DurationInMs = ", Duration) // GroupBy = ContainerId, ToolTip = strcat("DurationInMs = ",Duration)//, display_order
| order by StartTime, EndTime asc;
```

**Params:** `{_startTime}`, `{_endTime}`, `{_NodeId}`

---
