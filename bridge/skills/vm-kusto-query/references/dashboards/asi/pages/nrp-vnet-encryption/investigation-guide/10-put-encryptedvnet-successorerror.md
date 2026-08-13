# Put EncryptedVnet SuccessOrError

> Source: **NRP - Vnet Encryption** dashboard, chapter **Put EncryptedVnet SuccessOrError** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### IfPutVnetWithEncryptionSucceeded

_Widget purpose:_ Put EncryptedVnet SuccessOrError

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Put EncryptedVnet SuccessOrError`

```kusto
let opidLst=WriteOperationResponseEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
// | where SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"
| where OperationName == "PutVirtualNetworkOperation"
| where Request contains ```"encryption":{"enabled":true,```
| distinct OperationId;
QosEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where OperationId in (opidLst)
| summarize count() by Success, ErrorCode, Region
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `SubscriptionId != "c51a6f0a-b599-46bc-8484-6cb32b0ac038"` · `OperationName == "PutVirtualNetworkOperation"`

---
