# Route Updates

> Source: **NRP - Route Tables** dashboard, chapter **Route Updates** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Route Updates

### Tim Query Created for Andy

_Widget purpose:_ Route Updates

Cluster: `nrp` · Database: `mdsnrp` · Type: `Table`
Source panel: `Route Updates > Route Updates > Route Updates`

```kusto
QosEtwEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ResourceName =~ queryRouteTableName and ResourceGroup =~ queryResourceGroupName and SubscriptionId == querySubscriptionId
| where HttpMethod != "GET" and ResourceType == "routeTables"
| project PreciseTimeStamp, StartTime, DurationInMilliseconds, Success, UserError, ErrorCode, ErrorDetails, ResourceName, HttpMethod, OperationName, OperationId
| extend trunc = tostring(split(ErrorDetails, "at Microsoft.WindowsAzure")[0])
| extend trunc = coalesce(trunc, ErrorDetails)
| extend level = iff(not(Success), 'error', 'info')
| top 1000 by PreciseTimeStamp desc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryRouteTableName}`, `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `HttpMethod != "GET"`

---
