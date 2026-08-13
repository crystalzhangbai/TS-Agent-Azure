# (top-level)

> Source: **Aztec AzSM Application Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AzSM Application Builds

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Timeline`

```kusto
LogAzSMSnapshot
| where PreciseTimeStamp > ago(7d)
| where Cluster == "switzerlandn-prod-a" and applicationName == "fabric:/AzLifecycle-Slice3-P0"
| summarize StartTime = min(PreciseTimeStamp), EndTime = max(PreciseTimeStamp) by buildVersion
| project StartTime, EndTime, Content = buildVersion, Tooltip = strcat("Start: ", StartTime, "<br/>End: ", EndTime, "<br/>Build: ", buildVersion)
```

**Params:** `{queryCluster}`, `{queryApplicationName}`

**Signal filters seen in KQL:** `Cluster == "switzerlandn-prod-a"`

---

### Application Services

_Widget purpose:_ Services

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`

```kusto
AzSMServiceHealthEvent
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where Cluster == queryCluster and applicationName == queryApplicationName
| summarize arg_max(PreciseTimeStamp, *) by serviceName
| project serviceName, healthState
| order by serviceName asc
```

**Params:** `{queryCluster}`, `{queryApplicationName}`

---
