# Fabric Tables

> Source: **Azure Host — Azure Host Node** dashboard, chapter **Fabric Tables** (10 queries across 9 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Anvil Events

### Azure Host Anvil ForgeEvents

_Widget purpose:_ Anvil Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Table`
Source panel: `Fabric Tables > Anvil Events > Anvil Events > Anvil Events`

```kusto
AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (startTime .. endTime) and ResourceDependencies contains nodeId
| where  isnotempty(TreeNodeKey)
| where  TreeNodeKey !in ('Root', 'Node')
| summarize arg_max(PreciseTimeStamp, *) by RequestIdentifier, TreeNodeKey 
| order by RequestIdentifier, PreciseTimeStamp asc
| project PreciseTimeStamp, AnvilOperation=TreeNodeKey, AnvilRequestIdentifier=RequestIdentifier, ResourceId, ResourceType
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Container Health Snapshot

### Azure Host ContainerHealth Snapshot

_Widget purpose:_ LogContainerHealthSnapshot

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Fabric Tables > Container Health Snapshot > Container Health Snapshot > LogContainerHealthSnapshot`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp between (startTime .. endTime) and nodeId == nodeIdStr
| project PreciseTimeStamp, containerId, roleInstanceName, actualOperationalState, containerOsState, containerLifecycleState, vmExpectedHealthState, faultInfo
```

**Params:** `{startTime}`, `{endTime}`, `{nodeIdStr}`

---

## Fabric Fault Handler Recovery

### Azure Host Fabric FaultHandler Recovery

_Widget purpose:_ FaultHandlingRecoveryEventEtwTable

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric Tables > Fabric Fault Handler Recovery > Fabric Fault Handler Recovery > FaultHandlingRecoveryEventEtwTable`

```kusto
FaultHandlingRecoveryEventEtwTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp = tostring(PreciseTimeStamp), RecoveryResult, RecoveryAction, FaultSignature, Details, FaultRecoveryDurationInMinutes 
| sort by PreciseTimeStamp asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## Fabric Node Events

### Azure Host Fabric Node Events

_Widget purpose:_ TMMgmtNodeEventsEtwTable

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Fabric Tables > Fabric Node Events > Fabric Node Events > TMMgmtNodeEventsEtwTable`

```kusto
TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where Message !has "Received new Was for Container"
| project PreciseTimeStamp = tostring(PreciseTimeStamp), Message 
| sort by PreciseTimeStamp asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## Fabric Node Faults

### Azure Host Fabric Node Faults

_Widget purpose:_ TMMgmtNodeFaultEtwTable

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Fabric Tables > Fabric Node Faults > Fabric Node Faults > TMMgmtNodeFaultEtwTable`

```kusto
TMMgmtNodeFaultEtwTable
| where PreciseTimeStamp between (startTime .. endTime) and BladeID == nodeId
| project Time = tostring(Time), FaultCode, Reason, Details  
| sort by Time asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## Hawkeye Events

### Azure Host Hawkeye Events

_Widget purpose:_ Hawkeye Events

Cluster: `hawkeyedataexplorer.westus2.kusto.windows.net` · Database: `HawkeyeLogs` · Type: `Table`
Source panel: `Fabric Tables > Hawkeye Events > Hawkeye Events`

```kusto
HawkeyeTriageEvents
| where PreciseTimeStamp between ((queryFrom - 7d) .. (queryTo + 7d))
| where Input contains nodeId
| extend FaultTime = todatetime(parse_json(Input).FaultTime)
| where FaultTime between (queryFrom .. queryTo)
| project PreciseTimeStamp, FaultTime, ScenarioName, Output, Input
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---

## Node State Changes

### LogNodeSnapshot

_Widget purpose:_ Node State Changes

Cluster: `azurecm.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table` · Widget: `Tab`
Source panel: `Fabric Tables > Node State Changes`

```kusto
cluster('azurecm.centralus.kusto.windows.net').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp between (startTime..endTime)
| where nodeId == NodeID
| project PreciseTimeStamp, nodeId, nodeState, healthSignals, nodeAvailabilityState, faultInfo
```

**Params:** `{startTime}`, `{endTime}`, `{NodeID}`

---

### Azure Host Fabric Node State Changes

_Widget purpose:_ TMMgmtNodeStateChangedEtwTable

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Fabric Tables > Node State Changes > Node State Changes > TMMgmtNodeStateChangedEtwTable`

```kusto
TMMgmtNodeStateChangedEtwTable
| where PreciseTimeStamp between ((startTime - 1d) .. (endTime + 1d)) and BladeID == nodeId
| project StartTime = PreciseTimeStamp, OldState, NewState
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## Rogue Containers

### Gandalf Rogue Containers Query

_Widget purpose:_ GetRogueContainerData

Cluster: `https://gandalfdeepad.kusto.windows.net` · Database: `gandalf_deepad` · Type: `Table`
Source panel: `Fabric Tables > Rogue Containers > GetRogueContainerData`

```kusto
let startTime = _startTime;
let endTime = _endTime;
let fn_NodeId = _nodeId;
GetRogueContainerData()
| where PreciseTimeStamp between (startTime .. endTime)
| where NodeId == fn_NodeId
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

---

## SLAMeasurementTable

### Azure Host Fabric SLAMeasurementTable

_Widget purpose:_ TMMgmtSlaMeasurementEventEtwTable

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric Tables > SLAMeasurementTable > SLAMeasurementTable > TMMgmtSlaMeasurementEventEtwTable`

```kusto
TMMgmtSlaMeasurementEventEtwTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeID == nodeId
| project PreciseTimeStamp, RoleInstanceName, ContainerID, Context, EntityState, Detail0
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---
