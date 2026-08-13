# Playbook A — Unexpected VM Restarts (Deep)

> **Purpose**: Full KQL bodies for ~25 specific-fault TSGs under `/SME Topics/Unexpected Restarts/TSGs/*`, organized by failure mode. Use this **after** Step 2 of [`playbook-A-restarts-core.md`](playbook-A-restarts-core.md) has narrowed `RCALevel1` to a specific category.
>
> **Source TSGs** (csswiki / AzureIaaSVM): pages aggregated 2026-06-03 (initial 17) + 2026-06-04 backfill (CPU / Thermal / PSU / PowerStateUnknown / HV-Deadlock / AccelNet-Update / TOR / Overlake SoC / WinEvents / 70007 StopDestroy / 70019 / Tracks). Each section names its source TSG path so you can re-verify upstream.
>
> **Convention**: `{NodeId}`, `{ContainerId}`, `{StartTime}`, `{EndTime}`, `{SubscriptionId}`, `{TenantName}`, `{VMName}`, `{ContainerID}` (note both spellings appear in upstream TSGs). All times UTC.
>
> **Companion reference**: Host Windows EventIds (60+ entries with false-positive list and cluster-frequency check) live in [`windows-events-reference.md`](../catalogs/windows-events-reference.md).

---

## TOC

- **§ SW — Software / Host OS**
  - SW-1: Host Node Bugcheck (Watson dump analysis)
  - SW-2: 0xEF nt!PspCatchCriticalBreak
  - SW-3: PowerCycle Unhealthy Node (8-cluster chain)
    - SW-3.Q.HV-Deadlock — RS 1.86 Hyper-V deadlock variant (P2)
  - SW-4: Unhealthy Node Investigation (RCALevel2 router)
    - SW-4.Q70019 — 10-step 70019 Unhealthy Node chain (P1)
    - SW-4.Q.TrackTable — `unhealthynode` 30-track routing (P4)
  - SW-5: Host Node Marked Unallocatable
  - SW-6: Host CPU Saturation (HighCpuCounterNodeTable + ProfilerKLO) (M1)
  - SW-7: PowerStateUnknown Host-Agent Timeout 0xc1520007 (M4)
  - SW-8: StopDestroyContainer WorkflowTimeout 70007 + MemDefrag chain (M7)
- **§ HW — Hardware**
  - HW-1: Host Node Hardware Failure (comprehensive — WHEA/DCM/Sparkle)
  - HW-2: Disk Hardware Failure (DCM ResourceSnapshotHistory)
  - HW-3: Host Node Disk (Sparkle Partner_Func_DiskIssueDetection)
  - HW-4: NVMe Troubleshooting (NvmeDirect stack — 6 tables)
  - HW-5: Host Node Memory (ECC + Low Memory)
  - HW-6: IERR (Processor SEL)
  - HW-7: AN Overlake SoC — FaultCode 10036 (high memory)
    - HW-7.Q.ANUpdate — Accelerated Network update injected fault variant (P3)
  - HW-8: Thermal Trip (Power Off + Processor Thermal + Watchdog 2) (M2)
  - HW-9: PSU / Rack Manager FaultCode 31021 (M3)
- **§ STG — Storage / IO path**
  - STG-1: E17 Investigation (IaaS Disk Failure + XStore Triage)
  - STG-2: Blob Cache Disk Error — FaultCode 10005 + 0x80078000
  - STG-3: Live Migration VFPRestoreFailure (NMAgent Event 356)
  - STG-4: DataPath HostPlugin Update (DPHU)
- **§ MAINT — Maintenance / Updates**
  - MAINT-1: Host Node Update (NMAgent / Gandalf / RootHE chain)
- **§ NET — Networking-induced restarts**
  - NET-1: TOR Hardware Failure / Reload (M5)
  - NET-2: Overlake SoC Investigation (M6)
- **§ GUEST — Guest OS layer** (out-of-scope — delegate)
- **§ REF — Windows Events master table** → [`windows-events-reference.md`](../catalogs/windows-events-reference.md) (M8)

---

# § SW — Software / Host OS

## SW-1: Host Node Bugcheck (Watson dump analysis)

> **TSG**: `/Unexpected Restarts/TSGs/Host Node Bugcheck_Restarts`
> **Scope**: Host OS kernel-mode crashed; identify failure signature, fetch Watson dump analysis.
> **Escalation**: EEE Host Node + WheaXPFMCAFull lookup if HW-related signature.

### SW-1.Q1 — Get failure signature from VMA

```kusto
cluster("Vmainsight").database("vmadb").VMA
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 3h)
| where RCAEngineCategory !contains "Customer"
| distinct StartTime, EndTime, Cluster, NodeId, ContainerId, RoleInstanceName, RCALevel1, RCALevel2, RCA_CSS
```

### SW-1.Q2 — Resolve signature to KB article

```kusto
cluster("Vmainsight").database("Air").GetArticleIdByFailureSignature("<RCALevel1.RCALevel2>")
// e.g. GetArticleIdByFailureSignature("HostOSCrash.UnhealthyNode_OS Bugcheck 0x0000000a")
```

### SW-1.Q3 — Pull Watson crash + dump analysis

```kusto
let starttime = datetime({StartTime});
let endtime = datetime({EndTime});
let nodeid = "{NodeId}";
let azurewatsonlink = strcat("https://azurewatson.microsoft.com/?NodeId=", nodeid);
cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp between (starttime .. endtime)
| where nodeIdentity == nodeid
| where crashMode == "km"
| project PreciseTimeStamp, EventMessage, platform, crashMode, process, environment, dumpUid
| join kind=leftouter (
    cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
    | where PreciseTimeStamp between (starttime .. endtime)
    | project AnalyzedTime=PreciseTimeStamp, DumpAnalalysisMessage=EventMessage,
        faultingModule, faultingProcess, bucketString, crashTime, dumpType, bugId, bugLink, dumpUid
) on $left.dumpUid == $right.dumpUid
| extend AzureWatsonLink = azurewatsonlink
| project crashTime, AnalyzedTime, dumpType, platform, DumpAnalalysisMessage,
    faultingModule, faultingProcess, bugId, bugLink, AzureWatsonLink
```

---

## SW-2: 0xEF nt!PspCatchCriticalBreak

> **TSG**: `/Unexpected Restarts/TSGs/0xEF_nt!PspCatchCriticalBreak_Restarts`
> **Scope**: Specific bugcheck where a critical process was terminated → host bugcheck 0xEF.

### SW-2.Q1 — VMA detail for this VM/sub

```kusto
cluster("Vmainsight").database("vmadb").VMA
| where Subscription contains "{SubscriptionId}"
| where RoleInstanceName contains "{VMName}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project TenantName, PreciseTimeStamp, EndTime, Cluster, TenantId, NodeId, ContainerId,
    RCALevel1, RCALevel2, RCALevel3, DCM_RCA,
    DcmNodeState_OFRFaultCode, DcmNodeState_OFRReason, Detail,
    Watson_dumpUidLink, Watson_BugLink
| order by PreciseTimeStamp asc
```

### SW-2.Q2 — Container placement snapshot

```kusto
cluster("Azcsupfollower").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where roleInstanceName contains "{VMName}" and subscriptionId == "{SubscriptionId}"
| project PreciseTimeStamp, roleInstanceName, containerId, nodeId
| order by PreciseTimeStamp asc
```

### SW-2.Q3 — Container health timeline (faultInfo)

```kusto
cluster("Azcsupfollower").database("AzureCM").LogContainerHealthSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where roleInstanceName contains "{VMName}" and containerId == "{ContainerID}"
| project TIMESTAMP, containerIsolationState, containerId, containerLifecycleState,
    containerOsState, containerState, nodeId, faultInfo
| order by TIMESTAMP asc
```

### SW-2.Q4 — Node state during window

```kusto
cluster("AzureCM").database("AzureCM").LogNodeSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where nodeId == "{NodeId}"
| project PreciseTimeStamp, nodeId=toupper(nodeId), nodeState, nodeAvailabilityState, faultInfo
| order by PreciseTimeStamp asc
```

---

## SW-3: PowerCycle Unhealthy Node (8-cluster chain)

> **TSG**: `/Unexpected Restarts/TSGs/PowerCycle Unhealthy Node_Restarts`
> **Scope**: Fabric power-cycled a hung node. Signature is `NodeFault.UnhealthyNode_Inconclusive_Powercycled` or variants. Walks 8 different cluster/dbs to triangulate root cause.
> **Escalation**: EEE Host Node if dump-analysis points to OS layer.

### SW-3.Q1 — VMA failure signature

```kusto
cluster("Vmainsight").database("vmadb").VMA
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h)
    and NodeId == "{NodeId}"
    and RCAEngineCategory !contains "Customer"
| distinct StartTime, EndTime, Cluster, NodeId, ContainerId, RoleInstanceName, RCALevel1, RCALevel2, RCA_CSS
```

### SW-3.Q2 — Signature → KB

```kusto
cluster("Vmainsight").database("Air").GetArticleIdByFailureSignature("NodeFault.UnhealthyNode_Inconclusive_Powercycled")
```

### SW-3.Q3 — Maintenance / version-switch / NodeEvents in 24h

```kusto
let ServiceVersion = (cluster("sparklefollower.centralus.kusto.windows.net").database("AzureCM").ServiceVersionSwitch);
let RootHEGandalf = (cluster("azcsupfollower").database("AzureCM").RootHEGandalfInformationalEventEtwTable
    | extend RootHEGandalf_OldValue=OldVersion, RootHE_NewValueGandalf=NewVersion);
let NodeEvents = (cluster("azcsupfollower").database("AzureCM").TMMgmtNodeEventsEtwTable
    | where Message contains 'CreatePluginComplete' or Message contains 'UpdatePluginCompleted'
    | parse kind=regex Message with * ' = HostPluginName:' Component:string ', HostPluginSetupFile:' * 'HostPluginPackage:' package:string ', Action:' *);
union RootHEGandalf, ServiceVersion, NodeEvents
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h) and NodeId == "{NodeId}"
| summarize NodeUpdatedAtApprox=min(PreciseTimeStamp) by ServiceName, CurrentVersion, NewVersion, SourceOfService,
    RootHEGandalf_OldValue, RootHE_NewValueGandalf, Component, package, NodeId
| project-reorder NodeUpdatedAtApprox, NodeId
| order by NodeUpdatedAtApprox asc
```

### SW-3.Q4 — Host WindowsEventTable

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h)
    and NodeId == "{NodeId}"
| project TimeCreated, Cluster, EventId, ProviderName, Description
| order by TimeCreated asc nulls last
```

### SW-3.Q5 — WHEA Logger ⨯ WheaXPFMCAFull (uncorrectable HW errors)

```kusto
let StartTime = datetime({StartTime});
let EndTime = datetime({EndTime});
let nodeid = "{NodeId}";
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where NodeId == nodeid and PreciseTimeStamp between (StartTime..EndTime)
    and ProviderName == "Microsoft-Windows-WHEA-Logger"
| join kind=inner (
    cluster("sparkle.eastus").database("defaultdb").WheaXPFMCAFull
    | where PreciseTimeStamp between (StartTime..EndTime)
) on $left.NodeId == $right.NodeId
| project TIMESTAMP, ProviderName, ErrorRecordSeverity, PhysicalAddress, Status, RetryReadData,
    TimeCreated, EventId, Channel, Description, Cluster, NodeId
