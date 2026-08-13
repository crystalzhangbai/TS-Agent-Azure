# Insights

> Source: **Azure Host - Azure VM** dashboard, chapter **Insights** (10 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Host Insights

### node_insights_summary

_Widget purpose:_ Host Insights

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `sc` · Type: `Single` · Widget: `Tab`
Source panel: `Insights > Host Insights`

**Tables:** `SummarizeNodeInsights`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Sc').SummarizeNodeInsights(startTime, endTime, nodeId)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Latency  Insights (Aquila)

### Get  Disk Properties for Aquila

_Widget purpose:_ Latency  Insights (Aquila)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Tab`
Source panel: `Insights > Latency  Insights (Aquila)`

**Tables:** `OsXIOSurfaceCounterTable`, `OsUltraSSDCounterTable`
**Aggregations:** `summarize arg_max(PreciseTimeStamp, CachePolicy, BlobPath, ContainerId, EncryptionFlags, T by SurfaceName` · `summarize diskProps = strcat_array(make_list(disk), "^")`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and Cluster == cluster
| extend ContainerId = tostring(split(split(SurfaceName, "_")[0], "~")[0])
| where ContainerId == containerId or SurfaceName contains vmId
| union (cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsUltraSSDCounterTable | where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and Cluster == cluster and ContainerId contains containerId)
| parse BlobPath with * "/" NewBlobPath "?" *
| extend BlobPath = case(isnotempty(NewBlobPath), NewBlobPath, BlobPath)
| extend SurfaceName = case(isempty(SurfaceName), SurfaceGUID, SurfaceName)
| extend DiskSkuType = case(IsXIOdisk == 1, "Premium SSD", 
                            BlobPath contains "md-ssd-", "Standard SSD", 
                            IsXIOdisk == 0 and BlobPath !contains "md-ssd-" and Type == 0, "Standard HDD",
                            DiskSkuType == 0, "UltraSSD",
                            DiskSkuType == 1, "Premium SSD V2","")
| summarize arg_max(PreciseTimeStamp, CachePolicy, BlobPath, ContainerId,  EncryptionFlags, Type, StorageTenant, SDFTenant, Cluster, DiskType, SlotId,  DiskSkuType, ArmId, BSId, WSId) by SurfaceName
| distinct CachePolicy, SurfaceName, BlobPath, ContainerId,  EncryptionFlags, Type, StorageTenant, SDFTenant, Cluster, DiskType, SlotId,  DiskSkuType, ArmId, BSId, WSId
| extend disk = strcat_array(pack_array(BlobPath, SlotId, DiskSkuType), "#")
| summarize diskProps = strcat_array(make_list(disk), "^")
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`, `{cluster}`, `{vmId}`

---

### Get Tracker Guid

_Widget purpose:_ Latency  Insights (Aquila)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `fa` · Type: `Single` · Widget: `Tab`
Source panel: `Insights > Latency  Insights (Aquila)`

```kusto
print new_guid()
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### Progress Counter Query

_Widget purpose:_ Latency  Insights (Aquila)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `sc` · Type: `MultiRow` · Widget: `Tab`
Source panel: `Insights > Latency  Insights (Aquila)`

```kusto
datatable(counter: int) [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### get_control_startTime

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `fa` · Type: `Single` · Widget: `Row`
Source panel: `Insights > Latency  Insights (Aquila)`

```kusto
print (queryFrom - 1h)
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### Call Latency API 4

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Sc` · Type: `Single` · Widget: `Row`
Source panel: `Insights > Latency  Insights (Aquila)`

**Tables:** `CallAquilaLatencyInsightsApi2`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Sc').CallAquilaLatencyInsightsApi2(startTime=startTime, endTime=endTime, cluster=cluster, nodeId=nodeId, containerId=containerId, vmId=vmId, allBlobDetails=allBlobDetails, blobPath=blobPath, control_startTime=control_startTime, control_endTime=control_endTime, progress_guid=progress_guid)
```

**Params:** `{startTime}`, `{endTime}`, `{cluster}`, `{nodeId}`, `{containerId}`, `{blobPath}`, `{control_startTime}`, `{control_endTime}`, `{allBlobDetails}`, `{vmId}`, `{progress_guid}`

---

### Azure Host VM Active Blobs Filter

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `Row`
Source panel: `Insights > Latency  Insights (Aquila)`

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

## Other

### Azure Host VM Azure Core RCA

_Widget purpose:_ Azure Core RCA

Cluster: `moseisley` · Database: `Air` · Type: `Table`
Source panel: `Insights > Other > Azure Core RCA`

```kusto
//GetAzureCoreRCAForVM(startTime, endTime, containerId)
GetAzureCoreRCA_V2(startTime, endTime, containerId)
//| extend RCATeam_Component = strcat(RCATeam,"_",RCAComponent)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

### Azure Host VM VmAvailability Events 

_Widget purpose:_ VM Availability Impact Events

Cluster: `vmainsight` · Database: `Air` · Type: `Table`
Source panel: `Insights > Other > VM Availability Impact Events`

**Output columns:** `Timestamp`, `ImpactAIRGroup`, `EventType`, `FailureSignature`, `ImpactDurationTimeSpan`

```kusto
GetVMAvailabilityImpactEvents(vmId, startTime, endTime)
| project Timestamp, ImpactAIRGroup, EventType, FailureSignature, ImpactDurationTimeSpan
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`

---

## VM Insights

### Container_Insights_Summary

_Widget purpose:_ VM Insights

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `sc` · Type: `Single` · Widget: `Tab`
Source panel: `Insights > VM Insights`

**Tables:** `SummarizeContainerInsights`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Sc').SummarizeContainerInsights(startTime, endTime, containerId, nodeId)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---
