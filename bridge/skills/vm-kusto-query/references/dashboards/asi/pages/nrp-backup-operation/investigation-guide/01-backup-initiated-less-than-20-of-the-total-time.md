# Backup Initiated Less than 20% of the total time.

> Source: **NRP - BackupOperation** dashboard, chapter **Backup Initiated Less than 20% of the total time.** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Not scheduled backup

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Backup Initiated Less than 20% of the total time.`

```kusto
let datetimediff = datetime_diff('hour', endTime, startTime);
let totalBackupInitiated_threshold=datetimediff*2 *0.2;
let totalBackUpTriggered = (QosEtwEvent
    | where PreciseTimeStamp between(startTime..endTime)
    | where OperationName == 'BackupOperation'
    | where SourceAssemblyFileVersion contains "release/"
    | extend sliceNumber=SliceNum(SourceAssemblyFileVersion)
    | where sliceNumber >= 0 and sliceNumber <= 9
    | summarize totalBackupInitiated=count(), min(PreciseTimeStamp), max(PreciseTimeStamp) by Region, PartitionId
    | where totalBackupInitiated <= totalBackupInitiated_threshold);
totalBackUpTriggered
| order by totalBackupInitiated asc
```

**Params:** `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `OperationName == "BackupOperation"` · `SourceAssemblyFileVersion contains "release/"`

---
