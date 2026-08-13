# Allocation Activity

> Source: **Aztec — Clusters** dashboard, chapter **Allocation Activity** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Allocation Activity

### Stamp Allocation Activity 

_Widget purpose:_ Allocation Activity

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Allocation Activity > Allocation Activity`

```kusto
CapacityReservationAllocationActivity 
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where computeStamp =~ queryStamp
| project PreciseTimeStamp, activityName, capacityReservationName, errorType, errorCode, resultDetails
| order by PreciseTimeStamp desc
| take 1000
```

**Params:** `{queryStamp}`, `{queryFrom}`, `{queryTo}`

---
