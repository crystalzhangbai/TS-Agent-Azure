# Quick Links

> Source: **Life Cycle Management Investigation Guide** dashboard, chapter **Quick Links** (3 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Tenant Info by Account

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Single` · Widget: `CompoundWidgetContainer`
Source panel: `Quick Links`

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

## Pages - Storage Tools

### Get Tenant Info by Account

_Widget purpose:_ Pages - Storage Tools

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Single` · Widget: `Card`
Source panel: `Quick Links > Pages - Storage Tools`

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

### TrimStorageName

_Widget purpose:_ Pages - Storage Tools

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Single` · Widget: `Card`
Source panel: `Quick Links > Pages - Storage Tools`

```kusto
let trimmed_StorageName = trim(@"[\s]+", local_StorageNameName);
print StorageName = trimmed_StorageName ;
```

**Params:** `{local_StorageNameName}`

---
