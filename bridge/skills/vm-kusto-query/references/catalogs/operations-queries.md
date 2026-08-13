# Operations Queries — Hawkeye, Maintenance, Watson Bugchecks, Azure Policy Engine

---

## Hawkeye — Automated Unhealthy Node Analyzer

Cluster: `hawkeyedataexplorer.westus2.kusto.windows.net`
Database: `HawkeyeLogs`

Web UI: `aka.ms/WhyUnhealthy?startTime={StartTime}Z&endTime={EndTime}Z&nodeId={NodeId}`

### GetLatestHawkeyeRCAEvents — Automated RCA

```kusto
cluster('hawkeyedataexplorer.westus2.kusto.windows.net').database('HawkeyeLogs').GetLatestHawkeyeRCAEvents
| where RCATimestamp >= datetime({StartTime}) and RCATimestamp < datetime({EndTime})
| where NodeId == "{NodeId}"
| distinct RCATimestamp, NodeId, RCALevel1, RCALevel2, EscalateToOrg, EscalateToTeam
```

---

## Maintenance & Customer Notifications

Cluster: `icmcluster`
Databases: `ACM.Publisher`, `ACM.Backend`

### GetCommunicationsForSupport — Planned maintenance notifications

```kusto
let ParamSubscriptionId = '{SubscriptionId}';
cluster('icmcluster').database('ACM.Publisher').GetCommunicationsForSupport(Cloud="Public", Subid=ParamSubscriptionId, StartTime=ago(60d), EndTime=now())
| extend JSON = parse_json(list_json) | project-away list_json
| mv-expand JSON
| where JSON.Type contains "Maintenance"
| project Status = tostring(JSON.Status), Type = tostring(JSON.Type), TrackingId = tostring(JSON.TrackingId), ICMNumber = tostring(JSON.LSIID),
MaintenanceStartDate = todatetime(JSON.StartTime), MaintenanceEndDate = todatetime(JSON.EndTime), NotificationCreationDate = todatetime(JSON.CreateDate),
NotificationContent = tostring(JSON.CurrentDescription)
| where NotificationContent !contains "Azure SQL"
| order by MaintenanceStartDate desc
```

### AlbnTargets + PublishRequest — Outage/maintenance notifications

```kusto
cluster('Icmcluster').database('ACM.Publisher').AlbnTargets
| where Subscriptions contains "{SubscriptionId}"
| project CommunicationId
| join cluster('Icmcluster').database("ACM.Backend").PublishRequest on CommunicationId
| where CommunicationDateTime >= datetime({StartTime})
| order by CommunicationDateTime desc
| project CommunicationDateTime, CommunicationType, Title, IncidentId, RichTextMessage, CommunicationId
```

### PublishRequest — Specific incident details

```kusto
cluster('Icmcluster').database("ACM.Backend").PublishRequest
| where IncidentId == "{IncidentId}"
```

---

## Watson — Host Node Bugchecks

Cluster: `Azurewatsoncustomer`
Database: `AzureWatsonCustomer`

### CustomerCrashOccurredV2 — Bugcheck events

```kusto
cluster('Azurewatsoncustomer').database('AzureWatsonCustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where nodeIdentity == "{NodeId}" and crashMode == "km"
| project PreciseTimeStamp, nodeIdentity, EventMessage, crashMode
```

### CustomerCrashOccurredV2 + CustomerDumpAnalysisResultV2 — Bugcheck with faulting module

```kusto
cluster('Azurewatsoncustomer').database('AzureWatsonCustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where nodeIdentity == "{NodeId}" and crashMode == "km"
| join kind = leftouter
(cluster('Azurewatsoncustomer').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
) on $left.dumpUid == $right.dumpUid
| project PreciseTimeStamp, nodeIdentity, EventMessage, crashMode, faultingModule1, bucketString, dumpType, bugId, bugLink
```

---

## Azure Policy Engine — Host Update Workflow

Cluster: `azpe.kusto.windows.net`
Database: `azpe`

AzPE is used by Orchestrate Manager (OM) to send host update notifications to nodes and tenant approval requests.

### AzPEWorkflowEvent — Host update workflow

```kusto
let starttime = datetime({StartTime});
let endtime = datetime({EndTime});
let nodeid = "{NodeId}";
cluster('azpe.kusto.windows.net').database('azpe').AzPEWorkflowEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where WorkflowId contains nodeid
| where WorkflowType == "OM"
| where EntityId contains "AzPEHostUpdateMonitor"
| project PreciseTimeStamp, WorkflowInstanceGuid, WorkflowId, WorkflowType, WorkflowEventData
| order by PreciseTimeStamp asc
```

### AzPEWorkflowEvent — Storage Datapath (DPP) update impact monitor

Same `AzPEHostUpdateMonitor` workflow, used in the storage-datapath context to confirm a node's DPP cut-over event payload. The `WorkflowEventData.ImpactInformation.Impact.Value` JSON should show `DiskImpact: "Freeze"`, `ComputeImpact: "None"`, `EstimatedImpactDurationInSeconds: 9`.