```

### SW-3.Q6 — Bugcheck + Watson dump (same as SW-1.Q3 but full timeframe)

```kusto
let starttime = datetime({StartTime});
let endtime = datetime({EndTime});
let nodeid = "{NodeId}";
let azurewatsonlink = strcat("https://azurewatson.microsoft.com/?NodeId=", nodeid);
cluster("azurewatsoncustomer.kusto.windows.net").database("AzureWatsonCustomer").CustomerCrashOccurredV2
| where PreciseTimeStamp between (starttime .. endtime) and nodeIdentity == nodeid and crashMode == "km"
| project PreciseTimeStamp, EventMessage, platform, crashMode, process, environment, dumpUid
| join kind=leftouter (
    cluster("azurewatsoncustomer.kusto.windows.net").database("AzureWatsonCustomer").CustomerDumpAnalysisResultV2
    | where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    | project AnalyzedTime=PreciseTimeStamp, DumpAnalalysisMessage=EventMessage,
        faultingModule, faultingProcess, bucketString, crashTime, dumpType, bugId, bugLink, dumpUid
) on $left.dumpUid == $right.dumpUid
| extend AzureWatsonLink=azurewatsonlink
| project crashTime, AnalyzedTime, dumpType, platform, DumpAnalalysisMessage,
    faultingModule, faultingProcess, bugId, bugLink, AzureWatsonLink
```

### SW-3.Q7 — Hawkeye RCA events

```kusto
cluster("hawkeyedataexplorer.westus2.kusto.windows.net").database("HawkeyeLogs").GetLatestHawkeyeRCAEvents
| where RCATimestamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h) and NodeId == "{NodeId}"
| project FaultTime, NodeId, RCALevel1, RCALevel2
```

### RCALevel2 → RCA template mapping

| `RCALevel2` | Customer RCA template |
|---|---|
| `Inconclusive`, `Inconclusive: OS Liveness Undetermined`, `Inconclusive_Powercycled` | `VMA_RCA_Software_UnhealthyNode_Host_OS_PowerCycle_Inconclusive` |
| `Inconclusive_OrganicRecovery` | `VMA_RCA_Software_UnhealthyNode_Host_OS_PowerCycle_Inconclusive_Organic` |
| `Unhealthy Node`, `Likely OS Failure`, `Certain OS Failure` | `VMA_RCA_Software_UnhealthyNode_Host_OS_PowerCycle_Likely_OS_Failure` |
| `RdAgent APIs failing` | `VMA_RCA_Software_UnhealthyNode_Host_OS_PowerCycle_RdAgent_API_failing` |
| `Inconclusive_RdAgentUpdate_OrganicRecovery` | (RdAgent update path — check NMAgent change in SW-3.Q3) |

### SW-3.Q.HV-Deadlock — Hyper-V deadlock variant (RS 1.86 microcode)

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/Unhealthy Node Hyper-V Deadlock_Restarts`
> **Trigger**: VMA shows `Unplanned.NodeFault.PowerCycleUnhealthyNode` AND node is running **Host OS RS 1.86**. The deadlock is in Hyper-V; Watchdog 2 cannot interrupt the CPU. Mitigation = microcode update.

#### Q-HVD-1 — Confirm Host OS = RS 1.86

```kusto
cluster('rdosdata.kusto.windows.net').database('rdosdatapath').GetLatestHostOsVersionInventory()
| where NodeId == "{NodeId}"
| project Cluster, NodeId, OsFriendlyName
```

#### Q-HVD-2 — Microcode update window (last 10d)

```kusto
cluster('azcsupfollower').database('AzureCM').CSIMicrocodeEvents
| where env_time > ago(10d) and resourceId == "{NodeId}"
    and resultSignature == "UCODE_Update" and resultDescription == "Starting"
| project UcodeStart=env_time, NodeId=resourceId
```

#### Q-HVD-3 — SEL Watchdog Timer Expired (union 4 sources)

```kusto
let WindowStartTime = ago(10d);
let WindowStopTime = now();
union
  (cluster("Azuredcm").database("AzureDCMDb").RhwBmcSelItemEtwTableV1   | extend SelSource = "RhwBmcSelItemEtwTableV1"),
  (cluster("Azuredcm").database("AzureDCMDb").RhwChassisSelItemEtwTable | extend SelSource = "RhwChassisSelItemEtwTable"),
  (cluster("Azuredcm").database("AzureDCMDb").RhLiteDiagBmcSel          | extend SelSource = "RhLiteDiagBmcSel"),
  (cluster("Azuredcm").database("AzureDCMDb").RhLiteDiagSel             | extend SelSource = "RhLiteDiagSel"
     | extend BmcSelItemTimeStamp = SelTimeStamp)
| where BmcSelItemTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and ResourceId in ("{NodeId}") and BmcSelItemEventType != "CollectoreHeartbeat"
| extend HasHex = isnotempty(BmcSelItemRawHex), MissingHex = isempty(BmcSelItemRawHex)
| project Cluster, ResourceId, BmcSelItemTimeStamp, BmcSelItemEventType,
    BmcSelItemWmiDescription, SelSensorType, SelDetails, SelErrorCode
```

**Signature**: SEL shows Watchdog Timer Expired AND Q-HVD-1 returns RS 1.86 → confirmed Hyper-V deadlock. PG fix in testing; fleet-wide mitigation rolling out. Use `VMA_RCA_Software_UnhealthyNode_HV_Deadlock` template.

---

## SW-4: Unhealthy Node Investigation (RCALevel2 router)

> **TSG**: `/Unexpected Restarts/TSGs/Unhealthy Node Investigation_Restarts`
> **Scope**: Lighter-weight entrypoint to PowerCycle/Unhealthy diagnosis. Use this first; drop into SW-3 if RCALevel2 is `Inconclusive*`.

### SW-4.Q1 — VMA RCA by subscription

```kusto
cluster('vmainsight').database('vmadb').VMA
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h)
    and Subscription == "{SubscriptionId}" and RCAEngineCategory !contains "Customer"
| distinct StartTime, EndTime, RoleInstanceName, RCAEngineCategory, RCALevel1, RCALevel2, Cluster, ContainerId, NodeId
```

### SW-4.Q2 — LogNodeSnapshot (24h)

```kusto
cluster("azcsupfollower").database("AzureCM").LogNodeSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h) and nodeId == "{NodeId}"
| project PreciseTimeStamp, nodeId, nodeState, nodeAvailabilityState, containerCount, faultInfo
```

### SW-4.Q3 — Hawkeye

```kusto
cluster('hawkeyedataexplorer.westus2.kusto.windows.net').database('HawkeyeLogs').GetLatestHawkeyeRCAEvents
| where RCATimestamp >= datetime({StartTime}) and RCATimestamp < datetime({EndTime}) and NodeId == "{NodeId}"
| project FaultTime, NodeId, RCALevel1, RCALevel2
```

→ If RCALevel2 still `Inconclusive` after Hawkeye lag (24h), escalate to **EEE Host Node** by opening an ICM manually via ASC (Escalate ticket, CRI-HostNode).

### SW-4.Q70019 — 10-step 70019 Unhealthy Node chain

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/70019 Unhealthy Node_Restarts`
> **Trigger**: VMA `RCALevel2 == "70019"` or `NodeFault.UnhealthyNode` with workflow-id 70019. This is the **deep** chain — run AFTER SW-4.Q1..Q3 narrow the failure to 70019.

#### Q70019-1 — VMA all RCAs in window

```kusto
cluster("vmainsight").database("vmadb").VMA
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and NodeId == "{NodeId}"
| project StartTime, EndTime, NodeId, ContainerId, Cluster, RoleInstanceName,
    RCALevel1, RCALevel2, RCALevel3, RCAEngineCategory, RCA_CSS
```

#### Q70019-2 — Sparkle SEL (HW signal preceding 70019?)

```kusto
cluster("sparkle.eastus.kusto.windows.net").database("defaultdb").SparkleSELByNodeId(nodeId="{NodeId}")
| where BMCSelTimestamp between (datetime({StartTime}) .. datetime({EndTime}))
| project-reorder BMCSelTimestamp, PreciseTimeStamp, EventDataDetails1, SelSource
```

#### Q70019-3 — Anvil (auto-mitigation actions on node)

```kusto
cluster("anvilshareddata.kusto.windows.net").database("AnvilShared").AnvilNodeActionsHistory
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and NodeId == "{NodeId}"
| project PreciseTimeStamp, NodeId, ActionName, ActionStatus, ActionContext, RequestId
```

#### Q70019-4 — LogNodeSnapshot faultInfo timeline

```kusto
cluster("azcsupfollower").database("AzureCM").LogNodeSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and nodeId == "{NodeId}"
| project PreciseTimeStamp, Tenant, nodeId, nodeState, nodeAvailabilityState, containerCount, faultInfo
```

#### Q70019-5 — TMMgmt node events (workflow events on the node)

```kusto
cluster("azcsupfollower").database("AzureCM").TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and nodeId == "{NodeId}"
| where eventType has "70019" or message has "70019"
| project PreciseTimeStamp, nodeId, Tenant, eventType, message
```

#### Q70019-6 — Host Windows events (correlate at moment of failure)

```kusto
cluster("vmainsight").database("vmadb").WindowsEventTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and NodeId == "{NodeId}"
| where Level in ("Error", "Critical")
| project TimeCreated, EventId, ProviderName, Description
| order by TimeCreated asc
```

→ Cross-reference EventIds against [`windows-events-reference.md`](../catalogs/windows-events-reference.md).

#### Q70019-7 — Watson kernel-mode crashes on the node

```kusto
cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and nodeIdentity == "{NodeId}" and crashMode == "km"
| project PreciseTimeStamp, EventMessage, process, dumpUid
```

#### Q70019-8 — NetVMA quick visual check (no Kusto)
- Open <https://netvma.azure.net/> → search `{NodeId}` → look for Compute Heartbeat drops aligned to 70019 timestamp.

#### Q70019-9 — TMMgmt tenant events (was Fabric attempting a planned operation?)

```kusto
cluster("azcsupfollower").database("AzureCM").TMMgmtTenantEvents
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and Tenant == "{TenantName}"
| project PreciseTimeStamp, Tenant, eventType, message
```

#### Q70019-10 — SLA Measurement (was downtime customer-facing?)

```kusto
cluster("vmainsight").database("vmadb").VMAOutages
| where StartTime between (datetime({StartTime}) .. datetime({EndTime})) and NodeId == "{NodeId}"
| project StartTime, EndTime, Duration_min, RoleInstanceName, OutageReason
```

**Outcome routing**:
- HW signal in Q2/Q4 → § HW (HW-1..HW-9)
- Watson dump in Q7 → SW-1
- Workflow events show Fabric initiated → see MAINT-1
- All inconclusive → escalate EEE Host Node

### SW-4.Q.TrackTable — `unhealthynode` 30-track routing

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/Tracks for Unhealthy Node_Restarts`
> **Use**: Quick triage — query the `unhealthynode` Vmainsight table to see which of ~30 tracks Anvil assigned to this node; each track maps to a downstream TSG.

#### Q-Track-1 — Get track for node

