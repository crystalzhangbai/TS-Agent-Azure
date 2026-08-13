# (top-level)

> Source: **NodeService - NodeService_NodeView** dashboard, chapter **(top-level)** (33 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "NodeService_NodeView"

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `ResourceGet` · Widget: `Container`

```kusto
MycroftNodeSnapshot
| where NodeId == local_NodeId
| where PreciseTimeStamp > ago(10h)
| take 1
| project Cluster=ClusterName, NodeId, Region, PreciseTimeStamp, AzSMCluster=Cluster, HostName, OSBaseImageName = parse_json(HostingEnvironment).OSBaseImageName
```

**Params:** `{local_NodeId}`

---

### Networking dashboard query

Cluster: `?` · Database: `?` · Type: `Single` · Widget: `Card`

```kusto
console.log(data.queryTime);

function addHours(date, hours) {
  let dateObj = new Date(date);
  dateObj.setHours(dateObj.getHours() + hours);
  return dateObj.toISOString();
}

let response = [
    {
        "Networking DRI dashboard": ("https://dataexplorer.azure.com/dashboards/bea4ccac-baf1-45f3-b160-533232cbfdaa?p-_startTime=" +
                    addHours(data.queryTime, -1) + "&p-_endTime=" + addHours(data.queryTime, 1) +
                    "&p-_NodeId=v-" + data.queryNode + "&p-_ContainerId=all&p-_ICMId=all")
    }
];
callback(false, response);
```

**Params:** `{queryNode}`, `{queryTime}`

---

### NodeServiceVersion

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Card`

```kusto
NodeServiceOperationEtwTable
| where PreciseTimeStamp between ((faultTime-1h)..(faultTime+1h))
| where NodeId == nodeId
| project ServiceVersion
```

**Params:** `{nodeId}`, `{faultTime}`

---

### SDP Phase

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Single` · Widget: `Card`

```kusto
MycroftClusterSnapshot
| where ClusterName == cluster
| where PreciseTimeStamp between ((faultTime-1h)..(faultTime+1h))
| take 1
| project SDPPhase=VirtualEnvironment
```

**Params:** `{faultTime}`, `{cluster}`

---

### SocId

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Single` · Widget: `Card`

```kusto
LogNodeSnapshot
| where nodeId == _nodeId
| distinct socId;
```

**Params:** `{_nodeId}`

---

### ApSvcMgr State

_Widget purpose:_ NodeState

Cluster: `https://hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureDCMdb` · Type: `Timeline`

```kusto
PFClientBootstrapAvailability
| where PreciseTimeStamp between ((faultTime - 3h)..4h)
| where Id == queryNode
| project StartTime = PreciseTimeStamp, Content = iff(ApSvcMgrUp == 1, "ApSvcMgr - Up", "ApSvcMgr - Down"),
          Health = iff(ApSvcMgrUp == 1, "Healthy", "Unhealthy"),
          Tooltip = strcat("DcmState:", DcmState,
                           " DmState:", DmState,
                           " TmState:", TmState,
                           " PfAgentUp:", PfAgentUp,
                           " ApLauncherUp", ApLauncherUp)
| sort by StartTime asc
| serialize 
| extend FilterOut = Content == prev(Content) and isnotempty(next(StartTime))
| where FilterOut != 1
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), now())
| where EndTime != now()
| sort by StartTime asc
```

**Params:** `{queryNode}`, `{faultTime}`

---

### LogNodeSnapshot - NodeState

_Widget purpose:_ NodeState

Cluster: `https://hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Timeline`

```kusto
let raw = LogNodeSnapshot
| where PreciseTimeStamp between ((faultTime-5h)..6h)
| where nodeId == queryNode 
| project PreciseTimeStamp, nodeState, faultInfo, nsProgressHealthStatus, cmNodeWasChannelHealthStatus, cmNodeWillBeChannelHealthStatus, nodeServiceMadariAggregatedHealth, nodeServiceMadariPublisherHealth, nodeServiceMadariSubscriberHealth, tipNodeSessionId, diskConfiguration, currentBareMetalState;
let nodeState = raw
| project StartTime=PreciseTimeStamp, Content=nodeState, Health = iff(nodeState == "Ready", "Healthy",
                                                                     iff (nodeState in ("Unhealthy", "HumanInvestigate", "Dead", "OutForRepair"), "Unhealthy",
                                                                     "Neutral")),
          Tooltip = faultInfo, GroupBy = "NodeState";
let progressHealth = raw | project StartTime=PreciseTimeStamp, Content=nsProgressHealthStatus, Health = iff(nsProgressHealthStatus == "Healthy", "Healthy", "Unhealthy"), GroupBy = "NSProgressHealth",Tooltip = nsProgressHealthStatus;
let wasHealth = raw | project StartTime=PreciseTimeStamp, Content=cmNodeWasChannelHealthStatus, Health = iff(cmNodeWasChannelHealthStatus == "Healthy", "Healthy", "Unhealthy"), GroupBy = "CMNSWasHealth",Tooltip = cmNodeWasChannelHealthStatus;
let willBeHealth = raw | project StartTime=PreciseTimeStamp, Content=cmNodeWillBeChannelHealthStatus, Health = iff(cmNodeWillBeChannelHealthStatus == "Healthy", "Healthy", "Unhealthy"), GroupBy = "CMNSWillBeHealth",Tooltip = cmNodeWillBeChannelHealthStatus;
let madariAggrHealth = raw | project StartTime=PreciseTimeStamp, Content=nodeServiceMadariAggregatedHealth, Health = iff(nodeServiceMadariAggregatedHealth == "Healthy", "Healthy", "Unhealthy"), GroupBy = "MadariAggrHealth",Tooltip = nodeServiceMadariAggregatedHealth;
let nodeServiceMadariPublisherHealth = raw | project StartTime=PreciseTimeStamp, Content=nodeServiceMadariPublisherHealth, Health = iff(nodeServiceMadariPublisherHealth == "Healthy", "Healthy", "Unhealthy"), GroupBy = "MadariPublisherHealth",Tooltip = nodeServiceMadariPublisherHealth;
let nodeServiceMadariSubscriberHealth = raw | project StartTime=PreciseTimeStamp, Content=nodeServiceMadariSubscriberHealth, Health = iff(nodeServiceMadariSubscriberHealth == "Healthy", "Healthy", "Unhealthy"), GroupBy = "MadariSubscriberHealth",Tooltip = nodeServiceMadariSubscriberHealth;
let isTip = raw | project StartTime=PreciseTimeStamp, Content=iff(tipNodeSessionId=="00000000-0000-0000-0000-000000000000","ProdNode", "TipNode"), Health = iff(tipNodeSessionId=="00000000-0000-0000-0000-000000000000", "Healthy", "Degraded"), GroupBy = "IsTip",Tooltip = tipNodeSessionId;
let diskConfiguration = raw | project StartTime=PreciseTimeStamp, Content=diskConfiguration, GroupBy="DiskConfiguration", Tooltip = diskConfiguration;
let baremetalState = raw | project StartTime=PreciseTimeStamp, Content=currentBareMetalState, GroupBy="CurrentBareMetalState", Tooltip = currentBareMetalState;
nodeState
| union progressHealth
| union wasHealth
| union willBeHealth
| union madariAggrHealth
| union nodeServiceMadariPublisherHealth
| union nodeServiceMadariSubscriberHealth
| union isTip
| union diskConfiguration
| union baremetalState
| order by GroupBy asc, StartTime asc
| serialize 
| extend FilterOut = (GroupBy == prev(GroupBy) and Content == prev(Content) and isnotempty(next(StartTime)) and GroupBy == next(GroupBy))
| where FilterOut != 1
| extend EndTime = case(isnotempty(next(StartTime)) and GroupBy == next(GroupBy), next(StartTime), now()), Tooltip = iff(isempty(Tooltip), next(Tooltip), Tooltip)
| where EndTime != now()
| extend Tooltip = strcat(tostring(StartTime), ": ", Tooltip)
| sort by GroupBy asc, StartTime asc
```

**Params:** `{queryNode}`, `{faultTime}`

---

### Madari errors

_Widget purpose:_ NodeState

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
NodeServiceMadariEventsEtwTable
| where NodeId == queryNode
| where Message endswith_cs "CreateSocketHandlerAndConnect, error connecting socket."
| parse Message with * "(HR = " error ")" *
| where PreciseTimeStamp between ((faultTime - 3h)..4h)
| project StartTime=PreciseTimeStamp, Content=error, Health="Unhealthy"
```

**Params:** `{queryNode}`, `{faultTime}`

---

### Anvil Repair Diagnostics

_Widget purpose:_ NodeState

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Timeline`

```kusto
AnvilRepairServiceForgeEvents
| where ResourceId == queryNode
| where PreciseTimeStamp > faultTime - 1h and PreciseTimeStamp < faultTime + 1h
| where (
    (MessageTrigger == "OnExecuteAction" and TreeActionName == "PingRdAgentAction") or 
    (MessageTrigger == "OnExecuteAction" and TreeActionName == "AnvilNodeSacDiagnosticsCollectionAction" and (
        Message contains "NodeService.exe" or Message contains "apsvcmgr.exe" or Message contains "rdagent.exe"
    ))
)
| project bin(PreciseTimeStamp, 2s), TreeActionName, Message
| summarize make_list(Message) by TreeActionName, PreciseTimeStamp
| extend Message = strcat_array(list_Message, "")
| project-away list_Message
| extend RdAgentRunning=Message contains " rdagent.exe"
| extend PfNodeServiceRunning=Message contains " PfNodeService.exe"
| extend NodeServiceRunning=Message contains " NodeService.exe"
| extend ApSvcMgrRunning=Message contains " apsvcmgr.exe"
| project StartTime=PreciseTimeStamp, Content=case(
    Message contains "RDAgent is pinged", "AnvilSuccessfullyPingedRdAgent",
    Message contains "Not able to ping RDAgent", "AnvilFailedToPingRdAgent",
    TreeActionName == "AnvilNodeSacDiagnosticsCollectionAction", strcat(
        "NodeServiceRunning: ", NodeServiceRunning, ", ",
        "PfNodeServiceRunning: ", PfNodeServiceRunning, ", ",
        "RdAgentRunning: ", RdAgentRunning, ", ",
        "ApSvcMgrRunning: ", ApSvcMgrRunning, "\n"
    ),
    "Unexpected!"
), Message, GroupBy=TreeActionName
```

**Params:** `{queryNode}`, `{faultTime}`

---

### NodeService Exits

_Widget purpose:_ NodeState

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
let entries = materialize(NodeServiceExitEtwTable
| where NodeId == nodeId
| where PreciseTimeStamp between ((faultTime-45m)..faultTime)
| project StartTime=PreciseTimeStamp, Content=tostring(ExitCode), NodeId);
let entryCount = entries
| summarize count(), arg_max(StartTime, ExitCode=Content) by NodeId
| extend MoreThan50 = case(count_ > 50, "True", "False");
let tooManyEntriesRaw = materialize(datatable(Test:string) [""]
| extend StartTime=(faultTime-45m), EndTime=faultTime, Message="More than 50 entries, please query NodeServiceExitEtwTable directly. Last ExitCode=", MoreThan50="True");
let tooManyEntries = tooManyEntriesRaw
| join kind=inner entryCount on MoreThan50
| project StartTime, EndTime, Content=strcat(Message, ExitCode);
union
tooManyEntries,
(entries
| join kind=inner entryCount on NodeId
| where count_ < 50)
| project StartTime, EndTime, Content
```

**Params:** `{faultTime}`, `{nodeId}`

---

### Fabric incarnations

_Widget purpose:_ NodeState

Cluster: `mycroft.westcentralus.kusto.windows.net` · Database: `Mycroft` · Type: `Timeline`

```kusto
MycroftClusterSnapshot
| where ClusterName == fabricCluster
| where PreciseTimeStamp > faultTime - 5h and PreciseTimeStamp < faultTime + 1h
| project StartTime = PreciseTimeStamp, Content=IncarnationId
| sort by StartTime asc
| serialize 
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), now())
| where EndTime != now()
| sort by StartTime asc
```

**Params:** `{faultTime}`, `{fabricCluster}`

---

### SEL Events

_Widget purpose:_ NodeState

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `Timeline`

```kusto
cluster("sparkle.eastus").database("defaultdb").SparkleSELByNodeId(_nodeId, _faultTime - 2h, _faultTime + 2h)
| where BMCSelTimestamp > _faultTime - 2h and BMCSelTimestamp < _faultTime + 2h
| where SensorType == "Power Unit" or SensorType == "Memory" or SensorType == "Processor"
| project BMCSelTimestamp, EventDataDetails1, EventDataDetails2, EventDataDetails3, SensorType, EventDetail, NodeId
| extend Content=case(
    EventDataDetails1 contains "Power Off", "Power Off",
    EventDataDetails1 contains "Processor Automatically Throttled", EventDataDetails1,
    EventDataDetails1 contains "Correctable ECC", EventDataDetails2,
    ""
)
| where Content != ""
| project StartTime=BMCSelTimestamp, Content, Tooltip=Content, GroupBy="Realtime SEL Logs"
| union (
cluster("sparkle.eastus").database("defaultdb").SparkleOFRSelByNodeId(_nodeId, _faultTime, _faultTime + 1d)
| project BMCSelTimestamp, EventDataDetails1
| where EventDataDetails1 contains "Bus Correctable Error"
| summarize count(), arg_max(BMCSelTimestamp, EventDataDetails1) by EventDataDetails1
| project StartTime=_faultTime,
          Content="Correctable Memory errors found during OFR diagnostics when node enters OFR",
          GroupBy="OFR Sel Logs"
)
```

**Params:** `{_faultTime}`, `{_nodeId}`

**Signal filters seen in KQL:** `SensorType == "Power Unit"` · `EventDataDetails1 contains "Bus Correctable Error"`

---

### TOR Send Packet Health

_Widget purpose:_ NodeState

Cluster: `aznwsdn.kusto.windows.net` · Database: `aznwmds` · Type: `Timeline`

```kusto
cluster('aznwsdn').database('aznwmds').TorPingSendAggreEvent
| where TIMESTAMP between ((bin(_faultTime, 5m) - 1h) .. bin(_faultTime, 5m) + 1h)
| where NodeId =~ _nodeId
| make-series PacketsSent = max(SendCount) default=0 on TIMESTAMP in range ((_faultTime - 1h), (_faultTime + 1h), 5m)
| mv-expand PacketsSent, TIMESTAMP
| extend max_TIMESTAMP=todatetime(TIMESTAMP)+5m
| project StartTime=todatetime(TIMESTAMP), EndTime=max_TIMESTAMP, Health=case(PacketsSent > 0, "Healthy", PacketsSent == 0, "Unhealthy", "Unknown")
| extend Content=Health
```

**Params:** `{_nodeId}`, `{_faultTime}`

---

### TOR Recv Packet Health

_Widget purpose:_ NodeState

Cluster: `aznwsdn.kusto.windows.net` · Database: `aznwmds` · Type: `Timeline`

```kusto
cluster('aznwsdn').database('aznwmds').TorPingRecvAggreEvent
| where TIMESTAMP between ((bin(_faultTime, 5m) - 1h) .. bin(_faultTime, 5m) + 1h)
| where NodeId =~ _nodeId
| make-series PacketsSent = max(RecvCount) default=0 on TIMESTAMP in range ((_faultTime - 1h), (_faultTime + 1h), 5m)
| mv-expand PacketsSent, TIMESTAMP
| extend max_TIMESTAMP=todatetime(TIMESTAMP)+5m
| project StartTime=todatetime(TIMESTAMP), EndTime=max_TIMESTAMP, Health=case(PacketsSent > 0, "Healthy", PacketsSent == 0, "Unhealthy", "Unknown")
| extend Content=Health
```

**Params:** `{_nodeId}`, `{_faultTime}`

---

### TOR InMaintenance

_Widget purpose:_ NodeState

Cluster: `aznwsdn.kusto.windows.net` · Database: `aznwmds` · Type: `Timeline`

```kusto
let tor = database('aznwmds').TorPingSendAggreEvent
| where NodeId =~ _nodeId
| take 1 // Assumption that the tor doesn't change throughout lifetime of the node
| project TorName;
cluster('azphynet.kusto.windows.net').database('azdhmds').f_DeviceHealthLookupMultiSearch(_faultTime - 30m, _faultTime + 30m, todynamic(toscalar(tor)))
| where Status contains "InMaintenance"
| project StartTime=TIMESTAMP,
          EndTime=TIMESTAMP + 5m,
          Content="ToRInMaintenance",
          Health="Unhealthy"
