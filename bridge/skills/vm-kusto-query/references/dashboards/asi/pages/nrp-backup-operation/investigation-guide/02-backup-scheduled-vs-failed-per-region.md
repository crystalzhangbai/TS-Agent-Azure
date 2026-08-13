# Backup Scheduled vs Failed Per Region

> Source: **NRP - BackupOperation** dashboard, chapter **Backup Scheduled vs Failed Per Region** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Backup Scheduled

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Backup Scheduled vs Failed Per Region`

```kusto
let totalBackUpTriggered = (QosEtwEvent
    | where PreciseTimeStamp between(startTime..endTime)
    | where Region == region and OperationName == 'BackupOperation'
    | where SourceAssemblyFileVersion contains "release/"
    | extend sliceNumber=SliceNum(SourceAssemblyFileVersion)
    | where sliceNumber >= 0 and sliceNumber <= 9
    | summarize totalBackupInitiated=count(), min(TIMESTAMP), max(TIMESTAMP) by Region, SourceAssemblyFileVersion, PartitionId, bin(PreciseTimeStamp, 5h));
let totalFailedBackUpPersliceRegion = (QosEtwEvent
    | where PreciseTimeStamp between(startTime..endTime)
    | where Region == region and OperationName == 'BackupOperation'
    | where UserError == 0 and Success == 0 and isnotempty(ErrorDetails)
    | where SourceAssemblyFileVersion contains "release/"
    | extend sliceNumber=SliceNum(SourceAssemblyFileVersion)
    | where sliceNumber >= 0 and sliceNumber <= 9
    | summarize totalBackUpOperationFailedCount=count(), make_set(ErrorCode), arg_max(PreciseTimeStamp, ErrorDetails), make_set(StackTrace) by Region, SourceAssemblyFileVersion, PartitionId, bin(PreciseTimeStamp, 5h));
let backup_fails=totalBackUpTriggered 
    | join kind= leftouter totalFailedBackUpPersliceRegion on Region, PartitionId
    | extend totalFailedPercent = toreal(totalBackUpOperationFailedCount)/totalBackupInitiated
    | project Region, SourceAssemblyFileVersion, PartitionId, totalBackUpOperationFailedCount =iff(isnull(totalBackUpOperationFailedCount), 0, totalBackUpOperationFailedCount), 
        totalBackupInitiated, totalFailedPercent = iff(isnull(totalFailedPercent), real(0), totalFailedPercent) , min_TIMESTAMP, max_TIMESTAMP, 
        ErrorCode_Details = ExceptionMessageHash( set_ErrorCode, ErrorDetails);
backup_fails
| order by ErrorCode_Details asc;
```

**Params:** `{startTime}`, `{endTime}`, `{region}`

**Signal filters seen in KQL:** `SourceAssemblyFileVersion contains "release/"`

---
