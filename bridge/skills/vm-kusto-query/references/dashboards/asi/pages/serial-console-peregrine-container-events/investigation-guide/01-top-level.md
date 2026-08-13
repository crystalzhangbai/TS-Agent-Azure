# (top-level)

> Source: **Peregrine_ContainerEvents** dashboard, chapter **(top-level)** (15 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Peregrine_ContainerEvents"

Cluster: `hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
let bmcMycroft = cluster('mycroft.westcentralus.kusto.windows.net').database('Mycroft').MycroftContainerSnapshot
| where ContainerId == local_containerId
| take 1;
let azcoreMycroft = cluster('azcore.centralus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
| where ContainerId == local_containerId
| take 1;
let hawkeye = cluster('hawkeyekustocluster.centralus.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where containerId == local_containerId
| take 1;
bmcMycroft
| union azcoreMycroft
| take 1
| project TimeWhenContainerIdIsPresent=PreciseTimeStamp, Region=Tenant, ContainerType, ContainerLifeCycleOwner, Cluster=ClusterName, containerId=ContainerId, ContainerId, NodeId, VirtualMachineUniqueId, TenantName, RoleInstanceName, BillingContext, SubscriptionId;
```

**Params:** `{local_containerId}`

---

### WillBePublishesToMadariFromAzCiM

_Widget purpose:_ Container Information

Cluster: `vmadiag.kusto.windows.net` · Database: `AzureCM` · Type: `Timeline`

```kusto
cluster('vmadiag').database('AzureCM').AzCiMContainerWillBe
| where PhysicalContainerId == containerId
| where PreciseTimeStamp > queryFrom and PreciseTimeStamp < queryTo
| sort by PreciseTimeStamp asc
| project PreciseTimeStamp, Revision=parse_json(WillBe).revision, State=tostring(parse_json(WillBe).state)
| serialize 
| where prev(State) != State
| project Table="WillBePublishesToMadari",
          StartTime=PreciseTimeStamp, 
          Content=case(isempty(Revision), "Deleted",
                       State),
          Tooltip=case(isempty(Revision), "Deleted",
                       strcat("Revision=", Revision))
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
let UberEventTable = materialize(NodeServiceEventEtwTable
| where PreciseTimeStamp > queryFrom - 5m and PreciseTimeStamp < queryTo + 5m
| where NodeId == nodeId
| where ScopeIdentifier == containerId
| where ((Message has_cs "Updated Was") or 
         (Message has_cs "Overpacking" or Message has_cs "Container workflow blocked"))
| project PreciseTimeStamp, Message);

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
| scan with_match_id=match_id declare (StartTime: datetime, step: string) with (
    step s1 output=none: Content != prev_Content => step='s1', StartTime=CurrentTime;
    //step s2 output=none: Content == prev_Content => step='s2', StartTime=s1.StartTime; 
    step s2 output=all: Content != next_Content => step='s2', StartTime=s1.StartTime; 
)
| sort by StartTime asc
| extend EndTime = case(next(StartTime) != "", next(StartTime), queryTo)
| project StartTime=StartTime,
          EndTime=EndTime,
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
| scan with_match_id=match_id declare (StartTime: datetime, step: string) with (
    step s1 output=none: Content != prev_Content => step='s1', StartTime=CurrentTime;
    //step s2 output=none: Content == prev_Content => step='s2', StartTime=s1.StartTime; 
    step s2 output=all: Content != next_Content => step='s2', StartTime=s1.StartTime; 
)
| sort by StartTime asc
| extend EndTime = case(next(StartTime) != "", next(StartTime), queryTo)
| project StartTime=StartTime,
          EndTime=EndTime,
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
| scan with_match_id=match_id declare (StartTime: datetime, step: string) with (
    step s1 output=none: Content != prev_Content => step='s1', StartTime=CurrentTime;
    //step s2 output=none: Content == prev_Content => step='s2', StartTime=s1.StartTime; 
    step s2 output=all: Content != next_Content => step='s2', StartTime=s1.StartTime; 
)
| sort by StartTime asc
| extend EndTime = case(next(StartTime) != "", next(StartTime), queryTo)
| project StartTime=StartTime,
          EndTime=EndTime,
          Content=Content,
          Tooltip=Tooltip,
          GroupBy="ProvisioningState",
          SortHelper=3;
//ContainerWorkflowBlocked
let ContainerWorkflowBlocked = UberEventTable
| where (Message has_cs "Overpacking" or Message has_cs "Container workflow blocked")
| sort by PreciseTimeStamp asc
| parse Message with * "overpackedCaseReason=" OverpackedCaseReason
| parse Message with * "Container workflow blocked: " WorkflowBlockedReason "." *
| parse Message with * "EscalateTo: " EscalateTo "." *
| project Table="OverpackingTable",
          StartTime=PreciseTimeStamp,
          Content=case(OverpackedCaseReason != "", OverpackedCaseReason,
                       WorkflowBlockedReason)
| summarize min(StartTime), max(StartTime), count() by Content
| project StartTime=min_StartTime,
          EndTime=max_StartTime,
          Content,
          Tooltip=tostring(count_),
          GroupBy=strcat("ContainerWorkflowBlocked_", Content),
          SortHelper=4;
// Union of above tables
StateSerialized | union GuestOsStateSerialized | union ProvisioningStateSerialized | union ContainerWorkflowBlocked
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
| where PreciseTimeStamp > datetime(2023-11-14 00:27:04.3339850) - 5m and PreciseTimeStamp < datetime(2023-11-14 00:27:04.3339850) + 5m
| where NodeId == '9fab58ea-6aa1-67ba-1fb7-36bba067505a'
| where Message !contains "ResourceHealthEvents"
| parse Message with * "[request_id=" RequestId "]" *
| parse Message with * "[CRPActivityId=" CRPActivityId "]" *
| project StartTime=PreciseTimeStamp, Content=strcat("RequestId=", RequestId), Metadata=strcat("RequestId=", RequestId, " CRPActivityId=", CRPActivityId), Message, Health=case(Message contains "error", "Unhealthy", "")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmId}`, `{nodeId}`

**Signal filters seen in KQL:** `NodeId == "9fab58ea-6aa1-67ba-1fb7-36bba067505a"`

---

### lxprov

_Widget purpose:_ Container Information

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
let ActivityIds=IfxOperationV2v1EtwTable
| where PreciseTimeStamp between(queryFrom..queryTo)
| where OperationName == 'GuestOsKVPItems'
| where ContextInCsv has _container_id
| distinct ActivityId;
IfxOperationV2v1EtwTable
| where PreciseTimeStamp between(queryFrom..queryTo)
| where ParentActivityId in (ActivityIds)
| where OperationName == 'KVPData'
| extend raw_data = substring(ContextInCsv, indexof(ContextInCsv, ",")+1)
| extend double_quoted_json = substring(raw_data, 1, strlen(raw_data) - 2)
| extend data_json = replace_string(double_quoted_json, "\"\"", "\"")
| extend ts = parse_json(data_json)["ts"]
| extend Content=substring(ContextInCsv, indexof(ContextInCsv, "|", 0, -1, 2)+1, indexof(ContextInCsv, "|", 0, -1, 4)-indexof(ContextInCsv, "|", 0, -1, 2)-1)
| where Content has_any ("_setup_ephemeral_networking", "get_metadata_from_imds", "_poll_imds", "get-reprovision-data-from-imds", "_report_ready", "_report_failure")
| project ts, StartTime=todatetime(ts), Tooltip=substring(ContextInCsv, 0, indexof(ContextInCsv, ",")-1), Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_container_id}`

**Signal filters seen in KQL:** `OperationName == "GuestOsKVPItems"` · `OperationName == "KVPData"`

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

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Table`

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
