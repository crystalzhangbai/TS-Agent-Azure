# PutVmss sub lock duration for Peregrine vmss downscale

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **PutVmss sub lock duration for Peregrine vmss downscale** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssSubLockPeregrineVmssScaleDown

_Widget purpose:_ PutVmss sub lock duration for Peregrine vmss downscale

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `PutVmss sub lock duration for Peregrine vmss downscale`

```kusto
let psd= FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom.. queryTo)
| where Region == region
| where OperationName == "PutVMScaleSetOperation"
| extend isPeregrineScaleDown = iff(Message startswith "VMSS on Peregrine is getting scaled down", 1,0)
| where isPeregrineScaleDown  == 1
| distinct OperationId;
let regex="Operation (.+) \\((.+)\\) released lock (.+) after (\\d+) ms";
FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom.. queryTo)
| where Region == region
| where OperationId in (psd)
| where EventCode == "LockReleased"
| extend LockName=extract(regex, 3, Message)
| extend LockDuration=toint(extract(regex, 4, Message))
| where LockName == SubscriptionId
| summarize sum(LockDuration) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"` · `EventCode == "LockReleased"`

---
