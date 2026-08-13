# Storage Requests

> Source: **ARM Activity Ids Investigation Guide** dashboard, chapter **Storage Requests** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Storage Requests for Activity Id

_Widget purpose:_ Storage Requests

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `Table`
Source panel: `Storage Requests`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Storage').StorageRequests
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where isnotempty(queryActivityId) and ActivityId == queryActivityId
    | where httpStatusCode > -1
    | project TIMESTAMP, operationName, accountName, type = resourceType, source = resourceName, durationInMilliseconds, httpStatusCode
)
| order by TIMESTAMP asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryActivityId}`

---