```

**Params:** `{_nodeId}`, `{_faultTime}`

**Signal filters seen in KQL:** `Status contains "InMaintenance"`

---

### CM WillBe Generation

_Widget purpose:_ NodeState

Cluster: `hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Timeline`

```kusto
CMClientCriticalEventEtwTable
| where NodeId == _nodeId
| where PreciseTimeStamp between ((_faultTime - 2h)..(_faultTime+2h))
| project PreciseTimeStamp, ErrorMessage
| summarize StartTime=min(PreciseTimeStamp), EndTime=max(PreciseTimeStamp) by Content=ErrorMessage
| extend Health="Unhealthy"
```

**Params:** `{_nodeId}`, `{_faultTime}`

---

### TOR in Quarantine Network

_Widget purpose:_ NodeState

Cluster: `azphynet.kusto.windows.net` · Database: `azdhmds` · Type: `Timeline`

```kusto
let startTime = faultTime - 5h;
let endTime = faultTime + 1h;
cluster('azphynet.kusto.windows.net').database('azdhmds').LinkLifecycleState
| where StartDevice == toupper(hostName)
| project StartTime=TIMESTAMP, EndDevice, OriginalState, State
| sort by EndDevice, StartTime asc
| serialize
| extend EndTime = case(EndDevice == next(EndDevice), next(StartTime), max_of(endTime, StartTime))
| where EndTime > startTime and StartTime < endTime
| where State != "InProduction"
| project StartTime=max_of(StartTime, startTime),
          EndTime=min_of(EndTime, endTime),
          Content=State,
          GroupBy=strcat("TorDeviceInQuarantineNetwork: ", EndDevice),
          Health=iff(State == "InProduction", "Healthy", "Unhealthy")
