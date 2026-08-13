# Aggregated LCM Account Policy Execution Summary (Below number of Rows)

> Source: **Life Cycle Management Investigation Guide** dashboard, chapter **Aggregated LCM Account Policy Execution Summary (Below number of Rows)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Aggregate Account LCM run result

_Widget purpose:_ Aggregated LCM Account Policy Execution Summary (Below number of Rows)

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Table`
Source panel: `Aggregated LCM Account Policy Execution Summary (Below number of Rows)`

```kusto
ETWEventOLCMSchedulerDispatchStatsProdHourly
| union ETWEventOLCMScannerStatsProdHourly
//| where TIMESTAMP between (startofweek(queryFrom) .. endofweek(queryTo))
| where TIMESTAMP between ((queryFrom) .. (queryTo))
| where AccountName == trim(@"[\s]+", storageAccountName)
| extend temp = RowsDeleted + RowsMoveToCool + RowsMoveToArchive + RowsMoveToHot + RowsMoveToCold, taskID = trim(@'^\[\"|\"\]$',tostring(split(TaskId, "_", 3)))
| summarize TotalDispatched = dcountif(TaskId,Action contains "dis"), min(PreciseTimeStamp), max(PreciseTimeStamp),sum(RowsScanned),TotalProcessed = sum(temp), sum(RowsDeleted), sum(RowsMoveToHot),sum(RowsMoveToCool), sum(RowsMoveToCold), sum(RowsMoveToArchive), sum(RowsFailed),TasksInitialPull = dcountif(TaskId,Action startswith "init"),TasksCompleted = dcountif(TaskId,Action startswith "comp"),TaskFailed = dcountif(TaskId,Action contains "drop"),make_set_if(HResult,Action contains "drop"),ErrorsOccuredDuringRun = make_set_if(HResult,Action !contains "drop" and Action contains "faile") by AccountName, bin(ScheduledTime,1d), Action, ActivityId, taskID
| extend timetaken = max_PreciseTimeStamp - min_PreciseTimeStamp
| where Action == "Completed" or Action == "Failed"
| project ScheduledTime, Action, ActivityId, taskID, sum_RowsScanned,TotalProcessed, sum_RowsMoveToHot, sum_RowsMoveToCool, sum_RowsMoveToCold, sum_RowsMoveToArchive, sum_RowsDeleted ,sum_RowsFailed,TotalDispatched,TasksInitialPull,TasksCompleted,TaskFailed,set_HResult,timetaken,ErrorsOccuredDuringRun
| order by ScheduledTime desc
 

// ETWEventOLCMSchedulerDispatchStatsProdHourly
// | union ETWEventOLCMScannerStatsProdHourly
// | where TIMESTAMP between (startofweek(queryFrom) .. endofweek(queryTo))
// | extend temp = RowsDeleted + RowsMoveToCool + RowsMoveToArchive + RowsMoveToHot + RowsMoveToCold
// | summarize TotalDispatched = dcountif(TaskId,Action contains "dis"), min(PreciseTimeStamp), max(PreciseTimeStamp),sum(RowsScanned),TotalProcessed = sum(temp), sum(RowsDeleted), sum(RowsMoveToHot),sum(RowsMoveToCool), sum(RowsMoveToCold), sum(RowsMoveToArchive), sum(RowsFailed),TasksInitialPull = dcountif(TaskId,Action startswith "init"),TasksCompleted = dcountif(TaskId,Action startswith "comp"),TaskFailed = dcountif(TaskId,Action contains "drop"),make_set_if(HResult,Action contains "drop"),ErrorsOccuredDuringRun = make_set_if(HResult,Action !contains "drop" and Action contains "faile") by AccountName, bin(ScheduledTime,1d)
// | extend timetaken = max_PreciseTimeStamp - min_PreciseTimeStamp
// | project ScheduledTime,Action = actionToFilter, sum_RowsScanned,TotalProcessed, sum_RowsMoveToHot, sum_RowsMoveToCool, sum_RowsMoveToCold, sum_RowsMoveToArchive, sum_RowsDeleted ,sum_RowsFailed,TotalDispatched,TasksInitialPull,TasksCompleted,TaskFailed,set_HResult,timetaken,ErrorsOccuredDuringRun
// | order by ScheduledTime desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`

**Signal filters seen in KQL:** `Action == "Completed"`

---
