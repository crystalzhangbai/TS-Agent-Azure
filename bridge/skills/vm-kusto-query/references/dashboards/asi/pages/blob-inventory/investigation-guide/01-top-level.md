# (top-level)

> Source: **Blob Inventory Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Tenant Info by Account

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Single` · Widget: `CompoundWidgetContainer`

```kusto
XStoreAccountPropertiesHourly()
| where TimePeriod > ago(3d)
| where Account startswith strcat(trim(@"[\s]+", accountName),";")
| order by TimePeriod desc 
| take 1
| project Tenant, Subscription
// if Account not found, retuns empty Tenant instead of ASI error
| union (        
    print Tenant=""
)
| sort by Tenant nulls last
| limit 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{accountName}`

---
