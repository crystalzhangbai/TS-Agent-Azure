# Insights

> Source: **Azure Host — Azure Host Node** dashboard, chapter **Insights** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Host Insights Summary

### node_insights_summary

_Widget purpose:_ Host Insights Summary

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `sc` · Type: `Single` · Widget: `Tab`
Source panel: `Insights > Host Insights Summary`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Sc').SummarizeNodeInsights(startTime, endTime, nodeId)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Other

### Azure Host Azure Core RCA

_Widget purpose:_ Azure Core RCA

Cluster: `moseisley` · Database: `Air` · Type: `Table`
Source panel: `Insights > Other > Azure Core RCA`

```kusto
GetAzureCoreRCAForNode(startTime, nodeId)
| project TimeStamp, RCAConfidence, ResourceId, RCALevel1, RCALevel2, RCALevel3, EscalateTo
| where RCALevel1 != "NoCorrelationsFound"
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `RCALevel1 != "NoCorrelationsFound"`

---
