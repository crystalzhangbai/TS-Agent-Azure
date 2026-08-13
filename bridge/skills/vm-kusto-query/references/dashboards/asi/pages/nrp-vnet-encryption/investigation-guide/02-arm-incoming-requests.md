# ARM Incoming Requests

> Source: **NRP - Vnet Encryption** dashboard, chapter **ARM Incoming Requests** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ARM Incoming Requests

Cluster: `https://armprod.kusto.windows.net` · Database: `ARMProd` · Type: `Table`
Source panel: `ARM Incoming Requests`

```kusto
HttpIncomingRequests
| where (TIMESTAMP > startTime and TIMESTAMP < endTime)
| where subscriptionId == "c51a6f0a-b599-46bc-8484-6cb32b0ac038"
//| where (targetUri contains "NrpCreateVM" and targetUri contains "encrypted") or targetUri contains "encryption"
| where operationName !contains "get" and operationName !contains "delete"
| where durationInMilliseconds > 1
| project correlationId, operationName, targetUri, durationInMilliseconds, httpStatusCode, targetResourceProvider
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `subscriptionId == "c51a6f0a-b599-46bc-8484-6cb32b0ac038"`

---
