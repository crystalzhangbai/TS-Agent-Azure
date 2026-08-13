# Disk Health

> Source: **Aztec Nodes Investigation Guide** dashboard, chapter **Disk Health** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Disk Health Status

### Node Disk Health

_Widget purpose:_ Disk Health Status

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Disk Health > Disk Health Status`

```kusto
NodeDiskHealthStatusEtwTable  
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where NodeId == queryNodeId
| summarize 
    TotalDisks = max(TotalDisks), 
    HealthyDisks = min(HealthyDisks), 
    OnlineDisks = min(OnlineDisks), 
    TotalNonVhdDisks = max(TotalNonVhdDisks), 
    HealthyNonVhdDisks = min(HealthyNonVhdDisks), 
    OnlineNonVhdDisks = min(OnlineNonVhdDisks)
    by bin(PreciseTimeStamp, 30m)
| order by PreciseTimeStamp asc
```

**Params:** `{queryNodeId}`

---
