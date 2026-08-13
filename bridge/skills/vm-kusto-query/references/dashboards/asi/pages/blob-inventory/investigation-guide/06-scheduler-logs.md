# Scheduler Logs

> Source: **Blob Inventory Investigation Guide** dashboard, chapter **Scheduler Logs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Blob Inventory Scheduler Logs

_Widget purpose:_ Scheduler Logs

Cluster: `https://xstore.westcentralus.kusto.windows.net/` · Database: `xstore` · Type: `Table`
Source panel: `Scheduler Logs`

```kusto
let _accountName = storageAccountName;
let _policyRunId = runID;
let dispatchTime = toscalar(BlobInventoryManifestTaskTable | where isnotempty(_policyRunId) and  PolicyRunId == _policyRunId | take 20 | summarize min(DispatchTime));
let startTime = iff (isempty(dispatchTime), queryFrom, dispatchTime - 1h);
let endTime = iff (isempty(dispatchTime), queryTo, dispatchTime + 10m);
let results = BlobInventorySchedulerActionStatsTable
| where TIMESTAMP between (startTime .. (endTime))  and AccountName == _accountName and isnotempty(_accountName)
| extend HomeTenantName = Tenant, Time = bin(TIMESTAMP, 30m), TaskId = ""
| invoke BlobInventoryExtendDebuggingLinks();
let versions = ETWEventOLCMSchedulerDispatchStatsProdHourly 
| where TIMESTAMP between (startTime .. (endTime)) and Tenant in (results | distinct Tenant) and isnotempty(_accountName)
| distinct RoleInstance, Time = bin(TIMESTAMP, 30m), ProductVersion;
let resultsWithVersions = results
| join kind=leftouter(versions) on RoleInstance, Time;
resultsWithVersions
| invoke BlobInventoryExtendErrorDescription()
| project TIMESTAMP, ProductVersion = iff(isnotempty(ProductVersion), ProductVersion, ProductVersion1), policyRunId, Action, ErrorCode, ErrorDescription, ActionStats, ActivityId, RoleInstance, Tenant//, XDS, FrontEndLink
| sort by TIMESTAMP desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`, `{runID}`

---
