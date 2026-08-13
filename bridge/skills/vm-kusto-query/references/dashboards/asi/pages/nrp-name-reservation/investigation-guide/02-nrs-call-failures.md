# NRS Call Failures

> Source: **NRP - NRP Name Reservation** dashboard, chapter **NRS Call Failures** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### NRS call failures

_Widget purpose:_ NRS Call Failures

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `NRS Call Failures`

```kusto
let opidLst=WriteOperationResponseEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where Message contains "name reservation"
| distinct OperationId;
FrontendOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where OperationId in (opidLst)
| where EventCode contains "NameReservationFailure"
| project OperationId, Region, Message, EventCode
```

**Params:** `{startTime}`, `{endTime}`, `{Region}`

**Signal filters seen in KQL:** `Message contains "name reservation"` · `EventCode contains "NameReservationFailure"`

---
