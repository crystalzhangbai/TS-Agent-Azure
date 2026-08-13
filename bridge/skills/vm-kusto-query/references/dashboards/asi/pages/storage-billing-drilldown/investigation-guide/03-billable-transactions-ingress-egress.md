# Billable Transactions, Ingress & Egress

> Source: **Storage Billing Drilldown Investigation Guide** dashboard, chapter **Billable Transactions, Ingress & Egress** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Account Billable Transactions

_Widget purpose:_ Billable Transactions, Ingress & Egress

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xdataanalytics` · Type: `TimeSeries`
Source panel: `Billable Transactions, Ingress & Egress`

```kusto
let accountName = storageAccountName;
AccountTransactionsDaily
| where TimePeriod between (startofweek(queryFrom) .. queryTo)
| where AccountName startswith strcat(trim(@"[\s]+", accountName), ";")
| where TransactionType == "user"
| where RequestType !in ("XBlobFE_All", "XFileFE_All", "XQueueFE_All", "XTableFE_All")
| extend BillableEgressInMB = BillableEgress / (1024 * 1024)
| extend BillableIngressInMB = BillableIngress / (1024 * 1024)
| project TimePeriod, AccountName, Tenant, RequestType, TransactionType, TransactionCount, BillableTransactionCount, BillableEgressInMB, BillableIngressInMB, BillableEgress, BillableIngress
| summarize sum(BillableTransactionCount), sum(BillableEgressInMB), sum(BillableIngressInMB) by TimePeriod
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`

**Signal filters seen in KQL:** `TransactionType == "user"`

---
