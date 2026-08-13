# Emerging Issues (part 4/4)

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Emerging Issues** (9 queries, part 4 of 4).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## VM Impacted after Host Agent Update

### LogContainerHealthSnapshot

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > VM Impacted after Host Agent Update > Check LogContainerHealthSnapshot`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo 
| where containerId == queryContainerId and faultInfo has "0x8abc0308"
| project PreciseTimeStamp, nodeId, containerId, roleInstanceName, faultInfo
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---

### TMMgmtNodeEventsEtwTable_UnexpectedRestart DS

_Widget purpose:_ TMMgmtNodeEventsEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Emerging Issues > VM Impacted after Host Agent Update > Check TMMgmtNodeEventsEtwTable > TMMgmtNodeEventsEtwTable`

```kusto
TMMgmtNodeEventsEtwTable  
| where  NodeId == query_NodeId
| where PreciseTimeStamp >= query_StartTime
| where PreciseTimeStamp <= query_EndTime
| where Message contains "0x8ABC0308"
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, Message
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_NodeId}`

**Signal filters seen in KQL:** `Message contains "0x8ABC0308"`

---

### VMA2 DS

_Widget purpose:_ VMA

Cluster: `Vmainsight` · Database: `vmadb` · Type: `Table`
Source panel: `Emerging Issues > VM Impacted after Host Agent Update > Check VMA > VMA`

```kusto
VMA 
| where PreciseTimeStamp >= query_StartTime and PreciseTimeStamp <= query_EndTime 
| where NodeId == query_NodeId and RCALevel1 =="ContainerFault" and RCALevel2 == "ContainerFaultCode 10005_NSRaised_RetriesFailed_CreateContainer_0x8abc0308_"
| distinct  PreciseTimeStamp,NodeId, RoleInstanceName,RCAEngineCategory,RCALevel1, RCALevel2, RCA_CSS
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_NodeId}`

---

## VM Metric Drops due to HyperVStorageStack Overlogging

### HyperVStorageStackTable_all DS

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > VM Metric Drops due to HyperVStorageStack Overlogging > HyperVStorageStackTable_all`

```kusto
HyperVStorageStackTable
| where NodeId == query_node
| where TIMESTAMP between (todatetime(query_startTime) .. todatetime(query_endTime))
| count
```

**Params:** `{query_startTime}`, `{query_endTime}`, `{query_node}`

---

### HyperVStorageStackTable_vhdmp DS

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > VM Metric Drops due to HyperVStorageStack Overlogging > HyperVStorageStackTable_vhdmp`

```kusto
HyperVStorageStackTable
| where NodeId == query_node
| where TIMESTAMP between (todatetime(query_startTime) .. todatetime(query_endTime))
| where Message contains "VhdmpiVhdExecuteScsi"
| count
```

**Params:** `{query_startTime}`, `{query_endTime}`, `{query_node}`

**Signal filters seen in KQL:** `Message contains "VhdmpiVhdExecuteScsi"`

---

### HyperVStorageStackTable_writeError DS

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > VM Metric Drops due to HyperVStorageStack Overlogging > HyperVStorageStackTable_writeError`

```kusto
HyperVStorageStackTable
| where NodeId == query_node
| where TIMESTAMP between (todatetime(query_startTime) .. todatetime(query_endTime))
| where Message contains "WriteError"
| count
```

**Params:** `{query_startTime}`, `{query_endTime}`, `{query_node}`

**Signal filters seen in KQL:** `Message contains "WriteError"`

---

## VM reboot when trying to detach disks (UpdateContainer failure 0x80070961)

### VM reboot when trying to detach disks

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > VM reboot when trying to detach disks (UpdateContainer failure 0x80070961)`

```kusto
VmServiceVirtualDiskOperations
| where PreciseTimeStamp between (startTime .. endTime) and NodeId =~ query_NodeId and Operation == "DestroyVirtualDisk" and ResultCode in ("0x80070961","0x8abc0303") and ContainerId == query_ContainerId
| join kind=inner (cluster("azcsupfollower.kusto.windows.net").database("AzureCM").TMMgmtNodeEventsEtwTable
| where TIMESTAMP between (startTime .. endTime) 
| where NodeId =~ query_NodeId and Message has query_ContainerId and Message has "since data disks change") on $left.NodeId == $right.NodeId
| project PreciseTimeStamp, ContainerId, Operation, Stage,  DiskType, DiskFullPath, DiskBackingStore, ResultCode, DurationMillis, DiskLocation, Message
| take 1
```

**Params:** `{startTime}`, `{endTime}`, `{query_NodeId}`, `{query_ContainerId}`

---

## VM Restarts after Internal Shutdown

### CAD_StandardStorage DS

_Widget purpose:_ CAD

Cluster: `vmainsight.kusto.windows.net` · Database: `CAD` · Type: `Table`
Source panel: `Emerging Issues > VM Restarts after Internal Shutdown > Check CAD > CAD`

```kusto
CAD
| where PreciseTimeStamp > query_BeginTime and PreciseTimeStamp < query_EndTime
| where ContainerId == query_ContainerId and Storage_AccountName contains "md-hdd"
| project StartTime, EndTime, RoleInstanceName, AvailabilityState, VmVhds, Storage_AccountName, Storage_VhdCount, TotalDowntimeInMin, TotalUptimeInMin, DurationInMin
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

### WindowsEvents_Internalrestart DS

_Widget purpose:_ WindowsEventTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Emerging Issues > VM Restarts after Internal Shutdown > Check WindowsEventTable > WindowsEventTable`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId
| where EventId == 18508 and Description has query_ContainerId
| project-rename InternalStopTimestamp = TIMESTAMP
| join kind=inner (cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId
| where EventId == 18500 and Description has query_ContainerId) on $left.NodeId == $right.NodeId
| project-rename StartVMTimestamp = TIMESTAMP
| where (StartVMTimestamp - InternalStopTimestamp) between (9min .. 11min)
| project InternalStopTimestamp,EventId,ProviderName, Description, StartVMTimestamp, EventId1,ProviderName1,Description1
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`, `{query_ContainerId}`

---
