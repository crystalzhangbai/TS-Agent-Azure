# Route Table Updates

> Source: **NRP - Route Tables** dashboard, chapter **Route Table Updates** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Route Table Changes

_Widget purpose:_ Route Table Updates

Cluster: `nrp` · Database: `mdsnrp` · Type: `Timeline`
Source panel: `Route Table Updates`

```kusto
cluster("nrp.kusto.windows.net").database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between(queryFrom..queryTo) 
| where ResourceName =~ queryRouteTableName and ResourceGroup =~ queryResourceGroupName and SubscriptionId == querySubscriptionId 
| where ResourceType == "routeTables" and HttpMethod != "GET"
| project todatetime(StartTime), Content = OperationName, OperationId, CorrelationRequestId, NRPGatewayRequestId, ClientOperationId, 
    DurationInMilliseconds, Success, ErrorCode, ErrorDetails, InternalErrorCode
| extend Health = iff(Success, "", "Unhealthy")
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryRouteTableName}`, `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `ResourceType == "routeTables"`

---
