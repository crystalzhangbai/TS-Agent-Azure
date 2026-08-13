# Metrics Comparison

> Source: **Azure VM Compare Investigation Guide** dashboard, chapter **Metrics Comparison** (9 queries across 3 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### get_control_startTime

_Widget purpose:_ Metrics Comparison

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `fa` · Type: `Single` · Widget: `Tab`
Source panel: `Metrics Comparison`

```kusto
print (queryFrom - 1h)
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### Retrieve Resource "Azure VM"

_Widget purpose:_ Metrics Comparison

Cluster: `AzureCM` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Tab`
Source panel: `Metrics Comparison`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and assert(isnotempty(local_containerId) or isnotempty(local_virtualMachineUniqueId), "Either a container Id or VM Id must be specified")
| where (isempty(local_containerId) or containerId == local_containerId) and (isempty(local_virtualMachineUniqueId) or virtualMachineUniqueId == local_virtualMachineUniqueId)
| union (
    cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and assert(isnotempty(local_containerId) or isnotempty(local_virtualMachineUniqueId), "Either a container Id or VM Id must be specified")
    | where (isempty(local_containerId) or ContainerId == local_containerId) and (isempty(local_virtualMachineUniqueId) or VirtualMachineUniqueId == local_virtualMachineUniqueId) and isnotempty(RoleInstanceName)
    | extend containerId = ContainerId, creationTime = tostring(CreationTime), roleInstanceName = RoleInstanceName, 
         subscriptionId = SubscriptionId, containerType = PolicyName, virtualMachineUniqueId = VirtualMachineUniqueId,
         nodeId = NodeId, tipNodeSessionId = TipNodeSessionId, tenantName = TenantName, availabilitySetName = AvailabilitySetName,
         billingType = "", roleType = RoleType, additionalContainerProperties = AdditionalContainerProperties, Tenant = ClusterName
)
| summarize arg_max(PreciseTimeStamp, creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, nodeId, tipNodeSessionId, Tenant, tenantName, availabilitySetName, billingType, roleType, additionalContainerProperties, RegionFriendlyName) by containerId
| distinct creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, containerId, nodeId, tipNodeSessionId, Tenant, tenantName, availabilitySetName, billingType, roleType, additionalContainerProperties, RegionFriendlyName
| parse roleInstanceName with "_" VMName
| extend additionalContainerProperties = parse_json(additionalContainerProperties)
| extend DiskControllerType = tostring(additionalContainerProperties.DiskControllerType)
| join kind=leftouter (
    LogContainerPolicySnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h))
    | summarize arg_min(PreciseTimeStamp, memoryInMB, hostMemoryReservationInMBytes) by Tenant, policyInstanceName
    | project Tenant, policyInstanceName, memoryInMB, hostMemoryReservationInMBytes
) on Tenant and $left.containerType == $right.policyInstanceName
| join kind=inner(
    LogClusterSnapshot
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h))
    | distinct shoeboxMdmAccountName, Tenant
) on Tenant
| join kind=leftouter (
    cluster('storageclient.eastus.kusto.windows.net').database('Fa').GuestOSDetailEtwTable
    | where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and ContainerId =~ local_containerId
    | summarize arg_max(PreciseTimeStamp, OSType, OSVersion, VMType, OSName, OSKernelVersion) by ContainerId
    | project ContainerId, GuestOSType = OSType, GuestOSName = OSName, GuestOSVersion = OSVersion, GuestOSKernelVersion = OSKernelVersion, VMType
) on $left.containerId == $right.ContainerId
| project-away Tenant1, Tenant2, policyInstanceName, ContainerId
| extend globalFrom = globalFrom, globalTo = globalTo
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_containerId}`, `{local_nodeId}`, `{local_virtualMachineUniqueId}`

---

### Get Vm Details For Container 2

_Widget purpose:_ Metrics Comparison

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Single` · Widget: `Tab`
Source panel: `Metrics Comparison`

```kusto
LogContainerSnapshot | where PreciseTimeStamp between(startTime-5h..endTime+5h) and containerId =~ containerIdentifier 
| union (
    database('AzureCP') .MycroftContainerSnapshot
    | where PreciseTimeStamp between(startTime-5h..endTime+5h) and ContainerId =~ containerIdentifier 
    | extend Tenant = ClusterName, nodeId = NodeId, containerId = ContainerId, virtualMachineUniqueId = VirtualMachineUniqueId
)
| distinct Tenant, nodeId, containerId, virtualMachineUniqueId
| distinct Tenant, nodeId, containerId, virtualMachineUniqueId
```

