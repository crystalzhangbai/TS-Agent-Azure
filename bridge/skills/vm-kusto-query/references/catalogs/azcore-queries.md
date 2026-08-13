# AzCore/RDOS Queries — HyperV, VM Health, Node Service, OS Logs, Performance

Cluster: `azcore.centralus.kusto.windows.net` (also `Rdosmc` for Mooncake, `Rdosff` for FairFax)
Database: `Fa`

---

## Windows Events

### WindowsEventTable — Host node Windows events

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between(datetime({StartTime})..datetime({EndTime}))
| where NodeId == '{NodeId}'
| where not (ProviderName == "NETLOGON" and EventId == 3095)
| where not (ProviderName == 'IPMIDRV' and EventId == 1004)
| where not (ProviderName == "VhdDiskPrt" and EventId == 47)
| where ProviderName <> "CMClientLib"
| where EventId <> 7000 and EventId <> 1023
| where EventId !in (505, 504, 146, 145, 142)
| project todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by TimeCreated asc
```

EventId filter tips:
- `18500, 18502, ...18560` — HyperV container events
- `2004, 3050, 3122, 12030` — low memory condition
- `ProviderName contains "UpdateNotification"` — VM-PHU update details
- Extended cross-correlation list for VhdDiskPrt Event 16 / disk-IO / lease investigation: `EventId in (2004, 129, 147, 149, 157, 153, 51, 52, 7, 41, 47, 17, 11, 16, 140, 500, 501, 18590, 23, 55, 130, 131, 141, 154, 482, 1, 2, 35, 305, 3050, 3122, 12030, 12817, 18560)` plus the special pattern `EventId == 504 and Description contains "srbstatus 5"`. Used by [VhdDiskPrt Event 16 Investigation TSG](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495986/Azure_Virtual-Machine_Performance_TSG_VhdDiskPrts_Events_Investigation) to find disk hardware / lease / memory events around the time of a VhdDiskPrt Event 16.

### WindowsEventTable — Event 505 local disk latency histogram parsing

Event 505 contains a histogram of local disk I/O latency. Parse the `5120+ms`, `10000+ms`, and `20000+ms` buckets to detect tail-latency outliers on the host's local disks (impacts host caching and temp drive).

```kusto
let dateTime_StartTimePFD = datetime_add('day', +1, datetime({StartTime}));
let dateTime_StartTime = datetime_add('hour', -1, dateTime_StartTimePFD);
let dateTime_EndTime = datetime_add('hour', +1, dateTime_StartTimePFD);
cluster("Azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (dateTime_StartTime..dateTime_EndTime) and EventId == 505 and NodeId == "{NodeId}"
| extend length = strlen(Description), latstring = indexof(Description,"20000+ms")
| extend latencies = substring(Description,latstring+26, length-latstring)
| extend point = indexof(latencies, "."), llen = strlen(latencies)
| extend latfinal = substring(latencies, 0, point)
| extend commasix= split(latfinal,",",8), commaten= split(latfinal,",",9), commatwen= split(latfinal,",",10), commatwenplus= split(latfinal,",",11)
| extend csixlen = strlen(commasix), ctenlen = strlen(commaten), ctwenlen = strlen(commatwen), ctwenplen = strlen(commatwenplus)
| extend bucketsix = substring(commasix,2,csixlen-4)
| extend bucketten = substring(commaten,2,ctenlen-4)
| extend buckettwen = substring(commatwen,2,ctwenlen-4)
| extend buckettwenplus = substring(commatwenplus,2,ctwenplen-4)
| extend length3 = strlen(Description), latstring3 = indexof(Description,"10000+ms")
| extend latencies3 = substring(Description,latstring3+26, length3-latstring3)
| extend point3 = indexof(latencies3, "."), llen = strlen(latencies3)
| extend latfinal3 = substring(latencies3, 0, point3)
| extend commaten2= split(latfinal3,",",12), commatenplus2= split(latfinal3,",",13)
| extend ctenlen2 = strlen(commaten2), ctenplen2 = strlen(commatenplus2)
| extend bucketten2 = substring(commaten2,2,ctenlen2-4)
| extend buckettenplus2 = substring(commatenplus2,2,ctenplen2-4)
| extend length2 = strlen(Description), point2 = indexof(Description,"5120+ms")
| extend latency = substring(Description,point2+17, length2-point2)
| extend llen = strlen(latency), commafive= split(latency,",",3), commafiveplus= split(latency,",",4)
| extend clen = strlen(commafive), cplen = strlen(commafiveplus)
| extend bucketfive = substring(commafive,2,clen-4)
| extend bucketfiveplus = substring(commafiveplus,2, cplen-5)
| where ((point2 > 0 and toint(bucketfive) > 50) or (point2 > 0 and toint(bucketfiveplus) > 0)) or ((latstring3 > 0 and toint(bucketten2) > 0) or (latstring3 > 0 and toint(buckettenplus2) > 0)) or ((latstring > 0 and toint(bucketsix) > 50) or (latstring > 0 and (toint(bucketten) > 0 or toint(buckettwen) > 0 or toint(buckettwenplus) > 0)))
| project Description
| take 5
```

Interpretation:
- Returns rows where one of the higher latency buckets is non-trivial — a real signal that host local disks (HDD/SSD backing temp drive and host cache) saw multi-second I/O.
- Often paired with WindowsEventTable Event 147 (">30s IO") for the same window — see TSG [Host Node Investigation_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495968).
- If hits land inside a performance impact window, VM cached reads (`CurAvgRxLatInms` in Host Analyzer) and temp-drive writes will be impacted.

### WindowsEventTable — EventId 12817 (WS2012R2 IDE-mode resource VHD slow I/O)

Host raises EventId 12817 when it detects a guest VM accessing the resource (temp) VHD via the slow IDE path instead of the SCSI/VSP path. Only affects **Windows Server 2012 R2** guests where the I/O driver fell back to IDE; the symptom is sustained `<10 MB/s` on the resource VHD even though the underlying local disk is healthy. Sometimes the event is not reported at all yet a guest-side benchmark still measures poor perf — escalate based on guest measurement in that case.

**Per-node lookup (known NodeId + window):**

```kusto
cluster('azcsupfollower').database('azurecm').WindowsEventTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where EventId == "12817"
| project TimeCreated, Computer, Cluster, EventId, ProviderName, Description
| order by TimeCreated asc
```

**Subscription-wide sweep (find all affected VMs in a sub for the last 30 m):**

```kusto
let subid = "{SubscriptionId}";
let roleinstances = cluster('azcsupfollower').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp > ago(2h) and subscriptionId == subid
| summarize count() by Tenant, nodeId, containerId, roleInstanceName, Region
| project containerId, roleInstanceName, Region;
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp > ago(30m) and EventId == 12817
  and tostring(split(Description, "'")[1]) in (roleinstances)
  and EventOccurrenceCount > 5
| extend containerId = tostring(split(Description, "'")[1])
| summarize sum(EventOccurrenceCount) by containerId, Cluster, NodeId, Description
| join kind=inner (roleinstances) on containerId
| project Region, roleInstanceName, TotalEvents = sum_EventOccurrenceCount, containerId
```

Interpretation:
- `TotalEvents > 5` per container — strong signal the guest is on the IDE path.
- The container roleInstanceName extracted from `Description` (between single quotes) maps back to the customer VM via `LogContainerSnapshot`.
- **Mitigation**: WS2012R2 is the only affected SKU and is end-of-extended-support — guidance is to upgrade to WS2016+. No host-side fix exists.

Reference: [Poor IO Performance on Windows Server 2012 R2_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FPoor-IO-Performance-on-Windows-Server-2012-R2_Perf).

---

## VM Performance

### VmCounterFiveMinuteRoleInstanceCentralBondTable — Container performance

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where VmId == '{ContainerId}'
| project PreciseTimeStamp, Cluster, TenantId, NodeId, VmId, RoleInstanceId, CounterName, SampleCount, AverageCounterValue, MinCounterValue, MaxCounterValue
```

### VmShoeboxCounterTable — Shoebox source data

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmShoeboxCounterTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where VmId == "{ContainerId}"
| project PreciseTimeStamp, Cluster, RoleInstanceId, VmResourceType, MDMCounterName, MDMAccountName, DurationInMinutes, AverageValue
```

---

## HyperV Investigation

### HyperVHypervisorTable — Hypervisor version

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVHypervisorTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId == "{NodeId}"
| where TaskName in ('Hyp version', 'Hal config', 'Hypervisor hotpatch state') or TaskName contains 'config'
| project PreciseTimeStamp, Cluster, TaskName, Message
```

### HyperVAnalyticEvents — HyperV errors & warnings

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").HyperVAnalyticEvents
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == '{NodeId}' and Level < 4
| extend leveldescription = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, NodeId, Level, leveldescription, ProviderName, TaskName, EventMessage, Message
```

### HyperVWorkerTable — HyperV worker events

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").HyperVWorkerTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between(datetime({StartTime})..2h)
| where Message contains "{ContainerId}" or Message contains "{VMId}"
| where Level <= 4
| project PreciseTimeStamp, EventId, Level, ProviderName, TaskName, Message
```

### HyperVWorkerTable — Memory allocation delays (>120s)

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").HyperVWorkerTable
| where PreciseTimeStamp between(datetime({StartTime})..datetime({EndTime}))
| where NodeId == "{NodeId}"
| where TaskName == "TimeSpentInMemoryOperation" and Message has "ReservingRam" and Message has "CreateRamMemoryBlocks"
| extend length = strlen(Message), secstring = indexof(Message, "Seconds")
| extend strSeconds = substring(Message, secstring+9, length-secstring)
| extend Seconds = trim_end("}", strSeconds)
| where todouble(Seconds) > 120
| project PreciseTimeStamp, Message, Seconds
```

### HyperVVmmsTable — VMMS events

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").HyperVVmmsTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| project PreciseTimeStamp, Message, Cluster, EventMessage
```

### WindowsEventTable — Hyper-V Worker memory operation failures

Used when investigating `FabricCallback / InternalPowerOffVMOperation / DetachedAsync-Post` — host-side memory allocation failures that surface as VM crash/power-off on supplied `NodeId`. The three EventIds map to Hyper-V Worker memory-operation failures.

```kusto
cluster('azcore.centralus.kusto.windows.net').database('fa').WindowsEventTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId == "{NodeId}"
| where ProviderName contains "Microsoft-Windows-Hyper-V-Worker"
| where EventId in ("12030", "3122", "3050")
| project PreciseTimeStamp, EventId, TaskName, Message
```

Pair with the `TimeSpentInMemoryOperation` query above to confirm the affected VM IDs and the operation that timed out. TSG anchor: [FabricCallback-InternalPowerOffVMOperation-DetachedAsync-Post wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1084288).

### GetHyperVVmIdFromContainerId() — Cross-table function (ContainerId → HyperV VmId)

Hyper-V worker / VMMS / WindowsEventTable rows on Azure RDOS use the **Hyper-V VmId** (a GUID generated when the VM is registered with the host) — NOT the platform `ContainerId`. This helper function maps the two so you can pivot from `LogContainerSnapshot` (ContainerId) into Hyper-V-side data. Required to chase `FabricCallback / InternalPowerOff` cases end-to-end.

```kusto
let _hyperVVmId = toscalar(
  cluster('azcore.centralus.kusto.windows.net').database("SharedWorkspace")
    .GetHyperVVmIdFromContainerId("{NodeId}", "{ContainerId}", datetime({StartTime}), datetime({EndTime}))
);
// _hyperVVmId now usable to filter Hyper-V tables on Message contains _hyperVVmId
// or WindowsEventTable | where Message contains _hyperVVmId
```

Typical guest event IDs you'll then filter on (in `Fa.WindowsEventTable` or guest-collected logs):
- `18601` — VM successfully booted
- `18500` — VM successfully started
- Other Hyper-V Worker / guest-OS error IDs as they appear

---

## Guest KVP Data (Cross-Layer Provisioning Trace)

### IfxOperationV2v1EtwTable — Guest OS KVP items / KVPData

KVP (Key-Value Pair) is the channel the in-guest agent uses to report state to the host. Used during `OSProvisioningTimedOut` investigation to confirm whether the in-guest agent ever talked back, what version it was, and what it reported. Required when CRP says "VM brought up successfully" but the customer's image / cloud-init still fails — the KVP trail proves whether the agent inside the guest actually reached out.

Pattern: first query gets `ActivityId`s correlated with the target ContainerId via `GuestOsKVPItems`, then second query pulls the actual `KVPData` payloads.

```kusto
let ActivityIds = cluster("azcore.centralus.kusto.windows.net").database("Fa").IfxOperationV2v1EtwTable
  | where PreciseTimeStamp > ago(10d)
  | where OperationName == "GuestOsKVPItems"
  | where ContextInCsv contains "{ContainerId}"
  | project ActivityId;
cluster("azcore.centralus.kusto.windows.net").database("Fa").IfxOperationV2v1EtwTable
| where PreciseTimeStamp > ago(10d)
| where OperationName == "KVPData"
| where ActivityId in (ActivityIds)
| project PreciseTimeStamp, ActivityId, OperationName, ContextInCsv
```

Use the `ContextInCsv` payload to extract agent version, last reported state, and any error keys the guest pushed up before the timeout. TSG anchor: [Provisioning Workflow wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495735).

---

## VM Lifecycle Geneva Trace (Cross-Container)

### acccvmtmgeneva.Log — VM lifecycle Geneva trace (by tagId / ContainerId)

End-to-end Geneva trace for VM lifecycle, keyed by `tagId` (= ContainerId). Use this when you need a single chronological log of everything the platform did to a specific VM across multiple container lifetimes (Redeploy / LM changes the ContainerId, so collect all of them first via `MycroftContainerSnapshot`). Required for deep `FabricCallback` / `InternalPowerOff` investigations where the per-table queries don't give you the cross-component picture.

```kusto
let _vmId = "{VirtualMachineUniqueId}";
let containerIds = toscalar(
  cluster("azcore.centralus").database("AzureCP").MycroftContainerSnapshot
  | where PreciseTimeStamp > ago(6d) and VirtualMachineUniqueId == _vmId
  | summarize make_set(ContainerId)
);
cluster("azcore.centralus").database("acccvmtmgeneva").Log
| where PreciseTimeStamp > ago(6d) and tagId in (containerIds)
| project PreciseTimeStamp, tagId, Message, Component, Level
| order by PreciseTimeStamp asc
```

TSG anchor: [FabricCallback-InternalPowerOffVMOperation-DetachedAsync-Post wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1084288).

### HyperVStorageStackTable — Storage stack events

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").HyperVStorageStackTable
| where NodeId == "{NodeId}" and PreciseTimeStamp between(datetime({StartTime})..2h)
| where Message contains "{ContainerId}" or Message contains "{VMId}"
| extend leveldescription = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, Level, leveldescription, ProviderName, TaskName, Message
```

### HyperVVidTable — VID (memory) errors

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").HyperVVidTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| project PreciseTimeStamp, Cluster, Level, ProviderName, OpcodeName, KeywordName, TaskName, Task, EventMessage, Message
```

Note: VID = Virtual Infrastructure Driver. Memory errors: EventId 5043, 5039, 5038.

### HyperVStorageStackTable — NVMe controller error investigation

Investigate NVMe controller failures on a host node; filter for critical error codes `c000050a` (I/O error) and `c0000184` (failed to start controller).

```kusto
let queryFrom = {_StartTime};
let queryTo   = {_EndTime};
let nodeId    = '{NodeId}';
cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVStorageStackTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId =~ nodeId
| where ProviderName contains "nvme"
| where Level <= 2
| where Message has 'c000050a' or Message has 'c0000184'
| project PreciseTimeStamp, NodeId, Message
```

Interpretation:
- `c000050a` — NVMe I/O error (disk controller communication failure)
- `c0000184` — Failed to start NVMe controller
- Level ≤ 2 filters for errors only (1=fatal, 2=error)
- If present during a VM reboot window, suspect NVMe hardware failure; escalate to hardware team
- Cross-reference with `DiskHealthRawStateEtwTable` for per-disk health correlation

---

## VM Health (RDOS perspective)

### VmHealthRawStateEtwTable — VM availability (logged every 15s)

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").VmHealthRawStateEtwTable
| where ContainerId == "{ContainerId}"
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
```

Note: Column `IsVscStateOperational` is always `0` on `AllDisksInStripe` nodes. Use NetVMA/VFPPortMetrics for correct VSC state.

### VmHealthTransitionStateEtwTable — VM state changes only

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").VmHealthTransitionStateEtwTable
| where ContainerId == "{ContainerId}"
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
```

---

## Node Service

### NodeServiceOperationEtwTable — StartContainer timing

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").NodeServiceOperationEtwTable
| where PreciseTimeStamp between (({StartTime}) .. ({EndTime}))
| where NodeId =~ '{NodeId}'
| where Identifier contains "{ContainerId}"
| project PreciseTimeStamp, OperationName, Identifier, Result, ResultCode, RequestTime, CompleteTime
```

If StartContainer > 5 minutes, it indicates performance issues on the node.

### NodeServiceEventEtwTable — RD Agent / node service events

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").NodeServiceEventEtwTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == "{NodeId}"
| where Message contains "{ContainerId}"
```

---

## OS Logs & File Versions

### OsLoggerTable — OS error logs

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").OsLoggerTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where ComponentName != "XDiskSvc" and LogErrorLevel == "Error"
| project PreciseTimeStamp, Cluster, NodeId, ActivityId, ComponentName, FunctionName, LogErrorLevel, ResultCode, ErrorDetails
```

### OsFileVersionTable — File version changes on node

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").OsFileVersionTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == "{NodeId}"
| where FileName contains "storahci"
| project PreciseTimeStamp, Cluster, NodeId, FileName, FileVersion
```

---

## Guest Agent & Extensions

### GuestAgentExtensionEvents — Guest agent heartbeat & extension status

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where ContainerId == '{ContainerId}'
| where PreciseTimeStamp > ago(2h)
| where Operation in ('HeartBeat', 'ReportStatus', 'VmSettingsSummary')
| top 10 by PreciseTimeStamp desc
| project PreciseTimeStamp, GAVersion, OSVersion, Operation, OperationSuccess,
    Name, Version, Message, ContainerId, VMId
```

Key columns:
- `Operation` — `HeartBeat` (agent alive), `ReportStatus` (status report to CRP), `VmSettingsSummary` (wireserver comms)
- `OperationSuccess` — `True` = healthy, `False` = issue
- `GAVersion` — e.g. `WALinuxAgent-2.15.0.1`
- `Name` / `Version` — extension name & version (for extension-specific events)
- `Message` — heartbeat counter, error details, extension status info

### GuestAgentExtensionEvents — All extension errors

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where ContainerId == '{ContainerId}'
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where OperationSuccess == false
| project PreciseTimeStamp, GAVersion, OSVersion, Operation, Name, Version, Message, ContainerId, VMId
```

---

## Network & VFP Investigation (Host-Side Version & Deployment)

Cluster: `azcore.centralus.kusto.windows.net` | Database: `Fa` / `OvlProd`

Host-side VFP schema, version, and deployment-folder inspection. For data-plane
traffic / flow analysis (VfpFlowStatsTable, VfpRuleTable), explore the same
`Fa` database with `.show tables` filtered by `Vfp`.

### Schema Discovery

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VfpOperationalTable | getschema
```

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VfpPortMetrics | getschema
| where ColumnName contains "ersion" or ColumnName contains "ajor" or ColumnName contains "inor"
```

```kusto
cluster('Azurecm').database('AzureCM').LogNodeSnapshot | getschema
| where ColumnName contains_cs "vfp" or ColumnName contains_cs "Vfp" or ColumnName contains_cs "VFP"
    or ColumnName contains_cs "Major" or ColumnName contains_cs "Minor"
```

### VfpOperationalTable — Query VFP data by NodeId

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VfpOperationalTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId in ({NodeIds})
| project PreciseTimeStamp, NodeId, *
| take 10
```

### OverlakeUnitStatusTable — VFP unit version on SoC nodes

```kusto
set nopartialfailures = false;
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').OverlakeUnitStatusTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == '{SoCId}'
| where Name contains "vfp" or Name contains "VFP" or Name contains "virtualfiltering"
| project PreciseTimeStamp, NodeId, UnitName, Name, Version, ActiveState
| order by PreciseTimeStamp desc
| take 20
```

### OsFileVersionTable — VFP driver file version

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').OsFileVersionTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId in ({NodeIds})
| where FileName contains "vfp" or FileName contains "VFP"
| project PreciseTimeStamp, NodeId, FileName, FileVersion, ProductVersion
| take 20
```

### OverlakeDeploymentFolderVersions — VFP deployment folder version

```kusto
set nopartialfailures = false;
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').OverlakeDeploymentFolderVersions
| where TIMESTAMP >= datetime({StartTime}) and TIMESTAMP <= datetime({EndTime})
| where MachineName contains '{SoCIdPrefix}'
| where FolderName contains "VFP" or FolderName contains "vfp" or ServiceName contains "VFP" or ServiceName contains "vfp"
| project TIMESTAMP, MachineName, FolderName, ServiceName, CurrentVersion, CurrentServiceVersion
| take 20
```

### WindowsEventTable — VFP-related events on host nodes

```kusto
set nopartialfailures = false;
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId in ({NodeIds})
| where Message contains "VFP" or Message contains "vfp" or ProviderName contains "VFP"
| project PreciseTimeStamp, NodeId, ProviderName, EventId, Message
| take 20
```

---

## Overlake / SoC Inventory

Cluster: `azcore.centralus.kusto.windows.net` | Database: `OvlProd`

Deployment-folder and service inventory for SoC / Overlake nodes (used in
SoC / Boost-for-Storage / VFP version investigations).

### OverlakeDeploymentFolderVersions — All folders on a SoC node

```kusto
set nopartialfailures = false;
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').OverlakeDeploymentFolderVersions
| where TIMESTAMP >= datetime({StartTime}) and TIMESTAMP <= datetime({EndTime})
| where MachineName contains '{SoCIdPrefix}'
| summarize any(CurrentServiceVersion), any(CurrentVersion) by FolderName
| order by FolderName asc
```

### OverlakeUnitStatusTable — All services with versions on a node

```kusto
set nopartialfailures = false;
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').OverlakeUnitStatusTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == '{SoCId}'
| summarize any(Version) by Name
| order by Name asc
```

### OverlakeUnitStatusTable — Services with non-empty versions only

```kusto
set nopartialfailures = false;
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').OverlakeUnitStatusTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == '{SoCId}'
| where Version != ""
| summarize any(Version) by Name
| order by Name asc
```

### Schema reference

```kusto
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').OverlakeDeploymentFolderVersions | getschema
```

```kusto
cluster('Azurecm').database('AzureCM').LogNodeSnapshot | getschema
| where ColumnName contains "ersion" or ColumnName contains "ndpa" or ColumnName contains "agent" or ColumnName contains "driver"
```

---

## Storage Host-Side Investigation

### StorVscEventsTable — Storage VSC (Virtual Storage Client) events

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').StorVscEventsTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == "{NodeId}"
| where ContainerId == "{ContainerId}" or Message contains "{ContainerId}"
| project PreciseTimeStamp, NodeId, Level, ProviderName, TaskName, EventMessage, Message
| order by PreciseTimeStamp asc
```

Interpretation:
- VSC events relate to the guest-to-host storage path
- Errors here can cause disk IO failures inside the VM
- Correlate with `HyperVStorageStackTable` for the full storage stack picture

### OsBlobCacheInternalCounterTable — Blob cache write congestion / paused-writes counter

Use to detect the "AirDiskBlip BlobCache Write during Congestion" driver bug (DPP 153 fix). Run together with `HyperVStorageStackTable` filtered on bug GUID `a271beec-e1d3-4217-ae2b-74f075270dcf` and `AirDiskIOBlipEvents` (vmainsight) for the three-step confirmation flow in the TSG.

```kusto
let startTime = datetime({StartTime});
let endTime   = datetime({EndTime});
let nodeId    = "{NodeId}";
cluster("azcore.centralus.kusto.windows.net").database("Fa").OsBlobCacheInternalCounterTable
| where PreciseTimeStamp > startTime and PreciseTimeStamp < endTime
| where NodeId in~ (nodeId)
| project PreciseTimeStamp, DeltaFUnmapLinkReferenced, DeltaBSWaitForOldData, DeltaBSWaitForWriteLimit,
    BSPausedWrites, DeltaBSPausedWrites, DeltaBSPausedWritesTimeout, BSPausedWritesTimeout, DeltaBSLargeReadCount
```

Interpretation:
- `DeltaBSPausedWrites > 0` or `DeltaBSPausedWritesTimeout > 0` while `DeltaBSWaitForOldData > 0` → blob cache aggressively paused writes (the documented bug pattern).
- Pair with `HyperVStorageStackTable` filtered on `EventMessage has "a271beec-e1d3-4217-ae2b-74f075270dcf"` to confirm the driver bug GUID is firing.
- Mitigation: change disk cache to `ReadOnly` or `None`; permanent fix in DPP 153 rollout.
- TSG: [AirDiskBlip BlobCache Write during Congestion_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/AirDiskBlip-BlobCache-Write-during-Congestion_Perf).

### OsVhddiskEventTable — VhdDiskPrt Event 2/3/16 binary data parse

The rich diagnostic data for VhdDiskPrt Events 2, 3, and 16 lives in `ParamBinary1` as a hex blob; little-endian substring extraction is the only way to get `ErrorCode`, `ClientRequestId`, `HttpCode`, sequence numbers, etc. Use after spotting Event 2/3/16 in `WindowsEventTable`.

**Compact form (Event 16, error code only):**

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').OsVhddiskEventTable
| where PreciseTimeStamp between(datetime({StartTime})..datetime({EndTime}))
| where NodeId == '{NodeId}' and EventId == 16
| extend ErrorCode = strcat(substring(ParamBinary1, 46, 2), substring(ParamBinary1, 44, 2), substring(ParamBinary1, 42, 2), substring(ParamBinary1, 40, 2))
| project PreciseTimeStamp, ParamBinary1, ErrorCode
```

**Full form (Event 2/3, all fields):**

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').OsVhddiskEventTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| extend ErrorCode      = strcat(substring(ParamBinary1, 46, 2), substring(ParamBinary1, 44, 2), substring(ParamBinary1, 42, 2), substring(ParamBinary1, 40, 2)),
         ClientRequestId = strcat(substring(ParamBinary1, 94, 2), substring(ParamBinary1, 92, 2), substring(ParamBinary1, 90, 2), substring(ParamBinary1, 88, 2),
                                  substring(ParamBinary1, 86, 2), substring(ParamBinary1, 84, 2), substring(ParamBinary1, 82, 2), substring(ParamBinary1, 80, 2)),
         Time           = strcat(substring(ParamBinary1, 102, 2), substring(ParamBinary1, 100, 2), substring(ParamBinary1, 98, 2), substring(ParamBinary1, 96, 2)),
         LocalPort      = strcat(substring(ParamBinary1, 106, 2), substring(ParamBinary1, 104, 2)),
         PendingRequest = substring(ParamBinary1, 108, 2),
         RxCxnTimeoutFactor = substring(ParamBinary1, 110, 2),
         LastStatus     = strcat(substring(ParamBinary1, 150, 2), substring(ParamBinary1, 148, 2), substring(ParamBinary1, 146, 2), substring(ParamBinary1, 144, 2)),
         SequenceNumber = strcat(substring(ParamBinary1, 158, 2), substring(ParamBinary1, 156, 2), substring(ParamBinary1, 154, 2), substring(ParamBinary1, 152, 2)),
         Offset         = strcat(substring(ParamBinary1, 174, 2), substring(ParamBinary1, 172, 2), substring(ParamBinary1, 170, 2), substring(ParamBinary1, 168, 2),
                                 substring(ParamBinary1, 166, 2), substring(ParamBinary1, 164, 2), substring(ParamBinary1, 162, 2), substring(ParamBinary1, 160, 2)),
         IoLength       = strcat(substring(ParamBinary1, 182, 2), substring(ParamBinary1, 180, 2), substring(ParamBinary1, 178, 2), substring(ParamBinary1, 176, 2)),
         RecvStatus     = strcat(substring(ParamBinary1, 190, 2), substring(ParamBinary1, 188, 2), substring(ParamBinary1, 186, 2), substring(ParamBinary1, 184, 2)),
         HttpCode       = strcat(substring(ParamBinary1, 198, 2), substring(ParamBinary1, 196, 2), substring(ParamBinary1, 194, 2), substring(ParamBinary1, 192, 2)),
         Retries        = substring(ParamBinary1, 200, 2),
         Flags          = substring(ParamBinary1, 202, 2),
         ResubmitCount  = substring(ParamBinary1, 204, 2),
         TxCxnTimeoutFactor = substring(ParamBinary1, 206, 2)
| project ClientRequestId, Time, LocalPort, PendingRequest, RxCxnTimeoutFactor, LastStatus, SequenceNumber,
    Offset, IoLength, RecvStatus, HttpCode, Retries, Flags, ResubmitCount, TxCxnTimeoutFactor, ParamBinary1
```

Common Event 2/3 error codes (look up at `errors/` or via `net helpmsg`):
- `0xc0000241` — `STATUS_CONNECTION_ABORTED` (network)
- `0x81700038` — `XDiskSequenceNumberMismatch`
- `0xc00000b5` — `STATUS_IO_TIMEOUT`
- `0xC0000120` — `STATUS_CANCELLED`
- `0xC00000A3` — `STATUS_DEVICE_NOT_READY` (usually guest throttling)
- `0xc0000196` — `STATUS_REMOTE_SESSION_LIMIT` (usually guest throttling)

References: [VhdDiskPr Event 2 and 3_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/VhdDiskPr-Event-2-and-3_Perf), [VhdDiskPrt Event 16 Investigation_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/VhdDiskPrt-Event-16-Investigation_Perf).

### DiskHealthRawStateEtwTable — Per-disk health on the node

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').DiskHealthRawStateEtwTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where NodeId == "{NodeId}"
| where ContainerId == "{ContainerId}"
| project PreciseTimeStamp, ContainerId, NodeId, DiskId, IsHealthy,
    LatencyMs, IOPSRead, IOPSWrite, ThroughputReadBytesPerSec, ThroughputWriteBytesPerSec
| order by PreciseTimeStamp asc
```

Interpretation:
- `IsHealthy == false` — disk marked unhealthy on the host
- `LatencyMs` > 500 — high IO latency (may cause guest OS disk timeouts)
- Sudden IOPS drop to 0 — disk access lost
- Cross-reference with `AirDiskIOBlipEvents` in VMInsight for blip correlation

---

## Boot & Provisioning

### BootDiagnosticsTable — VM boot diagnostics (serial console)

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').BootDiagnosticsTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where ContainerId == "{ContainerId}"
| project PreciseTimeStamp, ContainerId, NodeId, BootStage, Message, Duration
| order by PreciseTimeStamp asc
```

Interpretation:
- Tracks VM boot stages (BIOS, OS loader, kernel init, etc.)
- `BootStage` — identifies which boot phase the VM is in
- Long `Duration` in a specific stage indicates boot hang
- Useful for diagnosing VMs that don't come back after restart

---

## VM Performance Overview (Multi-Metric Pivot)

### VmCounterFiveMinuteRoleInstanceCentralBondTable — All key metrics in one view (5-min granularity)

Produces a single pivot table with CPU (Avg + Max), Memory (Available GB + Pressure), Network (In/Out MB), and Disk (Read/Write KBps) per 5-minute bucket. Useful for quickly correlating CPU spikes with other resource changes.

**Note**: `VmId` in this table is the **ContainerId** (not VirtualMachineUniqueId). Get it from `LogContainerSnapshot` first.

```kusto
let _startTime = datetime({StartTime});
let _endTime = datetime({EndTime});
let _containerId = '{ContainerId}';
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (_startTime .. _endTime)
| where VmId == _containerId
| extend ShortName = case(
    CounterName == 'Percentage CPU', 'CPU',
    CounterName has 'Guest Available Memory', 'Mem',
    CounterName has 'Current Pressure', 'MemPres',
    CounterName == 'Network In', 'NetIn',
    CounterName == 'Network Out', 'NetOut',
    CounterName == 'Disk Read Bytes/sec', 'DiskRead',
    CounterName == 'Disk Write Bytes/sec', 'DiskWrite',
    '')
| where ShortName != ''
| project PreciseTimeStamp, ShortName, Avg=AverageCounterValue, Max=MaxCounterValue
| evaluate pivot(ShortName, take_any(Avg), PreciseTimeStamp)
| join kind=inner (
    cluster('azcore.centralus.kusto.windows.net').database('Fa').VmCounterFiveMinuteRoleInstanceCentralBondTable
    | where PreciseTimeStamp between (_startTime .. _endTime)
    | where VmId == _containerId
    | where CounterName == 'Percentage CPU'
    | project PreciseTimeStamp, MaxCPU=round(MaxCounterValue, 2)
) on PreciseTimeStamp
| project TimestampUtc=PreciseTimeStamp,
    AvgCPU=round(CPU, 2),
    MaxCPU,
    AvailMemGB=round(Mem/1024, 2),
    NetInMB=round(NetIn/1048576, 2),
    NetOutMB=round(NetOut/1048576, 2),
    DiskReadKBps=round(DiskRead/1024, 2),
    DiskWriteKBps=round(DiskWrite/1024, 2),
    MemPressure=round(MemPres, 0)
| order by TimestampUtc asc
```

Output columns:
| Column | Description | Unit |
|--------|-------------|------|
| AvgCPU | 5-min average CPU utilization | % |
| MaxCPU | 5-min max CPU utilization | % |
| AvailMemGB | Guest available memory | GB |
| NetInMB | Network In (cumulative) | MB |
| NetOutMB | Network Out (cumulative) | MB |
| DiskReadKBps | Disk read throughput | KB/s |
| DiskWriteKBps | Disk write throughput | KB/s |
| MemPressure | Hyper-V Dynamic Memory pressure | % |

---

## Geneva Shoebox VM Performance Overview (1-min granularity)

### geneva_metrics_request — All key metrics in one view (1-min granularity)

Produces a single table with CPU (Avg + Max), Memory (Available GB), Network (In/Out MB), and VM-level disk throttle percentages (Cached/Uncached IOPS% and Bandwidth%) per 1-minute bucket. Provides finer granularity than the AzCore 5-min table above.

**Cluster**: Geneva Kusto endpoint (e.g., `https://sparkle.eastus.kusto.windows.net/blobstreamingdb` or any Geneva-enabled endpoint)
**Note**: Uses `geneva_metrics_request` plugin — cannot run on standard ADX. Use `VirtualMachineUniqueId` (not ContainerId).

```kusto
let startTime = datetime("{StartTime}");
let endTime = datetime("{EndTime}");
let vmId = "{VirtualMachineUniqueId}";
let shoeboxAccount = "{ShoeboxAccount}";
let query_cpu = strcat(@"metricNamespace('Shoebox').metric('Percentage CPU').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_mem = strcat(@"metricNamespace('Shoebox').metric('Available Memory Bytes').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let query_netin = strcat(@"metricNamespace('Shoebox').metric('Network In').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let query_netout = strcat(@"metricNamespace('Shoebox').metric('Network Out').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let query_vmcachediops = strcat(@"metricNamespace('Shoebox').metric('VM Cached IOPS Consumed Percentage').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_vmuncachediops = strcat(@"metricNamespace('Shoebox').metric('VM UnCached IOPS Consumed Percentage').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_vmcachedband = strcat(@"metricNamespace('Shoebox').metric('VM Cached Bandwidth Consumed Percentage').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_vmuncachedband = strcat(@"metricNamespace('Shoebox').metric('VM UnCached Bandwidth Consumed Percentage').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
evaluate geneva_metrics_request(shoeboxAccount, query_cpu, startTime, endTime)
| project TimestampUtc, AvgCPU=column_ifexists("Average",0.0), MaxCPU=column_ifexists("Max",0.0)
| join kind=fullouter (
    evaluate geneva_metrics_request(shoeboxAccount, query_mem, startTime, endTime)
    | project TimestampUtc, AvailMemGB=round(column_ifexists("Average",0.0)/1073741824, 2)
) on TimestampUtc
| join kind=fullouter (
    evaluate geneva_metrics_request(shoeboxAccount, query_netin, startTime, endTime)
    | project TimestampUtc, NetInMB=round(column_ifexists("Average",0.0)/1048576, 2)
) on TimestampUtc
| join kind=fullouter (
    evaluate geneva_metrics_request(shoeboxAccount, query_netout, startTime, endTime)
    | project TimestampUtc, NetOutMB=round(column_ifexists("Average",0.0)/1048576, 2)
) on TimestampUtc
| join kind=fullouter (
    evaluate geneva_metrics_request(shoeboxAccount, query_vmcachediops, startTime, endTime)
    | project TimestampUtc, CachedIOPS_Pct=column_ifexists("Max",0.0)
) on TimestampUtc
| join kind=fullouter (
    evaluate geneva_metrics_request(shoeboxAccount, query_vmuncachediops, startTime, endTime)
    | project TimestampUtc, UncachedIOPS_Pct=column_ifexists("Max",0.0)
) on TimestampUtc
| join kind=fullouter (
    evaluate geneva_metrics_request(shoeboxAccount, query_vmcachedband, startTime, endTime)
    | project TimestampUtc, CachedBW_Pct=column_ifexists("Max",0.0)
) on TimestampUtc
| join kind=fullouter (
    evaluate geneva_metrics_request(shoeboxAccount, query_vmuncachedband, startTime, endTime)
    | project TimestampUtc, UncachedBW_Pct=column_ifexists("Max",0.0)
) on TimestampUtc
| where isnotempty(TimestampUtc)
| project-away TimestampUtc1, TimestampUtc2, TimestampUtc3, TimestampUtc4, TimestampUtc5, TimestampUtc6, TimestampUtc7
| order by TimestampUtc asc
```

Shoebox account mapping (from `get_vmdash_link.py` region detection):
| Region | Shoebox Account |
|--------|----------------|
| North Europe | AzComputeShoeboxNEU |
| West Europe | AzComputeShoeboxWEU |
| East US | AzComputeShoeboxEUS |
| East US 2 | AzComputeShoeboxEUS2 |
| West US 2 | AzComputeShoeboxWUS2 |
| Southeast Asia | AzComputeShoeboxSEA |
| East Asia | AzComputeShoeboxEAS |

Output columns:
| Column | Description | Unit |
|--------|-------------|------|
| AvgCPU / MaxCPU | CPU utilization (1-min) | % |
| AvailMemGB | Guest available memory | GB |
| NetInMB / NetOutMB | Network In/Out (cumulative) | MB |
| CachedIOPS_Pct | VM Cached IOPS consumed | % (0 = no throttling) |
| UncachedIOPS_Pct | VM Uncached IOPS consumed | % |
| CachedBW_Pct | VM Cached Bandwidth consumed | % |
| UncachedBW_Pct | VM Uncached Bandwidth consumed | % |
