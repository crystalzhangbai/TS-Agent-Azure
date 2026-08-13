# LCM Task Execution Details 

> Source: **Life Cycle Management Investigation Guide** dashboard, chapter **LCM Task Execution Details ** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Aggregate LCM Tasks

_Widget purpose:_ LCM Task Execution Details 

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Table`
Source panel: `LCM Task Execution Details `

```kusto
ETWEventOLCMScannerStatsProdHourly 
| where TIMESTAMP between (queryFrom .. queryTo)
| where AccountName == trim(@"[\s]+", storageAccountName) 
| order by ActionTime asc 
| extend CompleteTime = iff(Action == "Completed", ActionTime, datetime(1000-01-01T00:00:00.0Z))
| summarize StartTime = min(ActionTime), LastAtionTime = max(ActionTime), CompletedTime=max(CompleteTime), ActionList=make_list(Action), make_set(HResult), TimeUsedInSecond=sum(ElapsedTimeInSecond) by AccountName,TaskId, ScheduledTime
//| where list_Action !contains "Completed"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`

---
