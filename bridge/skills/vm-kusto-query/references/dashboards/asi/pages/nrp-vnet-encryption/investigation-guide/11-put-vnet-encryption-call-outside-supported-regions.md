# Put Vnet Encryption Call Outside Supported Regions

> Source: **NRP - Vnet Encryption** dashboard, chapter **Put Vnet Encryption Call Outside Supported Regions** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### callOutsideSupportedRegions

_Widget purpose:_ Put Vnet Encryption Call Outside Supported Regions

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Put Vnet Encryption Call Outside Supported Regions`

```kusto
let regions = dynamic(["uswestcentral", "usnorth", "uscentraleuap", "useast2euap", "useast2", "uswest2"]); 
QosEtwEvent 
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where Region !in (regions) 
| where OperationId in (
( WriteOperationResponseEtwEvent 
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where Region !in (regions) 
| where OperationName == "PutVirtualNetworkOperation" 
| where Request contains ```"encryption":{"enabled":true``` 
| project OperationId )
) 
| summarize count() by bin(PreciseTimeStamp, 1h), Region, Success, ErrorCode, SourceAssemblyFileVersion, SubscriptionId
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "PutVirtualNetworkOperation"`

---
