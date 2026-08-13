# AzSM

> Source: **Aztec — Tenant** dashboard, chapter **AzSM** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Tenant AzSM Application

_Widget purpose:_ AzSM

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Single` · Widget: `Card`
Source panel: `AzSM`

```kusto
let from = datetime_add("day", -1, queryTenantTimestamp);
let too = datetime_add("day", 1, queryTenantTimestamp);
AzSMTenantSnapshotV2
| where PreciseTimeStamp between(from..too)
| where tenantName == queryTenantName
| top 1 by PreciseTimeStamp desc
| project Cluster, applicationName
```

**Params:** `{queryTenantName}`, `{queryTenantTimestamp}`

---
