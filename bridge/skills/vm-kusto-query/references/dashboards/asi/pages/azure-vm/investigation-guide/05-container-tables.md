# Container Tables

> Source: **Azure Host - Azure VM** dashboard, chapter **Container Tables** (7 queries across 6 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Container Faults

### Gandalf Container Fault Query

_Widget purpose:_ ContainerFaults

Cluster: `gandalfdeepad` · Database: `gandalf_deepAD` · Type: `Table`
Source panel: `Container Tables > Container Faults > ContainerFaults`

**Tables:** `ContainerFaults`
**Output columns:** `PreciseTimeStamp`, `ContainerId`, `FabricOperation`, `Reason`, `statusCode`, `Details`, `faultInfo`, `EscalateTo`

```kusto
cluster('gandalfdeepad').database('gandalf_deepAD').ContainerFaults
| where TIMESTAMP between (['_startTime']..['_endTime'])
| where NodeId == ['_nodeId']
| where isempty(['_containerId']) or ContainerId == ['_containerId']
| project PreciseTimeStamp, ContainerId, FabricOperation, Reason, statusCode, Details, faultInfo, EscalateTo
| sort by PreciseTimeStamp
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`, `{_containerId}`

---

## Container Health Snapshot

### Azure Host VM Container Health Snapshot

_Widget purpose:_ LogContainerHealthSnapshot

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Container Tables > Container Health Snapshot > Container Health Snapshot > LogContainerHealthSnapshot`

**Tables:** `LogContainerHealthSnapshot`
**Output columns:** `PreciseTimeStamp`, `containerId`, `containerState`, `actualOperationalState`, `containerOsState`, `vmExpectedHealthState`, `faultInfo`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h)) and (virtualMachineUniqueId == vmId and containerId == cId)
| project PreciseTimeStamp, containerId, containerState, actualOperationalState, containerOsState, vmExpectedHealthState, faultInfo
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{cId}`

---

## Container Snapshot History for VMId

### Gandalf Rogue Container Query

_Widget purpose:_ Container Snapshot History for VMId

Cluster: `https://gandalfdeepad.kusto.windows.net` · Database: `gandalf_deepad` · Type: `MultiRow` · Widget: `Tab`
Source panel: `Container Tables > Container Snapshot History for VMId`

```kusto
let startTime = _startTime;
let endTime = _endTime;
let fn_ContainerId = _container_id;
let fn_NodeId = _node_id;

GetRogueContainerData()
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == fn_NodeId and ContainerId == fn_ContainerId
```

**Params:** `{_startTime}`, `{_endTime}`, `{_container_id}`, `{_node_id}`

---

### Azure Host VM ContainerSnapshot History

_Widget purpose:_ LogContainerSnapshot

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Container Tables > Container Snapshot History for VMId > Container Snapshot History for VMId > LogContainerSnapshot`

**Tables:** `LogContainerSnapshot`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between ((startTime - 1d) .. (endTime + 1d)) and (virtualMachineUniqueId == vmId)
| distinct creationTime, Tenant, containerId, nodeId, roleInstanceName
| extend creationTime = todatetime(creationTime)
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{cId}`

---

## NodeService Events

### NodeService Events

_Widget purpose:_ NodeServiceEventEtwTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Container Tables > NodeService Events > NodeServiceEventEtwTable`

**Tables:** `NodeServiceEventEtwTable`
**Output columns:** `PreciseTimeStamp`, `Message`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == nodeId
| where ScopeIdentifier == containerId
| where Message !contains "]: ContainerManager" and Message !contains "]: WorkflowStarted" and Message !contains "]: Workflow resumed"
| project PreciseTimeStamp, Message
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

## RdAgent Ifx Operations

### RdAgent Container Traces

_Widget purpose:_ IfxOperationV2v1EtwTable

Cluster: `https://azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Container Tables > RdAgent Ifx Operations > IfxOperationV2v1EtwTable`

**Tables:** `IfxOperationV2v1EtwTable`
**Output columns:** `StartTime`, `EndTime`, `OperationName`, `Time`, `ResultSignature`, `ContextInCsv`

```kusto
cluster('Azcore').database('Fa').IfxOperationV2v1EtwTable
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where NodeId == nodeId
| where ContextInCsv contains containerId
| where OperationName != "ContainerOutOfGoal"  // Remove verbosity
| extend Time = DurationIn100ns/10000000.0
| extend StartTime = TIMESTAMP-(Time*1s)
| project StartTime, EndTime=PreciseTimeStamp, OperationName, Time, ResultSignature, ContextInCsv
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

**Signal filters seen in KQL:** `OperationName != "ContainerOutOfGoal"`

---

## Rogue Container

### Gandalf Rogue Container Query

_Widget purpose:_ GetRogueContainerData

Cluster: `https://gandalfdeepad.kusto.windows.net` · Database: `gandalf_deepad` · Type: `Table`
Source panel: `Container Tables > Rogue Container > GetRogueContainerData`

```kusto
let startTime = _startTime;
let endTime = _endTime;
let fn_ContainerId = _containerId;
let fn_NodeId = _nodeId;
GetRogueContainerData()
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == fn_NodeId and ContainerId == fn_ContainerId
```

**Params:** `{_startTime}`, `{_endTime}`, `{_containerId}`, `{_nodeId}`

---
