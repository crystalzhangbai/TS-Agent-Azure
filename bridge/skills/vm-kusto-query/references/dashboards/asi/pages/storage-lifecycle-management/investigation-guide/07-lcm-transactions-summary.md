# LCM Transactions Summary

> Source: **Life Cycle Management Investigation Guide** dashboard, chapter **LCM Transactions Summary** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get LCM Transactions

_Widget purpose:_ LCM Transactions Summary

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xdataanalytics` · Type: `Table`
Source panel: `LCM Transactions Summary`

```kusto
XStoreAccountTransactionsHourly
| where TimePeriod between (queryFrom .. queryTo)
| where Account contains strcat(trim(@"[\s]+", storageAccountName),";") and TransactionType == "lcmservice"
| summarize sum(BillableTransactionCount),sum(TransactionCount), sum(TotalSuccessCount), sum(TotalIngress), sum(TotalEgress) by RequestType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`

---
