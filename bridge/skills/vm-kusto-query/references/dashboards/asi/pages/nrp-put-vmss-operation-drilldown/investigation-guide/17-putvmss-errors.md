# PutVmss errors

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **PutVmss errors** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssFailuresPerVmss

_Widget purpose:_ PutVmss errors

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `PutVmss errors`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where OperationName == "PutVMScaleSetOperation"
| where Success == false
| where SubscriptionId == subId
| where ResourceGroup =~ resourceGroup and ResourceName =~ resourceName
| extend usererr = iff (UserError == true, 1, 0)
| extend servererror = iff(UserError == false, 1, 0)
| summarize IsUserError = sum(usererr), ServerError = sum(servererror) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`, `{region}`, `{resourceGroup}`, `{resourceName}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"`

---
