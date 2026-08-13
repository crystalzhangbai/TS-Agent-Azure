# (top-level)

> Source: **ARM — Sub Throttling** dashboard, chapter **(top-level)** (8 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Sub Throttling"

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `ResourceGet` · Widget: `Container`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpIncomingRequests
    | where PreciseTimeStamp between(globalFrom..globalTo)
    | where subscriptionId == local_subscriptionId and httpStatusCode == 429
    | project subscriptionId
    | take 1
)
| take 1
```

**Params:** `{local_subscriptionId}`, `{globalFrom}`, `{globalTo}`

---

### Retrieve Resource "Subscriptions"

_Widget purpose:_ Subscription Details

Cluster: `genevareference.westcentralus` · Database: `AzureGraph` · Type: `ResourceGet` · Widget: `Card`

```kusto
Customer_Subscription
| where Id =~ local_SubscriptionId
| take 1
```

**Params:** `{local_SubscriptionId}`

---

### Get Throttling

_Widget purpose:_ ARM Throttling Detector

Cluster: `armprodgbl.eastus` · Database: `armprod` · Type: `IssueDetector`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpIncomingRequests
    | where PreciseTimeStamp between(queryFrom..queryTo)
    | where subscriptionId == querySubId and TaskName != "HttpIncomingRequestStart"
)
| summarize Requests = count(), Throttled = countif(httpStatusCode == 429)
| extend Title = "**Subscription throttling requests (429)**"
| extend Severity = iif(Throttled == 0, 'Info', 'Error')
| extend Description = iif(Throttled == 0, 
    'The subscription is not getting throttled, no 429 ARM response in selected time range.', 
    'The subscription is throttled, please review more details in this page to decide where the throttling comes from.'
)
| project Title, Severity, Description
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`

---

### Get RP Throttling

_Widget purpose:_ RP Throttling Detector

Cluster: `armprodgbl.eastus` · Database: `armprod` · Type: `IssueDetector`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpOutgoingRequests
    | where PreciseTimeStamp between(queryFrom..queryTo)
    | where subscriptionId == querySubId
    | where httpStatusCode == 429
)
| summarize Count = count()
| extend Title = "**Resource Provider throttling requests (429)**"
| extend Severity = iif(Count == 0, 'Info', 'Error')
| extend Description = iif(Count == 0, 
    strcat("Resource Providers do not return 429 response in selected time range."), 
    strcat("Specific RP requests is throttled, please review more details in this page and contact related RP team as needed.")
)
| project Title, Severity, Description
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`

---

### Subscription Requests

_Widget purpose:_ Throttled Requests (429)

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

### Get Sub Requests

_Widget purpose:_ ARM Layer

Cluster: `armprodgbl.eastus` · Database: `armprod` · Type: `TimeSeries`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpIncomingRequests
    | where PreciseTimeStamp between(queryFrom..queryTo)
    | where subscriptionId == querySubId and TaskName != "HttpIncomingRequestStart"
)
| summarize GeneralReads = countif(httpMethod == "GET"), GeneralWrites = countif(httpMethod == "PUT" or httpMethod == "PATCH" or httpMethod == "POST"), Deletes = countif(httpMethod == "DELETE") by bin(PreciseTimeStamp, 1h)
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`

---

### ARM - throttles by provider

_Widget purpose:_ Throttles By Provider

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `TimeSeries`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpOutgoingRequests
    | where PreciseTimeStamp between(queryFrom..queryTo)
    | where subscriptionId == querySubId and httpStatusCode == 429
)
| summarize 429_Count = dcount(ActivityId) by bin(PreciseTimeStamp, 15m), targetResourceProvider
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`

---

### Get RP Throttling

_Widget purpose:_ Resource Provider Layer

Cluster: `armprodgbl.eastus` · Database: `armprod` · Type: `Table`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpOutgoingRequests
    | where PreciseTimeStamp between(queryFrom..queryTo)
    | where subscriptionId == querySubId and httpStatusCode == 429
)
| summarize 429_Count = count() by bin(PreciseTimeStamp, 1h), operationName, hostName, targetResourceProvider
| order by 429_Count desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`

---
