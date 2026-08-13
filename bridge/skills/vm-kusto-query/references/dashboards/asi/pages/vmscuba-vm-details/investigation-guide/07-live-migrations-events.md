# Live Migrations Events

> Source: **VM Scuba - VM Details** dashboard, chapter **Live Migrations Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-LiveMigrationsEvents

_Widget purpose:_ Live Migrations Events

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `Live Migrations Events`

```kusto
let LiveMigrationSessionCreated= cluster("AzureCM").database("AzureCM").LiveMigrationSessionCreatedLog
| where sessionId == sessionId ;
let LiveMigrationSessionComplete =cluster("AzureCM").database("AzureCM").LiveMigrationSessionCompleteLog  
| where sessionId == sessionId ;
union 
LiveMigrationSessionCreated,LiveMigrationSessionComplete
```

**Params:** `{queryFrom}`, `{queryTo}`, `{sessionId}`

---
