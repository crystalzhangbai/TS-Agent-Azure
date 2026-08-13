# Overlake / SoC

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Overlake / SoC** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### OverlakeNodeMap

_Widget purpose:_ Overlake / SoC

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `Single` · Widget: `Card`
Source panel: `Overlake / SoC`

```kusto
let socId = toscalar(cluster('azcore.centralus.kusto.windows.net').database('SharedWorkspace').htos(queryNodeId) | take 1);
let overlakeEnabled = iff(isempty(socId), "Not Enabled", "Enabled");
print overlakeEnabled, NodeId = queryNodeId, SocNodeId = socId
| join kind=leftouter(cluster('azcore.centralus.kusto.windows.net').database('OvlProd').LinuxOverlakeVersion
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId =~ socId
) on $left.SocNodeId == $right.NodeId
| project OverlakeState = overlakeEnabled, NodeId = queryNodeId, SocNodeId = socId, MachineName, MachineFunction, Version = PRETTY_NAME, Region
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---
