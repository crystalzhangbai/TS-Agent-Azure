# Ocular

> Source: **CRP — Scale Sets** dashboard, chapter **Ocular** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Ocular

### Ocular Summary Logs with Resource Name

_Widget purpose:_ Control Plane Traces

Cluster: `ocularcentralus.centralus.kusto.windows.net` · Database: `FunctionDB` · Type: `CoBeTimeline`
Source panel: `Ocular > Ocular > Control Plane Traces`

```kusto
GetOcularSummaryLogs(
    querySubscriptionId, 
    queryResourceGroupName, 
    queryResourceName, 
    queryFrom, 
    queryTo)
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryResourceName}`, `{queryFrom}`, `{queryTo}`

---
