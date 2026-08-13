# Updates

> Source: **Azure Host — Azure Host Node** dashboard, chapter **Updates** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## SoC Updates

### Azure Host Node SoC Updates

_Widget purpose:_ SoC Updates

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `Table`
Source panel: `Updates > SoC Updates`

```kusto
let nodeDetails = cluster("azurehn.kusto.windows.net").database("Azurehn").fn_GetNodeInfo_v2(startTime - 2h, endTime + 2h, nodeId, "");
let SocId = toscalar(nodeDetails | distinct SocId);
OverlakeServiceManagerStatus
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 2h))
| where EventType == "versionswitch"
| where (NodeId =~ SocId and isnotempty(SocId))
| order by PreciseTimeStamp desc
| extend detailsParsed = parse_json(detail)
| extend CurrentVersion=tostring(detailsParsed.Version)
| extend NewVersion=tostring(detailsParsed.NewVersion)
| extend UpgradeType = "SOC"
| project PreciseTimeStamp, ServiceName, UpgradeType, CurrentVersion, NewVersion
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `EventType == "versionswitch"`

---
