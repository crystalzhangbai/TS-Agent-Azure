# (top-level)

> Source: **Aztec — Tenant** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Tenants"

_Widget purpose:_ Tenant {{tenantName}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogTenantSnapshot
| where PreciseTimeStamp between (globalFrom .. globalTo)
| where tenantName == local_tenantName
| summarize arg_max(PreciseTimeStamp, *) by tenantName
| extend CreationDate = todatetime(dateCreated)
| extend serviceInstancesDetailsDynamic = parse_json(serviceInstancesDetails)
```

**Params:** `{local_tenantName}`, `{globalFrom}`, `{globalTo}`

---

### Tenant Features

_Widget purpose:_ Tenant {{tenantName}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `FeatureList` · Widget: `Container`

```kusto
LogTenantSnapshot 
| where tenantName == queryTenantName
| top 1 by PreciseTimeStamp desc
| project isSpannable, isCreatedViaReserveActivate, isSpanned, isAzPEEnabled, hasManagementRole
| project features = pack(
    "MR Enabled", iif(tobool(hasManagementRole), "Enabled", "Disabled"),
    "Spannable", iif(tobool(isSpannable), "Enabled", "Disabled"), 
    "CreatedViaReserveActivate", iif(tobool(isCreatedViaReserveActivate), "Enabled", "Disabled"), 
    "Spanned", iif(tobool(isSpanned), "Enabled", "Disabled"), 
    "AzPE Enabled", iif(tobool(isAzPEEnabled), "Enabled", "Disabled"))    
| mv-expand bagexpansion=array features
| project FeatureName = tostring(features[0]), State = tostring(features[1])
```

**Params:** `{queryTenantName}`

---

### Tenant AzSM Features

_Widget purpose:_ Tenant {{tenantName}}

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `FeatureList` · Widget: `Container`

```kusto
AzSMTenantSnapshotV2
| where tenantName == queryTenantName
| top 1 by PreciseTimeStamp desc
| extend isAzSmTenant = tenantOwners contains "AzSM"
| project isAzPEEnabledTenant, isCreatedViaReserveActivate, isPreprovisionedTenant, isServiceHealingPending, isSlbV2Tenant, isTenantOnDedicatedHost
| project features = pack(
    "AzPEEnabledTenant", iif(tobool(isAzPEEnabledTenant), "Enabled", "Disabled"), 
    "CreatedViaReserveActivate", iif(tobool(isCreatedViaReserveActivate), "Enabled", "Disabled"), 
    "PreprovisionedTenant", iif(tobool(isPreprovisionedTenant), "Enabled", "Disabled"), 
    "ServiceHealingPending", iif(tobool(isServiceHealingPending), "Enabled", "Disabled"),
    "SlbV2Tenant", iif(tobool(isSlbV2Tenant), "Enabled", "Disabled"),
    "TenantOnDedicatedHost", iif(tobool(isTenantOnDedicatedHost), "Enabled", "Disabled"))
| mv-expand bagexpansion=array features
| project FeatureName = tostring(features[0]), State = tostring(features[1])
```

**Params:** `{queryTenantName}`

---