```

**Params:** `{hostName}`, `{faultTime}`

**Signal filters seen in KQL:** `State != "InProduction"`

---

### Soc Health

_Widget purpose:_ NodeState

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Timeline`

```kusto
KyberNodeAggregatedHealthSnapshot
 | where PreciseTimeStamp between ((faultTime-5h)..6h)
 | where NodeId == queryNode
 | extend SocHwMonHB=tostring(parse_json(SocHealthSignals).SocHwMonHB.Status)
 | project StartTime=PreciseTimeStamp, Content=SocHwMonHB,
           Health = case(SocHwMonHB == "Healthy", "Healthy", SocHwMonHB == "", "Unknown", "Unhealthy"),
           GroupBy = "SocHealthSignals",
           Tooltip = SocHealthSignals
 | order by GroupBy asc, StartTime asc
 | serialize 
 | extend FilterOut = (GroupBy == prev(GroupBy) and Content == prev(Content) and isnotempty(next(StartTime)) and GroupBy == next(GroupBy))
 | where FilterOut != 1
 | extend EndTime = case(isnotempty(next(StartTime)) and GroupBy == next(GroupBy), next(StartTime), now()), Tooltip = iff(isempty(Tooltip), next(Tooltip), Tooltip)
 | where EndTime != now()
 | extend Tooltip = strcat(tostring(StartTime), ": ", Tooltip)
 | sort by GroupBy asc, StartTime asc
```

