# Avg Time Taken To Read VNet

> Source: **NRP - Vnet Encryption** dashboard, chapter **Avg Time Taken To Read VNet** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Avg Time Taken To Read VNet

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Avg Time Taken To Read VNet`

```kusto
let operationName = "GetTenantClustersOperation"; 
FrontendOperationEtwEvent 
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
// | where SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"
| where OperationName == operationName 
| where Message contains "Reading the vnet encryption status took"
| parse Message with "Reading the vnet encryption status took " readTime " ms"
| extend readTime = toint(readTime)
| summarize avgReadTime = avgif(readTime, readTime > 0) by bin(PreciseTimeStamp, 1h)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"` · `Message contains "Reading the vnet encryption status took"`

---
