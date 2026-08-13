# Runner Sub Failure in CRP logs

> Source: **NRP - Vnet Encryption** dashboard, chapter **Runner Sub Failure in CRP logs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### runnerErrorInCRP

_Widget purpose:_ Runner Sub Failure in CRP logs

Cluster: `https://azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `Table`
Source panel: `Runner Sub Failure in CRP logs`

```kusto
ApiQosEvent
| where (TIMESTAMP > startTime and TIMESTAMP < endTime)
| where subscriptionId == "c51a6f0a-b599-46bc-8484-6cb32b0ac038"
| where (resourceGroupName contains "NrpCreateVM" and resourceGroupName contains "encrypted") or resourceGroupName contains "encryption"
| where operationName !contains "get" and operationName !contains "delete"
| where errorDetails != ""
| project region, resourceGroupName, operationName, operationId, resultCode, errorDetails
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `subscriptionId == "c51a6f0a-b599-46bc-8484-6cb32b0ac038"`

---
