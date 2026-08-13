# VM Counters — ASAP (OVL 2.0+)

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Counters** (35 queries, part 2 of 7).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## ASAP (OVL 2.0+)

### GetASAPNSIndicesGlobalKQL

_Widget purpose:_ ASAP (OVL 2.0+)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Tab`
Source panel: `VM Counters > ASAP (OVL 2.0+)`

**Tables:** `AsapMapVmToDiskOVL2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(nodeId, containerId, queryFrom, queryTo) | sort by NsIndex | distinct Value = tostring(NsIndex);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`

---

### AsapContainerFOStatsAllDisks_GlobalKQL

_Widget purpose:_ ASAP (OVL 2.0+)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Tab`
Source panel: `VM Counters > ASAP (OVL 2.0+)`

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
AsapContainerFOStatsAsapPf(nodeId, containerId, queryFrom, queryTo, _nsIndex=_NsIndex) 
    //
    | project VfId, PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs, MaxWriteLatencyMs ,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs,
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs, 
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              VfId,
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

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`, `{_NsIndex}`

---

### asapFOStats_FOPercentsQuery_asapPF

_Widget purpose:_ %FO of Total IO: Per VM, FO Disks only i.e UseSwpe = 0

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > %FO of Total IO: Per VM, FO Disks only i.e UseSwpe = 0`

**Tables:** `AsapPfEtwTraceLogEventViewExtended`
**Aggregations:** `summarize TotalIO = sum(TotalCompletedIO), TotalFOIO = sum(FOCompletedIO), TotalPOIO = sum` · `summarize AVG_FOPercent = round(avg(PercentOfFOCompletedIO),2) by bin(PreciseTimeStamp, st`
**Output columns:** `PreciseTimeStamp`, `AVG_FOPercent`

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
//
// Scaffold time series to enforce fixed 5m bins
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
let AsapVmToVFMapping = AsapMapVmToDiskOVL2(nodeId, _containerId, queryFrom, queryTo) | distinct VfId;
//AsapVmToVFMapping | as AsapVmToVFMapping; // DEBUG
//
AsapPfEtwTraceLogEventViewExtended
    | where PreciseTimeStamp between (queryFrom .. queryTo ) and NodeId  == nodeId and EventId == 1265
    | project Cluster, NodeId, containerId, PreciseTimeStamp, EventId, EventName, Message
    | extend json = parse_json(Message)
    | extend UseSwpe = toint(json.UseSwpe), VfId = tolong(json.VfId),  NsId = toint(json.NsId), NsIndex = toint(json.NsIndex),
             NamespaceType = toint(json.NamespaceType), CachePolicy = toint(json.CachePolicy), 
             TotalCompletedIO = todouble(json.TotalCompletedIO), 
             FOCompletedIO = todouble(json.FOCompletedIO),
             POCompletedIO = todouble(json.POCompletedIO),
             POCompletedReadIO = todouble(json.POCompletedReadIO),
             POCompletedWriteIO = todouble(json.POCompletedWriteIO)
    // APPL MAP CONTAINER TO VF ID Logic to pull data from correct VM we intended
    | where VfId in (AsapVmToVFMapping) or containerId == _containerId
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
                by Cluster, NodeId, VfId, bin(PreciseTimeStamp, stepSize)
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
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{_containerId}`

---

### MinLatencyFloorDelaysPV2VMQuery

_Widget purpose:_ Avg & Max New Min Latency floor delays PV2: (Unit is in terms of FPGA cycles, MaxDeltaCycles = NewMinLatencyFloor - CurrentMinLatencyFloor)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Avg & Max New Min Latency floor delays PV2: (Unit is in terms of FPGA cycles, MaxDeltaCycles = NewMinLatencyFloor - CurrentMinLatencyFloor)`

**Tables:** `AsapPfEtwTraceLogEventViewExtended`
**Aggregations:** `summarize MaxNewMinLatFloorDelayCycles = max(NewMinLatencyFloorDelay), // Worst-case appli`

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
let _getVFNSInfo = AsapMapVmToDiskOVL2(_nodeId, _containerId, queryFrom, queryTo) ;
//
AsapPfEtwTraceLogEventViewExtended
| where PreciseTimeStamp between (queryFrom .. queryTo) and EventId == 7118
        and  NodeId == _nodeId 
        and (
                (containerId == _containerId) // container match found (this field available 6.91+ PF)
                or (NsIndex in (_getVFNSInfo | distinct NsIndex)) // if older PF < 6.91, match via NSIndex
            )
// APPLY NSINDEX FILTERS TO FILTER ON SPECIFIC NAMESPACE
| where NsIndex == _NsIndex or _NsIndex == ""
| project PreciseTimeStamp, NodeId, EventId, EventName, json
//
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
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_nodeId}`, `{_containerId}`, `{_NsIndex}`

---

### GetNsIndicesForContainer

_Widget purpose:_ Avg & Max New Min Latency floor delays PV2: (Unit is in terms of FPGA cycles, MaxDeltaCycles = NewMinLatencyFloor - CurrentMinLatencyFloor)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Avg & Max New Min Latency floor delays PV2: (Unit is in terms of FPGA cycles, MaxDeltaCycles = NewMinLatencyFloor - CurrentMinLatencyFloor)`

