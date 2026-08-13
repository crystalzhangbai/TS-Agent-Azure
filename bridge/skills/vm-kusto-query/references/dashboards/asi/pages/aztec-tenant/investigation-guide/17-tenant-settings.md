# Tenant Settings

> Source: **Aztec — Tenant** dashboard, chapter **Tenant Settings** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## AzPETenantSettingsSnapshot 

### Query AzPETenantSettingsSnapshot

_Widget purpose:_ AzPETenantSettingsSnapshot 

Cluster: `Azpe` · Database: `Azpe` · Type: `Table`
Source panel: `Tenant Settings > AzPETenantSettingsSnapshot `

```kusto
AzPETenantSettingsSnapshot
| where PreciseTimeStamp between (min_of(queryFrom, datetime_add('day',-1, queryTo)) .. queryTo)
| where TenantName == queryTenantName
| summarize arg_max(PreciseTimeStamp, *) by Name
| project PreciseTimeStamp, Name, Value
| order by Name asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

## LogTenantOverridableSettingsSnapshot

### Query LogTenantOverridableSettingsSnapshot

_Widget purpose:_ LogTenantOverridableSettingsSnapshot

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Tenant Settings > LogTenantOverridableSettingsSnapshot`

```kusto
LogTenantOverridableSettingsSnapshot
| where PreciseTimeStamp between (min_of(queryFrom, datetime_add('day',-1,queryTo)) .. queryTo)
| where tenantName == queryTenantName
| summarize arg_max(PreciseTimeStamp, *) by name
| project PreciseTimeStamp, name, value
| order by name asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---
