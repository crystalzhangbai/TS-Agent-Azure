# (top-level)

> Source: **EEE Storage - xstore transaction resource 01** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "xstore transaction resource 01"

Cluster: `xstore.kusto.windows.net` · Database: `xdataanalytics` · Type: `ResourceGet` · Widget: `Container`

```kusto
XStoreAccountTransactionsDaily
| where TimePeriod between (globalFrom .. globalTo )
| where Account startswith local_Account
```

**Params:** `{local_Account}`, `{globalFrom}`, `{globalTo}`

---

### xstore transaction hourly table 01

Cluster: `xstore.kusto.windows.net` · Database: `xdataanalytics` · Type: `Table`

```kusto
XStoreAccountTransactionsDaily
| where TimePeriod between (queryFrom .. queryTo)
| where Account startswith local_account
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_account}`

---