**Tables:** `AsapMapVmToDiskOVL2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(nodeId, containerId, queryFrom, queryTo) | sort by NsIndex | distinct Value = tostring(NsIndex);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### ExceptionsCountQuery_PerVM

_Widget purpose:_ Counts of Exceptions Per VM:

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CategoryChart`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Counts of Exceptions Per VM:`

**Tables:** `Asap_FOExceptions_HttpTranscodeTable`, `AsapPfEtwTraceLogEventViewExtended`
**Aggregations:** `summarize count_ = count() by SubCode //, bin(PreciseTimeStamp, stepSize)`
**Output columns:** `SubCode`, `count_`

```kusto
let _getNsIndicesForContainer = AsapMapVmToDiskOVL2(nodeId, _containerId, queryFrom, queryTo) | distinct NsIndex;
// _getNsIndicesForContainer | as _getNsIndicesForContainer;
let hasNs = toscalar(_getNsIndicesForContainer | count);
//
// IMPORTANT! Please note : We dont expect to see same NODE_NSINDEX unique pair at same given time. 
// So as long as we query one node and one container, we only have unique NSIndex expected so this should work
//
// IMPORTANT! Please also note: Only some exception events carry NSindex (Event 6028, 6029, 6031) in their payload but others (such as 6016,6048) don't. Filing bug for these
// This also means DRIs should note that if we are seeing X,Y,Z exceptions on node level but in VM level we see only X, its likely that Y,Z events dont have NS/VF info 
// which is why they are missed.
// 
AsapPfEtwTraceLogEventViewExtended
| where NodeId == nodeId and PreciseTimeStamp between (queryFrom .. queryTo ) 
        and (EventId between (6000..6500) or EventId == 6504)
        and (
                containerId == _containerId 
                or (hasNs > 0 and NsIndex in (_getNsIndicesForContainer))
            ) // <---- Lookup exceptions for Namespaces associated w your Container
//
// Extend helper columns
| extend Code = tostring(json.HttpSubCode), PfVer = tostring(json.ProductVersion), 
         dd_fo_throttle = tolong(json.dd_fo_throttle),
         dd_report_error = coalesce( tolong(json.DD_Report_Error), tolong(json.dd_report_error))
| project  PreciseTimeStamp, containerId, VfId, NsId, NsIndex, EventId, EventName, Code, dd_fo_throttle, dd_report_error, Message, json
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
| summarize count_ = count() by SubCode //, bin(PreciseTimeStamp, stepSize)
| order by count_ 
| project  SubCode, count_
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{_containerId}`

---

### GetNsIndicesForContainer

_Widget purpose:_ DD Backend Latency in Ms (Works for 6.91+ PF Versions Only)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > DD Backend Latency in Ms (Works for 6.91+ PF Versions Only)`

**Tables:** `AsapMapVmToDiskOVL2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(nodeId, containerId, queryFrom, queryTo) | sort by NsIndex | distinct Value = tostring(NsIndex);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### ASAP_DD_Backend_Latency_Query

_Widget purpose:_ DD Backend Latency in Ms (Works for 6.91+ PF Versions Only)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > DD Backend Latency in Ms (Works for 6.91+ PF Versions Only)`

**Tables:** `DdxTargetPerfRequest`, `AsapPfEtwTraceLogEventViewExtendedDD`
**Aggregations:** `summarize //SlowIoCount = count(), AvgTotalTimeMs = round(avg(TotalTimeMs), 2), MaxTotalTi by bin(PreciseTimeStamp, stepSize)`

```kusto
// Adaptive time bin — finer granularity for shorter windows
let duration = queryTo - queryFrom;
let stepSize = case(
    duration < 24h, 30s,    // <1 day:  30-second bins for precise debugging
    duration < 3d,  5m,     // 1-3 days: 5-minute bins
    duration < 7d,  15m,    // 3-7 days: 15-minute bins
    duration < 14d, 30m,    // 1-2 weeks: 30-minute bins
    duration < 30d, 1h,     // 2-4 weeks: hourly bins
    3h                      // 30-60 days: 3-hour summary
);
// Time scaffold — ensures continuous time series with no gaps
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
// Resolve VF IDs for the target container
let _vmVfIds = AsapMapVmToDiskOVL2(nodeId, _containerId, queryFrom, queryTo)
    | distinct VfId;
// Map VF IDs → DD VirtualDiskIDs via PF EventId 75 (namespace mapping)
let DiskIdList = materialize(
    AsapPfEtwTraceLogEventViewExtendedDD
    | where PreciseTimeStamp between (queryFrom .. queryTo)
        and NodeId == nodeId
        and EventId == 75
    | where VfId in (_vmVfIds) or containerId contains _containerId
    | where _NsIndex == "" or NsIndex == _NsIndex
    | distinct VirtualDiskID = tostring(json.VirtualDiskID)
);
// Query DD backend slow IO, decompose latency, join with scaffold
cluster('xdataplane.kusto.windows.net').database('DirectDrive').DdxTargetPerfRequest
| where PreciseTimeStamp between (queryFrom .. queryTo)
    and DiskId in (DiskIdList)
    and SlowIo == "1"
| extend
    TotalTimeMs = TotalTimeIn100NsUnits / 10000.0,
    GetOutDataTimeMs = GetOutDataTimeIn100NsUnits / 10000.0,
    StorageTimeMs = (TotalTimeIn100NsUnits - GetOutDataTimeIn100NsUnits) / 10000.0
| summarize
    //SlowIoCount = count(),
    AvgTotalTimeMs = round(avg(TotalTimeMs), 2),
    MaxTotalTimeMs = round(max(TotalTimeMs), 2),
    AvgGetOutDataTimeMs = round(avg(GetOutDataTimeMs), 2),
    MaxGetOutDataTimeMs = round(max(GetOutDataTimeMs), 2),
    AvgStorageTimeMs = round(avg(StorageTimeMs), 2),
    MaxStorageTimeMs = round(max(StorageTimeMs), 2)
    by bin(PreciseTimeStamp, stepSize)
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
| project
    PreciseTimeStamp = ts,
    //SlowIoCount = coalesce(SlowIoCount, 0),
    AvgTotalTimeMs = coalesce(AvgTotalTimeMs, 0.0),
    MaxTotalTimeMs = coalesce(MaxTotalTimeMs, 0.0),
    AvgGetOutDataTimeMs = coalesce(AvgGetOutDataTimeMs, 0.0),
    MaxGetOutDataTimeMs = coalesce(MaxGetOutDataTimeMs, 0.0),
    AvgStorageTimeMs = coalesce(AvgStorageTimeMs, 0.0),
    MaxStorageTimeMs = coalesce(MaxStorageTimeMs, 0.0)
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{_containerId}`, `{_NsIndex}`

