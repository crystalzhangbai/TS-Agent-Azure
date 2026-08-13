# (top-level)

> Source: **ARM — Subscriptions** dashboard, chapter **(top-level)** (4 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Subscriptions"

Cluster: `customerdomrptwus3prod.westus3` · Database: `customerdomdata` · Type: `ResourceGet` · Widget: `Container`

```kusto
cluster('customerdomrptwus3prod.westus3').database('customerdomdata').CustomerModel
| where SubscriptionGuid == local_SubscriptionId
| take 1
| project SubscriptionGuid, FriendlySubscriptionName, SubscriptionCreatedDate, SubscriptionStartDate, DeprovisionedDate, 
    CurrentSubscriptionStatus, OfferName, OfferType, CloudType, TenantCountryCode, TPID, TPNameTranslated, S500, RegionName,
    SubsidiaryName, BillingType, CloudCustomerName, TenantId, TenantName, StrategicType
```

**Params:** `{local_SubscriptionId}`, `{globalFrom}`, `{globalTo}`

---

### Subscription Requests

_Widget purpose:_ Requests

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `TimeSeries`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpIncomingRequests
    | where PreciseTimeStamp between(queryFrom..queryTo)
    | where subscriptionId == querySubscriptionId and TaskName != "HttpIncomingRequestStart"
)
| summarize Requests = count(), InternalServiceErrors = countif(httpStatusCode >= 500), Throttled = countif(httpStatusCode == 429) by bin(PreciseTimeStamp, 30m)
| order by PreciseTimeStamp asc
```

**Params:** `{querySubscriptionId}`, `{queryFrom}`, `{queryTo}`

---

### Subscription Requests by User Agent

_Widget purpose:_ Requests by User Agent

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `TimeSeries`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpIncomingRequests
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where subscriptionId =~ querySubscriptionId and TaskName != "HttpIncomingRequestStart"
    | where isempty(queryOptionalFilter) 
        or (
            (queryOptionalFilter == "400s" and httpStatusCode >= 400 and httpStatusCode < 500)
        or
            (queryOptionalFilter == "500s" and httpStatusCode >= 500)
        )
    | where isnotempty(userAgent)
    | extend userAgentWithStatus = strcat(split(userAgent, "/")[0], "-", httpStatusCode)
    | summarize Requests = count() by userAgentWithStatus, bin(PreciseTimeStamp, 30m)
)
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscriptionId}`, `{queryOptionalRegion}`, `{queryOptionalFilter}`

---

### Filter - Request Errors

_Widget purpose:_ Requests by User Agent

Cluster: `?` · Database: `?` · Type: `Filter` · Widget: `TimeSeries`

```kusto
[
    { "Value": "400s"},
    { "Value": "500s"}
]
```

---
