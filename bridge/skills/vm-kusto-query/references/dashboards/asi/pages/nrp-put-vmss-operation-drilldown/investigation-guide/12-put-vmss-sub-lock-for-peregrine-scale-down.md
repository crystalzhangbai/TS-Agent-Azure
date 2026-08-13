# Put Vmss sub lock for Peregrine scale down

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Put Vmss sub lock for Peregrine scale down** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssSubLockPeregrineScaleDownPerSub

_Widget purpose:_ Put Vmss sub lock for Peregrine scale down

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Put Vmss sub lock for Peregrine scale down`

```kusto
let psd= FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom.. queryTo)
| where Region == region
| where SubscriptionId == subId
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

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"` · `EventCode == "LockReleased"`

---
