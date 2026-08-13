# (top-level)

> Source: **ARM Customer Journey Investigation Guide** dashboard, chapter **(top-level)** (10 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Customer Journey"

Cluster: `apadata.westus.kusto.windows.net` · Database: `Sandbox` · Type: `ResourceGet` · Widget: `Container`

```kusto
print subscriptionId=local_subscriptionId
```

**Params:** `{local_subscriptionId}`

---

### new subscriptions

Cluster: `apadata.westus.kusto.windows.net` · Database: `sandbox` · Type: `Single` · Widget: `Card`

```kusto
Hack21_NewSubscriptions
| where subscriptionguid == SubscriptionId
| project subscriptionguid, subscriptionname, subscriptioncreateddate, paymentmethodtype, aibillingtype, aiorganizationname, aioffername,tpid, SegmentName,IndustryName, VerticalCategoryName, RegionName
```

**Params:** `{SubscriptionId}`

---

### Retention

Cluster: `apadata.westus.kusto.windows.net` · Database: `Sandbox` · Type: `Timeline`

```kusto
Hack21_NewSubscriptions_Retention
| where subscriptionId == SubscriptionId
| project
    StartTime = startofmonth(datetime(2021-09-01)),
    EndTime = endofmonth(datetime(2021-09-01)),
    Content = tostring(IsActiveAfter30Days),
    Health = iff(IsActiveAfter30Days > 0, "Healthy", "Unhealthy")
```

**Params:** `{SubscriptionId}`

---

### Control Plane Request

Cluster: `apadata.westus.kusto.windows.net` · Database: `Sandbox` · Type: `Timeline`

```kusto
Hack21_HttpRequests
| where subscriptionId == SubscriptionId
| summarize count() by bin(PreciseTimeStamp, 1d)
| project
    StartTime = startofday(PreciseTimeStamp),
    EndTime = endofday(PreciseTimeStamp),
    Content = tostring(count_)
```

**Params:** `{SubscriptionId}`

---

### Client Failures

Cluster: `apadata.westus.kusto.windows.net` · Database: `Sandbox` · Type: `Timeline`

```kusto
Hack21_HttpRequests
| where subscriptionId == SubscriptionId
| where httpStatusCode >= 400 and httpStatusCode < 500
| summarize count(), make_set(operationName) by bin(PreciseTimeStamp, 1d), httpStatusCode
| extend errors = strcat(httpStatusCode, ":", set_operationName)
| summarize     
    Content = tostring(make_set(httpStatusCode)),
    TotalFailure = sum(count_),
    Details = make_list(errors)
    by PreciseTimeStamp
| project 
    StartTime = startofday(PreciseTimeStamp),
    EndTime = endofday(PreciseTimeStamp),
    Content,
    TotalFailure,
    Details,
    Health = "Degraded"
```

**Params:** `{SubscriptionId}`

---

### Server Failures

Cluster: `apadata.westus.kusto.windows.net` · Database: `Sandbox` · Type: `Timeline`

```kusto
Hack21_HttpRequests
| where subscriptionId == SubscriptionId
| where httpStatusCode >= 500
| project
    StartTime = PreciseTimeStamp,
    EndTime = PreciseTimeStamp,
    Content = strcat(authorizationAction, ":", httpStatusCode)
| union (
Hack21_WriteOperations
| where subscriptionId == SubscriptionId
| where operationStatus != "Succeeded"
| project
    StartTime = requestStartTime,
    EndTime = requestStartTime,
    Content = strcat(operationName, ":", errorCode)
)
| extend Health = "Unhealthy"
```

**Params:** `{SubscriptionId}`

**Signal filters seen in KQL:** `operationStatus != "Succeeded"`

---

### Write Operations

Cluster: `apadata.westus.kusto.windows.net` · Database: `Sandbox` · Type: `Timeline`

```kusto
Hack21_WriteOperations
| where subscriptionId == SubscriptionId
| where operationName endswith "write"
| order by requestStartTime asc
| extend WindowId = row_window_session(requestStartTime, 1d, 8h)
| summarize
    StartTime = min(requestStartTime),
    EndTime = max(requestStartTime),
    Content = tostring(make_set(operationName)),
    FaiureCount = countif(operationStatus != "Succeeded") by WindowId
| project
    StartTime,
    EndTime,
    Content,
    Health = iff(FaiureCount == 0, "Healthy", "Unhealthy")
```

**Params:** `{SubscriptionId}`

**Signal filters seen in KQL:** `operationName endswith "write"`

---

### ARM - Doc Views

Cluster: `apadata.westus.kusto.windows.net` · Database: `Sandbox` · Type: `Timeline`

```kusto
Hack21_DocViews
| where subscriptionId == SubscriptionId
| order by StartDateTime asc 
| extend WindowId = row_window_session(StartDateTime, 1d, 8h)
| summarize 
    StartTime = min(StartDateTime),
    EndTime = max(StartDateTime),
    Content = tostring(make_list(Url))
    by WindowId
| where isnotempty(StartTime)    
| project 
    StartTime,
    EndTime,
    Content,
    Health = "Neutral"
```

**Params:** `{SubscriptionId}`

---

### Portal Traffic

Cluster: `apadata.westus.kusto.windows.net` · Database: `Sandbox` · Type: `Timeline`

```kusto
Hack21_HttpRequests
| where subscriptionId == querySubscriptionId
| extend Client = getClientName(clientApplicationId, userAgent)
| summarize TotalRequests = count(), PortalRequests = countif(Client == "Azure Portal") by bin(PreciseTimeStamp, 1d)
| where PortalRequests > 0
| project 
    StartTime = startofday(PreciseTimeStamp),
    EndTime = endofday(PreciseTimeStamp),
    Content = strcat(tostring(toint(PortalRequests * 100.0 / TotalRequests)), "%"),
    TotalRequests,
    PortalRequests,
    Health = "Healthy"
```

**Params:** `{querySubscriptionId}`

---

### Non-Portal Traffic

Cluster: `apadata.westus.kusto.windows.net` · Database: `Sandbox` · Type: `Timeline`

```kusto
Hack21_HttpRequests
| where subscriptionId == querySubscriptionId
| extend Client = getClientName(clientApplicationId, userAgent)
| summarize TotalRequests = count(), NonPortalRequests = countif(Client != "Azure Portal"), Clients =make_set(Client) by bin(PreciseTimeStamp, 1d)
| where NonPortalRequests > 0
| project 
    StartTime = startofday(PreciseTimeStamp),
    EndTime = endofday(PreciseTimeStamp),
    Content = strcat(tostring(toint(NonPortalRequests * 100.0 / TotalRequests)), "%"),
    TotalRequests,
    NonPortalRequests,
    Clients,
    Health = "Neutral"
```

**Params:** `{querySubscriptionId}`

---
