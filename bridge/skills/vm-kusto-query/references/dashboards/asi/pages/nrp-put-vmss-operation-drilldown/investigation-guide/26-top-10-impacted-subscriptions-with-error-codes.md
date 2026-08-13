# Top 10 impacted subscriptions with error codes

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Top 10 impacted subscriptions with error codes** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssFailuresTopSubs

_Widget purpose:_ Top 10 impacted subscriptions with error codes

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Top 10 impacted subscriptions with error codes`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region == region
| where OperationName == "PutVMScaleSetOperation"
| where Success == false
| where SliceNum( SourceAssemblyFileVersion) < 10
| where ErrorCode != "RedirectToNetworkSubscriptionRequired"
| extend ErrorDetails = substring(ErrorDetails,0, 350)
| summarize count() by SubscriptionId, ErrorCode, ErrorDetails
| order by count_ desc 
| take 10
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"` · `ErrorCode != "RedirectToNetworkSubscriptionRequired"`

---
