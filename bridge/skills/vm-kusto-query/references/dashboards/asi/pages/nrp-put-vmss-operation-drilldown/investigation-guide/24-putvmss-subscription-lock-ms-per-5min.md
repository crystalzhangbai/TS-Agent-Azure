# PutVmss subscription lock ms (per 5min)

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **PutVmss subscription lock ms (per 5min)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssSubLockPerResource

_Widget purpose:_ PutVmss subscription lock ms (per 5min)

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `PutVmss subscription lock ms (per 5min)`

```kusto
let regex="Operation (.+) \\((.+)\\) released lock (.+) after (\\d+) ms";
FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName in ("PutVMScaleSetOperation")
| where ResourceGroup =~ resourceGroup and ResourceName =~ resourceName
| where EventCode == "LockReleased"
| extend LockName=extract(regex, 3, Message)
| extend LockDuration=toint(extract(regex, 4, Message))
| where LockName == subId
| summarize SubLockDuration = sum(LockDuration) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`, `{resourceGroup}`, `{resourceName}`

**Signal filters seen in KQL:** `EventCode == "LockReleased"`

---
