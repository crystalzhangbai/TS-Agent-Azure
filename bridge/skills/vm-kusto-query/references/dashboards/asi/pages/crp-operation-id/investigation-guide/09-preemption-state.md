# Preemption State

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **Preemption State** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Preemption

_Widget purpose:_ Preemption State

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`
Source panel: `Preemption State`

```kusto
union
(cluster('azcrp.kusto.windows.net').database('crp_allprod').ContextActivity
| where PreciseTimeStamp between (starttime .. endtime)
| where activityId == operationid
| where message contains "is requesting preemption." or message contains "Not preempting current execution as it was preempted too many times."
| parse message with "Activity " preemption_operationId " is requesting preemption. Current preemption count is " preemption_count "."
| order by PreciseTimeStamp asc
| extend preemption_status = case (message contains "is requesting preemption.", "Preempted", 
    message contains "Not preempting current execution as it was preempted too many times.", "Failed to preempt / Preempted too many times", "No Preemption")
| project PreciseTimeStamp, preemption_operationId, preemption_count, preemption_status),
(print PreciseTimeStamp = datetime(null), preemption_operationId = "", preemption_count = 0, preemption_status = "Not Preempted")
| top 1 by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{operationid}`

**Signal filters seen in KQL:** `message contains "is requesting preemption."`

---
