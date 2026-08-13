# SRP Operations

> Source: **Storage Control Plane Dashboard Investigation Guide** dashboard, chapter **SRP Operations** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### List SRP Operations 

_Widget purpose:_ SRP Operations

Cluster: `https://xstorepartners.kusto.windows.net/` · Database: `SRP` · Type: `Table`
Source panel: `SRP Operations`

```kusto
RegionalSRP_ServiceApiQosEvent
| where PreciseTimeStamp between ( queryFrom .. queryTo)
| where subscriptionId == subID and account == accountName
| where method != iff(isNoGet, 'GET', '')
| where correlationId has corrID
| project PreciseTimeStamp, Tenant, RoleInstance, subscriptionId, operationId, clientRequestId, correlationId, operationName, resourceGroupName, durationInMilliseconds, e2EDurationInMilliseconds, httpStatusCode, exceptionType, errorDetails, region, method, account, status
```

**Params:** `{queryFrom}`, `{queryTo}`, `{accountName}`, `{subID}`, `{corrID}`, `{isNoGet}`

---
