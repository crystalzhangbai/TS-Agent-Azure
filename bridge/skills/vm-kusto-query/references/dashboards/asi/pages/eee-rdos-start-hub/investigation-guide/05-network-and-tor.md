# Network & TOR

> Source: EEE RDOS Start Hub dashboard (17 queries).

Use when investigating: **network packet loss, TOR (top-of-rack) switch issues, NMAgent failures, SoC/FPGA/Overlake host networking, wireserver, VFP**. These queries cover the platform side of guest network problems.

---

### ToR-Hosts PingMesh

_Purpose:_ Network Health

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Timeline`

```kusto
let devicename = toscalar(cluster('azphynet').database('azdhmds').Servers
| where NodeId =~ nodeid
| project DeviceName );
let tor = toscalar(cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice == devicename
| project EndDevice);
let nodeIdlist = (cluster('azphynet').database('azdhmds').DeviceInterfaceLinks
| where EndDevice =~ tor and LinkType =~ 'DeviceInterfaceLink'
| summarize by DeviceName = StartDevice
| join kind = inner (
    cluster('azphynet').database('azdhmds').Servers
) on DeviceName
| summarize by NodeId);
let numOfNodes = tolong(toscalar(nodeIdlist|count));
cluster('aznwsdn').database('aznwmds').TorPingSendAggreEvent
| where TIMESTAMP between(queryFrom .. queryTo )
| where NodeId in~ (nodeIdlist)
| summarize SendCount = max(SendCount) by TIMESTAMP, NodeId
| join kind = leftouter (
    cluster('aznwsdn').database('aznwmds').TorPingRecvAggreEvent
    | where TIMESTAMP between(queryFrom .. queryTo )
    | where NodeId in~ (nodeIdlist)
    | summarize RecvCount = max(RecvCount) by TIMESTAMP, NodeId
) on TIMESTAMP, NodeId
| extend RecvCount = iff(isnull(RecvCount), 0, RecvCount)
| project StartTime = TIMESTAMP, rate = todouble(RecvCount)/todouble(SendCount) * 100, NodeId, RecvCount, SendCount
| summarize rate = min(rate), SendCount = toint(sum(SendCount)), RecvCount = toint(sum(RecvCount)), dcount(NodeId) by StartTime
| order by StartTime asc
| extend Health = case (
    dcount_NodeId < numOfNodes-1, "Unhealthy",
    rate < 90, "Unhealthy",    
    rate >= 100, "Healthy", 
    "Degraded")    
| extend flag = case (Health <> prev(Health), "changed", 
    isempty(next(StartTime)), "ended", 
    datetime_diff("Minute", next(StartTime), StartTime) > 5, "ended",
    "")
| where flag != ""
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), queryTo)
| where flag != "ended"    
| project StartTime, EndTime, rate, Health, Content = Health, ["Number of Responded Nodes"] =dcount_NodeId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

**Signal filters seen in KQL:** `flag != "ended"`

---

### Host-ToR PingMesh

_Purpose:_ Network Health

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Timeline`

```kusto
TorPingSendAggreEvent
| where TIMESTAMP >= starttime and TIMESTAMP < endtime
| where NodeId =~ nodeid
| summarize SendCount = max(SendCount) by TIMESTAMP, NodeId
| join kind = leftouter
(
TorPingRecvAggreEvent
| where TIMESTAMP >= starttime and TIMESTAMP < endtime 
| where NodeId =~ nodeid
| summarize RecvCount = max(RecvCount) by TIMESTAMP, NodeId
)on TIMESTAMP, NodeId
| extend RecvCount = iff(isnull(RecvCount), 0, RecvCount)
| project TIMESTAMP, NodeId, Availability = todouble(RecvCount) / todouble(SendCount) * 100, SendCount = toint(SendCount), RecvCount = toint(RecvCount), TimeWindowInMinutes = int(5)
| order by TIMESTAMP asc
| extend StartTime = TIMESTAMP
| extend Health = case (Availability == 100, "Healthy",
    Availability == 200, "Healthy", // Dual ToR Recv 2x Reply
    Availability < 90, "Unhealthy", 
    "Degraded")
| extend flag = case (Health <> prev(Health), "changed", 
    isempty(next(TIMESTAMP)), "ended", 
    datetime_diff("Minute", next(TIMESTAMP), TIMESTAMP) > 5, "ended",
    "")
| where flag != ""    
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), endtime)
| where flag != "ended"
| extend Content = Health
| project StartTime, EndTime, Content
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `flag != "ended"`

---

### ToR Health Event

_Purpose:_ Network Health

Cluster: `azphynet` · Database: `azdhmds` · Type: `Timeline`

