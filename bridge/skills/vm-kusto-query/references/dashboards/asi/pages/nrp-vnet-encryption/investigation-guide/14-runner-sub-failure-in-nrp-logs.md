# Runner Sub Failure in NRP logs

> Source: **NRP - Vnet Encryption** dashboard, chapter **Runner Sub Failure in NRP logs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### runner sub 

_Widget purpose:_ Runner Sub Failure in NRP logs

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Runner Sub Failure in NRP logs`

```kusto
QosEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == "c51a6f0a-b599-46bc-8484-6cb32b0ac038"
| where OperationName !contains "get" and OperationName !contains "delete"
| where Success == 0 
| where ErrorCode != "RetryableError" and ErrorCode != "TaskCanceled"
| project Region, OperationName, ResourceGroup, CorrelationRequestId, OperationId, ErrorCode, ErrorDetails
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `SubscriptionId == "c51a6f0a-b599-46bc-8484-6cb32b0ac038"` · `ErrorCode != "RetryableError"`

---
