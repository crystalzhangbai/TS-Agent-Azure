# Host Events

> Source: **Azure Host - Azure VM** dashboard, chapter **Host Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Events for ContainerId (from Hyper-V/ASAP/Blobcache/Vhddisk)

### Azure Host VM TDPR HyperV Events

_Widget purpose:_ Events for ContainerId (from Hyper-V/ASAP/Blobcache/Vhddisk)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Events > Events for ContainerId (from Hyper-V/ASAP/Blobcache/Vhddisk)`

**Tables:** `TDPR_OperationName2TeamServiceMap`, `IfxOperationV2v1EtwTable`, `WindowsEventTable`, `HyperVStorageStackTable`, `HyperVVmmsTable`, `AsapPfEtwEventTable`
**Output columns:** `PreciseTimeStamp`, `ProviderName`, `EventId`, `Description`, `level`

```kusto
let operations = cluster("https://egpublic.westus.kusto.windows.net").database("eg").TDPR_OperationName2TeamServiceMap
| where Service == "StorageClient"
| distinct OperationName;
let allOperationsWithContainer = cluster('azcore.centralus.kusto.windows.net').database('Fa').IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and OperationName in (operations)
        and  * contains containerId;
let rootoperationIds = allOperationsWithContainer | distinct RootOperationId;
let activityIds = allOperationsWithContainer | distinct ActivityId;
let parentActivityIds = allOperationsWithContainer | distinct ParentActivityId;
let VfId = toscalar(AsapPfEtwEventTable
| where PreciseTimeStamp between ((startTime - 5m) .. (endTime + 5m)) and NodeId == nodeId
        and EventMessage contains containerId
        and EventMessage contains "AsapPf indicates that VfId="
| parse EventMessage with "AsapPf indicates that VfId=" VfId " " *
| distinct VfId);
let blobs = OsXIOHealthSignalEvent
| where PreciseTimeStamp between ((startTime - 30m) .. (endTime + 30m))
        and NodeId == nodeId and SurfaceName contains containerId
