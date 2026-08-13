# Node Diagnostic Details

> Source: **Unhealthy Node Analysis - Node Recovery Detail** dashboard, chapter **Node Diagnostic Details** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Node Diagnostic Detail

_Widget purpose:_ Node Diagnostic Details

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Single` · Widget: `Card`
Source panel: `Node Diagnostic Details`

```kusto
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (st ..et ) and ResourceDependencies contains nId
| where TreeActionName == "ExecuteAnvilNodeDiagnosticsAction" and Message contains "HasUnCorrectableErrorsInSel"
| extend Message = parse_json(Message)
| project PreciseTimeStamp, TreeNodeKey, TreeActionName, Message, RequestIdentifier, Tenant, ResourceId
| summarize arg_min(PreciseTimeStamp, *) by ResourceId
| where isnotempty(Message)
| sort by PreciseTimeStamp asc
```

**Params:** `{st}`, `{et}`, `{nId}`

**Signal filters seen in KQL:** `TreeActionName == "ExecuteAnvilNodeDiagnosticsAction"`

---
