# LCM Scheduler Actions

> Source: **Life Cycle Management Investigation Guide** dashboard, chapter **LCM Scheduler Actions** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Aggregate LCM Scheduler Actions

_Widget purpose:_ LCM Scheduler Actions

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Table`
Source panel: `LCM Scheduler Actions`

```kusto
ETWEventOLCMSchedulerActionStatsEventTableHourly  
| where TIMESTAMP between (queryFrom .. queryTo)
| where AccountName == trim(@"[\s]+", storageAccountName)
| summarize SchedulerActionStart = min(TIMESTAMP), SchedulerActionEnds = max(TIMESTAMP), SchedulerActionList=make_list(Action), SchedulerActionResult=make_set(HResult), EffectiveLCMPolicy = max(Policy) by AccountName, ActivityId, RoleInstance
| extend Duration = SchedulerActionEnds - SchedulerActionStart
| extend LCMTaskScheduled = iif((SchedulerActionList) has_all ("AccountTasksDispatched"), True, False)
| order by AccountName asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`

---
