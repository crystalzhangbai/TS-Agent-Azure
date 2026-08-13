# Put Vmss operation failures

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Put Vmss operation failures** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssFailuresPerSub

_Widget purpose:_ Put Vmss operation failures

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Put Vmss operation failures`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where OperationName == "PutVMScaleSetOperation"
| where Success == false
| where SubscriptionId == subId
| extend usererr = iff (UserError == true, 1, 0)
| extend servererror = iff(UserError == false, 1, 0)
| summarize IsUserError = sum(usererr), ServerError = sum(servererror) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"`

---
