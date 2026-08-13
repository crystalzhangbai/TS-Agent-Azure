# PutVmss sub lock duration (ms) by region

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **PutVmss sub lock duration (ms) by region** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssSubLockPerRegion

_Widget purpose:_ PutVmss sub lock duration (ms) by region

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `PutVmss sub lock duration (ms) by region`

```kusto
let regex="Operation (.+) \\((.+)\\) released lock (.+) after (\\d+) ms";
FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo )
| where Region == region
| where OperationName in ("PutVMScaleSetOperation")
| where EventCode == "LockReleased"
| extend LockName=extract(regex, 3, Message)
| extend LockDuration=toint(extract(regex, 4, Message))
| where LockName == SubscriptionId
| summarize SubLockDuration = sum(LockDuration) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

**Signal filters seen in KQL:** `EventCode == "LockReleased"`

---
