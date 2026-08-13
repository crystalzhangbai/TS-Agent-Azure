# NRP — Private Endpoint: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:53.899Z.
> Total: 9 unique KQL queries across 1 panels (11 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 9

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Private Endpoint" | ResourceGet | argwus2nrpone.westus2 | AzureResourceGraph | local_name, local_resourceGroup, local_subscriptionId, local_timestamp, globalFrom, globalTo |
| 2 | NRP PE Operations Logs - QosEtwEvent | MultiRow | nrp | mdsnrp | subscriptionIdParam, resourceGroupParam, resourceNameParam |
| 3 | NRP PE Operations Logs -FrontendOperationEtwEvent | MultiRow | nrp | mdsnrp | OperationIdParam, OperationNameParam, TimeStampParam, ResourceGroupParam, ResourceNameParam, local_timestamp |
| 4 | Private Endpoint IPs | Table | argwus2nrpone.westus2 | AzureResourceGraph | queryFrom, queryTo, qSub, qRg, qName |
| 5 | Find Vnet Id | Single | nrpbi.westus | mdsnrpbi | SubscriptionIdParam, LocationParam, ArmUriParam, local_timestamp |
| 6 | Grab all the resources tied to PE | MultiRow | nrpbi.westus | mdsnrpbi | KeyParam |
| 7 | Get all resources tied to PE (name-only) | Single | nrpbi.westus | mdsnrpbi | KeyParam |
| 8 | FullResourceLogs | MultiRow | nrp | mdsnrp | subscriptionIdParam, resourceGroupParam, resourceNameParamArray |
| 9 | RNM NSMPlus State Propagation | MultiRow | Aznwsdn | aznwmds | DCMTRegionParam, VNetIdParam, local_timestamp |
