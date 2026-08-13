# Account Rules Status & SLO

> Source: **Blob Inventory Investigation Guide** dashboard, chapter **Account Rules Status & SLO** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Account Inventory Rules & SLO

_Widget purpose:_ Account Rules Status & SLO

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Table`
Source panel: `Account Rules Status & SLO`

```kusto
let PendingTaskState = "Pending";
let SucceededTaskState = "Succeeded";
let _startTime = startofweek(queryFrom);
BlobInventorySloTable
| where DispatchTime between (_startTime..queryTo) and AccountName == storageAccountName and isnotempty(storageAccountName) and PolicyRunId has runID
| summarize arg_max(TIMESTAMP, ManifestTaskState, DispatchTime, AccountType, InventoryFormat, BilledObjectsCount, ObjectCountFromBilling) by TaskId, RuleName
| extend TaskDuration = iff(ManifestTaskState == PendingTaskState, now() - DispatchTime, TIMESTAMP - DispatchTime)
| where not(ManifestTaskState == PendingTaskState and TaskDuration < 1d)
| extend MeetSLO = ManifestTaskState == SucceededTaskState and TaskDuration < 1d, true, false
| summarize RunCount=count(), SloMet = countif(MeetSLO == true), SloNotMet = countif(MeetSLO == false), percentile(BilledObjectsCount, 50), percentile(ObjectCountFromBilling, 50) by InventoryFormat, AccountType, RuleName
| extend MetSloRetio = round(100. * SloMet / (SloMet + SloNotMet), 3)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`, `{runID}`

---
