# Tenant  SLA & UD Walk

> Source: **Aztec — Tenant** dashboard, chapter **Tenant  SLA & UD Walk** (5 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Tenant  SLA & UD Walk

### Tenant Change Profiling Events

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > Tenant Change Profiling Events`

```kusto
TMMgmtTenantChangeProfilingEventEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo) 
| where TenantName == queryTenantName
| project PreciseTimeStamp, Tenant, TenantID, TenantGeneration, CurrentUD, ChangeEventType, FromState, ToState, UserField, RoleName, RoleInstanceName, ContainerId, TimeSinceLastChange
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### Qury TMMgmtSlaMeasurementEventEtwTable

_Widget purpose:_ Tenant SLA Events - TMMgmtSlaMeasurementEventEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > Tenant SLA Events - TMMgmtSlaMeasurementEventEtwTable`

```kusto
TMMgmtSlaMeasurementEventEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, RoleInstanceName,ContainerID, NodeID, Tenant, Context, EntityState, Detail0, Region, TenantName, TenantID
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query TMMgmtHighLatencyUDWalkEtwTable

_Widget purpose:_ TMMgmtHighLatencyUDWalkEtwTable

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > TMMgmtHighLatencyUDWalkEtwTable`

```kusto
TMMgmtHighLatencyUDWalkEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, TenantName, UpgradeId, UpdateDomain, Duration, UserFriendlyMessage
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable

_Widget purpose:_ TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > UD Walk for IaaS > TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable`

```kusto
TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable

_Widget purpose:_ TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Tenant  SLA & UD Walk > Tenant  SLA & UD Walk > UD Walk for PaaS > TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable`

```kusto
TMMgmtTenantUDWalkRoleQuorumDetailsEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---