**Params:** `{startTime}`, `{endTime}`, `{containerIdentifier}`

---

### Azure Host VM Active Blobs Filter

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Filter` · Widget: `Row`
Source panel: `Metrics Comparison`

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

### Azure Host VM Active Blobs Filter For Container 2

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `fa` · Type: `Filter` · Widget: `Row`
Source panel: `Metrics Comparison`

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

### HeatMap_Type_Filter

Cluster: `azcore.centralus.kusto.windows.net` · Database: `fa` · Type: `Filter` · Widget: `Row`
Source panel: `Metrics Comparison`

```kusto
datatable(Value:string, Description:string)
[
    "HistogramLatencyQuantiles_HeatMap", "HistogramLatencyQuantiles (Default)",
    "OsXIOXdiskCounterTable_HeatMap", "OsXIOXdiskCounterTable",
    "OsXIOSurfaceCounterTable_HeatMap", "OsXIOSurfaceCounterTable",
    "BurstCounters_HeatMap", "BurstCounters",
    "OsBlobCacheInternalCounterTable_HeatMap", "OsBlobCacheInternalCounterTable"
]
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### Flip Baseline Container

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `fa` · Type: `Filter` · Widget: `Row`
Source panel: `Metrics Comparison`

```kusto
datatable(Value:string, Description:string)
[
    "Container1", "Compares Container2 with Container1",
    "Container2", "Compares Container1 with Container2"
]
```

**Params:** `{queryFrom}`, `{queryTo}`

---

##  

### Time Difference in Page Time Range

_Widget purpose:_  

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `fa` · Type: `Single` · Widget: `Markdown`
Source panel: `Metrics Comparison >  `

```kusto
print abs((queryTo- queryFrom)/1h)
```

**Params:** `{queryFrom}`, `{queryTo}`

---

## {{Description}} {{Value}}

### Build_HeatMap

_Widget purpose:_ {{Description}} {{Value}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `fa` · Type: `Heatmap`
Source panel: `Metrics Comparison > {{Description}} {{Value}}`

```kusto
let heatMapData =  
cluster('storageclient.eastus.kusto.windows.net').database('Sc').GetAquilaLatencyInsightsHeatMap
(
    startTime1 = tostring(iff(baseline == "Container2" or baseline == "", startTime1, startTime2)),
    endTime1 = tostring(iff(baseline == "Container2" or baseline == "", endTime1, endTime2)),
    cluster1 = tostring(iff(baseline == "Container2" or baseline == "", cluster1, cluster2)),
    nodeId1 = tostring(iff(baseline == "Container2" or baseline == "", nodeId1, nodeId2)),
    containerId1 = tostring(iff(baseline == "Container2" or baseline == "", containerId1, containerId2)),
    blobPath1 = tostring(iff(baseline == "Container2" or baseline == "", blobPath1, blobPath2)),
    startTime2 = tostring(iff(baseline == "Container2" or baseline == "", startTime2, startTime1)),
    endTime2 = tostring(iff(baseline == "Container2" or baseline == "", endTime2, endTime1)),
    cluster2 = iff(baseline == "Container2" or baseline == "", cluster2, cluster1),
    nodeId2 = iff(baseline == "Container2" or baseline == "", nodeId2, nodeId1),
    containerId2 = iff(baseline == "Container2" or baseline == "", containerId2, containerId1),
    blobPath2 = iff(baseline == "Container2" or baseline == "", blobPath2, blobPath1),
    heatMapType = heatMapType
);
let flagged = 
    heatMapData
    | where filterVerbosity == true or tostring(Health) in ("Unhealthy")
    | project RowLabel;
heatMapData
| where filterVerbosity == true or RowLabel in (flagged)
| project 
    ColumnLabel = todatetime(ColumnLabel),
    RowLabel = tostring(RowLabel),
    Health = tostring(Health),
    Value = toreal(Value),
    Min = toreal(Min),
    Max = toreal(Max),
    Normalized = toreal(Normalized)
| sort by ColumnLabel asc, RowLabel asc
```

**Params:** `{startTime1}`, `{endTime1}`, `{cluster1}`, `{containerId1}`, `{nodeId1}`, `{blobPath1}`, `{startTime2}`, `{endTime2}`, `{cluster2}`, `{containerId2}`, `{nodeId2}`, `{blobPath2}`, `{heatMapType}`, `{filterVerbosity}`, `{baseline}`

---