```kusto
let devicename = toscalar(cluster('azphynet').database('azdhmds').Servers
| where NodeId =~ nodeid
| project DeviceName );
let tor = toscalar(cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice == devicename
| project EndDevice);
cluster('azphynet.kusto.windows.net').database('azdhmds').f_DeviceHealthLookupSimple(StartTime=queryFrom, EndTime=queryTo,SearchTerm=tor)
| project StartTime = TIMESTAMP, DeviceName, FailureReason, FailureSignal, HealthCategory, Health, Confidence, Persistence_1h, MetricValue, endDeviceIP, Content = FailureSignal
| extend Health = iif(FailureReason contains nodeid, "Error", "Neutral")
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### ToR Update

_Purpose:_ Network Health

Cluster: `azwan.kusto.windows.net` · Database: `FUSE` · Type: `Timeline`

```kusto
let devicename = toscalar(cluster("azphynet.kusto.windows.net").database("azdhmds").Servers
| where NodeId =~ queryNodeId
| project DeviceName );
let tor = toscalar(cluster("azphynet.kusto.windows.net").database("azdhmds").DeviceInterfaceLinks
| where StartDevice == devicename
| project EndDevice);
cluster("azwan.kusto.windows.net").database("FUSE").FUSE
| where Timestamp between ((queryFrom - 1h) .. (queryTo + 1h))
| where device contains tor
| where progress == "Finished"
| project Timestamp,  action, progress, targetState, jobId, StartTime = createTime, EndTime = endTime
| extend Content = strcat(action, " - ", targetState)
| extend Health  = "Degraded"
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `progress == "Finished"`

---

### ToR - Anvil Event

_Purpose:_ Network Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `aplat` · Type: `Timeline`

```kusto
let networkDeviceId = toscalar(cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(startofday(queryFrom) .. endofday(queryTo))
| where ResourceId == queryNodeId
| top 1 by PreciseTimeStamp desc
| project NetworkDeviceId);
cluster("aplat.westcentralus.kusto.windows.net").database("aplat").AnvilRepairServiceRequestSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ResourceId == networkDeviceId
| where SubStatus == "Received"
| extend Request = parse_json(Request)
| extend FaultCodeString = Request.RepairContext.FaultCodeString
| extend FaultReason = Request.RepairContext.FaultReason
| extend FaultTime = Request.RepairContext.Time
| project PreciseTimeStamp, RequestIdentifier, RequestAuthor, FaultCodeString, FaultReason, FaultTime, Request, Status, SubStatus, CorrelationIdentifier
| extend Content = tostring(FaultCodeString)
| extend StartTime = PreciseTimeStamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `SubStatus == "Received"`

---

### Wireserver Heartbeat

_Purpose:_ Network Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
WireserverHeartbeatEtwTable
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId == nodeid
| project PreciseTimeStamp, Status, Pid
| sort by PreciseTimeStamp asc
| serialize 
| extend prevTime = case (isnotempty(prev(PreciseTimeStamp)), prev(PreciseTimeStamp), starttime)
| extend prevDiff = PreciseTimeStamp - prevTime
| extend Health = case ( (prevDiff >= 62s and prevDiff != 0s and isnotempty(prev(PreciseTimeStamp))), "Unhealthy", "Healthy")
| extend flag = case (Health <> prev(Health), "changed" , "")
| where flag <> ""
| extend Content = Health
| extend StartTime = case (isnotempty(prevTime), prevTime, starttime)
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), endtime)
| project StartTime, EndTime, Content, prevDiff, Pid
```

**Params:** `{nodeid}`, `{starttime}`, `{endtime}`

---

### NMAgent Health

_Purpose:_ Network Health

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Timeline`

```kusto
AggVmHealthFailureVscStateEventTable
| where healthEventTime between (queryFrom .. queryTo)
| where NodeId  == queryNodeId
| where ContainerId  == queryContainerId
| where NMAgentHealth != 1
| summarize  arg_max(healthEventTime, NMAgentHealth), HealthReason = tostring(set_difference(array_sort_asc(make_set(split(HealthState, "___"))), pack_array("")))  by StartTimeStamp, EndTimeStamp
| order  by StartTimeStamp asc
| extend StartTime  = StartTimeStamp
| extend Health = case(NMAgentHealth == 1, "Healthy", NMAgentHealth == 0, "Unhealthy", "Degraded") 
| extend Tooltip = strcat("NMAgentHealth: ", NMAgentHealth, ", HealthState: ", tostring(HealthReason))
| extend Content = tostring(Health)
| extend EndTime = EndTimeStamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`

---

### NMAgent Event

_Purpose:_ Network Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp  between(starttime .. endtime)
| where NodeId == nodeid
| where ProviderName == "NMAgent"
| project PreciseTimeStamp, StartTime = todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| extend Content = Description //, EndTime = datetime_add("minute", 1, StartTime)
| order by StartTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ProviderName == "NMAgent"`