```kusto
cluster("Vmainsight").database("vmadb").unhealthynode
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and NodeId == "{NodeId}"
| project PreciseTimeStamp, Cluster, NodeId, Track, TrackDetails, AnvilAction, RCALevel1, RCALevel2
```

#### Track → TSG / RCA routing (selected high-value tracks)

| Track | Routing |
|---|---|
| `BugCheck` / `OSCrash` | SW-1 + SW-2 |
| `PowerCycle*` / `Inconclusive` | SW-3 (+ SW-3.Q.HV-Deadlock if RS 1.86) |
| `RdAgentUnresponsive` / `RUNTIME_VM_CONTAINER_E_VMAL_CALL_TIMEOUT` | SW-7 (PowerStateUnknown) |
| `StopDestroy*` / `WorkflowTimeout 70007` | SW-8 |
| `WHEA*` / `MCE*` / `IERR` | HW-1 / HW-6 |
| `DiskIssue*` / `Storport500` | HW-3 + STG-1 |
| `MemoryECC*` / `LowMemory` | HW-5 |
| `ThermalTrip` / `PowerOff` | HW-8 |
| `PSU*` / `RM*` / `FaultCode31021` | HW-9 |
| `NetworkLink*` / `TorReload` | NET-1 |
| `Overlake*` / `SoC*` / `0xbadfd` | NET-2 / HW-7 |
| `Manually injected fault - high memory usage` (10036) | HW-7 |
| `Manually injected fault - mitigate accelnet issue` (10036) | HW-7.Q.ANUpdate |
| `HostUpdate` / `NMAgent` / `Gandalf` / `RootHE` | MAINT-1 |
| `Unallocatable_ResetNodeHealth` | SW-5 |

**Note**: When Track is missing or `Unknown`, fall back to SW-4.Q70019 full chain.

---

## SW-5: Host Node Marked Unallocatable

> **TSG**: `/Unexpected Restarts/TSGs/Host Node Marked Unallocatable_Restarts`
> **Scope**: Node was marked Unallocatable → all VMs got live-migrated.

### SW-5.Q1 — Node snapshot with faultInfo

```kusto
cluster("AzureCM").database("AzureCM").LogNodeSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 3d)
    and nodeId == "{NodeId}"
| project PreciseTimeStamp, Tenant, nodeId, containerCount, isIsolated, nodeState, diskConfiguration,
    cmNodeChannelAggregatedHealthStatus, nodeAvailabilityState, faultInfo
```

### faultInfo `OrangeType` patterns to look for

- `Unallocatable_ResetNodeHealth` — explicit unallocatable marking
- `Reason: "Manually injected fault - high memory usage"` + `FaultCode: 10036` → § HW-7 (AN Overlake SoC)
- `Reason: "Manually injected fault - mitigate accelnet issue"` + `FaultCode: 10036` → § HW-7.Q.ANUpdate (Accelerated Network update — planned maintenance variant)
- `FabricOperationString: "ForceNodeState"` → manual injection by Anvil / Tardigrade

---

## SW-6: Host CPU Saturation

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/Host Node CPU Investigation_Restarts`
> **Scope**: High Hyper-V Root CPU on the host (NOT guest CPU). Sustained host-root saturation can starve VMA / VMMS / Storport workers → E17, heartbeat loss, PowerCycle.
> **Always look only at Hyper-V Root** for Host CPU (Host Analyzer → "Host Metrics" / "Host Charts").

### SW-6.Q1 — High CPU events on the node

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').HighCpuCounterNodeTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h)
    and NodeId == "{NodeId}"
```

### SW-6.Q2 — Resolve `{NodeId}` to hostname (for Azure Profiler trace lookup)

```kusto
cluster("azcsupfollower.kusto.windows.net").database("AzureCM").LogNodeSnapshot
| where PreciseTimeStamp > ago(1h) and nodeId == "{NodeId}"
| project TIMESTAMP, Tenant, hostName, Region, DataCenterName, AvailabilityZone
```

### SW-6 — Azure Profiler call-stack analysis (no Kusto)

- Open Azure Profile viewer: <http://azprofilerclko>
- → **View Data from Specific Compute Hosts** → choose `NodeHighCPU` or `Node8CoresCPU` → select year/month/day → cluster/tenant → hostname (from SW-6.Q2).
- Double-click the orange bar → expand call stack → identify driver / process / PG team.
- If high host CPU caused VM impact (E17 / heartbeat loss) → ICM EEE.

### SW-6 — ASI cross-check

- **Azure Host Node** → `Host Tables / HighCPU Table` — <https://asi.azure.ms/services/Azure%20Host/pages/Azure%20Host%20Node>
- **EEE RDOS Start Hub** — <https://asi.azure.ms/services/EEE%20RDOS/pages/Start%20Hub>
- **EEE RDOS WF Unexpected Restart** — <https://asi.azure.ms/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart>

### Known issues / cross-references
- IERR investigation: HW-6
- High guest CPU (NOT host root): TSG `/SME Topics/Performance/Troubleshoot High CPU issue` → delegate to Performance SME

---

## SW-7: PowerStateUnknown Host-Agent Timeout (0xc1520007)

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/PowerStateUnknown Leads to VM Reboot_Restarts`
> **Scope**: Host Agent (RD Agent) bug — when GetComputeUsageInfo VMAL call times out, Agent cannot determine VM power state → **stops and restarts the VM**. Behaviour confirmation requires **all three** patterns below.

### SW-7 confirmation pattern (all required)

1. ASC Availability Graph shows pattern `dh_emergingissue` (Agent restart blip)
2. **Three combinations** in `VmHealthRawStateEtwTable`:
   - `VmHyperVIcHeartbeat == "HeartBeatStateNonRecoverableError"`
   - `VmPowerState == "PowerStateUnknown"`
   - `IsVscStateOperational == "1"` (network still OK)
3. RD Agent log contains error **`0xc1520007`** (`RUNTIME_VM_CONTAINER_E_VMAL_CALL_TIMEOUT`) at `RuntimeVmContainer::GetComputeUsageInfoInternal`

### SW-7.Q1 — Confirm VmHealthRawState triplet

```kusto
cluster('azcore.centralus').database('Fa').VmHealthRawStateEtwTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and ContainerId == '{ContainerId}'
| project PreciseTimeStamp, VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted,
    IsVscStateOperational, Context
```

### SW-7.Q2 — Confirm LogContainerHealthSnapshot Unhealthy + Unknown

```kusto
cluster('azcsupfollower').database('AzureCM').LogContainerHealthSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and containerId == '{ContainerId}'
| project PreciseTimeStamp, Tenant, roleInstanceName, tenantName, containerId, nodeId,
    containerState, actualOperationalState, containerLifecycleState, containerOsState, faultInfo
```

Look for: `containerState == "ContainerStateUnhealthy"`, `actualOperationalState == "Unknown"`, `containerOsState == "ContainerOsStateUnhealthy"`.

### SW-7.Q3 — NetVMA cross-check

- Open <https://netvma.trafficmanager.net/?startTime={Start}&endTime={End}&value={NodeId}> → confirm **all VMs on the node** show intermittent Compute Heartbeat drops, but **host pingmesh is fine** (network-side healthy → narrows to host Agent issue).

### Outcome / RCA
- All three signals present → confirmed Agent bug → use customer template stating "recently discovered platform issue, fix in progress, no ETA".
- Engage Host Agent / RD Agent PG by opening an ICM manually via ASC (Escalate ticket; select the EEE/PG queue + CRI template).

---

## SW-8: StopDestroyContainer WorkflowTimeout 70007 + MemDefrag chain

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/StopDestroyContainer Workflow Timeout 70007_Restarts`
> **Scope**: Workflow `StopDestroyContainer` timed out (signature `70007`). Most common root cause = **memory defragmentation** on the host that blocks the container teardown.

### SW-8.Q1 — LogContainerSnapshot for the container

```kusto
cluster("azcsupfollower").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and containerId == "{ContainerId}"
| project PreciseTimeStamp, Tenant, nodeId, containerId, roleInstanceName,
    containerState, containerLifecycleState, faultInfo
```

### SW-8.Q2 — VMA + Watson + HW failures on the same node

```kusto
cluster("vmainsight").database("vmadb").VMA
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and NodeId == "{NodeId}"
| project StartTime, EndTime, RoleInstanceName, RCALevel1, RCALevel2, RCA_CSS
```

```kusto
cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsoncustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and nodeIdentity == "{NodeId}" and crashMode == "km"
| project PreciseTimeStamp, EventMessage, process, dumpUid
```

### SW-8.Q3 — Hawkeye RCA

```kusto
cluster("hawkeyedataexplorer.westus2").database("HawkeyeLogs").GetLatestHawkeyeRCAEvents
| where RCATimestamp between (datetime({StartTime}) .. datetime({EndTime})) and NodeId == "{NodeId}"
| project FaultTime, NodeId, Scenario, RCALevel1, RCALevel2
```

### SW-8.Q4 — Anvil node actions

```kusto
cluster("anvilshareddata.kusto.windows.net").database("AnvilShared").AnvilNodeActionsHistory
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and NodeId == "{NodeId}"
| project PreciseTimeStamp, ActionName, ActionStatus, ActionContext
```

### SW-8.Q5 — Host Update events (was an update co-incident?)

```kusto
cluster("Vmainsight").database("vmadb").RootHENodeGoalVersionChange
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and NodeId == "{NodeId}"
| project PreciseTimeStamp, NodeId, OldValue, NewValue
```

### SW-8.Q6 — Windows events on the host (70007 / 18190 / 19050..19064 / 21102)

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and NodeId == "{NodeId}"
| where EventId in (18190, 19050, 19060, 19062, 19064, 21102) or Description has "70007"
| project TimeCreated, EventId, ProviderName, Description
```

→ EventId reference: [`windows-events-reference.md`](../catalogs/windows-events-reference.md) § VM-impacting events.

### SW-8.Q7 — TMMgmt + LogNodeSnapshot for 70007 string

```kusto
union
  (cluster("azcsupfollower").database("AzureCM").TMMgmtNodeEventsEtwTable
     | where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
         and nodeId == "{NodeId}" and (eventType has "70007" or message has "70007")
     | project PreciseTimeStamp, Source="TMMgmt", nodeId, message=tostring(message)),
  (cluster("azcsupfollower").database("AzureCM").LogNodeSnapshot
     | where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
         and nodeId == "{NodeId}" and faultInfo has "70007"
     | project PreciseTimeStamp, Source="LogNodeSnapshot", nodeId, message=tostring(faultInfo))
| order by PreciseTimeStamp asc
```

### SW-8.Q8 — MemDefrag chain (the usual root cause)

**a) AirLiveMigrationEvents (concurrent LM activity → memory pressure)**

```kusto
cluster("vmainsight").database("Air").AirLiveMigrationEvents
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and (SourceNodeId == "{NodeId}" or TargetNodeId == "{NodeId}")
| project PreciseTimeStamp, SourceNodeId, TargetNodeId, ContainerId, MigrationResult, MigrationDurationMs
```

**b) HyperVWorkerTable (VMWP memory consumption)**

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").HyperVWorkerTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and NodeId == "{NodeId}"
| project PreciseTimeStamp, NodeId, ContainerId, WorkingSetMB, PrivateBytesMB, HandleCount
```

**c) Gandalf leak-detection events**

