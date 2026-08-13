# (top-level)

> Source: **NodeService - Peregrine_ContainerEvents** dashboard, chapter **(top-level)** (17 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Peregrine_ContainerEvents"

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `ResourceGet` · Widget: `Container`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
| where ContainerId == local_containerId
| take 1
| project TimeWhenContainerIdIsPresent=PreciseTimeStamp, Region=Tenant, ContainerType, ContainerLifeCycleOwner, Cluster=ClusterName, containerId=ContainerId, ContainerId, NodeId, VirtualMachineUniqueId, TenantName, RoleInstanceName, BillingContext, SubscriptionId, AzLogicalContainerId;
```

**Params:** `{local_containerId}`, `{globalFrom}`, `{globalTo}`

---

### WillBePublishesToMadariFromAzCiM

_Widget purpose:_ Container Information

Cluster: `https://azcim-centralus.centralus.kusto.windows.net` · Database: `AZCIM` · Type: `Timeline`

```kusto
AzCiMContainerWillBe
| where PhysicalContainerId == containerId
| where PreciseTimeStamp > queryFrom and PreciseTimeStamp < queryTo
| sort by PreciseTimeStamp asc
| parse WillBe with '{"revision":' Revision ',' * '"state":"' State '",' *
| project PreciseTimeStamp, Revision, State, WillBe
| serialize 
| where prev(State) != State
| project Table="WillBePublishesToMadari",
          StartTime=PreciseTimeStamp, 
          Content=case(isempty(Revision), "Deleted",
                       State),
          Tooltip=case(isempty(Revision), "Deleted",
                       strcat("Revision=", Revision)),
          WillBe
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

### NS Madari WillBe/Was Interactions

_Widget purpose:_ Container Information

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
NodeServiceMadariEventsEtwTable
| where (
    RelativePath == strcat("/containers/", containerId, "/willbe") and Operation == "MadariNotificationCallback"
    ) or (
    RelativePath == strcat("/containers/", containerId, "/was") and Operation == "MadariPublisherUpdateNodeWithUserMetadata"
    )
| parse Message with * "user metadata:MadariUserMetadata { data_version: " DataVersion "," *
| where PreciseTimeStamp > queryFrom and PreciseTimeStamp < queryTo
| project GroupBy=case(Operation == "MadariNotificationCallback", "WillBeReceiptsFromMadari (NS POV)",
                       Operation == "MadariPublisherUpdateNodeWithUserMetadata", "WasPublishesToMadari (NS POV)", "UnknownInteractions"),
          StartTime=PreciseTimeStamp,
          Content=tostring(DataVersion),
          Tooltip=strcat(Message, " MadariVersion=", MadariVersion)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

### NodeService Completed Operations

_Widget purpose:_ Container Information

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
NodeServiceOperationEtwTable
| where PreciseTimeStamp > queryFrom - 5m and PreciseTimeStamp < queryTo + 5m
//| where Region == region
| where NodeId == nodeId
| where Identifier contains_cs containerId
| where OperationName != "QueryContainer"
| project StartTime=RequestTime,
          EndTime=AcknowledgeTime,
          Content=OperationName,
          Health=case(ResultCode==0, "Healthy", "Unhealthy"),
          ResultCode,
          DetailsJson
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`

**Signal filters seen in KQL:** `OperationName != "QueryContainer"`

---

### NodeService Started Operations

_Widget purpose:_ Container Information

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp > queryFrom - 5m and PreciseTimeStamp < queryTo + 5m
| where NodeId == nodeId
| where ScopeIdentifier == containerId
| where Message has_cs "Begin Operation"
| project PreciseTimeStamp, Message, Pid
| parse Message with * "Begin Operation (WillBeRevision:" WillBeRevision ", WillBeMinorRevision:" WillBeMinorRevision ") [" Operation "]"
| sort by PreciseTimeStamp asc
| project StartTime=PreciseTimeStamp,
          Content=Operation,
          Tooltip=strcat("WillBeRevision:", WillBeRevision, " WillBeMinorRevision:", WillBeMinorRevision, " Pid:", Pid)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### ContainerTimeline

_Widget purpose:_ Container Information

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
let UberEventTable = materialize(macro-expand isfuzzy=true AzCoreKusto as data
(
data.database('Fa').NodeServiceEventEtwTable
| where PreciseTimeStamp > queryFrom - 5m and PreciseTimeStamp < queryTo + 5m
| where NodeId == nodeId
| where ScopeIdentifier == containerId
| where (Message has_cs "Updated Was")
| project PreciseTimeStamp, Message
)
);
// Updated Was records
let WasDocuments = UberEventTable
| where Message has_cs "Updated Was"
| parse Message with * "Updated Was rev:" WasRevision " healthrev:" HealthRevision " updaterev:" UpdateRev " state:" State "(" * ") guestOsState:" GuestOsState "(" * ") provisioningState:" ProvisioningState "(" *
| project PreciseTimeStamp, Message, WasRevision, HealthRevision, UpdateRev, State, GuestOsState, ProvisioningState;
// State
let State = WasDocuments
| project CurrentTime=PreciseTimeStamp,
          Content=State,
          Tooltip=strcat("WillBeRevision:", WasRevision)
| sort by CurrentTime asc;
let StateSerialized = State
| serialize // The purpose of the next few steps is to coaslesce the next few rows together 
| extend prev_Content=prev(Content), next_Content=next(Content)
| where not(prev_Content == Content and Content == next_Content)
| extend prev_time = prev(CurrentTime)
| where prev_time != ""
| project StartTime=prev_time,
          EndTime=CurrentTime,
          Content=Content,
          Tooltip=Tooltip,
          GroupBy="State",
          SortHelper=1;
// Guest OS State
let GuestOsState = WasDocuments
| project CurrentTime=PreciseTimeStamp,
          Content=GuestOsState,
          Tooltip=strcat("WillBeRevision:", WasRevision)
| sort by CurrentTime asc;
let GuestOsStateSerialized = GuestOsState
| serialize // The purpose of the next few steps is to coaslesce the next few rows together 
| extend prev_Content=prev(Content), next_Content=next(Content)
| where not(prev_Content == Content and Content == next_Content)
| extend prev_time = prev(CurrentTime)
| where prev_time != ""
| project StartTime=prev_time,
          EndTime=CurrentTime,
          Content=Content,
          Tooltip=Tooltip,
          GroupBy="GuestOSState",
          SortHelper=2;
// Provisioning State
let ProvisioningState = WasDocuments
| project CurrentTime=PreciseTimeStamp,
          Content=ProvisioningState,
          Tooltip=strcat("WillBeRevision:", WasRevision)
| sort by CurrentTime asc;
let ProvisioningStateSerialized = ProvisioningState
| serialize // The purpose of the next few steps is to coaslesce the next few rows together 
| extend prev_Content=prev(Content), next_Content=next(Content)
| where not(prev_Content == Content and Content == next_Content)
| extend prev_time = prev(CurrentTime)
| where prev_time != ""
| project StartTime=prev_time,
          EndTime=CurrentTime,
          Content=Content,
          Tooltip=Tooltip,
          GroupBy="ProvisioningState",
          SortHelper=3;
// Union of above tables
StateSerialized | union GuestOsStateSerialized | union ProvisioningStateSerialized
| sort by SortHelper asc, StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### Fault Events

_Widget purpose:_ Container Information

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Timeline`

```kusto
MycroftContainerHealthSnapshot
| where ContainerId == containerId
| where PreciseTimeStamp > queryFrom - 15m and PreciseTimeStamp < queryTo + 15m
| where FaultInfo != ""
| extend ExtendedDetails=parse_json(FaultInfo).ExtendedDetails
| mv-expand ExtendedDetails
| where parse_json(ExtendedDetails).Name == "EscalateTo"
| project PreciseTimeStamp, EscalateTo=parse_json(ExtendedDetails).Value, Reason=parse_json(FaultInfo).Reason, FaultTime=parse_json(FaultInfo).Time
| project FaultTime=todatetime(FaultTime),
          Content=substring(tostring(Reason), 0, 20),
          Tooltip=strcat("Reason: ", Reason, ",  EscalateTo: ", EscalateTo)
| serialize // The purpose of the next few steps is to coaslesce the next few rows together 
| extend prev_Tooltip=prev(Tooltip), next_Tooltip=next(Tooltip)
| scan with_match_id=match_id declare (StartTime: datetime, step: string) with (
    step s1 output=none: Tooltip != prev_Tooltip => step='s1', StartTime=FaultTime;
    //step s2 output=none: Content == prev_Content => step='s2', StartTime=s1.StartTime; 
    step s2 output=all: Tooltip != next_Tooltip => step='s2', StartTime=case(FaultTime < s1.StartTime, FaultTime, s1.StartTime); 
)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

### IsTip

_Widget purpose:_ Container Information

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Timeline`

```kusto
MycroftNodeSnapshot
| where NodeId == nodeId
| where PreciseTimeStamp > queryFrom - 1h and PreciseTimeStamp < queryTo + 1h
| project PreciseTimeStamp,
          Content=case(TipNodeSessionId == "00000000-0000-0000-0000-000000000000", "ProdNode", "TipNode")
| sort by PreciseTimeStamp asc
| serialize // The purpose of the next few steps is to coaslesce the next few rows together 
| extend prev_Content=prev(Content), next_Content=next(Content)
| scan with_match_id=match_id declare (StartTime: datetime, step: string) with (
    step s1 output=none: Content != prev_Content => step='s1', StartTime=PreciseTimeStamp;
    step s2 output=all: Content != next_Content => step='s2', StartTime=s1.StartTime; 
)
| sort by StartTime asc
| extend EndTime = case(next(StartTime) != "", next(StartTime), queryTo)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

### Was/WillBe publishes (Madari POV)

_Widget purpose:_ Container Information

Cluster: `aznwsdn.kusto.windows.net` · Database: `sdnpubsub` · Type: `Timeline`

```kusto
PubSubAPICall
| where (additional has_cs strcat("/hosts/", nodeId, ",")) 
| where (additional has_cs strcat("/containers/", containerId, "/was,") or additional has_cs strcat("/containers/", containerId, "/willbe,"))
| extend GroupBy=case(additional has_cs strcat("/containers/", containerId, "/was,"), "WasPublishes (Madari POV)",
                      additional has_cs strcat("/containers/", containerId, "/willbe,"), "WillBePublishes (Madari POV)", "MadariEvents")
| parse additional with * "Data Version: " DataVersion "," *
| where PreciseTimeStamp > queryFrom - 5m and PreciseTimeStamp < queryTo + 5m
| project StartTime=PreciseTimeStamp,
          Content=strcat("DataVersion: ", DataVersion),
          GroupBy
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

---

### AzPubSub Publishing

_Widget purpose:_ Container Information

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
NodeServiceHostProxyEtwTable
| where PreciseTimeStamp > queryFrom - 5m and PreciseTimeStamp < queryTo + 5m
| where NodeId == nodeId
| where Message !contains "ResourceHealthEvents"
| parse Message with * "[request_id=" RequestId "]" *
| parse Message with * "[CRPActivityId=" CRPActivityId "]" *
| project StartTime=PreciseTimeStamp, Content=strcat("RequestId=", RequestId), Metadata=strcat("RequestId=", RequestId, " CRPActivityId=", CRPActivityId), Message, Health=case(Message contains "error", "Unhealthy", "")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmId}`, `{nodeId}`

---

### ContainerWorkflowBlocked

_Widget purpose:_ Container Information

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
// Container Workflow Blocked
macro-expand isfuzzy=true AzCoreKusto as data (
    data.database('Fa').IfxOperationV2v1EtwTable
    | where NodeId == nodeId
    | where ContextInCsv startswith_cs strcat("ContainerId,", containerId) or OperationName startswith_cs "ProcessingWillBeBlocked_"
    | where PreciseTimeStamp > queryFrom and PreciseTimeStamp < queryTo
    | where OperationName != "ContainerOutOfGoal"
    | project StartTime = PreciseTimeStamp - (DurationIn100ns / pow(10, 7) * 1s),
              EndTime = PreciseTimeStamp,
              GroupBy = OperationName,
              Content = OperationName,
              Tooltip = OperationName,
              BlockedTimeInSeconds = tostring(DurationIn100ns / pow(10, 7) * 1s)
)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

**Signal filters seen in KQL:** `OperationName != "ContainerOutOfGoal"`

---

### Madari Operation Failures

_Widget purpose:_ Container Information

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
NodeServiceMadariEventsEtwTable
| where PreciseTimeStamp between (queryFrom..queryTo)
| where RelativePath contains containerId or (vmUniqueId != "" and ContextSelector contains vmUniqueId) or (azLogicalContainerId != "" and ContextSelector contains azLogicalContainerId)
| where Message contains "Failed"
| project PreciseTimeStamp, Message, Operation, RelativePath, ContextSelector
| summarize count(), min(PreciseTimeStamp), max(PreciseTimeStamp), arg_max(PreciseTimeStamp, Message) by Operation, ContextSelector, RelativePath, bin(PreciseTimeStamp, 5m)
| project StartTime = min_PreciseTimeStamp,
              EndTime = max_PreciseTimeStamp,
              GroupBy = Operation,
              Content = Message,
              Tooltip = strcat("Count=", tostring(count_)),
              Health = "Unhealthy"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{vmUniqueId}`, `{azLogicalContainerId}`

**Signal filters seen in KQL:** `Message contains "Failed"`

---

### NodeService Exits

_Widget purpose:_ Container Information

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

### ApSvcMgr State

_Widget purpose:_ NodeState

Cluster: `https://hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureDCMdb` · Type: `Timeline`

```kusto
PFClientBootstrapAvailability
| where PreciseTimeStamp between (queryFrom..queryTo)
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

**Params:** `{queryNode}`, `{queryFrom}`, `{queryTo}`

---

### LogNodeSnapshot - NodeState

_Widget purpose:_ NodeState

Cluster: `https://hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Timeline`

```kusto
let raw = LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom..queryTo)
| where nodeId == queryNode 
| project PreciseTimeStamp, nodeState, faultInfo, nsProgressHealthStatus, cmNodeWasChannelHealthStatus, cmNodeWillBeChannelHealthStatus,tipNodeSessionId;
let nodeState = raw
| project StartTime=PreciseTimeStamp, Content=nodeState, Health = iff(nodeState == "Ready", "Healthy",
                                                                     iff (nodeState in ("Unhealthy", "HumanInvestigate", "Dead", "OutForRepair"), "Unhealthy",
                                                                     "Neutral")),
          Tooltip = faultInfo, GroupBy = "NodeState";
let progressHealth = raw | project StartTime=PreciseTimeStamp, Content=nsProgressHealthStatus, Health = iff(nsProgressHealthStatus == "Healthy", "Healthy", "Unhealthy"), GroupBy = "NSProgressHealth",Tooltip = nsProgressHealthStatus;
let wasHealth = raw | project StartTime=PreciseTimeStamp, Content=cmNodeWasChannelHealthStatus, Health = iff(cmNodeWasChannelHealthStatus == "Healthy", "Healthy", "Unhealthy"), GroupBy = "CMNSWasHealth",Tooltip = cmNodeWasChannelHealthStatus;
let willBeHealth = raw | project StartTime=PreciseTimeStamp, Content=cmNodeWillBeChannelHealthStatus, Health = iff(cmNodeWillBeChannelHealthStatus == "Healthy", "Healthy", "Unhealthy"), GroupBy = "CMNSWillBeHealth",Tooltip = cmNodeWillBeChannelHealthStatus;
let isTip = raw | project StartTime=PreciseTimeStamp, Content=iff(tipNodeSessionId=="00000000-0000-0000-0000-000000000000","ProdNode", "TipNode"), Health = iff(tipNodeSessionId=="00000000-0000-0000-0000-000000000000", "Healthy", "Degraded"), GroupBy = "IsTip",Tooltip = tipNodeSessionId;
nodeState
| union progressHealth
| union wasHealth
| union willBeHealth
| union isTip
| order by GroupBy asc, StartTime asc
| serialize 
| extend FilterOut = (GroupBy == prev(GroupBy) and Content == prev(Content) and isnotempty(next(StartTime)) and GroupBy == next(GroupBy))
| where FilterOut != 1
| extend EndTime = case(isnotempty(next(StartTime)) and GroupBy == next(GroupBy), next(StartTime), now()), Tooltip = iff(isempty(Tooltip), next(Tooltip), Tooltip)
| where EndTime != now()
| extend Tooltip = strcat(tostring(StartTime), ": ", Tooltip)
| sort by GroupBy asc, StartTime asc
```

**Params:** `{queryNode}`, `{queryFrom}`, `{queryTo}`

---

### Fault Information

_Widget purpose:_ Container Health Information 

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`

```kusto
MycroftContainerHealthSnapshot
| where ContainerId == containerId
| where PreciseTimeStamp > queryFrom - 15m and PreciseTimeStamp < queryTo + 15m
| extend ExtendedDetails=case(parse_json(FaultInfo).ExtendedDetails != "", parse_json(FaultInfo).ExtendedDetails, dynamic([{"Name":"EscalateTo","Value":"No Fault"}]))
| mv-expand ExtendedDetails
| where parse_json(ExtendedDetails).Name == "EscalateTo"
| project TIMESTAMP, EscalateTo=parse_json(ExtendedDetails).Value, Reason=parse_json(FaultInfo).Reason, FaultTime=parse_json(FaultInfo).Time,  FirstStartedTime, OsState, IsolationState, LifecycleState
| sort by TIMESTAMP asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

### EG links

_Widget purpose:_ EG Links for IaaS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Table`

```kusto
let tenant = cluster('azcore.centralus').database('AzureCP').MycroftContainerSnapshot
| where PreciseTimeStamp >= queryFrom - 1h and PreciseTimeStamp <= queryTo + 1h
| where ContainerId == containerId
| project PreciseTimeStamp, ContainerId, TenantName
| distinct TenantName;
cluster('executiongraph').database('eg').IaasVmOperations
| where StartTime >= queryFrom - 1h and StartTime <= queryTo + 1h
| where TenantName in (tenant)
| project TIMESTAMP, CrpOperationName, OperationName, TenantName, ContainerId, EgUrl
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