---

### NM Programming

_Purpose:_ Network Health

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Timeline`

```kusto
AggVmHealthFailureVscStateEventTable
| where healthEventTime  between (queryFrom .. queryTo)
| where NodeId  == queryNodeId
| where ContainerId  == queryContainerId
| where PortProgrammingStatus != 1
| summarize healthEventTime = arg_max(healthEventTime, PortProgrammingStatus)  by StartTimeStamp, EndTimeStamp
| extend StartTime  = StartTimeStamp
| extend Health = case( PortProgrammingStatus == 1, "Healthy", PortProgrammingStatus == 0, "Unhealthy", "Degraded")
| extend Content = Health
| extend Tooltip = tostring(PortProgrammingStatus)
| extend EndTime = EndTimeStamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

---

### SoC OS Update

_Purpose:_ Network Health

Cluster: `azurehn.kusto.windows.net` · Database: `Azurehn` · Type: `Timeline`

```kusto
let _ContainerId = '';
let _NodeId = queryNodeId;
let _endTime = queryTo;
let _startTime = queryFrom;
let NodeInformation = () {
    let impactedContainerId = tolower(["_ContainerId"]);
    let impactStartTime =["_startTime"];
    let impactEndTime = ["_endTime"];
    let output = materialize(cluster("azurehn.kusto.windows.net").database("Azurehn").fn_GetNodeInfo_v2(impactStartTime, impactEndTime,["_NodeId"], impactedContainerId));
    output
};
let impactedContainerId = tolower(["_ContainerId"]);
let impactStartTime =["_startTime"];
let impactEndTime = ["_endTime"];
let impactedNodeId = toscalar(NodeInformation | project NodeId);
let socID = toscalar(NodeInformation | project SocId);
let query=strcat(```cluster("```, toscalar(NodeInformation | project AzCoreCluster),```").database('OvlProd').LinuxOverlakeSystemd()
| where NodeId =~ impactedNodeId or NodeId =~ socID
| where PreciseTimeStamp between (impactStartTime .. impactEndTime)
| where _SYSTEMD_UNIT startswith "SocOsUpdate"
| project PreciseTimeStamp, Severity=case(PRIORITY == 2, "Crit", PRIORITY == 3, "Error", PRIORITY == 4, "Warn", PRIORITY == 5, "Notice", PRIORITY == 6, "Info", PRIORITY == 7, "Debug", "Undef"),
          MESSAGE, _PID, _SYSTEMD_UNIT```);
evaluate execute_query(".", query)
| where MESSAGE startswith "SocOsUpdate: SoC-OS version"
| extend StartTime = PreciseTimeStamp
| summarize arg_max(MESSAGE,StartTime) 
| project StartTime,Content = MESSAGE
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `_SYSTEMD_UNIT startswith "SocOsUpdate"` · `MESSAGE startswith "SocOsUpdate: SoC-OS version"`

---

### SoC Pilot Fish State

_Purpose:_ Network Health

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(queryFrom .. queryTo)
// | where ResourceId == queryNodeId
| where PairId == queryNodeId
| order by PreciseTimeStamp asc
| extend flag = case (prev(PfState) <> PfState, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp), queryTo)
| extend Content = strcat (PfState, " ", PfRepairState)
| extend Health = case (PfState == "H", "Healthy", 
    PfState in ("D", "C", "F"), "Unhealthy",
    "Degraded")
| project StartTime, EndTime, Tenant, ResourceId, PairId, LifecycleState, PfState, PfRepairState, HealthSummary, FaultCode, FaultDescription, IPAddress, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### SoC PF Update

_Purpose:_ Network Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').OverlakeServiceManagerStatus
| where  PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h))
| where NodeId =~ querySocNodeId 
| where EventType == "versionswitch"
| order by PreciseTimeStamp desc
| extend detailsParsed = parse_json(detail)
| extend CurrentVersion=tostring(detailsParsed.Version)
| extend NewVersion=tostring(detailsParsed.NewVersion)
| project PreciseTimeStamp, ServiceName, CurrentVersion, NewVersion, NodeId, MachineName, Cluster
| extend StartTime = PreciseTimeStamp
| extend Content = strcat(ServiceName, ": ", NewVersion)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySocNodeId}`

**Signal filters seen in KQL:** `EventType == "versionswitch"`

---

### SoC Signal Event

_Purpose:_ Network Health

Cluster: `overlakedata.southcentralus.kusto.windows.net` · Database: `overlake-syslog` · Type: `Timeline`