```kusto
cluster("azcsupfollower").database("AzureCM").GandalfLeakDetectionEvents
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and nodeId == "{NodeId}"
| project PreciseTimeStamp, nodeId, process, leakType, message
```

**d) LogNodeSnapshot MemDefrag faults**

```kusto
cluster("azcsupfollower").database("AzureCM").LogNodeSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime})) and nodeId == "{NodeId}"
| where faultInfo has "MemDefrag" or faultInfo has "DefragMemoryRequested"
| project PreciseTimeStamp, nodeId, faultInfo
```

**e) WindowsEvent 2004 (Resource Exhaustion Detector — low VM)**

```kusto
cluster("vmainsight").database("vmadb").WindowsEventTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and NodeId == "{NodeId}" and EventId == 2004
| project TimeCreated, EventId, ProviderName, Description
```

### Outcome
- MemDefrag chain shows pressure → escalate Hyper-V / Memory Manager PG.
- No MemDefrag signal → fall back to SW-4.Q70019 (general unhealthy chain).

---

# § HW — Hardware

## HW-1: Host Node Hardware Failure (comprehensive)

> **TSG**: `/Unexpected Restarts/TSGs/Host Node Hardware Failure Investigation_Restarts`
> **Scope**: All HW fault paths — LogNodeSnapshot, WHEA, Sparkle SEL, Disk events, DCM repair history.

### HW-1.Q1 — LogNodeSnapshot faultInfo

```kusto
cluster("AzureCM").database("AzureCM").LogNodeSnapshot
| where nodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project PreciseTimeStamp, Tenant, nodeId, containerCount, isIsolated, nodeState, diskConfiguration,
    cmNodeChannelAggregatedHealthStatus, nodeAvailabilityState, faultInfo
```

### HW-1.Q2 — WheaXPFMCAFull on host (Sparkle direct)

```kusto
cluster('sparkle.eastus.kusto.windows.net').database('defaultdb').WheaXPFMCAFull
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId == "{NodeId}"
| project PreciseTimeStamp, ProviderName, ErrorRecordSeverity, PhysicalAddress, Status, RetryReadData
```

### HW-1.Q3 — WHEA Logger ⨯ WheaXPFMCAFull

```kusto
let StartTime = datetime({StartTime});
let EndTime = datetime({EndTime});
let nodeid = "{NodeId}";
cluster("Azcore.centralus").database("Fa").WindowsEventTable
| where NodeId == nodeid and PreciseTimeStamp between (StartTime..EndTime)
    and ProviderName == "Microsoft-Windows-WHEA-Logger"
| join kind=inner (
    cluster("sparkle.eastus").database("defaultdb").WheaXPFMCAFull
    | where PreciseTimeStamp between (StartTime..EndTime)
) on $left.NodeId == $right.NodeId
| project TIMESTAMP, ProviderName, ErrorRecordSeverity, PhysicalAddress, Status, RetryReadData,
    TimeCreated, EventId, Channel, Description, Cluster, NodeId
```

### HW-1.Q4 — Sparkle SEL by node (with dedup)

```kusto
cluster("sparkle.eastus").database("defaultdb").SparkleSELByNodeId("{NodeId}")
| where BMCSelTimestamp > datetime({StartTime})
| where BMCSelTimestamp < datetime({EndTime})
| project-reorder BMCSelTimestamp, PreciseTimeStamp, EventDataDetails1
| summarize DuplicateCount=count(), tostring(make_set(SelSource)), tostring(make_set(EventDataDetails1)) by BMCSelTimestamp, RawHex
```

### HW-1.Q5 — WindowsEventTable cleaned (drop common noise)

```kusto
cluster("azcore.centralus").database("Fa").WindowsEventTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where EventId !in ('505','146','4','145','142','155','154','504','510','511','3095','411','1008','36871')
| project TimeCreated, Cluster, EventId, ProviderName, Description
| order by TimeCreated asc nulls last
```

### HW-1.Q6 — Faulty Disk join (StorPort/stornvme/Disk + DCM inventory)

```kusto
let nodes = pack_array("{NodeId}");
let DaysAgo = time(2d);
let windows_events = cluster("Azcore.centralus").database("Fa").WindowsEventTable
    | where PreciseTimeStamp >= ago(DaysAgo) - 2h
    | where NodeId in~ (nodes) and Cluster contains "prdapp"
    | where ProviderName in~ ("Microsoft-Windows-StorPort", "stornvme", "Disk")
    | where EventId in (11, 15, 129, 7, 51, 52, 157, 500) and EventId !in (500, 504, 549, 505)
    | project PreciseTimeStamp, Cluster, NodeId, ProviderName, Channel, EventId, Description;
let storage_events = materialize(cluster("Azcore.centralus").database("Fa").WindowsStorageEvents
    | where PreciseTimeStamp > ago(DaysAgo) - 2h
    | where Cluster contains "prdapp" and NodeId in~ (nodes)
    | where ProviderName in~ ("Microsoft-Windows-StorPort", "stornvme")
    | parse Description with * "The IO failed counts are " IOFailedCounts "." *
    | parse Description with * "had opcode " opcode1 " and " * "SrbStatus " SrbStatus1 " and " * "ScsiStatus" ScsiStatus1 "." * "(" kcq1 ")." *
    | parse Description with * "opcode was " opcode2 " and " * "SrbStatus " SrbStatus2 " and " * "ScsiStatus" ScsiStatus2 "." * "(" kcq2 ")." *
    | where EventId in (500, 504, 549) or (EventId == 505 and isnotempty(IOFailedCounts) and IOFailedCounts != "0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0")
    | extend OpCode = iff(isempty(opcode1), tohex(toint(opcode2)), tohex(toint(opcode1)))
    | extend SrbStatus = iff(isempty(SrbStatus1), tohex(toint(SrbStatus2)), tohex(toint(SrbStatus1)))
    | extend ScsiStatus = iff(isempty(SrbStatus1), tohex(toint(ScsiStatus2)), tohex(toint(ScsiStatus1)))
    | extend kcq = iff(isempty(kcq1), kcq2, kcq1)
    | extend SCSIAddress = toint(Target), SCSILUN = toint(Lun), SCSIPort = toint(Port), SCSIBus = toint(Path)
    | join kind=inner (cluster('Azuredcm').database('AzureDCMDb').dcmInventoryComponentDisk
        | extend DriveSerialNumber = trim(@"[^\w]+", DriveSerialNumber)
    ) on NodeId, SCSIPort, SCSIBus, SCSIAddress, SCSILUN
    | project PreciseTimeStamp, EventId, Version, Level, Description, Cluster, NodeId,
        DriveSerialNumber, DriveProductId, FirmwareRevision, DriveBusType, SystemDrive,
        OpCode, SrbStatus, ScsiStatus, kcq, IOFailedCounts,
        DeviceGuid, Region, DataCenter, ProviderName, Channel, EventData);
union storage_events, windows_events
| summarize arg_max(EventId, *) by EventId
| sort by PreciseTimeStamp asc, NodeId
```

### HW-1.Q7 — Node repair history (V2 — newer)

```kusto
cluster("Azuredcm").database("AzureDCMDb").ResourceSnapshotHistoryV2
| where ResourceId == "{NodeId}"
| project PowerCycleTime, UnexpectedRebootTime, RepairCode, RepairResolutionDetails,
    RepairRequireHardwareDiscovery, PreciseTimeStamp
```

### HW-1.Q8 — Node repair history (V1 — fault descriptions)

```kusto
cluster("Azuredcm").database("AzureDCMDb").ResourceSnapshotHistoryV1
| where ResourceId == "{NodeId}"
| project PreciseTimeStamp, LifecycleState, NeedFlags, FaultCode, FaultDescription
```

### HW-1.Q9 — DCM FaultCode → Owning team

```kusto
cluster("Azuredcm").database("AzureDCMDb").FaultCodeTeamMapping
| where FaultCode == "{FaultCode}"
| project FaultCode, FaultReason
```

---

## HW-2: Disk Hardware Failure

> **TSG**: `/Unexpected Restarts/TSGs/Disk Hardware Failure_Restarts`
> **Scope**: Disk HW broke → caused IO failures or Guest bugcheck or SH.

### HW-2.Q1 — Generic disk failure (V2)

```kusto
cluster("Azuredcm").database("AzureDCMDb").ResourceSnapshotHistoryV2
| where ResourceId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project PowerCycleTime, UnexpectedRebootTime, RepairCode, RepairResolutionDetails,
    RepairRequireHardwareDiscovery, PreciseTimeStamp
```

### HW-2.Q2 — Generic disk failure (V1, non-null FaultDescription)

```kusto
cluster("Azuredcm").database("AzureDCMDb").ResourceSnapshotHistoryV1
| where ResourceId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where FaultDescription != "<null>"
| project PreciseTimeStamp, LifecycleState, NeedFlags, FaultCode, FaultDescription
```

### HW-2.Q3 — Service Healing time (Fc cluster, tenant scope)

```kusto
cluster("azcore.centralus").database("Fc").TMMgmtTenantEventsEtwTable
| where TenantName == "{TenantName}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project PreciseTimeStamp, Message, TaskName
```

### HW-2.Q4 — Node pulled out for repair

```kusto
cluster("azcore.centralus").database("Fc").TMMgmtNodeStateChangedEtwTable
| where BladeID == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project PreciseTimeStamp, BladeID, OldState, NewState
```

---

## HW-3: Host Node Disk (Sparkle HHS detection functions)

> **TSG**: `/Unexpected Restarts/TSGs/Host Node Disk Investigation_Restarts`
> **Scope**: Hardware team's canonical disk-issue detection functions in Sparkle. Use these instead of hand-rolled disk error queries when available.

### HW-3.Q1 — Disk Issue Detection (per-event input)

```kusto
cluster("https://sparkle.eastus.kusto.windows.net").database("defaultdb").Partner_Func_DiskIssueDetection(
    Events: (EventTime:datetime, NodeId:string, EventInfo:string))
// Pipe in WindowsEventTable rows you suspect; function returns classified disk-issue verdict.
```

### HW-3.Q2 — Disk Issue Detection (time-range scan)

```kusto
cluster("https://sparkle.eastus.kusto.windows.net").database("defaultdb").Partner_Func_DiskIssueDetectionTimeRange(
    Nodes: (NodeId:string),
    StartTime: datetime,
    EndTime: datetime)
// Pass a list of suspect NodeIds + window; HHS rules return rich disk-issue verdicts.
```

### Notes
- Both are **stored functions** — invoke as `cluster(...).database(...).FunctionName(args)`, do not query as tables.
- See also `dcmInventoryComponentDisk` (HW-1.Q6) for serial/firmware mapping.

---

## HW-4: NVMe Troubleshooting (NvmeDirect stack)

> **TSG**: `/Unexpected Restarts/TSGs/NVMe Troubleshooting_Restart` (note: singular `Restart` in upstream path)
> **Scope**: VM restart / IO blip on NVMe disk. Tables here are NOT in the core hub.
> **Symptom**: Host WindowsEventTable EventId 6002/6003 from Nvme providers; or NVMe IOCTL "Controller stopped / Starting Physical Controller (CC.EN: 0->1)" → physical controller reset (see ICM 589031519 / 597353168).
> **Note for ASAP / Azure Boost**: if Host has `OverlakeVersion`, use `asap-storage-queries.md` for Azure Boost / ASAP-specific checks; the escalation path may differ.

