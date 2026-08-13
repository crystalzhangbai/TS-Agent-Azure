# ARM Operations

> Source: **Storage Control Plane Dashboard Investigation Guide** dashboard, chapter **ARM Operations** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get account ARM requests

_Widget purpose:_ ARM Operations

Cluster: `https://armprodgbl.eastus.kusto.windows.net/` · Database: `ARMProd` · Type: `Table`
Source panel: `ARM Operations`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpIncomingRequests
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where subscriptionId =~ subID and TaskName != "HttpIncomingRequestStart"
    | where targetResourceProvider == "MICROSOFT.STORAGE"
    | where targetUri matches regex  strcat("https://management.azure.com:443/subscriptions/", subID, "/resourceGroups/.*/providers/Microsoft.Storage/storageAccounts/", accountName, "/.*")
    | where correlationId has corrID
    | where httpMethod != iff(isNoGet, 'GET', '')
    | limit 1000
)
| order by PreciseTimeStamp asc
| project TIMESTAMP, Level, ActivityId, correlationId, principalOid, operationName, httpMethod, httpStatusCode, targetUri, clientIpAddress, apiVersion, contentLength, durationInMilliseconds, targetResourceProvider, targetResourceType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{accountName}`, `{subID}`, `{corrID}`, `{isNoGet}`

**Signal filters seen in KQL:** `targetResourceProvider == "MICROSOFT.STORAGE"`

---
