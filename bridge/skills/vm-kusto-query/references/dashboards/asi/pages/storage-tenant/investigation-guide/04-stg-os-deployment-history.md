# STG OS Deployment History

> Source: **Storage Tenant Investigation Guide** dashboard, chapter **STG OS Deployment History** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Tenant STGOS Deployment History

_Widget purpose:_ STG OS Deployment History

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Table`
Source panel: `STG OS Deployment History`

```kusto
STGOSDeploymentHistory
| where StartDate > queryFrom
| where FinishDate < queryTo
| where Tenant == tenant
```

**Params:** `{queryFrom}`, `{queryTo}`, `{tenant}`

---