### HW-4.Q1 — NVMe error events 6002/6003

```kusto
let queryFrom = datetime("{StartTime}");
let queryTo = datetime("{EndTime}");
let queryNodeId = "{NodeId}";
let fn_startTime = queryFrom - 2d;
let fn_endTime = queryTo + 2d;
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp >= fn_startTime and PreciseTimeStamp <= fn_endTime
| where NodeId =~ queryNodeId
| where EventId in (6002, 6003)
| distinct TimeCreated, NodeId, Level, Channel, EventId, ProviderName, Description
```

### HW-4.Q2 — HyperVStorageStackTable (NvmeDirect providers, Level<3)

```kusto
let fn_faultTime = datetime("{StartTime}");
let fn_startTime = fn_faultTime - 1d;
let fn_endTime = fn_faultTime + 1d;
let fn_nodeId = "{NodeId}";
cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVStorageStackTable
| where ProviderName in (
    "Microsoft.Windows.HyperV.Storage.NvmeDirect",
    "Microsoft.Windows.HyperV.NvmeDirect.Telemetry",
    "Microsoft.Windows.HyperV.Storage.NvmeDirect2",
    "Microsoft.Windows.HyperV.Storage.NvmeDirect2.Activity")
| where NodeId == fn_nodeId
| where PreciseTimeStamp between (fn_startTime..fn_endTime)
| where Level < 3
| project PreciseTimeStamp, Pid, Tid, ProviderName, EventId, TaskName, Message, EventMessage, Level, Opcode
| order by PreciseTimeStamp desc
```

### HW-4.Q3 — HyperVEventsV2 (function, filters by container)

```kusto
let _startTime = datetime("{StartTime}");
let _endTime = datetime("{EndTime}");
let _nodeId = "{NodeId}";
let _containerId = "{ContainerId}";
cluster("azcore.centralus.kusto.windows.net").database("SharedWorkspace").HyperVEventsV2(
    fn_nodeId=['_nodeId'], fn_containerId=['_containerId'],
    fn_startTime=['_startTime'], fn_endTime=['_endTime'])
```

### HW-4.Q4 — DirectAccessEvent (PCI bus 100,0,0 = primary NVMe)

```kusto
let fn_startTime = datetime("{StartTime}") - 1d;
let fn_endTime = datetime("{EndTime}");
let fn_nodeId = "{NodeId}";
cluster('azcore.centralus.kusto.windows.net').database('Fa').DirectAccessEvent
| where NodeId == fn_nodeId
| where PreciseTimeStamp between (fn_startTime..fn_endTime)
| where LocationPath == "PCI bus 100, device 0, function 0"
| project PreciseTimeStamp, Cluster, NodeId, ContainerId, ResultCode, Operation, Stage, DirectAccessType, LocationPath, SerialNumber
| order by PreciseTimeStamp asc
```

### HW-4.Q5 — HyperVStorageStackErrors (function, narrow window)

```kusto
let fn_startTime = datetime("{StartTime}");
let fn_endTime = fn_startTime + 5m;
let fn_nodeId = "{NodeId}";
let fn_containerId = "{ContainerId}";
cluster('azcore.centralus.kusto.windows.net').database('SharedWorkspace').HyperVStorageStackErrors(
    fn_nodeId, fn_startTime, fn_endTime)
| order by PreciseTimeStamp asc
```

### HW-4.Q6 — Controller stop/start messages

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").HyperVStorageStackTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime("{StartTime}") .. 30m)
    and Message contains "Controller"
| project PreciseTimeStamp, NodeId, TaskName, Message, EventMessage
```

### HW-4.Q7 — Sparkle Partner_NVMeHealthLog (HW side, media errors)

```kusto
let fn_nodeId = "{NodeId}";
let fn_faultTime = datetime("{StartTime}");
let fn_startTime = fn_faultTime - 4d;
let fn_endTime = fn_faultTime + 1d;
cluster('sparkle.eastus.kusto.windows.net').database('defaultdb').Partner_NVMeHealthLog
| where PreciseTimeStamp between (fn_startTime .. fn_endTime)
| where NodeId == fn_nodeId
| project PreciseTimeStamp, NodeId, Serial, MediaErrors
```

### HW-4.Q8 — Sparkle Partner_E523_DevRCA (vendor RCA decode)

```kusto
let fn_nodeId = "{NodeId}";
let fn_faultTime = datetime("{StartTime}");
let fn_startTime = fn_faultTime - 4d;
let fn_endTime = fn_faultTime + 1d;
cluster('sparkle.eastus.kusto.windows.net').database('defaultdb').Partner_E523_DevRCA
| where EventTime between (fn_startTime .. fn_endTime)
| where NodeId == fn_nodeId
| project EventTime, NodeId, SCTDescription, SCDescription, DriveSerialNumber, ErrorType, EventDefinition, EventData
```

### Known benign signal
> `DevCtx FFFFD609015CC3D0: [---] Unknown Ioctl 41018` is **benign**. NvmeDirect received a command it doesn't recognize — not indicative of an NVMe stack error. Ref: TSG: NVMe Direct Errors (eng.ms RDOS).

---

## HW-5: Host Node Memory

> **TSG**: `/Unexpected Restarts/TSGs/Host Node Memory Investigation_Restarts`
> **Scope**: Low memory, ECC errors, and related VM start failures.

### HW-5.Q1 — Resource-Exhaustion-Detector (host low memory)

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where EventId == "2004" and ProviderName contains "Microsoft-Windows-Resource-Exhaustion-Detector"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h) and NodeId == "{NodeId}"
```

### HW-5.Q2 — Hyper-V Worker low-memory event IDs (VM start failures)

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where EventId in ("12030", "3122", "3050", "3030") and ProviderName contains "Microsoft-Windows-Hyper-V-Worker"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h) and NodeId == "{NodeId}"
```

### HW-5.Q3 — Tenant events for "0x8007000E" (out of memory error)

```kusto
cluster("Azcsupfollower").database("AzureCM").TMMgmtTenantEventsEtwTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h)
    and TenantName == "{TenantName}"
| where Message contains "0x8007000E"
| project PreciseTimeStamp, Message, TenantName, EventMessage
```

### HW-5.Q4 — Sparkle SEL Uncorrectable ECC (memory HW)

```kusto
cluster("sparkle.eastus").database("defaultdb").SparkleSELByNodeId(
    nodeId="{NodeId}", startTime=ago(3d), endTime=ago(1h))
| where EventDetail contains "Uncorrectable ECC"
| project BMCSelTimestamp, NodeId, SelSource, Cluster, GeneratorId, SensorType, EventDetail, BlobUrl, CorrelationId
```

### Memory-related Event IDs to know
- **Event 153** (Disk) — Disk missing inside Guest OS, often caused by low memory on host
- **Event 41** — Dirty shutdown (combined with memory pressure)
- **Memory Correctable ECC** vs **Uncorrectable ECC** — uncorrectable is HW-replace-worthy

---

## HW-6: IERR (Internal Error — CPU SEL)

> **TSG**: `/Unexpected Restarts/TSGs/IERR Investigation_Restarts`
> **Scope**: CPU IERR signature in BMC SEL → typically requires HW replacement.

### HW-6.Q1 — Sparkle SEL filter for IERR

```kusto
cluster("sparkle.eastus").database("defaultdb").SparkleSELByNodeId(
    nodeId="{NodeId}", startTime=datetime({StartTime})-1d, endTime=datetime({EndTime})+1d)
| where EventDataDetails1 contains "IERR" or EventDetail contains "IERR" or RawHex contains "IERR"
| project BMCSelTimestamp, NodeId, SelSource, SensorType, EventDetail, EventDataDetails1, RawHex
```

### Signature pattern
- Look for `"Processor": "IERR"` in the SEL `EventDetail` JSON.
- If found → HW failure, escalate to Hardware team (DCM auto-marks NeedRepair).
- Cross-check HW-1.Q7/Q8 (`ResourceSnapshotHistoryV1/V2`) for repair history.

---

## HW-7: AN Overlake SoC — FaultCode 10036

> **TSG**: `/Unexpected Restarts/TSGs/Accelerated Network FaultCode 10036_Restarts`
> **Scope**: NVA VM with Accelerated Networking on Azure Boost (Overlake) host — SoC memory >95% utilization → fabric marks node unallocatable → LM triggered.
> **Escalation**: Azure Networking via `OPEX-VM-AZNET-Collaboration-Guidelines_Process`.

### HW-7.Q1 — VMA join with LogNodeSnapshot Unallocatable

```kusto
let nodelist = (
    cluster("vmainsight").database("vmadb").VMA
    | where PreciseTimeStamp between (datetime({StartTime}) .. now())
        and Subscription == "{SubscriptionId}"
        and RoleInstanceName has_any ("{VMName}")
    | distinct StartTime, EndTime, NodeId, TenantName, RoleInstanceName, RCALevel1, RCALevel2, RCALevel3,
        Cluster, UD, Subscription, Usage_ResourceGroupName, Region, RCA_CSS, ContainerId, VmUniqueId,
        Watson_CrashDumpLink, Watson_BugLink, Watson_DumpType, E17_ClusterFailureReportUrl
    | distinct NodeId, RoleInstanceName);
cluster("azurecm").database("AzureCM").LogNodeSnapshot
| where TIMESTAMP > datetime({StartTime}) and nodeId in (nodelist | project NodeId)
| project TIMESTAMP, nodeId, nodeAvailabilityState, faultInfo, Tenant, isMaintenanceOs
| where nodeAvailabilityState != 'Available'
| summarize start=min(TIMESTAMP), end=max(TIMESTAMP) by nodeId, Tenant, isMaintenanceOs, nodeAvailabilityState, faultInfo
| join kind=inner nodelist on $left.nodeId == $right.NodeId
| project-away NodeId
| project-reorder start, end, RoleInstanceName
```

### faultInfo signature
```json
{
  "Reason": "Manually injected fault - high memory usage",
  "FaultCode": 10036,
  "Details": "Manually injected fault - high memory usage",
  "NodeFaultType": 3,
  "FabricOperationString": "ForceNodeState",
  "ExtendedDetails": [
    {"Name": "AllowLM", "Value": "True"},
    {"Name": "ASM_AvailabilityState", "Value": "Unallocatable"},
    {"Name": "IsIssuedByAnvil", "Value": "true"}
  ]
}
```

### Mitigation
- Distribute NVA traffic load across multiple instances → reduce per-node SoC memory consumption.
- Long-term: PG-tracked improvement.

### HW-7.Q.ANUpdate — Accelerated Network update variant (planned maintenance)

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/Accelerated Network Update Requiring Reboot_Restarts`
> **Trigger**: Same `FaultCode == 10036` as HW-7 base, but `faultInfo.Reason` is the literal string **`"Manually injected fault - mitigate accelnet issue"`** (not high memory). This is **planned maintenance** to update accelerated-network components — full node reboot required, LM attempted but may fail → VM restart possible. Customer is typically notified in advance.

#### Q-ANUpd-1 — Confirm AccelNet update injection

```kusto
cluster('Azcsupfollower').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and nodeId == "{NodeId}"
| where faultInfo contains "Manually injected fault - mitigate accelnet issue"
| project PreciseTimeStamp, nodeId, Tenant, RoleInstance, containerCount, faultInfo
```

