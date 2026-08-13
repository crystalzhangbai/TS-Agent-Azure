# VM Charts

> Source: **Azure VM Compare Investigation Guide** dashboard, chapter **VM Charts** (3 queries across 3 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Guest CPU Counters (30 seconds)

### Azure VM MetricsPerContainer

_Widget purpose:_ Guest CPU Counters (30 seconds)

Cluster: `intmgmtshared.centralus.kusto.windows.net` · Database: `Fleet` · Type: `TimeSeries`
Source panel: `VM Charts > Guest CPU Counters (30 seconds)`

```kusto
MetricsPerContainer
| where PreciseTimestamp between (queryFrom .. queryTo) and ContainerId == containerId
| project-away Timestamp, NodeId, ContainerId, BlobOffset
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

## VM 5 Min Counters for {{containerId1}}

### Azure Host VM CPU Usage

_Widget purpose:_ VM 5 Min Counters for {{containerId1}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Charts > VM 5 Min Counters for {{containerId1}}`

```kusto
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (startTime .. endTime) and VmId == containerId
| project PreciseTimeStamp, CounterName, AverageCounterValue
```

**Params:** `{nodeId}`, `{containerId}`, `{startTime}`, `{endTime}`

---

## VM 5 Min Counters for {{containerId2}}

### Azure Host VM CPU Usage

_Widget purpose:_ VM 5 Min Counters for {{containerId2}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Charts > VM 5 Min Counters for {{containerId2}}`

```kusto
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (startTime .. endTime) and VmId == containerId
| project PreciseTimeStamp, CounterName, AverageCounterValue
```

**Params:** `{nodeId}`, `{containerId}`, `{startTime}`, `{endTime}`

---