**Params:** `{faultTime}`, `{queryNode}`

---

### SeedIncarnation query

_Widget purpose:_ NodeState

Cluster: `aznwsdn.kusto.windows.net` · Database: `sdnpubsub` · Type: `Timeline`

```kusto
cluster('aznwsdn.kusto.windows.net').database('sdnpubsub').PubSubAPICall
| parse additional with * "pk: " contextSelector ", rp: " relativePath "," *
| where contextSelector endswith nodeId
| where action == "UpdateNode"
| where PreciseTimeStamp > faultTime - 1h and PreciseTimeStamp < faultTime + 1h
| project PreciseTimeStamp, userIdentity, contextSelector, relativePath, action, dataSize
| project StartTime=PreciseTimeStamp,
          Tooltip="First launch after Boot",
          Content="First time NodeService writes to seedincarnation after boot",
          GroupBy="SeedIncarnation"
```

**Params:** `{nodeId}`, `{faultTime}`

**Signal filters seen in KQL:** `action == "UpdateNode"`

---

### SocHB

_Widget purpose:_ NodeState

Cluster: `azdeployer.kusto.windows.net` · Database: `AzDeployerKusto` · Type: `Timeline`

```kusto
let data = cluster('wdgeventstore').database('hostosdeploy').nodes
| where nodeId == _nodeId
| project nodeId, machineName, tenant;
let gapThreshold = 5m;   // any delta larger than this between samples = gap
let socMachineName = data | project strcat(machineName, "SOC");
let segments =
    cluster('azdeployer.kusto.windows.net').database('AzDeployerKusto').OMWorkerRepairGenerator
    | where PreciseTimeStamp > _faultTime - 4h and PreciseTimeStamp < _faultTime + 1h
    | where machineName in (socMachineName)
    | project PreciseTimeStamp, machineName, nodeHealth=toint(nodeHealth)
    | extend Health = iff(nodeHealth == 6, "Healthy", "Unhealthy")
    | order by machineName asc, PreciseTimeStamp asc
    | extend prevHealth = prev(Health), prevMachine = prev(machineName)
    | extend isNewSegment = (Health != prevHealth) or (machineName != prevMachine)
    | extend segmentId = row_cumsum(toint(isNewSegment))
    | summarize StartTime = min(PreciseTimeStamp),
                EndTime  = max(PreciseTimeStamp),
                UnhealthyMinutes = max(60 - nodeHealth * 10)
            by segmentId, machineName, Health;
let gaps =
    segments
    | order by machineName asc, StartTime asc
    | extend nextStart = next(StartTime), nextMachine = next(machineName)
    | where machineName == nextMachine and (nextStart - EndTime) > gapThreshold
    | project StartTime = EndTime, EndTime = nextStart, machineName,
              Health = "Gap", UnhealthyMinutes = long(null);
segments
| union gaps
| extend Content = strcat(machineName, " ", Health,
            iff(Health == "Unhealthy", strcat(" (~", UnhealthyMinutes, " min)"), ""))
| project StartTime, EndTime, Content, Health
| order by StartTime asc
```