**Expected faultInfo signature**:

```json
{
  "Reason": "Manually injected fault - mitigate accelnet issue",
  "FaultCode": 10036,
  "NodeFaultType": 3,
  "FabricOperation": 1,
  "FabricOperationString": "ForceNodeState",
  "NodeState": 10,
  "ExtendedDetails": [
    {"Name": "FaultedByExternalEntity", "Value": "azdeployerapi.trafficmanager.net"},
    {"Name": "ASM_AvailabilityState", "Value": "Unallocatable"},
    {"Name": "RequestAuthor", "Value": "Fabric_Operator"},
    {"Name": "IsIssuedByAnvil", "Value": "true"},
    {"Name": "EvacuationStrategies", "Value": "All"}
  ]
}
```

#### Customer RCA template

Use `VMA_RCA_Maintenance_AccelNet_Update_Reboot` — explain Azure HostNet team identified a small fleet where AccelNet components require update to mitigate a reliability issue; node reboot required; LM attempted but may not succeed for all VMs. **Each VM unavailable up to 15 min** during the maintenance window. OS + data disks retained; temp disk reset.

---

## HW-8: Thermal Trip (Power Off + Processor Thermal + Watchdog 2)

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/Host OS Unhealthy with Thermal Trip_Restarts`
> **Scope**: Node powered off suddenly with no apparent reason — SEL shows the **triple signature**: `Power Unit: Power Off/Power Down` + `Processor: Thermal Trip` + `Watchdog 2: Timer expired status only`. Observed primarily on Lenovo HW (clusters `AMS09PrdApp37`, `DB4PrdApp31`).
> **Escalation**: HW Triage + Lenovo via Hardware PG.

### HW-8.Q1 — Sparkle SEL triple-signature check

```kusto
let query_BeginTime = datetime({StartTime});
let query_EndTime = datetime({EndTime});
let query_NodeId = "{NodeId}";
cluster("sparkle.eastus.kusto.windows.net").database("defaultdb").SparkleSELByNodeId(nodeId=query_NodeId)
| where BMCSelTimestamp >= query_BeginTime and BMCSelTimestamp <= query_EndTime
| project-reorder BMCSelTimestamp, PreciseTimeStamp, EventDataDetails1
| where EventDataDetails1 has_any ("Power Off/Power Down", "Thermal Trip", "Watchdog 2", "transition to Non-recoverable")
```

**Confirmation**: All three event-detail strings appear within seconds of each other:
- `{"Power Unit": "Power Off/Power Down"}`
- `{"Processor": "Thermal Trip"}`
- `{"Watchdog 2": "Timer expired status only"}`
- Often accompanied by `{"Discrete": "transition to Non-recoverable"}`

### HW-8 — Customer RCA (interim)

Use `VMA_RCA_Hardware_NodeReboot_ThermalTrip` (interim wording while Lenovo investigation continues): "A very small set of physical host nodes lost network connectivity, experienced a hard hang, and became unresponsive due to a hardware failure. Azure Compute and Hardware teams are actively investigating the root cause and are working with the hardware vendor to better understand the issue."

### Related ICMs (for pattern matching)
- 371562492, 371645150, 371796786, 371640627

---

## HW-9: PSU / Rack Manager FaultCode 31021

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/PSU_or_Power_Supply_Failure_or_PowerReset`
> **Scope**: Sudden node power-off caused by failing **Rack Manager (RM)**. A failing RM can damage BMC power-supply pins; when the RM reboots due to internal faults, nodes experience unplanned restarts.
> **Signal**: VMA `RCA_CSS == "Unplanned.NodeFault.FD_FAULT"` + Hawkeye `Scenario == "UnhealthyNode_Unexpected Reboot_PowerReset_NonFabricInitiated"` + SEL Power Supply Failure + AzureDCMDb shows RM `FaultCode == "31021"` (Vendor Attention).
> **Reference**: [Fault Code 31021 description](https://fcgb.selfservice.trafficmanager.net/FaultCodes/ViewFaultCodes?SearchString=31021).

### HW-9.Q1 — VMA RCA (FD_FAULT)

```kusto
let query_BeginTime = datetime({StartTime});
let query_EndTime = datetime({EndTime});
cluster("Vmainsight").database("vmadb").VMA
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime)
| where Subscription =~ "{SubscriptionId}"
    and RoleInstanceName has "{NodeId}"
    and RCAEngineCategory !contains "Customer"
    and RCA_CSS !has "Unknown"
| distinct PreciseTimeStamp, NodeId, RoleInstanceName, RCAEngineCategory,
    RCALevel1, RCALevel2, RCA_CSS, Cluster, ContainerId, CSS_SrID
```

### HW-9.Q2 — Hawkeye scenario

```kusto
cluster("hawkeyedataexplorer.westus2").database("HawkeyeLogs").HawkeyeRCAEvents
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId == "{NodeId}"
| extend EscalateToOrg = iff(EscalateToTeam == "CSI", "CSI", EscalateToTeam)
| distinct NodeId, Scenario, FaultTime, RCALevel1, RCALevel2, EscalateToOrg, EscalateToTeam
```

### HW-9.Q3 — Sparkle SEL (Power Supply Failure)

```kusto
let query_BeginTime = datetime({StartTime});
let query_EndTime = datetime({EndTime});
let query_NodeId = "{NodeId}";
cluster("sparkle.eastus").database("defaultdb").SparkleSELByNodeId(nodeId=query_NodeId)
| where BMCSelTimestamp between (query_BeginTime .. query_EndTime)
| project-reorder BMCSelTimestamp, PreciseTimeStamp, EventDataDetails1
| summarize DuplicateCount = count(),
    tostring(make_set(SelSource)),
    tostring(make_set(EventDataDetails1))
  by BMCSelTimestamp, RawHex
```

Look for `"Power Supply Failure detected"`.

### HW-9.Q4 — AzureDCMDb RM FaultCode 31021 lookup

> **Permission**: Request `Kusto HqseDB Reader` in CoreIdentity to access `hqse.hqsedb.VacateRMList`.

```kusto
cluster("sparklefollower.centralus.kusto.windows.net").database("AzureDCMDb").ResourceSnapshotV1
| where DeviceType == "Blade"
| where ResourceId in ("{NodeId}")
| extend PowerDeviceLocation = trim(" ", tostring(PowerDeviceLocation))
| project Tenant, NodeId = ResourceId, Model, LifecycleState, FaultCode, FaultDescription,
    PowerDeviceId, PowerDeviceLocation
| lookup (
    cluster("hqse").database("hqsedb").VacateRMList
    | where MoveReason in ("GPIOError", "RMBMCIssues", "UnknownRMNoData",
        "LoginOobLoginFalse", "ConfirmedUnsafe", "BUG 2268029 : Syslog")
    | project-rename PowerDeviceId = ResourceId
) on PowerDeviceId
| extend MoveReason = coalesce(MoveReason, "N/A")
| join kind=leftouter (
    cluster("Azuredcm").database("AzureDCMDb").ResourceSnapshotV1
    | where FaultCode == "31021"
    | extend RMName = trim(" ", tostring(Name))
    | project RMName, RMLifecycleState = LifecycleState, RMFaultcode = FaultCode
) on $left.PowerDeviceLocation == $right.RMName
| project Tenant, NodeId, Model, LifecycleState, FaultCode, FaultDescription, PowerDeviceId,
    RMName, MoveReason,
    RMLifecycleState = coalesce(tostring(RMLifecycleState), "N/A"),
    RMFaultcode = coalesce(tostring(RMFaultcode), "N/A")
```

**Confirmed signature**: `RMLifecycleState == "VendorAttention"` AND `MoveReason == "ConfirmedUnsafe"` AND `RMFaultcode == "31021"`.

### Next steps / RCA
- **General customer** → use template `VMA_RCA_Hardware_NodeReboot_PSU` (csswiki page 496288).
- **Mission-critical** → open ICM to PG (CHIE / HW Triage).
- **Long-term**: Unsafe RM replacement scheduled 2–3 years (tracked in WI `1937379`).

---

# § STG — Storage / IO path

## STG-1: E17 Investigation (IaaS Disk Failure + XStore Triage)

> **TSG**: `/Unexpected Restarts/TSGs/E17 Investigation_Restarts`
> **Scope**: Event 17 = IaaS Disk Failure. Cross-reference vmadb, host WindowsEventTable, and Xportal disk triage.

### STG-1.Q1 — VMALENS (RCALevel2 lookup)

```kusto
cluster("vmainsight").database("vmadb").VMALENS
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime("{StartTime}") .. datetime("{EndTime}"))
| project StartTime, EndTime, RoleInstanceName, Cluster, RCALevel2
```

### STG-1.Q2 — vmadb WindowsEventTable (aggregated)

```kusto
cluster("vmainsight").database("vmadb").WindowsEventTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime("{StartTime}") .. datetime("{EndTime}"))
| where EventId !in ("146", "0", "505", "504", "3095")
| project TIMESTAMP, EventId, Description
```

### STG-1.Q3 — Fa WindowsEventTable (host raw)

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime("{StartTime}") .. datetime("{EndTime}"))
| where EventId !in ("146", "0", "505", "504", "3095")
| project TIMESTAMP, EventId, Description
```

### STG-1.Q4 — Xportal Disk Failures (XStore triage)

```kusto
cluster("Xlivesite").database("XHealthDiskTriage").XHealth_DiskFailureXStoreTriage
| where NodeId == "{NodeId}"
| where env_time between (datetime("{StartTime}") .. datetime("{EndTime}"))
| project env_time, TriageCategory, TriageReason, TriageTimestamp, StorageRegion, StorageTenant, NodeId,
    ClusterFailureReportUrl, DiagnosticDetailsObject, DiskPath
```

### STG-1.Q5 — Xportal Disk Blackouts

```kusto
cluster("Xlivesite").database("XHealthDiskTriage").XHealth_DiskBlackoutXStoreTriage
| where NodeId == "{NodeId}"
| where EventTime between (datetime("{StartTime}") .. datetime("{EndTime}"))
| project EventTime, TriageCategory, TriageReason, TriageTimestamp, StorageRegion, StorageTenant, NodeId,
    ClusterFailureReportUrl, DiskPath
```

### STG-1.Q6 — Event17 table (with Xdiskreport URL)

```kusto
cluster("vmainsight").database("vmadb").Event17
| where E17_NodeId == "{NodeId}"
| where AccountName == "{StorageAccountName}"
| where E17_timestamp between (datetime("{StartTime}") .. datetime("{EndTime}"))
| project E17_timestamp, AccountName, VhdPath, E17_Cluster, E17_NodeId, E17_ErrorCode, XdiskErrorCode,
    RCA, RCAL2, TriageSummary, E17_ClusterFailureReportUrl
