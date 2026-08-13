# Top Error Code in Backup Operations

> Source: **NRP - BackupOperation** dashboard, chapter **Top Error Code in Backup Operations** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Backup Top Error

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Top Error Code in Backup Operations`

```kusto
let totalFailedBackUpPersliceRegion = (QosEtwEvent
    | where PreciseTimeStamp between(startTime..endTime)
    | where  OperationName == 'BackupOperation'
    | where UserError == 0 and Success == 0 and isnotempty(ErrorDetails)
    | where SourceAssemblyFileVersion contains "release/"
    | extend sliceNumber=SliceNum(SourceAssemblyFileVersion)
    | where sliceNumber >= 0 and sliceNumber <= 9
    | summarize failedErrorCount=count(),make_set(Region),  arg_max(PreciseTimeStamp, ErrorCode_Details= ExceptionMessageHash( ErrorCode, ErrorDetails)) by  StackTrace);
totalFailedBackUpPersliceRegion
| order by failedErrorCount;
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "BackupOperation"` · `SourceAssemblyFileVersion contains "release/"`

---
