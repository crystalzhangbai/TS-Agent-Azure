# CoBe Timeline

> Source: **ARM Correlation Ids Investigation Guide** dashboard, chapter **CoBe Timeline** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ARMCorrelationId

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `CoBeTimeline`
Source panel: `CoBe Timeline`

```kusto
let startTime = datetime_add('hour', -12, PreciseTimeStamp);
let endTime = datetime_add('hour', 12, PreciseTimeStamp);
let clusterName = "armprodgbl.eastus";
let dbName = "ARMProd";
ARMCorrelationId(correlationId, startTime, endTime, clusterName, dbName)
| extend CriticalEvent = parse_json(Properties)._CriticalEvent
| extend FilterCategory = case(CriticalEvent == True and isempty(ParentId), "CriticalEvent", CriticalEvent==False, "NonCriticalEvent","")
| extend InferFilterCategory = iff(isempty(FilterCategory), True, False);
```

**Params:** `{correlationId}`, `{PreciseTimeStamp}`

---
