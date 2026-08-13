# Transactions by Request Type

> Source: **Storage Account Investigation Guide** dashboard, chapter **Transactions by Request Type** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Storage Account Transactions By RequestType

_Widget purpose:_ Transactions by Request Type

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xdataanalytics` · Type: `CategoryChart`
Source panel: `Transactions by Request Type`

```kusto
AccountTransactionsDaily
| where TimePeriod >= queryFrom and TimePeriod < queryTo
| where AccountName startswith trim(@"[\s]+", accountName)
| where TransactionType == "user"
| where RequestType !in ("XBlobFE_All", "XFileFE_All", "XQueueFE_All", "XTableFE_All")
| extend TotalIngressInGB = TotalIngress / (1024 * 1024 * 1024)
| extend TotalEgressInGB = TotalEgress / (1024 * 1024 * 1024)
| project TimePeriod, AccountName, Tenant, RequestType, TransactionType, TransactionCount, BillableTransactionCount, TotalEgressInGB, TotalIngressInGB
| summarize sum(TransactionCount), sum(BillableTransactionCount) by RequestType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{accountName}`

**Signal filters seen in KQL:** `TransactionType == "user"`

---