---

### FailoverPOPercentsDD

_Widget purpose:_ DD: Failover PO (eSWPE) Reads vs Write Percents

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > DD: Failover PO (eSWPE) Reads vs Write Percents`

**Tables:** `AsapPfEtwTraceLogEventViewExtended`, `FailoverPOWritePercent`
**Aggregations:** `summarize TotalIO = sum(TotalCompletedIO), FO_IO = sum(FOCompletedIO), PO_IO = sum(POCompl`

```kusto
// Compute duration + dynamic step size (same logic as query #1)
let duration = _endTime - _startTime;
let stepSize = case(
        duration < 24h, 30s,
        duration < 3d,  5m,
        duration < 7d,  15m,
        duration < 14d, 30m,
        duration < 30d, 1h,
        3h
    );
// Align & scaffold time
let alignedStart = bin(_startTime, stepSize);
let alignedEnd   = bin(_endTime, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
let _vmVfIds = AsapMapVmToDiskOVL2(_NodeId, _containerId, _startTime, _endTime) 
               | distinct VfId;
    //_vmVfIds | as _vmVfIds; // debug
//
AsapPfEtwTraceLogEventViewExtended
| where NodeId == _NodeId and PreciseTimeStamp between (_startTime .. _endTime ) and EventId == 1265
| extend json= parse_json(Message)
| extend
    VfId                     = tolong(json.VfId),
    NsId                     = toint(json.NsId),
    NsIndex                  = tostring(json.NsIndex),
    NamespaceType            = toint(json.NamespaceType),
    UseSwpe                  = toint(json.UseSwpe),
    POCompletedReadIO        = todouble(json.POCompletedReadIO),
    POCompletedWriteIO       = todouble(json.POCompletedWriteIO),
    POCompletedIO            = todouble(json.POCompletedIO),
    FOCompletedReadIO        = todouble(json.FOCompletedReadIO),
    FOCompletedWriteIO       = todouble(json.FOCompletedWriteIO),
    FOCompletedIO            = todouble(json.FOCompletedIO),
    TotalCompletedIO         = todouble(json.TotalCompletedIO)
// Condition for FO capable disks
| where NsId != 1 and (UseSwpe == 0)
| where NamespaceType == 2
// APPLY FILTERS: FOR VM AND NSINDEX // <- PF 1265 Event carries Container ID in its payload rel6.91 onwards. for ver < 6.91, we need to map VFID
| where VfId in (_vmVfIds) or containerId == _containerId
| where _NsIndex  == "" or NsIndex == _NsIndex
| summarize
    TotalIO          = sum(TotalCompletedIO),
    FO_IO            = sum(FOCompletedIO),
    PO_IO            = sum(POCompletedIO),
    PO_Read_IO       = sum(POCompletedReadIO),
    PO_Write_IO      = sum(POCompletedWriteIO)
  by
    bin(PreciseTimeStamp, stepSize),
    NodeId
    //ContainerId = _containerId,
    //NamespaceType, NsId
// Percentages
| extend
    AvgFOPercent  = iff(TotalIO > 0,
            round(100.0 * FO_IO / TotalIO, 2),
            0.0),
    FailoverPOPercent =
        iff(TotalIO > 0,
            round(100.0 * PO_IO / TotalIO, 2),
            0.0),
    FailoverPOReadPercent =
        iff(TotalIO > 0,
            round(100.0 * PO_Read_IO / TotalIO, 2),
            0.0),
    FailoverPOWritePercent =
        iff(TotalIO > 0,
            round(100.0 * PO_Write_IO / TotalIO, 2),
            0.0)
// 
| project
    PreciseTimeStamp,
    NodeId,
    //NsId,
    AvgFOPercent,
    FailoverPOPercent,
    FailoverPOReadPercent,
    FailoverPOWritePercent
| order by PreciseTimeStamp asc
| join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts, 
              AvgFOPercent = coalesce(AvgFOPercent, 0.0),
              FailoverPOPercent = coalesce(FailoverPOPercent, 0.0),
              FailoverPOReadPercent = coalesce(FailoverPOReadPercent, 0.0),
              FailoverPOWritePercent = coalesce(FailoverPOWritePercent, 0.0)
    | order by PreciseTimeStamp asc
```

**Params:** `{_startTime}`, `{_endTime}`, `{_NodeId}`, `{_containerId}`, `{_NsIndex}`

---

### GetNsIndicesForContainer

_Widget purpose:_ DD: Failover PO (eSWPE) Reads vs Write Percents

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > DD: Failover PO (eSWPE) Reads vs Write Percents`

**Tables:** `AsapMapVmToDiskOVL2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(nodeId, containerId, queryFrom, queryTo) | sort by NsIndex | distinct Value = tostring(NsIndex);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### FOExceptions_PerVM

_Widget purpose:_ FO Exceptions Per VM 

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > FO Exceptions Per VM `

**Tables:** `Asap_FOExceptions_HttpTranscodeTable`, `AsapPfEtwTraceLogEventViewExtended`
**Aggregations:** `summarize count_ = count() by SubCode, bin(PreciseTimeStamp, stepSize)`
**Output columns:** `PreciseTimeStamp`, `SubCode`, `count_`

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
//
let _getNsIndicesForContainer = AsapMapVmToDiskOVL2(nodeId, _containerId, queryFrom, queryTo) | distinct NsIndex;
//_getNsIndicesForContainer | as _getNsIndicesForContainer;
let hasNs = toscalar(_getNsIndicesForContainer | count);
//
// IMPORTANT! Please note : We dont expect to see same NODE_NSINDEX unique pair at same given time. 
// So as long as we query one node and one container, we only have unique NSIndex expected so this should work
//
// IMPORTANT! Please also note: Only some exception events carry NSindex (Event 6028, 6029, 6031) in their payload but others (such as 6016,6048) don't. Filing bug for these
// This also means DRIs should note that if we are seeing X,Y,Z exceptions on node level but in VM level we see only X, its likely that Y,Z events dont have NS/VF info 
// which is why they are missed.
// 
AsapPfEtwTraceLogEventViewExtended
| where NodeId == nodeId and PreciseTimeStamp between (queryFrom .. queryTo ) 
        and (EventId between (6000..6500) or EventId == 6504)
        and (
        containerId == _containerId 
        or (hasNs > 0 and NsIndex in (_getNsIndicesForContainer))
      ) // <---- Lookup exceptions for Namespaces associated w your Container
// Extend helper columns
| extend Code = tostring(json.HttpSubCode), PfVer = tostring(json.ProductVersion), 
         dd_fo_throttle = tolong(json.dd_fo_throttle),
         dd_report_error = coalesce( tolong(json.DD_Report_Error), tolong(json.dd_report_error))
| project  PreciseTimeStamp, containerId, VfId, NsId, NsIndex, EventId, EventName, Code, dd_fo_throttle, dd_report_error, Message, json
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
| order by PreciseTimeStamp asc, count_ 
| project PreciseTimeStamp, SubCode, count_
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{_containerId}`

---

### asapContainerFOStats_asapPF_AllDisks

_Widget purpose:_ IOPS: FO vs PO (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > IOPS: FO vs PO (All Disks, includes boot disk)`

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
AsapContainerFOStatsAsapPf(nodeId, containerId, queryFrom, queryTo, _nsIndex=_NsIndex) 
    //
    | project VfId, PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs, MaxWriteLatencyMs ,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs,
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs, 
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              VfId,
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

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`, `{_NsIndex}`

---

### GetNsIndicesForContainer

_Widget purpose:_ IOPS: FO vs PO (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > IOPS: FO vs PO (All Disks, includes boot disk)`

**Tables:** `AsapMapVmToDiskOVL2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(nodeId, containerId, queryFrom, queryTo) | sort by NsIndex | distinct Value = tostring(NsIndex);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### asapContainerFOStats_asapPF_FODisks

_Widget purpose:_ IOPS: FO vs PO (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > IOPS: FO vs PO (FO enabled Disks)`

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
AsapContainerFOStatsAsapPf(nodeId, containerId, queryFrom, queryTo, _useSwpe="0", _nsIndex=_NsIndex) 
    //
    | project VfId, PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs, MaxWriteLatencyMs,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs,
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs, 
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              VfId,
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

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`, `{_NsIndex}`

---

### GetNsIndicesForContainer

_Widget purpose:_ IOPS: FO vs PO (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > IOPS: FO vs PO (FO enabled Disks)`

**Tables:** `AsapMapVmToDiskOVL2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(nodeId, containerId, queryFrom, queryTo) | sort by NsIndex | distinct Value = tostring(NsIndex);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### asapContainerFOStats_asapPF_AllDisks

_Widget purpose:_ Latency: Average & Max in Ms (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (All Disks, includes boot disk)`

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
AsapContainerFOStatsAsapPf(nodeId, containerId, queryFrom, queryTo, _nsIndex=_NsIndex) 
    //
    | project VfId, PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs, MaxWriteLatencyMs ,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs,
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs, 
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              VfId,
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

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`, `{_NsIndex}`

---

### GetNsIndicesForContainer

_Widget purpose:_ Latency: Average & Max in Ms (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (All Disks, includes boot disk)`

**Tables:** `AsapMapVmToDiskOVL2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(nodeId, containerId, queryFrom, queryTo) | sort by NsIndex | distinct Value = tostring(NsIndex);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### asapContainerFOStats_asapPF_FODisks

_Widget purpose:_ Latency: Average & Max in Ms (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (FO enabled Disks)`

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
AsapContainerFOStatsAsapPf(nodeId, containerId, queryFrom, queryTo, _useSwpe="0", _nsIndex=_NsIndex) 
    //
    | project VfId, PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs, MaxWriteLatencyMs,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs,
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs, 
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              VfId,
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

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`, `{_NsIndex}`

---

### GetNsIndicesForContainer

_Widget purpose:_ Latency: Average & Max in Ms (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Latency: Average & Max in Ms (FO enabled Disks)`

**Tables:** `AsapMapVmToDiskOVL2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(nodeId, containerId, queryFrom, queryTo) | sort by NsIndex | distinct Value = tostring(NsIndex);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### asapContainerFOStats_asapPF_AllDisks

_Widget purpose:_ MBPS: FO vs PO (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > MBPS: FO vs PO (All Disks, includes boot disk)`

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
AsapContainerFOStatsAsapPf(nodeId, containerId, queryFrom, queryTo, _nsIndex=_NsIndex) 
    //
    | project VfId, PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs, MaxWriteLatencyMs ,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs,
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs, 
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              VfId,
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

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`, `{_NsIndex}`

---

### GetNsIndicesForContainer

_Widget purpose:_ MBPS: FO vs PO (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > MBPS: FO vs PO (All Disks, includes boot disk)`

**Tables:** `AsapMapVmToDiskOVL2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(nodeId, containerId, queryFrom, queryTo) | sort by NsIndex | distinct Value = tostring(NsIndex);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### asapContainerFOStats_asapPF_FODisks

_Widget purpose:_ MBPS: FO vs PO (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > MBPS: FO vs PO (FO enabled Disks)`

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
AsapContainerFOStatsAsapPf(nodeId, containerId, queryFrom, queryTo, _useSwpe="0", _nsIndex=_NsIndex) 
    //
    | project VfId, PreciseTimeStamp, 
              FO_Read_IOPS, FO_Write_IOPS, PO_Read_IOPS, PO_Write_IOPS,
              FO_Read_Mbps, FO_Write_Mbps, PO_Read_Mbps, PO_Write_Mbps, 
              AvgReadLatencyMs, AvgWriteLatencyMs, 
              AvgBackendReadLatencyMs, AvgBackendWriteLatencyMs,
              AvgBqeReadLatencyMs, AvgBqeWriteLatencyMs,
              AvgSchedReadLatencyMs, AvgSchedWriteLatencyMs,
              MaxReadLatencyMs, MaxWriteLatencyMs,
              BqeMaxReadLatencyMs, BqeMaxWriteLatencyMs,
              BackendMaxReadLatencyMs, BackendMaxWriteLatencyMs, 
              SchedulerMaxReadLatencyMs, SchedulerMaxWriteLatencyMs
    // Join with scaffold to enforce full time range
    | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
    | project PreciseTimeStamp=ts,
              VfId,
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

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`, `{_NsIndex}`

---

### GetNsIndicesForContainer

_Widget purpose:_ MBPS: FO vs PO (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > MBPS: FO vs PO (FO enabled Disks)`

**Tables:** `AsapMapVmToDiskOVL2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVmToDiskOVL2(nodeId, containerId, queryFrom, queryTo) | sort by NsIndex | distinct Value = tostring(NsIndex);
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### asapFOStats_DisksSpreadFOPercent_asapPF

_Widget purpose:_ Spread of Disks and their %FO (UseSwpe =0)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CategoryChart`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 30s DiskMetrics for ASAP > Spread of Disks and their %FO (UseSwpe =0)`

**Tables:** `AsapPfEtwTraceLogEventViewExtended`, `AsapVmToVFMapping`
**Aggregations:** `summarize TotalIO = sum(TotalCompletedIO), TotalFOIO = sum(FOCompletedIO), TotalPOIO = sum` · `summarize DiskCount = dcount(NsId) by FOBucket`
**Output columns:** `FOBucket`, `DiskCount`

```kusto
//
let FO_Buckets = datatable(FOBucket:string)
[
    "IDLE", "0-1%","1-10%","10-20%","20-30%","30-40%",
    "40-50%","50-60%","60-70%","70-80%",
    "80-90%","90-99%", "99-99.5%","99.5-100%"
] 
| sort by FOBucket asc;
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
let AsapVmToVFMapping = AsapMapVmToDiskOVL2(nodeId, _containerId, queryFrom, queryTo) ;
//AsapVmToVFMapping | as AsapVmToVFMapping; // DEBUG
//
let _DiskFOPercents = AsapPfEtwTraceLogEventViewExtended
    | where PreciseTimeStamp between (queryFrom .. queryTo ) and NodeId  == nodeId and EventId == 1265
    | project Cluster, NodeId, containerId, PreciseTimeStamp, EventId, EventName, Message
    | extend json = parse_json(Message)
    | extend UseSwpe = toint(json.UseSwpe), 
             VfId = tolong(json.VfId),  NsId = toint(json.NsId), NsIndex = toint(json.NsIndex),
             NamespaceType = toint(json.NamespaceType), 
             CachePolicy = toint(json.CachePolicy), 
             TotalCompletedIO = todouble(json.TotalCompletedIO), 
             FOCompletedIO = todouble(json.FOCompletedIO),
             POCompletedIO = todouble(json.POCompletedIO),
             POCompletedReadIO = todouble(json.POCompletedReadIO),
             POCompletedWriteIO = todouble(json.POCompletedWriteIO)
    // APPL MAP CONTAINER TO VF ID Logic to pull data from correct VM we intended
    | where VfId in (AsapVmToVFMapping | distinct VfId) or containerId == _containerId
    // Apply FO condition
    | where UseSwpe == 0 
    // Remove OS disk, include only uncached data disks, also eliminate IDLE VM case so total IO is always non zero
    | where NsId != 0 and NamespaceType in (1,2)
    | where (NamespaceType == 1 and CachePolicy == 1) or (NamespaceType == 2 and CachePolicy == 0)
    | project-away Message, json 
    //
    // Summarize
    | summarize TotalIO = sum(TotalCompletedIO), 
                TotalFOIO = sum(FOCompletedIO),
                TotalPOIO = sum(POCompletedIO),
                TotalPOReads = sum (POCompletedReadIO) ,
                TotalPOWrites = sum (POCompletedWriteIO) 
                by Cluster, NodeId, VfId, NsId, NsIndex
    //    
    | extend PercentOfFOCompletedIO = round(100.0 * todouble(TotalFOIO) / todouble(TotalIO),2),
             PercentOfPOCompletedIO = round(100.0 * todouble(TotalPOIO) / todouble(TotalIO),2),
             PercentOfPOReads       = round(100.0 * todouble(TotalPOReads) / todouble(TotalIO),2),
             PercentOfPOWrites      = round(100.0 * todouble(TotalPOWrites) / todouble(TotalIO),2)
    | project VfId, NsId, NsIndex,FOPercent = PercentOfFOCompletedIO, TotalIO
    | extend FOBucket = case
         (
            TotalIO == 0, "IDLE",
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
            FOPercent >= 99 and FOPercent < 99.5, "99-99.5%",
            FOPercent >= 99.5 and FOPercent <= 100, "99.5-100%",
            "Other"
        )
        | summarize DiskCount = dcount(NsId) by FOBucket
        | sort by FOBucket asc
     ;
    //        
    _DiskFOPercents
        | join kind=rightouter FO_Buckets on FOBucket
        | extend DiskCount = coalesce(DiskCount, 0), FOBucket = FOBucket1
        | project FOBucket, DiskCount
        | sort by FOBucket asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{_containerId}`

---

### asapContainerFOStats_OsCounters_FOPercents

_Widget purpose:_ %FO of Total IO: Per VM, FO Disks only i.e UseSwpe = 0

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > %FO of Total IO: Per VM, FO Disks only i.e UseSwpe = 0`

**Aggregations:** `summarize AvgFOPercent = round(avg(FOPercent),2) by bin(PreciseTimeStamp, stepSize) // //`
**Output columns:** `PreciseTimeStamp`, `AVG_FOPercent`

```kusto
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
    duration < 3d, 5m,          // 
    duration < 14d, 15m,        // Slight aggregation
    duration < 30d, 30m,        // Smooth trend?
    1h                          // For 30–60 days
);
//
// Scaffold time series to enforce fixed 5m bins
let alignedStart = bin(queryFrom, stepSize);
let alignedEnd   = bin(queryTo, stepSize);
let TimeScaffold = range ts from alignedStart to alignedEnd step stepSize;
//
AsapContainerFOStatsOsCounters(nodeId, containerId, queryFrom, queryTo, _useSwpe="0")
     | project PreciseTimeStamp, FO_IOPS, PO_IOPS, Total_IOPS, PO_Read_IOPS, PO_Write_IOPS
     | extend FOPercent = round (100.0 * todouble(FO_IOPS )/ todouble(Total_IOPS), 2)
     | summarize AvgFOPercent = round(avg(FOPercent),2) by bin(PreciseTimeStamp, stepSize)
     //
     //
     | join kind=rightouter (TimeScaffold) on $left.PreciseTimeStamp == $right.ts
     | project PreciseTimeStamp=ts, AVG_FOPercent = coalesce(AvgFOPercent, 0.0)
     | order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`

---

### DiskCounts_FOPercents_OSCountersV2

_Widget purpose:_ Disk Spread based on FO Percent KPI (FO Disks only, UseSwpe = 0)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CategoryChart`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > Disk Spread based on FO Percent KPI (FO Disks only, UseSwpe = 0)`

**Tables:** `OsAsapCounterTable`
**Aggregations:** `summarize // IOPS Total FO_IOPS = sum(DeltaFoCompleted) / max(OsDiagDurationInSec), PO_IOP` · `summarize DiskCount = dcount(NsName) by FOBucket`
**Output columns:** `FOBucket`, `DiskCount`

```kusto
let FO_Buckets = datatable(FOBucket:string)
[
    "IDLE", "0-1%","1-10%","10-20%","20-30%","30-40%",
    "40-50%","50-60%","60-70%","70-80%",
    "80-90%","90-99%","99-100%"
] 
| sort by FOBucket asc;
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
    duration < 12h, 5m,   // very short window
    duration < 1d, 15m,     // up to 1 day
    duration < 7d, 12h,    // 1–7 days
    duration < 30d, 1d,
    7d                     // >7 days
);
let _DiskFOPercents = OsAsapCounterTable
    | where  NodeId  == nodeId and ContainerId == containerId and PreciseTimeStamp between (queryFrom .. queryTo ) 
    | where UseSwpe == 0
    | project PreciseTimeStamp, NodeId, ContainerId, NsName = NamespaceName, UseSwpe, DiskClass, CachePolicy, BlobPath, ArmId, 
              DeltaIOCompleted, 
              DeltaFoCompleted, 
              DeltaPoCompleted,
              //
              DeltaFoBytesCompleted,
              DeltaPoBytesCompleted,
              DeltaBytesCompleted,
              //
              DeltaFoReadCompleted,
              DeltaFoWriteCompleted,
              DeltaPoReadCompleted,
              DeltaPoWriteCompleted,
              //
              DeltaFoReadBytesCompleted, 
              DeltaFoWriteBytesCompleted, 
              DeltaPoReadBytesCompleted, 
              DeltaPoWriteBytesCompleted,
              //
              AverageReadLatencyMs = AverageReadLatency, 
              AverageWriteLatencyMs = AverageWriteLatency,
              DeltaIoLatencyDiskReadIoBucketMaxLatency, 
              DeltaIoLatencyDiskWriteIoBucketMaxLatency,
              OsDiagDurationInSec
    //
    | summarize 
                // IOPS Total
                FO_IOPS = sum(DeltaFoCompleted) / max(OsDiagDurationInSec),
                PO_IOPS = sum(DeltaPoCompleted) / max(OsDiagDurationInSec),
                Total_IOPS = sum(DeltaIOCompleted) / max(OsDiagDurationInSec),
                // 
                // IOPS R + W
                FO_Read_IOPS = sum(DeltaFoReadCompleted) / max(OsDiagDurationInSec),
                FO_Write_IOPS =sum(DeltaFoWriteCompleted) / max(OsDiagDurationInSec),
                PO_Read_IOPS = sum(DeltaPoReadCompleted) / max(OsDiagDurationInSec),
                PO_Write_IOPS =sum(DeltaPoWriteCompleted) / max(OsDiagDurationInSec),
                //
                // MBPS Total
                FO_MBPS = sum(DeltaFoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                PO_MBPS = sum(DeltaPoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                Total_MBPS =  sum(DeltaBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                //
                // MBPS R + W
                FO_Read_Mbps = sum(DeltaFoReadBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                FO_Write_Mbps = sum(DeltaFoWriteBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                PO_Read_Mbps = sum(DeltaPoReadBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                PO_Write_Mbps = sum(DeltaPoWriteBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                //
                // Latency computation - Avg and Max
                AvgReadLatencyInMS = avg(AverageReadLatencyMs), AvgWriteLatencyInMS = avg(AverageWriteLatencyMs),
                //
                MaxReadLatencyInMS = max(DeltaIoLatencyDiskReadIoBucketMaxLatency / 1000.0), 
                MaxWriteLatencyInMS = max(DeltaIoLatencyDiskWriteIoBucketMaxLatency / 1000.0)
                //
                by ContainerId, NsName, ArmId, BlobPath //, bin(PreciseTimeStamp, stepSize)
        //
         | extend FOPercent = round (100.0 * todouble(FO_IOPS )/ todouble(Total_IOPS), 2)
         | project ContainerId, NsName, FOPercent, Total_IOPS, BlobPath, ArmId
         | extend FOBucket = case
         (
            Total_IOPS == 0, "IDLE",
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
        | summarize DiskCount = dcount(NsName) by FOBucket
        | sort by FOBucket asc;
    // --- Force all buckets to appear
    _DiskFOPercents
        | join kind=rightouter FO_Buckets on FOBucket
        | extend DiskCount = coalesce(DiskCount, 0), FOBucket = FOBucket1
        | project FOBucket, DiskCount
        | sort by FOBucket asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`

---

### asapContainerFOStatsOsCounters

_Widget purpose:_ IOPS: FO vs PO (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > IOPS: FO vs PO (All Disks, includes boot disk)`

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
AsapContainerFOStatsOsCounters(_nodeId, _containerId, queryFrom, queryTo)
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
          AverageWriteLatencyMS = coalesce(AvgWriteLatencyInMS, 0.0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_containerId}`, `{_nodeId}`

---

### asapContainerFOStatsOsCountersUseSwpe0

_Widget purpose:_ IOPS: FO vs PO (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > IOPS: FO vs PO (FO enabled Disks)`

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
AsapContainerFOStatsOsCounters(_nodeId, _containerId, queryFrom, queryTo, _useSwpe="0")
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
          AverageWriteLatencyMS = coalesce(AvgWriteLatencyInMS, 0.0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_nodeId}`, `{_containerId}`

---

### asapContainerFOStats_OsCounters_AllDisks_Latency

_Widget purpose:_ Latency: Average & Max in Ms (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > Latency: Average & Max in Ms (All Disks, includes boot disk)`

**Tables:** `AsapContainerFOStatsOsCounters`

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
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapContainerFOStatsOsCounters(nodeId, containerId, queryFrom, queryTo)
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

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`

---

### asapContainerFOStats_OsCounters_FODisks_Latency

_Widget purpose:_ Latency: Average & Max in Ms (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > Latency: Average & Max in Ms (FO enabled Disks)`

**Tables:** `AsapContainerFOStatsOsCounters`

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
cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapContainerFOStatsOsCounters(nodeId, containerId, queryFrom, queryTo, _useSwpe= "0")
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

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`

---

### List_AllDisks_OsCounters

_Widget purpose:_ List FO Disks Names used for FO Stats

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > List FO Disks Names used for FO Stats`

**Tables:** `OsAsapCounterTable`
**Aggregations:** `summarize // IOPS Total FO_IOPS = sum(DeltaFoCompleted) / max(OsDiagDurationInSec), PO_IOP`
**Output columns:** `ContainerId`, `FOPercent`, `FOBucket`, `Total_IOPS`, `NsName`, `BlobPath`, `ArmId`

```kusto
let FO_Buckets = datatable(FOBucket:string)
[
    "IDLE", "0-1%","1-10%","10-20%","20-30%","30-40%",
    "40-50%","50-60%","60-70%","70-80%",
    "80-90%","90-99%","99-100%"
] 
| sort by FOBucket asc;
// Compute duration and choose step size dynamically
let duration = queryTo - queryFrom;
let stepSize = case(
    duration < 12h, 5m,   // very short window
    duration < 1d, 15m,     // up to 1 day
    duration < 7d, 12h,    // 1–7 days
    duration < 30d, 1d,
    7d                     // >7 days
);
OsAsapCounterTable
    | where  NodeId  == nodeId and ContainerId == containerId and PreciseTimeStamp between (queryFrom .. queryTo ) 
    | where UseSwpe == 0
    | project PreciseTimeStamp, NodeId, ContainerId, NsName = NamespaceName, UseSwpe, DiskClass, CachePolicy, BlobPath, ArmId, 
              DeltaIOCompleted, 
              DeltaFoCompleted, 
              DeltaPoCompleted,
              //
              DeltaFoBytesCompleted,
              DeltaPoBytesCompleted,
              DeltaBytesCompleted,
              //
              DeltaFoReadCompleted,
              DeltaFoWriteCompleted,
              DeltaPoReadCompleted,
              DeltaPoWriteCompleted,
              //
              DeltaFoReadBytesCompleted, 
              DeltaFoWriteBytesCompleted, 
              DeltaPoReadBytesCompleted, 
              DeltaPoWriteBytesCompleted,
              //
              AverageReadLatencyMs = AverageReadLatency, 
              AverageWriteLatencyMs = AverageWriteLatency,
              DeltaIoLatencyDiskReadIoBucketMaxLatency, 
              DeltaIoLatencyDiskWriteIoBucketMaxLatency,
              OsDiagDurationInSec
    //
    | summarize 
                // IOPS Total
                FO_IOPS = sum(DeltaFoCompleted) / max(OsDiagDurationInSec),
                PO_IOPS = sum(DeltaPoCompleted) / max(OsDiagDurationInSec),
                Total_IOPS = sum(DeltaIOCompleted) / max(OsDiagDurationInSec),
                // 
                // IOPS R + W
                FO_Read_IOPS = sum(DeltaFoReadCompleted) / max(OsDiagDurationInSec),
                FO_Write_IOPS =sum(DeltaFoWriteCompleted) / max(OsDiagDurationInSec),
                PO_Read_IOPS = sum(DeltaPoReadCompleted) / max(OsDiagDurationInSec),
                PO_Write_IOPS =sum(DeltaPoWriteCompleted) / max(OsDiagDurationInSec),
                //
                // MBPS Total
                FO_MBPS = sum(DeltaFoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                PO_MBPS = sum(DeltaPoBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                Total_MBPS =  sum(DeltaBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                //
                // MBPS R + W
                FO_Read_Mbps = sum(DeltaFoReadBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                FO_Write_Mbps = sum(DeltaFoWriteBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                PO_Read_Mbps = sum(DeltaPoReadBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                PO_Write_Mbps = sum(DeltaPoWriteBytesCompleted) / 1024.0 / 1024.0 / max(OsDiagDurationInSec),
                //
                // Latency computation - Avg and Max
                AvgReadLatencyInMS = avg(AverageReadLatencyMs), AvgWriteLatencyInMS = avg(AverageWriteLatencyMs),
                //
                MaxReadLatencyInMS = max(DeltaIoLatencyDiskReadIoBucketMaxLatency / 1000.0), 
                MaxWriteLatencyInMS = max(DeltaIoLatencyDiskWriteIoBucketMaxLatency / 1000.0)
                //
                by ContainerId, NsName, ArmId, BlobPath //, bin(PreciseTimeStamp, stepSize)
        //
         | extend FOPercent = round (100.0 * todouble(FO_IOPS )/ todouble(Total_IOPS), 2)
         | project ContainerId, NsName, FOPercent, Total_IOPS, BlobPath, ArmId
         | extend FOBucket = case
         (
            Total_IOPS == 0, "IDLE",
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
        | project ContainerId, FOPercent, FOBucket, Total_IOPS, NsName, BlobPath, ArmId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`

---

### asapContainerFOStatsOsCounters

_Widget purpose:_ MBPS, FO vs PO (All Disks, includes boot disk)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > MBPS, FO vs PO (All Disks, includes boot disk)`

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
AsapContainerFOStatsOsCounters(_nodeId, _containerId, queryFrom, queryTo)
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
          AverageWriteLatencyMS = coalesce(AvgWriteLatencyInMS, 0.0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_containerId}`, `{_nodeId}`

---

### asapContainerFOStatsOsCountersUseSwpe0

_Widget purpose:_ MBPS, FO vs PO (FO enabled Disks)

Cluster: `https://storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > 5m OsAsapCounters > MBPS, FO vs PO (FO enabled Disks)`

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
AsapContainerFOStatsOsCounters(_nodeId, _containerId, queryFrom, queryTo, _useSwpe="0")
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
          AverageWriteLatencyMS = coalesce(AvgWriteLatencyInMS, 0.0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_nodeId}`, `{_containerId}`

---

### Azure Host VM Active Blobs Filter

_Widget purpose:_ IO Stats for Disks

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > IO Stats for Disks`

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

### Azure Host VM ASAP 2.0 IO Stats

_Widget purpose:_ IO Stats for Disks

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > ASAP (OVL 2.0+) > IO Stats for Disks`

**Tables:** `OsAsapCounterTable`
**Aggregations:** `summarize FO_IOPS = sum(DeltaFoCompleted) / max(OsDiagDurationInSec), FO_MBPS = sum(DeltaF by bin(todatetime(OsDiagHostTimeStamp), 5s)`

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
