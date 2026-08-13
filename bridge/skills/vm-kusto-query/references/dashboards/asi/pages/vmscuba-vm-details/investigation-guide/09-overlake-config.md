# Overlake Config

> Source: **VM Scuba - VM Details** dashboard, chapter **Overlake Config** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-Overlake Config

Cluster: `gandalf.kusto.windows.net` · Database: `gandalf` · Type: `Table` · Widget: `Column`
Source panel: `Overlake Config`

```kusto
CADDAILY
| where RoleInstanceName == roleInstanceName
| extend isOverlake = iff((NodeSS_PairId != "00000000-0000-0000-0000-000000000000" and isnotempty(NodeSS_PairId)), "True", "False") 
| summarize arg_max(PreciseTimeStamp,*) by RoleInstanceName, isOverlake
| project PreciseTimeStamp, RoleInstanceName, Hardware_Generation, NodeSS_PairId, isOverlake
```

**Params:** `{queryFrom}`, `{queryTo}`, `{roleInstanceName}`

---