```

### STG-1.Q7 — NetVMA cross-check (Hyper-V VmSwitch / NIC drivers / DNS)

```kusto
cluster("vmainsight").database("vmadb").WindowsEventTable
| where NodeId contains "{NodeId}"
| where PreciseTimeStamp between (datetime("{StartTime}") .. datetime("{EndTime}"))
| where ProviderName in ('Microsoft-Windows-Hyper-V-VmSwitch', 'mlx4eth63', 'mlx4_bus', 'Microsoft-Windows-DNS-Client')
| project PreciseTimeStamp, NodeId, Cluster, EventId, ProviderName, Description
```

---

## STG-2: Blob Cache Disk Error — FaultCode 10005 + 0x80078000

> **TSG**: `/Unexpected Restarts/TSGs/Blob Cache Disk Error_Restarts`
> **Scope**: VM crashes due to bad host disk; later reboot fails → service-healed as Container Fault with `FaultCode 10005` + `0x80078000`. Classic pattern: BlobCache Event 1 → Disk Event 7/11.

### STG-2.Q1 — BlobCache Event 1 joined with Disk Event 7/11 (within 5min)

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and EventId == 1 and ProviderName == "BlobCache" and NodeId == "{NodeId}"
| project-rename CachErrorTimestamp = PreciseTimeStamp
| join (
    cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
    | where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
        and EventId in (11, 7)
) on NodeId
| project-rename DiskEventTimestamp = PreciseTimeStamp
| where (DiskEventTimestamp - CachErrorTimestamp) between (0min .. 5min) and CachErrorTimestamp <= DiskEventTimestamp
| project NodeId, CachErrorTimestamp, DiskEventTimestamp, EventId, DiskEvent=EventId1, ProviderName, Description
```

### STG-2.Q2 — Service Healing Trigger with FaultCode 10005 + 0x80078000

```kusto
cluster("AzureCM").database("AzureCM").ServiceHealingTriggerEtwTable
| where TenantName == "{TenantName}"
| where FaultCode == 10005 and FaultReason contains "0x80078000" and RoleInstanceName contains "{VMName}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project PreciseTimeStamp, TenantName, TriggerType, FaultReason, RoleInstanceName
```

### STG-2.Q3 — Same 0x80078000 in NodeEvents

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtNodeEventsEtwTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where Message contains "VmalError Value:0x80078000"
| project TIMESTAMP, NodeId, Message
```

### Pattern
1. **t0**: BlobCache Event 1 → Disk Event 7 / LSI_SAS2i Event 11 (bad disk)
2. **t0+ hours/days**: VM reboot attempt fails → service healed as Container Fault `FC 10005 / 0x80078000`
3. **Action**: Node should be removed from production. If monitoring missed it, request platform team manual removal.

---

## STG-3: Live Migration VFPRestoreFailure (NMAgent Event 356)

> **TSG**: `/Unexpected Restarts/TSGs/Live Migration Failure due to VFPRestoreFailure_Restarts`
> **Scope**: LM (often triggered by defrag or bad HW) fails because VFP state cannot be serialized/restored → VM restarts. Customer may see repeat impact if Azure keeps re-trying LM.
> **Root cause (internal)**: insufficient space on SoC to serialize VFP port state during LM.

### STG-3.Q1 — Container placement (get VMId + ContainerId)

```kusto
let sid = "{SubscriptionId}";
let vmname = "{VMName}";
cluster("azurecm").database("AzureCM").LogContainerSnapshot
| where subscriptionId == sid and roleInstanceName has vmname
| summarize arg_min(PreciseTimeStamp, containerId, nodeId, tenantName),
            arg_max(PreciseTimeStamp, containerId, nodeId, tenantName)
    by Tenant, roleInstanceName, subscriptionId, creationTime, virtualMachineUniqueId,
       containerId, nodeId, tenantName, containerType, billingType, updateDomain, availabilitySetName, RegionFriendlyName
| project ContainerCreationTime=todatetime(creationTime), StartTimeStamp=PreciseTimeStamp,
    EndTimeStamp=PreciseTimeStamp1, VMName=roleInstanceName, VMId=virtualMachineUniqueId,
    Cluster=Tenant, NodeId=nodeId, ContainerId=containerId, tenantName
```

### STG-3.Q2 — LM session ⨯ LiveMigrationFailureEvents

```kusto
let queryFrom = datetime({StartTime});
let queryTo = datetime({EndTime});
let vmid = "{VMId}";
let queryContainerId = "{ContainerId}";
let containers = cluster("azcsupfollower.kusto.windows.net").database("AzureCM").LogContainerSnapshot
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where (isnotempty(vmid) and virtualMachineUniqueId == vmid) or (isempty(vmid) and containerId == queryContainerId)
    | distinct containerId;
cluster("azurecm").database("AzureCM").LiveMigrationSessionCompleteLog
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where sourceContainerId in (containers)
| extend elapsedSec = totimespan(elapsedTime) / 1s
| extend Health = case(status == "Completed", "Healthy", status == "Faulted", "Unhealthy", "Degraded")
| extend Content = triggerType
| extend StartTime = PreciseTimeStamp - totimespan(elapsedTime)
| project StartTime, EndTime=PreciseTimeStamp, Health, Content, sessionId, status, elapsedTime, reason, message,
    sourceContainerId, sourceNodeId, destinationContainerId, destinationNodeId
| join kind=leftouter (
    cluster("azcsupfollower.kusto.windows.net").database("Air").LiveMigrationFailureEvents
    | where EventTime between (queryFrom .. queryTo)
    | where ObjectId in (containers)
    | project RCALevel1, RCALevel2, Diagnostics=parse_json(Diagnostics), sessionId=tostring(parse_json(Diagnostics).SessionId)
) on sessionId
| project-away sessionId1
| order by StartTime asc
```

### STG-3.Q3 — NMAgent Event 356 (Save of VFP State Failure)

```kusto
let nodeid = "{NodeId}";
let starttime = datetime({StartTime});
let endtime = datetime({EndTime});
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId == nodeid
| where ProviderName == "NMAgent"
| project PreciseTimeStamp, StartTime=todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| extend Content = Description
| order by StartTime asc
```

### Signature
- `RCALevel2 == "VFPRestoreFailure"` in VMA or LiveMigrationFailureEvents
- NMAgent `Event 356`: "Save of VFP State Failure for Container: <ContainerId>"

---

## STG-4: DataPath HostPlugin Update (DPHU)

> **TSG**: `/Unexpected Restarts/TSGs/DataPath HostPlugin Update_Restarts`
> **Scope**: Host data-path plugin update caused VM impact. Cross-cluster join of OS VHD events with SLA measurements.
> **Note**: Wiki search for the exact path returned 0 hits on 2026-06-03 — page may have been renamed. Use the queries below (captured from prior session) and fall back to MAINT-1 (Host Node Update) if signature matches.

### STG-4.Q1 — OsVhddiskEventTable (host OS VHD events)

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").OsVhddiskEventTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project PreciseTimeStamp, NodeId, ContainerId, EventId, Operation, ResultCode, Description
| order by PreciseTimeStamp asc
```

### STG-4.Q2 — SLA measurement events around the update

```kusto
cluster("AzureCM").database("AzureCM").TMMgmtSlaMeasurementEventEtwTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project PreciseTimeStamp, NodeId, ContainerId, SlaType, MeasurementValue, Threshold, Status
```

### STG-4.Q3 — Plugin update events on this node

```kusto
cluster("azcsupfollower").database("AzureCM").TMMgmtNodeEventsEtwTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where Message contains 'CreatePluginComplete' or Message contains 'UpdatePluginCompleted'
| parse kind=regex Message with * ' = HostPluginName:' Component:string ', HostPluginSetupFile:' * 'HostPluginPackage:' package:string ', Action:' *
| project PreciseTimeStamp, NodeId, Component, package, Message
```

### STG-4.Q4 — Hyper-V Worker DataPath events on this container

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and ProviderName == "Microsoft-Windows-Hyper-V-Worker"
| where Description contains "{ContainerId}"
| project TimeCreated, EventId, ProviderName, Description
| order by TimeCreated asc
```

---

# § MAINT — Maintenance / Updates

## MAINT-1: Host Node Update (NMAgent / Gandalf / RootHE chain)

> **TSG**: `/Unexpected Restarts/TSGs/Host Node Update Investigation_Restarts`
> **Scope**: Find which Host plugin/service was updated, when, and whether it caused VM impact. Confirm via VMPHU events and Hyper-V Worker save/resume (Event 18598 / 18518).
> **Customer RCA signal**: Verify Guest VM Event 1135 (cluster failover) before sending an RCA mentioning Host Update.

### MAINT-1.Q1 — RootHE node goal version change (datapath versions)

```kusto
cluster("Vmainsight").database("vmadb").RootHENodeGoalVersionChange
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h) and NodeId == "{NodeId}"
| distinct PreciseTimeStamp, NodeId, OldValue, NewValue
```

### MAINT-1.Q2 — OSHostplugin provider events

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h)
    and NodeId == "{NodeId}" and ProviderName contains "OSHostplugin"
| project TimeCreated, EventId, ProviderName, Channel, Description, NodeId
| order by TimeCreated asc
```

### MAINT-1.Q3 — Hyper-V Worker on specific container

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({StartTime}) + 24h)
    and NodeId == "{NodeId}" and ProviderName == "Microsoft-Windows-Hyper-V-Worker"
| where Description contains "{ContainerId}"
| project TimeCreated, EventId, ProviderName, Description
| order by TimeCreated asc
```

### MAINT-1.Q4 — Customer RCAs for VMPHU (by subscription)

```kusto
cluster("vmainsight").database("Air").GetVMPhuEventsBySubId("{SubscriptionId}", datetime({StartTime}), datetime({EndTime}))
| project Cluster, RoleInstanceName, ContainerId, NodeId=ResourceId,
    ImpactBeginTimeStamp, ImpactEndTimeStamp, ImpactDurationTimeSpan
```

### MAINT-1.Q5 — Customer RCAs for VMPHU (by VMID)

```kusto
cluster("vmainsight").database("Air").GetVMPhuEvents("{VMId}", datetime({StartTime}), datetime({EndTime}))
| project RoleInstanceName, EventType, ImpactBeginTimeStamp, ImpactEndTimeStamp, ImpactDurationTimeSpan
```

### MAINT-1.Q6 — VMPHU downtime via Event 18518 (resume) + 18598 (save) join

```kusto
let dateTime_StartTime = datetime({StartTime});
let dateTime_EndTime = datetime({EndTime});
let subscription = "{SubscriptionId}";
let vmName = "{VMName}";
cluster("azcsupfollower").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp between (dateTime_StartTime..dateTime_EndTime)
    and subscriptionId =~ subscription and roleInstanceName has vmName
| distinct nodeId, containerId
| join kind=leftouter (
    cluster("azcore.centralus").database("Fa").WindowsEventTable
    | where TIMESTAMP between (dateTime_StartTime..dateTime_EndTime)
        and EventId == "18518" and ProviderName == "Microsoft-Windows-Hyper-V-Worker"
    | extend resumeTimestamp = todatetime(TimeCreated)
) on $left.nodeId == $right.NodeId
| where Description has containerId
| join kind=leftouter (
    cluster("azcore.centralus").database("Fa").WindowsEventTable
    | where TIMESTAMP between (dateTime_StartTime..dateTime_EndTime)
        and EventId == "18598" and ProviderName == "Microsoft-Windows-Hyper-V-Worker"
    | extend saveTimestamp = todatetime(TimeCreated)
) on $left.nodeId == $right.NodeId
| where Description has containerId
| extend VMPHU_calc = resumeTimestamp - saveTimestamp
| project VMPHU_Downtime = format_timespan(VMPHU_calc, 'mm:ss'),
    saveTimestamp, resumeTimestamp, NodeId, containerId, subscription, vmName
