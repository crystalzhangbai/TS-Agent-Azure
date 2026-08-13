# Recent Run

> Source: **Blob Inventory Investigation Guide** dashboard, chapter **Recent Run** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Blob Inventory Task Run

_Widget purpose:_ Recent Run

Cluster: `xstore.westcentralus.kusto.windows.net` · Database: `xstore` · Type: `Table`
Source panel: `Recent Run`

```kusto
let _startTime = startofweek(queryFrom);
BlobInventoryManifestTaskTable
| where DispatchTime between (_startTime .. queryTo) and AccountName ==  trim(@"[\s]+", storageAccountName)
| where PolicyRunId has  trim(@"[\s]+", policyRunId) 
| join kind=leftouter(BlobInventoryErrorCodeDescriptions()) on ErrorCode
| summarize
    min(DispatchTime),
    max(EndTime), 
    make_set(TaskState),
    make_set(ErrorCode),
    make_set(ErrorDescription),
    (_, MinManifestTaskVersion) = arg_min(parse_version(ProductVersion), ProductVersion),
    (_1, MaxManifestTaskVersion) = arg_max(parse_version(ProductVersion), ProductVersion),
    max(BilledObjectsCount)
    by PolicyRunId, RuleName, RuleIdentifier
| where isnotempty(PolicyRunId)
| project-away _, _1
| extend Duration = max_EndTime - min_DispatchTime
| sort by min_DispatchTime desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`, `{policyRunId}`

---
