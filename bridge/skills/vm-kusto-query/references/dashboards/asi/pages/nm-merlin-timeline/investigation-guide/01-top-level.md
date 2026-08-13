# (top-level)

> Source: **Network Manager - MerlinTimeline** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "MerlinTimeline"

Cluster: `azurecm` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
let cluster = coalesce(local_Tenant, 'xxcv');
let s_containerId = coalesce(local_containerId, 'xxcv');
let s_interfaceId = coalesce(local_interfaceId, 'xxcv');
let vmUniqueId = coalesce(local_vmUniqueId, 'xxcv');
NetworkServiceManagerEvents
| where PreciseTimeStamp  between (startTime .. endTime)
| where Tenant =~ cluster
| where TaskName == 'LogMerlinInterfaceStateMachineCreated'
| where Message has_any (s_interfaceId, vmUniqueId, s_containerId)
| top 1 by PreciseTimeStamp asc
| parse Message with * 'containerId="' containerId:string '"' * 'merlinNetworkInterfaceInstanceId="' interfaceId:string '"' * 
| project PreciseTimeStamp, Tenant, containerId, interfaceId, vmUniqueId = local_vmUniqueId
```

**Params:** `{local_Tenant}`, `{local_containerId}`, `{local_interfaceId}`, `{local_vmUniqueId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `TaskName == "LogMerlinInterfaceStateMachineCreated"`

---

### MerlinTimelineFull

_Widget purpose:_ Merlin Timeline

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`

```kusto
let q_vmUniqueId = coalesce(tostring(toguid(vmUniqueId)), 'xcvv12f');
NetworkServiceManagerEvents
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime)
| where Tenant =~ cluster and TaskName !in ('LogMerlinNotificationReceived','NicInstanceManagerEvent','SwiftUpdates')
| where Message has_any (interfaceId, q_vmUniqueId, query_containerId)
| project PreciseTimeStamp, Event=strcat('NsmEvt: ', TaskName), Message
| union (
DCMNMQOSInfoEtwTable
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime)
| where Tenant =~ cluster and operation in ('BatchUpdateNetworkResource-Allocation', 'BatchUpdateNetworkResource-Release')
| where additionalMessage has query_containerId
| project PreciseTimeStamp, Event=strcat('NsmQos: ', operation), Message=strcat(additionalMessage, @"success=", success, " message=", message)
)
| union (
// NM programming
cluster('aznwsdn').database('aznwmds').InterfaceProgramEndFiveMinuteTable
| where TIMESTAMP between (query_BeginTime .. query_EndTime)
| where Cluster =~ cluster
| where ContainerId == query_containerId
| where Detail == 'Unblock Port Event' or Detail has 'DHCP'
| project PreciseTimeStamp = FirstTimeStamp, Event="NMAgent", Message = strcat_delim(", ", LastTimeStamp, MACAddress, Detail)
)
| union (
LogRoleInstanceSnapshot
| where PreciseTimeStamp between (query_BeginTime .. query_EndTime)
| where Tenant =~ cluster
| where containerId == query_containerId
| summarize arg_min(PreciseTimeStamp, *) by roleInstanceName, creationTime, containerId, isExpectedToRun, provisioningState, roleState
| project PreciseTimeStamp, Event=strcat("RoleInstance: ", roleInstanceName),
    Message=strcat("creation ", creationTime, " isExpectedToRun ", isExpectedToRun, " provisioningState ", provisioningState, " roleState ", roleState)
)
| top 1000 by PreciseTimeStamp asc
```

**Params:** `{cluster}`, `{query_containerId}`, `{interfaceId}`, `{vmUniqueId}`, `{query_BeginTime}`, `{query_EndTime}`

**Signal filters seen in KQL:** `Detail == "Unblock Port Event"`

---