**Params:** `{_nodeId}`, `{_faultTime}`

---

### WindowsEvents

_Widget purpose:_ NodeState

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
WindowsEventTable
| where PreciseTimeStamp between ((faultTime - 2h)..2h)
| where NodeId == queryNode
| where toint(EventId) == 147
| project StartTime=PreciseTimeStamp, Content="Event 147", Explanation=Description, AdditionalHelp="This usually means there is something wrong with the OS/firmware. Please work with Host OS teams"
```

**Params:** `{queryNode}`, `{faultTime}`

---

### ContainerState and ASILink

_Widget purpose:_ Containers

Cluster: `https://mycroft.westcentralus.kusto.windows.net` · Database: `Mycroft` · Type: `Timeline`

```kusto
let bmcMycroft = MycroftContainerHealthSnapshot
| where NodeId == queryNode
| where PreciseTimeStamp between ((faultTime - 3h)..4h);
let azcoreMycroft = cluster('azcore.centralus.kusto.windows.net').database('AzureCP').MycroftContainerHealthSnapshot
| where NodeId == queryNode
| where PreciseTimeStamp between ((faultTime - 3h)..4h);
let JoinedTable = materialize(bmcMycroft
| union azcoreMycroft
| sort by ContainerId, PreciseTimeStamp asc);
let GlobalMinMaxTimeStamps = JoinedTable
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp) by ContainerId
| project ContainerId, MinTime = min_PreciseTimeStamp - 5m, MaxTime=case(min_PreciseTimeStamp != max_PreciseTimeStamp, max_PreciseTimeStamp, now()) + 5m;
JoinedTable
| serialize 
| extend FilterOut = ContainerState == prev(ContainerState) and ContainerId == prev(ContainerId)
| where FilterOut != 1
| extend EndTime = case(isnotempty(next(PreciseTimeStamp)) and ContainerId == next(ContainerId), next(PreciseTimeStamp), now())
| join kind=inner GlobalMinMaxTimeStamps on ContainerId
| project StartTime=PreciseTimeStamp,
          EndTime=EndTime,
          Content=ContainerState,
          Tooltip=strcat(ContainerState, " Click for Container ASI Link"),
          GroupBy=ContainerId,
          ContainerState,
          OsState,
          ASILink=strcat("https://asi.azure.ms/view/services/NodeService/pages/Peregrine_ContainerEvents?containerId=", ContainerId, "&globalFrom=", MinTime, "&globalTo=", MaxTime)
```

