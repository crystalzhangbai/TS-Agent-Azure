# HostStorage CoPilot

> Source: **Azure Host Compare Investigation Guide** dashboard, chapter **HostStorage CoPilot** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### node_insights_summary

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `sc` · Type: `Single` · Widget: `Column`
Source panel: `HostStorage CoPilot`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Sc').SummarizeNodeInsights(startTime, endTime, nodeId)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---
