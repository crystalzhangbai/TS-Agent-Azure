# ServiceHealth

> Source: **Azure Host — Azure Host Node** dashboard, chapter **ServiceHealth** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Service Health Table

### Azure Host Node SoC Service Health

_Widget purpose:_ Service Health Table

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `Table`
Source panel: `ServiceHealth > Service Health Table`

```kusto
let nodeDetails = cluster("azurehn.kusto.windows.net").database("Azurehn").fn_GetNodeInfo_v2(startTime, endTime, nodeId, "");
let SocId = toscalar(nodeDetails | distinct SocId);
OverlakeServiceHealthTable()
| where PreciseTimeStamp between (startTime .. endTime)
| where (NodeId =~ SocId and isnotempty(SocId))
| project PreciseTimeStamp, Name, MemoryCur, MemoryMax, TotalThrottledUsec = ThrottledUsec, TotalUserUsec = UserUsec, TotalSystemUsec = SystemUsec, TotalThrottledNr = ThrottledNr
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---
