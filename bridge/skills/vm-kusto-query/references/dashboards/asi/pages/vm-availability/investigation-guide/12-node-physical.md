# Node (Physical)

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Node (Physical)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Node Hardware Properties

_Widget purpose:_ Node (Physical)

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Single` · Widget: `Card`
Source panel: `Node (Physical)`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(startofday(starttime) .. endofday(endtime))
| where ResourceId =~ nodeid
| top 1 by PreciseTimeStamp desc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---
