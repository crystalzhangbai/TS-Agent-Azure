# (top-level)

> Source: **Serial Console Home** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Portal Image Tag 

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `Table`

```kusto
PortalActivity
| where ['time'] > queryFrom
| where ['time'] < queryTo
| summarize dcount(sessionId), dcount(RPTenant) by portalVersion
```

**Params:** `{queryFrom}`, `{queryTo}`

---
