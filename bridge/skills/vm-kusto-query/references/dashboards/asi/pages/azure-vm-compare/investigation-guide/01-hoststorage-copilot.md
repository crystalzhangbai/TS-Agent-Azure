# HostStorage CoPilot

> Source: **Azure VM Compare Investigation Guide** dashboard, chapter **HostStorage CoPilot** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Summary for {{containerId1}}

### Container_Insights_Summary

_Widget purpose:_ Summary for {{containerId1}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `sc` · Type: `Single` · Widget: `Markdown`
Source panel: `HostStorage CoPilot > Summary for {{containerId1}}`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Sc').SummarizeContainerInsights(startTime, endTime, containerId, nodeId)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

## Summary for {{containerId2}}

### Container_Insights_Summary

_Widget purpose:_ Summary for {{containerId2}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `sc` · Type: `Single` · Widget: `Markdown`
Source panel: `HostStorage CoPilot > Summary for {{containerId2}}`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Sc').SummarizeContainerInsights(startTime, endTime, containerId, nodeId)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---
