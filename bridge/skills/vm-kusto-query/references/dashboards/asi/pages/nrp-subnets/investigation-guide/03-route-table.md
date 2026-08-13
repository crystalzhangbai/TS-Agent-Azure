# Route Table

> Source: **NRP - Subnets** dashboard, chapter **Route Table** (5 queries across 5 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Route Table

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Single` · Widget: `Container`
Source panel: `Route Table`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where (isnotempty(queryRouteTableName) and isnotempty(queryResourceGroupName)) 
    and (name =~ queryRouteTableName and resourceGroup =~ queryResourceGroupName) 
| where subscriptionId =~ querySubscriptionId
| where type == "microsoft.network/routetables" and not(partial) and not(deleted)
| summarize 
    arg_max(timestamp, properties), 
    take_any(name, type, tenantId, location, resourceGroup, subscriptionId, apiVersion)
    by id
| extend subnets = array_length(properties.subnets)
| extend routes = array_length(properties.routes)
| extend provisioningState = tostring(properties.provisioningState)
| extend disableBgpRoutePropagation = tobool(properties.disableBgpRoutePropagation)
| project id, name, type, tenantId, location, resourceGroup, subscriptionId, apiVersion,
    subnets, routes, provisioningState, disableBgpRoutePropagation
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryRouteTableName}`, `{queryOptionalHintTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/routetables"`

---

## Route Table Updates

### Route Table Changes

_Widget purpose:_ Route Table Updates

Cluster: `nrp` · Database: `mdsnrp` · Type: `Timeline`
Source panel: `Route Table > Route Table Updates`

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

## Route Updates

### Tim Query Created for Andy

_Widget purpose:_ Route Updates

Cluster: `nrp` · Database: `mdsnrp` · Type: `Table`
Source panel: `Route Table > Route Updates > Route Updates > Route Updates`

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

## Routes

### Route Table Routes

_Widget purpose:_ Routes

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Route Table > Routes > Routes > Routes`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isempty(queryOptionalHintTime) or timestamp between(datetime_add('day', -2, queryOptionalHintTime) .. datetime_add('hour', 6, queryOptionalHintTime))
| where (isnotempty(queryRouteTableName) and isnotempty(queryResourceGroupName))
    and (name =~ queryRouteTableName and resourceGroup =~ queryResourceGroupName)
| where subscriptionId =~ querySubscriptionId
| where type == "microsoft.network/routetables" and not(partial) and not(deleted)
| top 1 by timestamp desc 
| mv-expand route = properties.routes
| project route
| project name = tostring(route.name),
    id = tostring(route.name),
    provisioningState = tostring(route.properties.provisioningState),
    addressPrefix = tostring(route.properties.addressPrefix),
    nextHopType = tostring(route.properties.nextHopType),
    nextHopIpAddress = tostring(route.properties.nextHopIpAddress),
    hasBgpOverride = tobool(route.properties.hasBgpOverride)
| order by name desc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryRouteTableName}`, `{queryOptionalHintTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/routetables"`

---

## Snapshots

### NRP Route Table Snapshots

_Widget purpose:_ Route Table Snapshots (ARG)

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Route Table > Snapshots > Route Table Snapshots (ARG)`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isempty(queryHintTime) or timestamp between(datetime_add('day', -2, queryHintTime) .. datetime_add('hour', 6, queryHintTime))
| where name =~ queryName
| where resourceGroup =~ queryResourceGroupName and subscriptionId =~ querySubscriptionId
| where type == "microsoft.network/routetables" and not(partial)
| extend JSON = properties
| extend provisioningState = JSON.provisioningState
| extend resourceGuid = JSON.resourceGuid
| order by timestamp desc
// because we are descending, we need next instead
| extend PreviousJSON = next(properties)
| project-away properties
| project-reorder timestamp, deleted, source, provisioningState, type, rowId
| where strlen(tostring(JSON)) != strlen(tostring(PreviousJSON))
```

**Params:** `{queryName}`, `{queryResourceGroupName}`, `{querySubscriptionId}`, `{queryHintTime}`

**Signal filters seen in KQL:** `type == "microsoft.network/routetables"`

---