```kusto
let queryFrom = datetime({StartTime});
let queryTo   = datetime({EndTime});
let queryNodeId = "{NodeId}";
cluster("azpe.kusto.windows.net").database("azpe").AzPEWorkflowEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where WorkflowId contains queryNodeId
| where WorkflowType == "OM"
| where EntityId contains "AzPEHostUpdateMonitor"
| project StartTime = PreciseTimeStamp, WorkflowInstanceGuid, WorkflowId, WorkflowType,
    WorkflowEventType, WorkflowEventData,
    Content = strcat(WorkflowType, ':', WorkflowEventType), Health = 'Neutral'
| order by StartTime asc
```

Interpretation:
- Cross-reference with `azcsupfollower.AzureCM.ServiceVersionSwitch` (see `azurecm-queries.md`) to confirm the actual `NewVersion contains 'Datapath'` row on the same NodeId/timestamp.
- TSG: [Datapath Update Impact_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/Datapath-Update-Impact_Perf).

### GetScheduledEventsEnablementStatusV3() — Tenant Scheduled Events on/off

Used to confirm whether **Scheduled Events are enabled** on a tenant. When a customer reports "Restart/Redeploy is delayed by ~15 minutes", the most common cause is that Scheduled Events polling is enabled and the platform is waiting for the in-guest agent to acknowledge the event. Use this to confirm the enablement.

```kusto
cluster("Azpe.kusto.windows.net").database("azpe").GetScheduledEventsEnablementStatusV3("{TenantName}", datetime({Date}))
```

Output columns:
- `DeploymentId` — the tenant
- `LastLoggedStatusTimeStamp` — when the platform last received the status from the in-guest IMDS Scheduled Events endpoint
- `ScheduledEventsStatus` — `True` (enabled, expect 15 min delay on Restart/Redeploy) / `False` (not enabled — eliminate this cause)

If `True` → explain to customer; for perf-sensitive workloads the in-guest agent can pre-approve the event via IMDS POST `/metadata/scheduledevents` (`StartRequests` body) to avoid the wait.

TSG anchor: [Start-Stop-Operations-Taking-Too-Long wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495465) → § "How to confirm that Scheduled Events are enabled for the tenant".

---

## Storage Datapath Deployment Progress (DPP Rollout)

Cluster: `storageclient.eastus.kusto.windows.net`
Database: `Sc`

Used to answer "is DPP build X done rolling out in region Y?" \u2014 e.g. after telling a customer "your impact was a DPP 153 cut-over, the fixed build is DPP 173, here's the rollout status in your region."

### GetSimpleDeploymentProgress() — Region-level rollout summary

```kusto
let _buildLabel = '{BuildLabel}';     // e.g. 'Datapath_7_10_0_173_153_10_0_173'
let _region     = dynamic([{RegionList}]); // e.g. dynamic(['uksouth', 'asiaeast', 'japaneast', 'koreacentral', 'europewest', 'useast'])
let Deployment = () {
    cluster("storageclient.eastus.kusto.windows.net").database("Sc").GetSimpleDeploymentProgress(_buildLabel)
};
Deployment
| where isnull(_region) or Region in~ (_region)
| summarize
    Complete  = countif(TargetStatus =~ "Ok" or RolloutType =~ "CatchUp"),
    InRollout = countif(TargetStatus =~ "InRollout" and RolloutType =~ "Regular"),
    Remaining = countif(TargetStatus !~ "InRollout" and TargetStatus !~ "Ok" and RolloutType =~ "Regular"),
    Total     = count()
    by Region
| extend
    CompletionPercentage = round(100.0 * Complete / Total),
    lRegion              = tolower(Region)
| project Region, Complete, InRollout, Remaining, Total, CompletionPercentage
| order by Region asc
```

Interpretation:
- Per-region `CompletionPercentage` for the target DPP build label.
- Drop the `by Region` to `by StageOrder, Stage, Region` (uncomment in TSG version) for SafeFly stage breakdown.
- Source TSG: [Datapath Update Impact_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/Datapath-Update-Impact_Perf).

---

## Resource Health Signal Queries

### AirResourceHealthEvents — Resource Health annotations

Cluster: `vmainsight.kusto.windows.net`
Database: `Air`

```kusto
cluster('vmainsight.kusto.windows.net').database('Air').AirResourceHealthEvents
| where EventTime >= datetime({StartTime}) and EventTime <= datetime({EndTime})
| where SubscriptionId == "{SubscriptionId}"
| where ResourceName has "{VMName}"
| project EventTime, ResourceName, SubscriptionId, HealthStatus, PreviousHealthStatus,
    AnnotationName, Context, Category, RCALevel1, RCALevel2
| order by EventTime asc
```

Interpretation:
- `HealthStatus` values: `Available`, `Unavailable`, `Degraded`, `Unknown`
- `PreviousHealthStatus` → `HealthStatus` shows the transition
- `AnnotationName` — the annotation shown in the Azure portal Resource Health blade
- `Context` — additional context (JSON, use `parse_json()` for details)
- `Category` values: `PlannedMaintenance`, `Unplanned`, `UserInitiated`
- Useful for confirming what the customer sees in the Azure portal

