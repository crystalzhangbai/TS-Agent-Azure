# Put Vmss top 5 errors 

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Put Vmss top 5 errors ** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssFailurePerRegion

_Widget purpose:_ Put Vmss top 5 errors 

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Put Vmss top 5 errors `

```kusto
QosEtwEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where Region == region
| where Success == false
| where OperationName == "PutVMScaleSetOperation"
| where SliceNum( SourceAssemblyFileVersion) < 10
| where ErrorCode != "RedirectToNetworkSubscriptionRequired"
| extend ErrorDetails = substring(ErrorDetails, 0, 300)
| summarize count() by ErrorCode, ErrorDetails
| order by count_ desc 
| take 5
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"` · `ErrorCode != "RedirectToNetworkSubscriptionRequired"`

---
