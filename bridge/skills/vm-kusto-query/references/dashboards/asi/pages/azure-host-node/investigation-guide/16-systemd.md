# SystemD

> Source: **Azure Host — Azure Host Node** dashboard, chapter **SystemD** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## SystemD Journal Logs

### Azure Host Node SoC SystemD Logs

_Widget purpose:_ SystemD Journal Logs

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `Table`
Source panel: `SystemD > SystemD Journal Logs`

```kusto
let nodeDetails = cluster("azurehn.kusto.windows.net").database("Azurehn").fn_GetNodeInfo_v2(startTime - 2h, endTime + 2h, nodeId, "");
let SocId = toscalar(nodeDetails | distinct SocId);
LinuxOverlakeSystemd()
| where PreciseTimeStamp between (startTime .. endTime)
| where (NodeId =~ SocId and isnotempty(SocId))
| where toint(PRIORITY) <= 5 // case(PRIORITY == 2, "Crit", PRIORITY == 3, "Error", PRIORITY == 4, "Warn", PRIORITY == 5, "Notice", PRIORITY == 6, "Info", PRIORITY == 7, "Debug", "Undef")
| project PreciseTimeStamp, _PID, MESSAGE
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---