### Hawkeye RCA — Extended with SEL and repair correlation

```kusto
cluster('hawkeyedataexplorer.westus2.kusto.windows.net').database('HawkeyeLogs').GetLatestHawkeyeRCAEvents
| where RCATimestamp >= datetime({StartTime}) and RCATimestamp < datetime({EndTime})
| where NodeId == "{NodeId}"
| project RCATimestamp, NodeId, RCALevel1, RCALevel2, RCALevel3,
    EscalateToOrg, EscalateToTeam, FaultCode, SelSummary, RepairRecommendation
| order by RCATimestamp desc
```

Interpretation:
- Extended Hawkeye RCA includes SEL summary and repair recommendation
- `SelSummary` — summary of System Event Log findings (hardware errors)
- `RepairRecommendation` — suggested next steps (e.g., `ReplaceNode`, `RebootNode`, `MonitorNode`)
- `FaultCode` — correlate with `FaultCodeTeamMapping` in AzureDCMDb

---

## ICM Incident Correlation

### ICM Incident Details — Get incident details by ID

Cluster: `icmcluster`
Database: `IcMDataWarehouse`

```kusto
cluster('icmcluster').database('IcMDataWarehouse').Incidents
| where IncidentId == "{IncidentId}"
| project IncidentId, Title, Severity, Status, CreateDate, MitigateDate,
    ResolveDate, OwningTeamName, OwningServiceName, ImpactStartDateTime,
    ImpactMitigationDateTime, Summary
```

### ICM Incidents — Find incidents impacting a node/cluster

```kusto
cluster('icmcluster').database('IcMDataWarehouse').Incidents
| where CreateDate >= datetime({StartTime}) and CreateDate <= datetime({EndTime})
| where Keywords has "{NodeId}" or Keywords has "{Cluster}"
| project IncidentId, Title, Severity, Status, CreateDate, OwningTeamName,
    ImpactStartDateTime, ImpactMitigationDateTime
| order by CreateDate desc
```

Interpretation:
- Shows platform incidents that may have impacted the node/cluster
- Severity 0-2 incidents typically indicate significant platform issues
- `ImpactStartDateTime` / `ImpactMitigationDateTime` — define the impact window
- Cross-reference incident timing with VM downtime events

---

## ASW Case Analytics

### ASW Agent Case Volume — Engineer case volume (last 90 days)

Calculate case volume by ASW engineer alias for incidents created in the last 90 days, scoped to ASW customer TPIDs and ASW queues. Appends a total row and sorts by descending case volume.

Clusters: `bedrock.eastus.kusto.windows.net` (CSI), `supportrptwus3prod.westus3.kusto.windows.net` (KPISupportData)

```kusto
let ASWQueues = cluster('bedrock.eastus.kusto.windows.net').database("CSI").ASWQueue | project Queue;
let ASWCXTPID = cluster('bedrock.eastus.kusto.windows.net').database("CSI").ASWCustomer | project TPID;
let ASWAgentAlias = cluster('bedrock.eastus.kusto.windows.net').database("CSI").ASWStakeholder | where Role == "Engineer" | where BusinessUnit == "CSS-ASW" | project AgentAlias;
let StartTime = datetime(2025-01-01);
let EndTime = now();
let AgentData =
    cluster('supportrptwus3prod.westus3.kusto.windows.net').database('KPISupportData').AllCloudsSupportIncidentWithReferenceModelVNext
    | where CreatedDateTime >= ago(90d)
    | where Customer_TPID in (ASWCXTPID)
    | where CurrentQueueName in (ASWQueues)
    | where AgentAlias in (ASWAgentAlias | project AgentAlias)
    | summarize CaseVolume = count() by AgentAlias
    | join kind=leftouter (cluster('bedrock.eastus.kusto.windows.net').database("CSI").ASWStakeholder
        | project AgentAlias, AgentName) on AgentAlias
    | project AgentAlias, AgentName, CaseVolume;
let AggregatedTotals =
    AgentData
    | summarize TotalCaseVolume = sum(CaseVolume),
                 AgentCount = count()
    | extend AvgCaseVolume = TotalCaseVolume * 1.0 / AgentCount;
let TotalsRow =
    AggregatedTotals
    | extend AgentAlias = "Total", AgentName = "All Agents"
    | project AgentAlias, AgentName, TotalCaseVolume, AvgCaseVolume;
AgentData
| project AgentAlias, AgentName, CaseVolume
| union (
    TotalsRow
    | project AgentAlias, AgentName, CaseVolume = TotalCaseVolume
)
| order by CaseVolume desc
```

Interpretation:
- 4-table cross-cluster join: ASWQueue, ASWCustomer, ASWStakeholder (bedrock), AllCloudsSupportIncidentWithReferenceModelVNext (supportrptwus3prod)
- Last row ("Total") shows aggregate case volume and can be used to compute averages
- Modify `ago(90d)` to adjust the time window
