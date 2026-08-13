# MDM Dashboards

> Source: **Storage Account Investigation Guide** dashboard, chapter **MDM Dashboards** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## MDM Dashboards

### Get Account Tenant Info

_Widget purpose:_ MDM Dashboards

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Single` · Widget: `Card`
Source panel: `MDM Dashboards > MDM Dashboards`

```kusto
GetTenantCatalogLatest()
| where Tenant == tenant
| project Tenant, MDMShoeboxAccountName,MonitoringGcsStorageResourceTagValue,GeoRegion,RsrpName
// if Tenant not found, retuns empty results, instead of ASI exception
| union (       
    print MDMShoeboxAccountName="", MonitoringGcsStorageResourceTagValue="",GeoRegion="",RsrpName=""
)
| sort by Tenant nulls last
| limit 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{tenant}`

---

### UnixTimeFormat_Converter

_Widget purpose:_ MDM Dashboards

Cluster: `azcore.centralus` · Database: `Xstore` · Type: `Single` · Widget: `Card`
Source panel: `MDM Dashboards > MDM Dashboards`

```kusto
// Any cluster / Database can be used - using the same as to get Redis details - azcore.centralus / Xstore
let unixTime_queryFrom = datetime_diff('millisecond', queryFrom, datetime(1970-01-01));
let unixTime_queryTo = datetime_diff('millisecond', queryTo, datetime(1970-01-01));
print unixTime_queryFrom=unixTime_queryFrom, unixTime_queryTo=unixTime_queryTo;
```

**Params:** `{queryFrom}`, `{queryTo}`

---
