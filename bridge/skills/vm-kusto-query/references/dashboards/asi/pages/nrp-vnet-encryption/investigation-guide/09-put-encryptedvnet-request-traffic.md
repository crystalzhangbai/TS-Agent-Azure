# Put EncryptedVnet Request Traffic

> Source: **NRP - Vnet Encryption** dashboard, chapter **Put EncryptedVnet Request Traffic** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### put vnet traffic

_Widget purpose:_ Put EncryptedVnet Request Traffic

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Put EncryptedVnet Request Traffic`

```kusto
WriteOperationResponseEtwEvent
    | where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
    // | where SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"
    | where OperationName == "PutVirtualNetworkOperation"
    | where Request contains ```"encryption":{"enabled":true,```
    | summarize count() by bin(PreciseTimeStamp, 1h), Region
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"` · `OperationName == "PutVirtualNetworkOperation"`

---