**Params:** `{faultTime}`, `{queryNode}`

---

### Events Count

_Widget purpose:_ Node-level events count

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`

```kusto
let operation_count = NodeServiceOperationEtwTable
| where NodeId == queryNode
| make-series count() default=0 on PreciseTimeStamp from faultTime - 3h to faultTime + 1h step 5m
| mvexpand count_, PreciseTimeStamp to typeof(datetime);
let event_count = NodeServiceEventEtwTable
| where NodeId == queryNode
| make-series count() default=0 on PreciseTimeStamp from faultTime - 3h to faultTime + 1h step 5m
| mvexpand count_, PreciseTimeStamp to typeof(datetime);
let winevent_count = WindowsEventTable
| where NodeId == queryNode
| make-series count() default=0 on PreciseTimeStamp from faultTime - 3h to faultTime + 1h step 5m
| mvexpand count_, PreciseTimeStamp to typeof(datetime);
let rdagentupdater_count = RdAgentUpdaterEventTable
| where NodeId == queryNode
| make-series count() default=0 on PreciseTimeStamp from faultTime - 3h to faultTime + 1h step 5m
| mvexpand count_, PreciseTimeStamp to typeof(datetime);
operation_count
| join kind=fullouter  event_count on PreciseTimeStamp
| join kind=fullouter winevent_count on PreciseTimeStamp
| join kind=fullouter rdagentupdater_count on PreciseTimeStamp
| project PreciseTimeStamp, NSOperationsCount = toint(count_), NSEventsCount = toint(count_1), WindowsEventsCount = toint(count_2), RdAgentUpdaterEventsCount = toint(count_3)
```

**Params:** `{queryNode}`, `{faultTime}`

---

### Overlake Healthstore Data

_Widget purpose:_ Node-level events count

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `TimeSeries`

```kusto
OverlakeHsDataUploader
| where NodeId == nodeId
| where detail startswith '{"HS data'
| make-series sum(dataUploadSuccessCount) default=0 on PreciseTimeStamp from faultTime - 3h to faultTime + 1h step 10m
| mvexpand sum_dataUploadSuccessCount, PreciseTimeStamp to typeof(datetime)
| project PreciseTimeStamp, SoCEventsCount = toint(sum_dataUploadSuccessCount)
```

**Params:** `{faultTime}`, `{nodeId}`

**Signal filters seen in KQL:** `detail startswith "{"HS data"`

