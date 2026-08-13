# ARM — Sub Throttling: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T08:29:30.264Z.
> Total: 8 unique KQL queries across 1 panels (8 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 8

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Sub Throttling" | ResourceGet | armprodgbl.eastus | ARMProd | local_subscriptionId, globalFrom, globalTo |
| 2 | Retrieve Resource "Subscriptions" | ResourceGet | genevareference.westcentralus | AzureGraph | local_SubscriptionId |
| 3 | Get Throttling | IssueDetector | armprodgbl.eastus | armprod | queryFrom, queryTo, querySubId |
| 4 | Get RP Throttling | IssueDetector | armprodgbl.eastus | armprod | queryFrom, queryTo, querySubId |
| 5 | Subscription Requests | TimeSeries | armprodgbl.eastus | ARMProd | querySubscriptionId, queryFrom, queryTo |
| 6 | Get Sub Requests | TimeSeries | armprodgbl.eastus | armprod | queryFrom, queryTo, querySubId |
| 7 | ARM - throttles by provider | TimeSeries | armprodgbl.eastus | ARMProd | queryFrom, queryTo, querySubId |
| 8 | Get RP Throttling | Table | armprodgbl.eastus | armprod | queryFrom, queryTo, querySubId |
