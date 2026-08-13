# Jobs

> Source: **Aztec — Tenant** dashboard, chapter **Jobs** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Jobs

### Query TMMgmtMRJobSnapshotEtwTable

_Widget purpose:_ TMMgmtMRJobSnapshotEtwTable

Cluster: `Azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Jobs > Jobs > TMMgmtMRJobSnapshotEtwTable`

```kusto
TMMgmtMRJobSnapshotEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where TenantName == queryTenantName
| project PreciseTimeStamp, Tenant, JobId, TenantName, JobCreationTime, JobType, CurrentStepName, 
  JobStatus, IsManagementRoleEnabled, ArbitratorType, FilterResult, AffectedResourceImpact, AffectedResourceImpactPerRole
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Tenant Job Info

_Widget purpose:_ TMMgmtTenantManagementJobInfoEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Jobs > Jobs > TMMgmtTenantManagementJobInfoEtwTable`

```kusto
TMMgmtTenantManagementJobInfoEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where TenantName == queryTenantName
| project PreciseTimeStamp, Tenant, Context, JobID, JobType, JobStatus, Message , ResponsibleTeam
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---
