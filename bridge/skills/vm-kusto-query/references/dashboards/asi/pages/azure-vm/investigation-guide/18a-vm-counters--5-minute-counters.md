# VM Counters — 5 Minute Counters

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Counters** (1 queries, part 1 of 7).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## 5 Minute Counters

### Azure Host VM CPU Usage

_Widget purpose:_ VM Counters

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > 5 Minute Counters > 5 Minute Counters > VM Counters`

**Tables:** `VmCounterFiveMinuteRoleInstanceCentralBondTable`
**Output columns:** `PreciseTimeStamp`, `CounterName`, `AverageCounterValue`

```kusto
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (startTime .. endTime) and VmId == containerId
| project PreciseTimeStamp, CounterName, AverageCounterValue
```

**Params:** `{nodeId}`, `{containerId}`, `{startTime}`, `{endTime}`

---
