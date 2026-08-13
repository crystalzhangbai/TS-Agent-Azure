# High CPU

> Source: **Aztec Nodes Investigation Guide** dashboard, chapter **High CPU** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## High CPU

### Node High CPU

_Widget purpose:_ High CPU

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `High CPU > High CPU`

```kusto
HighCpuCounterNodeTable
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where NodeId == queryNodeId
| summarize Count = max(CounterValue) by CounterName, bin(PreciseTimeStamp, 15m)
| extend CounterName = replace("\\\\Hyper-V Hypervisor Root ", "", CounterName)
| project PreciseTimeStamp, CounterName, Count
```

**Params:** `{queryNodeId}`

---
