# LCM Account Policy Execution Stats

> Source: **Life Cycle Management Investigation Guide** dashboard, chapter **LCM Account Policy Execution Stats** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### LCM Account Policy Execution Stats

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Table`
Source panel: `LCM Account Policy Execution Stats`

```kusto
ETWEventOLCMAccountPolicyExecutionStatsTable
| where TIMESTAMP between (queryFrom .. queryTo)
| where AccountName == trim(@"[\s]+", accountName) 
| project TIMESTAMP, ActivityId, AccountName, RowsScanned, DispatchTime, StartTime, 
SuccessActions = (ActionDeleteSucceededBlobs + ActionDownToArchiveSucceededBlobs + ActionDownToColdSucceededBlobs + ActionDownToCoolSucceededBlobs), 
FailedActions = (ActionDeleteFailedBlobs + ActionDownToArchiveFailedBlobs + ActionDownToColdFailedBlobs + ActionDownToCoolFailedBlobs)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{accountName}`

---
