# Guest Perf Counters

> Source: **Azure Host - Azure VM** dashboard, chapter **Guest Perf Counters** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Guest Perf Counters (only for Host Storage Test Windows VMs)

### Azure Host VM HostStorage Guest Counters

_Widget purpose:_ Guest Perf Counters (only for Host Storage Test Windows VMs)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Sc` · Type: `TimeSeries`
Source panel: `Guest Perf Counters > Guest Perf Counters (only for Host Storage Test Windows VMs)`

**Tables:** `CounterTable`
**Output columns:** `PreciseTimeStamp`, `CounterName`, `CounterValue`

```kusto
CounterTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and RoleInstance == containerId
| project PreciseTimeStamp, CounterName, CounterValue
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
