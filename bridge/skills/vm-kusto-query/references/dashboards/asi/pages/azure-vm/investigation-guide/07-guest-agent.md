# Guest Agent

> Source: **Azure Host - Azure VM** dashboard, chapter **Guest Agent** (4 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Events

### Azure Host VM Guest Agent Events

_Widget purpose:_ Guest Agent Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Guest Agent > Events > Events > Guest Agent Events`

**Tables:** `GuestAgentExtensionEvents`

```kusto
GuestAgentExtensionEvents
| where PreciseTimeStamp between (startTime .. endTime) 
| where ContainerId == containerId and Operation !in ("HeartBeat", "Firewall")
| where qIncludeSummary or Operation != 'VmSettingsSummary'
| extend OperationSuccess = tobool(OperationSuccess)
| extend level = iff(OperationSuccess == false, 'error', '')
| project 
    PreciseTimeStamp, NodeId, VMId, ContainerId, NodeIdentity, OSVersion, TenantName, Name, Version, level,
    Operation, OperationSuccess, Message, Duration, TaskName, ResourceGroupName, RoleName, RoleInstanceName
| order by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{qIncludeSummary}`

---

## Generic Logs

### Azure Host VM Guest Agent Generic Logs

_Widget purpose:_ Guest Agent Generic Logs

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Guest Agent > Generic Logs > Generic Logs > Guest Agent Generic Logs`

**Tables:** `GuestAgentGenericLogs`
**Output columns:** `PreciseTimeStamp`, `Level`, `GAVersion`, `EventName`, `CapabilityUsed`, `Context1`, `Context2`, `Context3`

```kusto
GuestAgentGenericLogs
| where PreciseTimeStamp between (startTime .. endTime) and ContainerId == containerId
| where TaskName !startswith 'AKS.Runtime.memory_telemetry'
| project PreciseTimeStamp, Level, GAVersion, EventName, CapabilityUsed, Context1, Context2, Context3
| order by PreciseTimeStamp desc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

## Perf Counter

### Azure Host VM Guest Agent Perf Counters

_Widget purpose:_ Performance Counters

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Guest Agent > Perf Counter > Perf Counter > Performance Counters`

**Tables:** `GuestAgentPerformanceCounterEvents`
**Output columns:** `PreciseTimeStamp`, `Processors`, `RAM`, `GAVersion`, `OSVersion`, `Category`, `Counter`, `Value`

```kusto
GuestAgentPerformanceCounterEvents
| where PreciseTimeStamp between (startTime .. endTime) and ContainerId == containerId
| project PreciseTimeStamp, Processors, RAM, GAVersion, OSVersion, Category, Counter, Value
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

## Perf Counter Chart

### GuestAgentPerformanceCounterEvents

_Widget purpose:_ Performance Counter

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Guest Agent > Perf Counter Chart > Performance Counter`

**Tables:** `GuestAgentPerformanceCounterEvents`
**Output columns:** `PreciseTimeStamp`, `CounterName`, `Value`

```kusto
GuestAgentPerformanceCounterEvents
| where PreciseTimeStamp between (startTime .. endTime) and ContainerId == containerId
| project PreciseTimeStamp, CounterName = strcat(Category, "-", Instance, "-", Counter), Value
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---