| take 1
```

### MAINT-1.Q7 — Same VMPHU downtime via vmadb (alt path with NodeId+ContainerId)

```kusto
let dateTime_StartTime = datetime({StartTime});
let dateTime_EndTime = datetime({EndTime});
let node = "{NodeId}";
let containerId = "{ContainerId}";
cluster("Vmainsight").database("vmadb").WindowsEventTable
| where TIMESTAMP between (dateTime_StartTime..dateTime_EndTime)
    and EventId == "18518" and ProviderName == "Microsoft-Windows-Hyper-V-Worker" and NodeId == node
| extend resumeTimestamp = todatetime(TimeCreated)
| where Description has containerId
| join kind=leftouter (
    cluster("Vmainsight").database("vmadb").WindowsEventTable
    | where TIMESTAMP between (dateTime_StartTime..dateTime_EndTime)
        and EventId == "18598" and ProviderName == "Microsoft-Windows-Hyper-V-Worker"
    | extend saveTimestamp = todatetime(TimeCreated)
) on $left.NodeId == $right.NodeId
| where Description has containerId
| extend VMPHU_calc = resumeTimestamp - saveTimestamp
| project VMPHU_Downtime = format_timespan(VMPHU_calc, 'mm:ss'),
    saveTimestamp, resumeTimestamp, NodeId, containerId
| take 1
```

### MAINT-1.Q8 — Full update timeline (4-way union: ServiceManager + RootHE + Gandalf + NMAgent)

```kusto
let ServiceManger = (cluster("azcsupfollower").database("AzureCM").ServiceManagerInstrumentation);
let RootHE = (cluster("Vmainsight").database("vmadb").RootHENodeGoalVersionChange
    | extend RootHE_OldValue=OldValue, RootHE_NewValue=NewValue);
let RootHEGaldaf = (cluster("azcsupfollower").database("AzureCM").RootHEGandalfInformationalEventEtwTable
    | extend RootHEGandalf_OldValue=OldVersion, RootHE_NewValueGandalf=NewVersion);
let NMAgent = (cluster("vmainsight.kusto.windows.net").database("Air").AirMaintenanceEvents
    | extend PreciseTimeStamp = EventTime
    | extend Diagnostics = tostring(Diagnostics));
union ServiceManger, RootHE, RootHEGaldaf, NMAgent
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp < datetime({EndTime})
| where NodeId == "{NodeId}"
| summarize NodeUpdatedAtApprox=min(PreciseTimeStamp) by ServiceVersion, ServiceName,
    RootHE_OldValue, RootHE_NewValue, RootHEGandalf_OldValue, RootHE_NewValueGandalf,
    EventCategoryLevel2, EventCategoryLevel3, Component, OutageType, Diagnostics, NodeId
| project-reorder NodeUpdatedAtApprox, NodeId
| order by NodeUpdatedAtApprox asc
```

### MAINT-1.Q9 — NmAgent version pin on node

```kusto
cluster("azcsupfollower").database("AzureCM").ServiceManagerInstrumentation
| where NodeId == "{NodeId}" and ServiceName == "NmAgent" and PreciseTimeStamp > datetime({StartTime})
| summarize min(PreciseTimeStamp) by ServiceVersion, ServiceName
```

---

# § NET — Networking-induced restarts

## NET-1: TOR Hardware Failure / Reload

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/Network TOR Hardware Failure_Restarts`
> **Scope**: Top-of-Rack (TOR) switch failure causes E17 / IO timeout / unhealthy-node reboot on **all nodes in the rack**. Signature in VMA: `VMA_RCA_IO_Timeout_NodeReboot_TOR_e17` template.
> **Escalation**: Network — Cloudnet / TOR HW team.

### NET-1.Q1 — TOR reload reason (azwan FUSE)

```kusto
cluster('azwan').database('azwannet').FUSE
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where Device has "{ClusterName}" or HostName has "{TorName}"
| project PreciseTimeStamp, Device, HostName, ReloadReason, EventDetail
```

### NET-1.Q2 — Repeat device reload failures (`azphynet.dhDeviceReload`)

```kusto
cluster('azphynet').database('azdhmds').dhDeviceReload
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where DeviceName has "{TorName}" or Cluster == "{ClusterName}"
| project PreciseTimeStamp, DeviceName, Cluster, ReloadStatus, FailureReason, RetryCount
```

### NET-1.Q3 — VM list under faulty TOR (LogContainerSnapshot ⋈ DeviceInterfaceLinks)

```kusto
let faultyTor = "{TorName}";
let impactedNodes =
  cluster('azphynet').database('azdhmds').DeviceInterfaceLinks
  | where PeerDeviceName == faultyTor
  | distinct NodeId;
cluster("azcsupfollower").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
    and nodeId in (impactedNodes)
| distinct nodeId, containerId, roleInstanceName, Tenant, Subscription, RoleInstance
```

### NET-1 RCA
- Confirmed TOR reload → use `VMA_RCA_IO_Timeout_NodeReboot_TOR_e17` for all impacted VMs (batch RCA).
- If TOR replacement is needed → file a collab to the **Azure Networking team (ANP)** via DFM Create Collaboration (ANP triages and escalates to the networking PG; we file + follow up).

---

## NET-2: Overlake SoC Investigation

> **TSG**: `/SME Topics/Unexpected Restarts/TSGs/Overlake(SoC) Node Investigation_Restarts`
> **Scope**: Overlake is the host architecture that offloads network management to a dedicated **SoC (System-on-Chip)** card running Linux. Host OS / RDOS logs alone are insufficient — SoC OS + application logs must be inspected via Overlake-specific Kusto clusters.
> **Escalation**: **Azure Networking Pod (ANP)** team.

### NET-2.Q1 — Confirm node is Overlake (SoC attached)

```kusto
cluster("overlakedata.southcentralus.kusto.windows.net").database("overlake-syslog").OverlakeMap_Latest
| where NodeId =~ "{NodeId}"
| project SocNodeId
```

If a `SocNodeId` is returned → continue with NET-2.Q2+. Otherwise → not Overlake; investigate via NET-1 or HW-x.

### NET-2.Q2 — SoC OS processed signals (kernel crash / reboot)

```kusto
let socHostName = toscalar(
  cluster("overlakedata.southcentralus.kusto.windows.net").database("overlake-syslog").OverlakeMapV2
  | where NodeId == "{NodeId}"
  | project HostName
  | take 1);
cluster("overlakedata.southcentralus.kusto.windows.net").database("overlake-syslog").OverlakeSoCProcessedSignals
| where IngestionTime between (datetime({StartTime}) .. datetime({EndTime}))
| where MESSAGEList contains socHostName
| where Scenario <> "SELinuxViolations"
| project StartTimeStamp, EndTimeStamp, IngestionTime, Cluster, SoCNameList, Scenario, Component, MESSAGEList
```

### NET-2.Q3 — Linux SoC systemd log (use SHORT window — extremely large)

```kusto
cluster('azcore.centralus.kusto.windows.net').database('ovlprod').LinuxOverlakeSystemd
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId == "{SocNodeId}"
| project PreciseTimeStamp, SYSLOG_IDENTIFIER, _SYSTEMD_SLICE, _TRANSPORT, MESSAGE, MachineName, NodeId
```

### NET-2 — ASI cross-check
- EEE HostNode Start Hub → look for SoC kernel-dump / reboot events.
- DRI Dashboard SoC tile: <http://aka.ms/dridash> → input Time range, NodeId, ContainerID → click **SoC**.
- Node Story: <https://aka.ms/nodestory> (shows systemd + health logs visually).

### NET-2 — Known issue: error `0xbadfd` (VFP backplane hang)

If `LinuxOverlakeSystemd.MESSAGE` contains the error code **`0xbadfd`** in any of these patterns:
- `Create VFP port failed for PortExternal_XXXXXXXX with error 0xbadfd`
- `PortManager::GetExistingPortFromVfp GetVfpPortList failed with error 0xbadfd`
- `PortManager::PortManagerThreadProc: Get port from VFP failed with error 0xbadfd ...`

→ VFP backplane component is hung. **Engage Azure Networking Pod (ANP)** — do NOT file a new escalation to EEE HostNode.

### NET-2 RCA
- Any SoC OS issue confirmed → file a collab to **Azure Networking team (ANP)** via DFM Create Collaboration (ANP triages and, if backend, escalates to the networking PG; we follow up).
- Reference: [Project Overlake wiki](https://supportability.visualstudio.com/AzureNetworking/_wiki/wikis/Wiki/677371/Project-Overlake) · [Engineering Doc](https://eng.ms/docs/cloud-ai-platform/azure-core/core-compute-and-host/general-purpose-host-arunki/host-networking/datapath-documentation/overlake/overview).

---

# § GUEST — Guest OS (out of scope here)

For guest-side restart investigation:
- **Linux**: dmesg, journal, kdump, OOM-killer, panic — delegate to `vm-log-analyzer` (TSG `/Unexpected Restarts/TSGs/Linux Guest Restart_Restarts` is pure operational walkthrough, no Kusto).
- **Windows**: Event Log 41 / 1074 / 1076, BSOD minidump, CBS — delegate to `vm-log-analyzer` (TSG `/Unexpected Restarts/TSGs/Windows Guest Restart_Restarts` is pure operational walkthrough, no Kusto).

Both TSGs above contain zero Kusto queries — they describe lab-box / Serial Console / dump collection procedures.

---

## Cross-references

| When you need | Go to |
|---|---|
| The classification step (Step 2 of the workflow) | [`playbook-A-restarts-core.md`](playbook-A-restarts-core.md) § Step 2 |
| ASAP / NVMe-on-Boost specifics | `asap-storage-queries.md` |
| PCIe / GPU failure deep-dive | `pcie-failure-queries.md` + `PCIefatal_error.md` |
| Networking-side root causes (VPN/SLB/AppGW etc.) | `networking-queries.md` |
| Storage Account behavior (XStore / XArgus / billing) | `storage-account-queries.md` |
| Customer RCA email writeup | draft the customer RCA manually (keep internal identifiers out) |
| Hardware / platform escalation | Open an ICM manually via ASC for Hardware / XStore / EEE Host Node (Escalate ticket). If the root cause is networking (ANP), file a collab to the Azure Networking team instead (see NET rows below) |
| Sparkle SEL RawHex decode + PCIe BDF mapping | `PCIefatal_error.md` (Table 11 C2789 BDF→device, 115 rows) |
| **Host Windows EventId master table** (60+ events, false-positive list, cluster-frequency check) | [`windows-events-reference.md`](../catalogs/windows-events-reference.md) |
| **VmOsCompositeState helper** (VmHyperVIcHeartbeat / VmPowerState / HyperVHandshake / IsVscStateOperational) | TSG `/Unexpected Restarts/TSGs/VMOsCompositeStateDown_Restarts` — query lives in SW-7.Q1 |
| **NVA / Accelerated Networking** on Boost host | HW-7 + HW-7.Q.ANUpdate |
| **Overlake SoC** (network offload card) | NET-2 (file a collab to the Azure Networking team (ANP) via DFM Create Collaboration; ANP escalates to the networking PG) |
| **TOR / rack-wide impact** | NET-1 |
