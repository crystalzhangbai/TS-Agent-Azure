# Top 5 error stacks

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Top 5 error stacks** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssFailureErrorCodes

_Widget purpose:_ Top 5 error stacks

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Top 5 error stacks`

```kusto
QosEtwEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subId
| where Success == false
| where OperationName == "PutVMScaleSetOperation"
| extend ErrorDetails = substring(ErrorDetails, 0, 200)
| summarize count() by ErrorCode, ErrorDetails
| order by count_ desc 
| take 5
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"`

---
