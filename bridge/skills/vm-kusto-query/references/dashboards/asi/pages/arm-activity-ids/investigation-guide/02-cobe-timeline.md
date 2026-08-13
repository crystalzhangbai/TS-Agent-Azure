# CoBe Timeline

> Source: **ARM Activity Ids Investigation Guide** dashboard, chapter **CoBe Timeline** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ARMActivityId

_Widget purpose:_ CoBe Timeline

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `CoBeTimeline`
Source panel: `CoBe Timeline`

```kusto
let startTime = datetime_add('hour', -12, timeStamp);
let endTime = datetime_add('hour', 12, timeStamp);
let clusterName = "Armprod";
let dbName = "ARMProd";
ARMActivityId(activityId, startTime, endTime, clusterName, dbName);
```

**Params:** `{timeStamp}`, `{activityId}`

---
