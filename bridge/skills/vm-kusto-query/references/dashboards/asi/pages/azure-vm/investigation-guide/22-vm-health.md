# VM Health

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Health** (10 queries across 5 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## GHS Data

### GHS Annotations

_Widget purpose:_ GHS Annotations [VmUniqueId]

Cluster: `https://genevahealtheventsprod.kusto.windows.net` · Database: `ResourceHealthAnnotations` · Type: `Table`
Source panel: `VM Health > GHS Data > GHS Annotations [VmUniqueId]`

**Tables:** `ResourceHealthAnnotationEvent`
**Output columns:** `reportTime`, `annotation`, `eventMetadata`, `resourceType`

```kusto
let start = queryFrom;
let end = queryTo;
let VmUniqueId = VmId;
ResourceHealthAnnotationEvent
| where tenant == ShoeboxAccount
| where reportTime between (start..end)
| where armResourceId == VmUniqueId
| project reportTime, annotation, eventMetadata, resourceType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{ShoeboxAccount}`, `{VmId}`

---

### GHS Health Transitions

_Widget purpose:_ GHS Health Transitions [VmUniqueId]

Cluster: `https://genevahealtheventsprod.kusto.windows.net` · Database: `ResourceHealthTransitions` · Type: `Table`
Source panel: `VM Health > GHS Data > GHS Health Transitions [VmUniqueId]`

**Tables:** `ResourceHealthTransitionEvent`
**Output columns:** `resourceTransitionTime`, `reportTime`, `previousHealthStatus`, `newHealthStatus`, `eventMetadata`

```kusto
let start = queryFrom;
let end = queryTo;
let VmUniqueId = VmId;
ResourceHealthTransitionEvent
| where reportTime between (start..end)
| where tenant == ShoeboxAccount
| where armResourceId == VmUniqueId
| project resourceTransitionTime, reportTime, previousHealthStatus, newHealthStatus, eventMetadata
```

**Params:** `{queryFrom}`, `{queryTo}`, `{VmId}`, `{ShoeboxAccount}`

---

## Kyber Health Data

### Kyber Health Timeline

Cluster: `aplat.westcentralus` · Database: `APlat` · Type: `TimeSeries`
Source panel: `VM Health > Kyber Health Data > Kyber Health Timeline`

**Tables:** `KyberContainerHealthMetricData`
**Aggregations:** `summarize All = count(), IcHeartbeats = countif(IcHeartbeat), PowerState = countif(PowerSt by bin(PreciseTimeStamp, 5m)`
**Output columns:** `PreciseTimeStamp`, `ArmId`, `IcHeartbeat`, `PowerState`, `HyperVHandshake`, `CompositeState`, `IncarnationId`, `ApiVersion`

```kusto
KyberContainerHealthMetricData
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ContainerId == containerId
| project PreciseTimeStamp, ArmId, IcHeartbeat, PowerState, HyperVHandshake, CompositeState, IncarnationId, ApiVersion
| summarize 
    All = count(), 
    IcHeartbeats = countif(IcHeartbeat),
    PowerState = countif(PowerState),
    HyperVHandshake = countif(HyperVHandshake)
    by bin(PreciseTimeStamp, 5m)
| extend IcHeartbeats = round(IcHeartbeats / toreal(All) * 100)
| extend PowerState = round(PowerState / toreal(All) * 100)
| extend HyperVHandshake = round(HyperVHandshake / toreal(All) * 100)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

### Kyber Metrics

_Widget purpose:_ KyberAnnotationEvents

Cluster: `https://aplat.westcentralus.kusto.windows.net` · Database: `Aplat` · Type: `Table`
Source panel: `VM Health > Kyber Health Data > KyberAnnotationEvents`

**Tables:** `KyberAnnotationEvent`
**Output columns:** `OccurredTime`, `AnnotationName`, `AnnotationMetadata`, `ResourceIdentityMetadata`, `SourceServiceName`

```kusto
KyberAnnotationEvent
| where PreciseTimeStamp between(queryFrom..queryTo)
| where ContainerId == containerId
| project OccurredTime, AnnotationName, AnnotationMetadata, ResourceIdentityMetadata, SourceServiceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

### Kyber Container Health Metrics

_Widget purpose:_ KyberContainerHealthMetricData

Cluster: `https://aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`
Source panel: `VM Health > Kyber Health Data > KyberContainerHealthMetricData`

**Tables:** `KyberContainerHealthMetricData`
**Output columns:** `PreciseTimeStamp`, `ArmId`, `IcHeartbeat`, `PowerState`, `HyperVHandshake`, `CompositeState`, `IncarnationId`, `ApiVersion`

```kusto
KyberContainerHealthMetricData
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ContainerId == containerId
| project PreciseTimeStamp, ArmId, IcHeartbeat, PowerState, HyperVHandshake, CompositeState, IncarnationId, ApiVersion
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

## RdAgent Annotations

### AzPubSub RdAgent Events

_Widget purpose:_ AzPubSub Client Event(RdAgent Table)

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Health > RdAgent Annotations > AzPubSub Client Event(RdAgent Table)`

**Tables:** `RdAgentAzPubSubEtwTable`
**Output columns:** `PreciseTimeStamp`, `Message`, `Level`

```kusto
RdAgentAzPubSubEtwTable
| where PreciseTimeStamp between(queryFrom..queryTo)
| where NodeId == nodeId
| where Message contains containerId
| project PreciseTimeStamp, Message, Level
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`, `{containerId}`

---

### RdAgent Container Annotations

_Widget purpose:_ RHCAnnotations Raw View

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VM Health > RdAgent Annotations > RHCAnnotations Raw View`

**Tables:** `RhcAnnotationReportsEtwTable`
**Output columns:** `PreciseTimeStamp`, `Annotation`, `RHCChannelStatusCode`, `KyberChannelStatusCode`

```kusto
let start = queryFrom;
let end = queryTo;
cluster("Azcore").database("Fa").RhcAnnotationReportsEtwTable
| where PreciseTimeStamp >= start and PreciseTimeStamp < end
| where ContainerId == containerId
| project PreciseTimeStamp, Annotation, RHCChannelStatusCode, KyberChannelStatusCode
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

## RdAgent Health Metrics

### Azure Host VM Health

_Widget purpose:_ VM Health - All

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `VM Health > RdAgent Health Metrics > VM Health - All`

**Tables:** `VmHealthRawStateEtwTable`
**Output columns:** `PreciseTimeStamp`, `ContainerId`, `VmHyperVIcHeartbeat`, `VmPowerState`, `HasHyperVHandshakeCompleted`, `IsVscStateOperational`, `Context`

```kusto
VmHealthRawStateEtwTable
| where PreciseTimeStamp between (startTime .. endTime) and ContainerId == containerId
| project PreciseTimeStamp = tostring(PreciseTimeStamp), ContainerId, VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted, IsVscStateOperational, Context 
| extend level = case(VmHyperVIcHeartbeat == "HeartBeatStateOk", "info", "warning")
| sort by PreciseTimeStamp desc nulls last
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

### Azure Host VM Health - State Changes

_Widget purpose:_ VM Health - State Changes

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `VM Health > RdAgent Health Metrics > VM Health - State Changes`

**Tables:** `VmHealthRawStateEtwTable`
**Output columns:** `PreciseTimeStamp`, `ContainerId`, `VmHyperVIcHeartbeat`, `VmPowerState`, `HasHyperVHandshakeCompleted`, `IsVscStateOperational`, `Context`

```kusto
VmHealthRawStateEtwTable
| where PreciseTimeStamp between (startTime .. endTime) 
| where ContainerId == containerId
| project PreciseTimeStamp, ContainerId, VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted, IsVscStateOperational, Context 
| sort by PreciseTimeStamp asc
| extend PrevTime = prev(PreciseTimeStamp)
| extend NextTime = next(PreciseTimeStamp)
| extend PrevContainer = prev(ContainerId)
| extend PrevHeartbeat = prev(VmHyperVIcHeartbeat)
| extend PrevPowerState = prev(VmPowerState)
| extend PrevHandshake = prev(HasHyperVHandshakeCompleted)
| extend PrevVscStateOperational = prev(IsVscStateOperational)
| extend PrevContext = prev(Context)
| where 
    isnull(PrevTime) or 
    isnull(NextTime) or 
    (ContainerId != PrevContainer) or 
    (VmHyperVIcHeartbeat != PrevHeartbeat) or 
    (VmPowerState != PrevPowerState) or 
    (HasHyperVHandshakeCompleted != PrevHandshake) or 
    (IsVscStateOperational != PrevVscStateOperational) or 
    (Context != PrevContext) 
| project PreciseTimeStamp, ContainerId, VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted, IsVscStateOperational, Context 
| extend level = case(VmHyperVIcHeartbeat == "HeartBeatStateOk", "info", "warning")
| order by PreciseTimeStamp desc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

## Scheduled Events

### Azure Host VM Scheduled Event Notifications

_Widget purpose:_ Scheduled Events

Cluster: `azpe` · Database: `azpe` · Type: `Table`
Source panel: `VM Health > Scheduled Events > Scheduled Events`

**Tables:** `AzPEWorkflowEvent`
**Output columns:** `PreciseTimeStamp`, `WorkflowEventType`, `WorkflowEventData`

```kusto
let workflowId = cluster('azpe.kusto.windows.net').database('azpe').AzPEWorkflowEvent
| where PreciseTimeStamp between (startTime .. endTime) //and EntityId == tenantName 
        and WorkflowEventData contains roleInstanceName
| distinct WorkflowId;
cluster('azpe.kusto.windows.net').database('azpe').AzPEWorkflowEvent
| where PreciseTimeStamp between (startTime .. endTime) and WorkflowId in (workflowId) //and EntityId == tenantName
| project PreciseTimeStamp, WorkflowEventType, WorkflowEventData
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{roleInstanceName}`, `{tenantName}`

---