```kusto
let socHostName = toscalar(cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMap_Latest
| where NodeId == queryNodeId
| project hostMachineName
| take 1);
cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeSoCProcessedSignals
| where IngestionTime between (queryFrom..queryTo)
| where isnotempty(socHostName) and MESSAGEList contains strcat (socHostName, "SOC")
| where Scenario <> "SELinuxViolations"
| where Scenario in ("KernelDumps", "WatchDogReset", "KexecRepeatedBoots", "RebootTypes")
| extend Content = Scenario
| extend Health = "Unhealthy"
| project StartTime = StartTimeStamp, EndTime = EndTimeStamp, IngestionTime, Cluster, SoCNameList, Scenario, Component, MESSAGEList, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Scenario <> "SELinuxViolations"`

---

### SoC Azure Watson

_Purpose:_ Network Health

Cluster: `azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `Timeline`

```kusto
let azurewatsonlink = strcat("https://azurewatson.microsoft.com/?NodeId=", querySocNodeId);
cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. queryTo)
// | where nodeIdentity == queryNodeId
| where nodeIdentity == querySocNodeId
| where isnotempty(nodeIdentity) 
| project PreciseTimeStamp, EventMessage, platform, crashMode, process, environment, dumpUid
| join kind= leftouter (
    cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
    | where PreciseTimeStamp between (queryFrom..queryTo)
    | project AnalyzedTime=PreciseTimeStamp, DumpAnalalysisMessage=EventMessage, faultingModule, faultingProcess, bucketString, crashTime, dumpType, bugId, bugLink, dumpUid
) on $left.dumpUid == $right.dumpUid
| extend AzureWatsonLink=azurewatsonlink
| where crashTime <> ""
| project StartTime = todatetime(crashTime), AnalyzedTime, dumpType, crashMode, platform, DumpAnalalysisMessage, faultingModule, faultingProcess, bugId, bugLink, AzureWatsonLink
| extend Content = strcat(crashMode, " ", faultingProcess,"!",faultingModule)
| extend Health = case (crashMode == "um", "Degraded", "Unhealthy")
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySocNodeId}`

---

### SoC - Anvil Event

_Purpose:_ Network Health

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `aplat` · Type: `Timeline`

```kusto
cluster("aplat.westcentralus.kusto.windows.net").database("aplat").AnvilRepairServiceRequestSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ResourceId == querySocNodeId
| where SubStatus == "Received"
| extend Request = parse_json(Request)
| extend FaultCodeString = Request.RepairContext.FaultCodeString
| extend FaultReason = Request.RepairContext.FaultReason
| extend FaultTime = Request.RepairContext.Time
| project PreciseTimeStamp, RequestIdentifier, RequestAuthor, FaultCodeString, FaultReason, FaultTime, Request, Status, SubStatus, CorrelationIdentifier
| extend Content = tostring(FaultCodeString)
| extend StartTime = PreciseTimeStamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySocNodeId}`

**Signal filters seen in KQL:** `SubStatus == "Received"`

---

### SoC VNetAgent Event

_Purpose:_ Network Health

Cluster: `azcore.centralus` · Database: `OvlProd` · Type: `Timeline`

```kusto
let portIDs = materialize(cluster('aznwsdn').database('aznwmds').ContainerInformationEvent
| where ContainerId =~ queryContainerId
| where PreciseTimeStamp >= queryFrom - 96h and queryTo <= queryTo + 24h
| distinct PortId);
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').LinuxOverlakeSystemd
| where NodeId =~ queryNodeId or NodeId =~ querySocNodeId
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where PRIORITY in ("3", "4") // Error,  Warn
| where MESSAGE has_any (portIDs)
| where SYSLOG_IDENTIFIER == "vnetagent"
| extend MESSAGE1 = extract("VnetAgent::\\[.*\\](.*)", 1, MESSAGE)
| order by PreciseTimeStamp asc
| summarize PRIORITY = min(PRIORITY), message = make_set(MESSAGE1) by bin(PreciseTimeStamp, 1m)
| extend Health  = iif(PRIORITY == "3", "Error", "Degraded")
| project StartTime = PreciseTimeStamp, Content = iif(PRIORITY == "3", "Error", "Warning"), Message = tostring(message), Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`, `{querySocNodeId}`

**Signal filters seen in KQL:** `SYSLOG_IDENTIFIER == "vnetagent"`

---

### SoC Systemd Event

_Purpose:_ Network Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').LinuxOverlakeSystemd
| where PreciseTimeStamp between( queryFrom .. queryTo ) 
| where NodeId == querySocNodeId // SocNodeId
// need to add more filters once we get more known issues on SoC...
| where MESSAGE has "Too many open files" 
| project StartTime = PreciseTimeStamp, Cluster, MachineName, SocNodeId = NodeId, _TRANSPORT, _COMM, _SYSTEMD_UNIT, MESSAGE
| extend Content = 'TooManyOpenFiles', Health = 'Unhealthy'
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{querySocNodeId}`

**Signal filters seen in KQL:** `MESSAGE has "Too many open files"`

---
