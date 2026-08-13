# Account Billing Daily

> Source: **Storage Billing Drilldown Investigation Guide** dashboard, chapter **Account Billing Daily** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### List Account Billing Daily

_Widget purpose:_ Account Billing Daily

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xdataanalytics` · Type: `Table`
Source panel: `Account Billing Daily`

```kusto
XStoreAccountBillingDaily 
| where TimePeriod between (startofweek(queryFrom) .. queryTo)
| where AccountName startswith strcat(trim(@"[\s]+", storageAccountName), ";")
| where isempty(meterId) or MeterId == meterId
| project TimePeriod, AccountName, StgMeterName, MeterId, Quantity, ProratedQuantity
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`, `{meterId}`

---
