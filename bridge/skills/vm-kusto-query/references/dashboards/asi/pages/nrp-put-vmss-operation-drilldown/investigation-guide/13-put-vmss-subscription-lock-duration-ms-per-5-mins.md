# Put Vmss subscription lock duration (ms) per 5 mins

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Put Vmss subscription lock duration (ms) per 5 mins** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssSubLockPerSub

_Widget purpose:_ Put Vmss subscription lock duration (ms) per 5 mins

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Put Vmss subscription lock duration (ms) per 5 mins`

```kusto
let regex="Operation (.+) \\((.+)\\) released lock (.+) after (\\d+) ms";
FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName in ("PutVMScaleSetOperation")
| where EventCode == "LockReleased"
| extend LockName=extract(regex, 3, Message)
| extend LockDuration=toint(extract(regex, 4, Message))
| where LockName == subId
| summarize SubLockDuration = sum(LockDuration) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

**Signal filters seen in KQL:** `EventCode == "LockReleased"`

---