---

### Cluster level node unhealthy metrics

_Widget purpose:_ Cluster-level Unhealthy Node Count

Cluster: `hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `TimeSeries`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between ((faultTime-2h)..4h) and Tenant == cluster
| where nodeState == "Unhealthy"
| make-series nodeCount = dcount(nodeId) default=0 on PreciseTimeStamp from (faultTime-2h) to (faultTime+2h) step 30m
| mv-expand PreciseTimeStamp to typeof(datetime), nodeCount to typeof(long)
| project PreciseTimeStamp, nodeCount
```

**Params:** `{faultTime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "Unhealthy"`

---

### Node Snapshot

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`

```kusto
MycroftNodeHealthSnapshot
| where NodeId == nodeId
| where PreciseTimeStamp between ((faultTime-1h)..(faultTime+1h))
| extend ExtendedDetails=case(parse_json(FaultInfo).ExtendedDetails != "", parse_json(FaultInfo).ExtendedDetails, dynamic([{"Name":"EscalateTo","Value":"No Fault"}]))
| mv-expand ExtendedDetails
| where parse_json(ExtendedDetails).Name == "EscalateTo"
| project PreciseTimeStamp, NsdState, NodeServiceAggregatedHealthStatus, AvailabilityState, EscalateTo=parse_json(ExtendedDetails).Value, Reason=parse_json(FaultInfo).Reason, FaultTime=parse_json(FaultInfo).Time
| sort by PreciseTimeStamp asc
```

**Params:** `{nodeId}`, `{faultTime}`

---

### CMWorkerNodeServiceWas

Cluster: `https://hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
CMWorkerNodeServiceWasReceivedByChannel
| where PreciseTimeStamp between ((faultTime-2h)..3h)
| where NodeId == queryNode
| project PreciseTimeStamp, Revision, NodeServiceIncarnation
| top 500 by PreciseTimeStamp desc
| order by PreciseTimeStamp asc
```

**Params:** `{queryNode}`, `{faultTime}`

---

### CMWorkerNodeServiceWillBe

Cluster: `https://hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
CMWorkerNodeServiceWillBeSentToChannel
| where PreciseTimeStamp between ((faultTime-2h)..3h)
| where NodeId == queryNode
| project PreciseTimeStamp, Revision, NodeServiceIncarnation
| top 500 by PreciseTimeStamp desc
| order by PreciseTimeStamp asc
```

**Params:** `{queryNode}`, `{faultTime}`

---

### CMWorkerNodeEvents

Cluster: `https://hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
CMWorkerNodeEvents
| where PreciseTimeStamp between ((faultTime-3h)..4h)
| where nodeId == queryNode
| project PreciseTimeStamp, message, RoleInstance
| top 2000 by PreciseTimeStamp desc
| order by PreciseTimeStamp asc
```

**Params:** `{queryNode}`, `{faultTime}`

---

### MemoryReport

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `KernelAgent` · Type: `Table`

```kusto
KernelAgentEvents
| where PreciseTimeStamp between ((faultTime - 45m)..1h)
| where NodeId == queryNode
| where MetricName in ("memory", "report")
| project PreciseTimeStamp, MetricName, KaValueName
| order by PreciseTimeStamp asc
```

**Params:** `{queryNode}`, `{faultTime}`

---

### CPU_Usage

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`

```kusto
HighCpuCounterNodeTable
| where PreciseTimeStamp between ((faultTime - 45m)..1h)
| where NodeId == queryNode
| project PreciseTimeStamp, CounterValue
| order by PreciseTimeStamp asc
```

**Params:** `{queryNode}`, `{faultTime}`

---

### CPU Graph

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`

```kusto
HighCpuCounterNodeTable
| where PreciseTimeStamp between ((faultTime - 8h)..9h)
| where NodeId == queryNode
| summarize AvgCPU=avg(CounterValue) by bin(PreciseTimeStamp, 15m)
```

**Params:** `{queryNode}`, `{faultTime}`

---

### ProcessMemUsage

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `AutopilotDeployment` · Type: `TimeSeries`

```kusto
ProcessesPerfCounter
| where PreciseTimeStamp between ((faultTime - 8h)..9h)
| where NodeId == queryNode
| summarize max(PrivateUsage) by ImageName, bin(PreciseTimeStamp, 15m)
| summarize TotalPrivateUsage=sum(max_PrivateUsage), NSPrivateUsage=sumif(max_PrivateUsage, ImageName =~ "nodeservice.exe") by PreciseTimeStamp
```

**Params:** `{queryNode}`, `{faultTime}`

---