| parse BlobPath with * "8080" BlobPath "?" *
| where isnotempty(BlobPath)
| distinct BlobPath;
cluster('azcore.centralus').database('Fa').WindowsEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and * contains containerId
| extend PreciseTimeStamp = todatetime(TimeCreated)
| union (
        OsVhddiskEventTable
        | where PreciseTimeStamp between (startTime .. endTime)
                and NodeId == nodeId and ParamStr1 in (blobs) and EventId !in (48)
        | project PreciseTimeStamp, ProviderName, tostring(EventId), Description = ParamStr1
)
| union (
        VhdDiskEtwEventTable
        | where PreciseTimeStamp between (startTime .. endTime)
                and NodeId == NodeId and EventMessage !contains "FastPath Session Dropped"
        | parse EventMessage with * "blobpath:" BlobPath "." *
        | where BlobPath in (blobs)
        | project PreciseTimeStamp, ProviderName, tostring(EventId), Description = EventMessage
)
| union ( 
        AsapPfEtwEventTable | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
                and (* contains containerId 
                or EventMessage contains strcat("VfId=", VfId)
                or EventMessage contains strcat("VfId: ", VfId)
                or EventMessage contains strcat("VfId:", VfId)
                or EventMessage contains strcat("Virtual Function ", VfId))
                and isnotempty(VfId) and EventMessage !contains "VfId:4294967295"
        | extend EventId = tostring(EventId), Description = EventMessage
)
| union ( 
        AsapNvmeEtwEventTable | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
                and (* contains containerId 
                or EventMessage contains strcat("VfId=", VfId)
                or EventMessage contains strcat("VfId: ", VfId)
                or EventMessage contains strcat("VfId:", VfId)
                or EventMessage contains strcat("Virtual Function ", VfId))
                and isnotempty(VfId) and EventMessage !contains "VfId:4294967295"
        | extend EventId = tostring(EventId), Description = EventMessage
)
| union ( 
        AsapNvmeEtwTraceLogEventView | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
                and (* contains containerId 
                or Message contains strcat("VfId=", VfId)
                or Message contains strcat("VfId: ", VfId)
                or Message contains strcat("VfId:", VfId)
                or Message contains strcat("Virtual Function ", VfId))
                and isnotempty(VfId) and Message !contains "VfId:4294967295"
        | extend EventId = tostring(EventId), Description = Message
)
| union ( 
        AsapKmsEtwEventTable | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
                and (* contains containerId 
                or EventMessage contains strcat("VfId=", VfId)
                or EventMessage contains strcat("VfId: ", VfId)
                or EventMessage contains strcat("VfId:", VfId)
                or EventMessage contains strcat("Virtual Function ", VfId))
                and isnotempty(VfId) and EventMessage !contains "VfId:4294967295"
        | extend EventId = tostring(EventId), Description = EventMessage
)
| union ( 
        AsapKmsEtwTraceLogEventView | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
                and (* contains containerId 
                or Message contains strcat("VfId=", VfId)
                or Message contains strcat("VfId: ", VfId)
                or Message contains strcat("VfId:", VfId)
                or Message contains strcat("Virtual Function ", VfId))
                and isnotempty(VfId) and Message !contains "VfId:4294967295"
        | extend EventId = tostring(EventId), Description = Message
)
| union ( 
        AsapPfEtwTraceLogEventView | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
                and (* contains containerId 
                or Message contains strcat("VfId=", VfId)
                or Message contains strcat("VfId: ", VfId)
                or Message contains strcat("VfId:", VfId)
                or Message contains strcat("Virtual Function ", VfId))
                and isnotempty(VfId) and Message !contains "VfId:4294967295"
        | extend EventId = tostring(EventId), Description = Message
)
| union ( 
        AsapDpaEtwTraceLogEventView | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
                and (* contains containerId 
                or Message contains strcat("VfId=", VfId)
                or Message contains strcat("VfId: ", VfId)
                or Message contains strcat("VfId:", VfId)
                or Message contains strcat("Virtual Function ", VfId))
                and isnotempty(VfId) and Message !contains "VfId:4294967295"
        | extend EventId = tostring(EventId), Description = Message
)
| union ( 
        AsapNullEtwTraceLogEventView | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
                and (* contains containerId 
                or Message contains strcat("VfId=", VfId)
                or Message contains strcat("VfId: ", VfId)
                or Message contains strcat("VfId:", VfId)
                or Message contains strcat("Virtual Function ", VfId))
                and isnotempty(VfId) and Message !contains "VfId:4294967295"
        | extend EventId = tostring(EventId), Description = Message
)
| union ( 
        cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVStorageStackTable
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
                and (* contains containerId)
                and ProviderName != "Microsoft.Windows.HyperV.Management"
        | extend EventId = tostring(EventId), Description = case(isnotempty(EventMessage), EventMessage, Message)
)
| union ( 
        cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVVmmsTable
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId //and Level < 4
                and (* contains containerId)
                and ProviderName != "Microsoft.Windows.HyperV.Management"
        | extend EventId = tostring(EventId), Description = case(isnotempty(EventMessage), EventMessage, Message)
)
| union (
    OsXIOSurfaceCounterTable
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
        and (SurfaceName contains containerId) and DiskType == 1
    | project PreciseTimeStamp = todatetime(OsDiagHostTimeStamp), EventId = "", ProviderName = "BlobCacheSurfaceOsDisk", Description = strcat("DeltaReads: ", DeltaReads, " DeltaCacheReads: ", DeltaCacheReads, " DeltaWrites: ", DeltaWrites, " TotalGBRead: ",TotalGBRead, " TotalReads: ", TotalReads, " OsDiagDurationInSec: ", OsDiagDurationInSec)
)
| union (
    OsXIOXdiskCounterTable
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
        and (SurfaceName contains containerId) and DiskType == 1
    | project PreciseTimeStamp = todatetime(OsDiagHostTimeStamp), EventId = "", ProviderName = "XDiskOsDisk", Description = strcat("DelNWReads: ", DelNWReads, " DelNWWrites: ", DelNWWrites, " Del503Cnt: ", Del503Cnt, " DelXRetryCnt: ", DelXRetryCnt, " OsDiagDurationInSec: ", OsDiagDurationInSec)
)
| union (
    OsXIOSurfaceLatencyHistogramTableV2
    | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and SurfaceName contains containerId and DiskType == 1
    | extend   Gt_1_Sec = Bin_224 + Bin_225 + Bin_226 + Bin_227 + Bin_228 + Bin_229 + Bin_230 + Bin_231 + Bin_232 + Bin_233 + Bin_234 + Bin_235 + Bin_236 + Bin_237 + Bin_238 + Bin_239 + Bin_240 + Bin_241 + Bin_242 + Bin_243 + Bin_244 + Bin_245 + Bin_246 + Bin_247 + Bin_248 + Bin_249 + Bin_250 + Bin_251 + Bin_252 + Bin_253 + Bin_254 + Bin_255 + Bin_256,
               Gt_2_Sec = Bin_225 + Bin_226 + Bin_227 + Bin_228 + Bin_229 + Bin_230 + Bin_231 + Bin_232 + Bin_233 + Bin_234 + Bin_235 + Bin_236 + Bin_237 + Bin_238 + Bin_239 + Bin_240 + Bin_241 + Bin_242 + Bin_243 + Bin_244 + Bin_245 + Bin_246 + Bin_247 + Bin_248 + Bin_249 + Bin_250 + Bin_251 + Bin_252 + Bin_253 + Bin_254 + Bin_255 + Bin_256,
               Gt_5_Sec = Bin_228 + Bin_229 + Bin_230 + Bin_231 + Bin_232 + Bin_233 + Bin_234 + Bin_235 + Bin_236 + Bin_237 + Bin_238 + Bin_239 + Bin_240 + Bin_241 + Bin_242 + Bin_243 + Bin_244 + Bin_245 + Bin_246 + Bin_247 + Bin_248 + Bin_249 + Bin_250 + Bin_251 + Bin_252 + Bin_253 + Bin_254 + Bin_255 + Bin_256, 
               Gt_10_Sec = Bin_233 + Bin_234 + Bin_235 + Bin_236 + Bin_237 + Bin_238 + Bin_239 + Bin_240 + Bin_241 + Bin_242 + Bin_243 + Bin_244 + Bin_245 + Bin_246 + Bin_247 + Bin_248 + Bin_249 + Bin_250 + Bin_251 + Bin_252 + Bin_253 + Bin_254 + Bin_255 + Bin_256
    | where Gt_1_Sec > 0
    | project PreciseTimeStamp = todatetime(OsDiagHostTimeStamp), EventId = "", ProviderName = "BlobCacheSurfaceOsDisk", 
        Description = strcat("Histogram: ", HistogramTypeEnum, " Total IOs > 1s: ", Gt_1_Sec, " Total IOs > 5s: ", Gt_5_Sec, " Total IOs > 10s: ", Gt_10_Sec), Level = 2
)
| union (
        cluster('azcore.centralus.kusto.windows.net').database('Fa').IfxOperationV2v1EtwTable
        | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and OperationName in (operations) and 
                (
                * contains containerId
                or RootOperationId in (rootoperationIds)
                or ActivityId in (activityIds) or ActivityId in (parentActivityIds) or 
                ((ParentActivityId in (parentActivityIds) or ParentActivityId in (activityIds)) and ParentActivityId != "00000000-0000-0000-0000-000000000000")
                or (ParentActivityId == "00000000-0000-0000-0000-000000000000" and * contains containerId)
                )
        | project PreciseTimeStamp, ProviderName = OperationName, EventId = "", Description = strcat(OperationName, " took ", DurationIn100ns / 10000.0, " milliseconds.")
)
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, ProviderName, EventId, Description, level
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

**Signal filters seen in KQL:** `Service == "StorageClient"`

---
