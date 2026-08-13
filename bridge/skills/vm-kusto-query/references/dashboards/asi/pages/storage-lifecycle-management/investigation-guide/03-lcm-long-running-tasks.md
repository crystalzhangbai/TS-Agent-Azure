# LCM Long Running Tasks

> Source: **Life Cycle Management Investigation Guide** dashboard, chapter **LCM Long Running Tasks** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### LCM Long Running Task Stats

_Widget purpose:_ LCM Long Running Tasks

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Table`
Source panel: `LCM Long Running Tasks`

```kusto
ETWEventOLCMSchedulerLongRunningTasksStatsTable
| where TIMESTAMP between (queryFrom .. queryTo)
| where AccountName == trim(@"[\s]+", accountName)
| project TIMESTAMP, Tenant, RoleInstance, ActivityId, AccountName, Action, Reason, RowKey
```

**Params:** `{queryFrom}`, `{queryTo}`, `{accountName}`

---
