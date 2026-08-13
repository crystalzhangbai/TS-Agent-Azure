# Recovery Services Vaults — HSR: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:27:08.194Z.
> Total: 16 unique KQL queries across 1 panels (16 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 16

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "HSR" | ResourceGet | https://mabprod1 | MABKustoProd1 | local_HSRNameGivenInPreRegScript, local_LogicalContainerId, local_SubscriptionId |
| 2 | Backup Success Without user error | DataSummary | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId |
| 3 | Restore stats | DataSummary | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId |
| 4 | Protection Stats | DataSummary | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId |
| 5 | Registration Stats | DataSummary | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId |
| 6 | hdbnsutil tool mode value | Timeline | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId, alltaskids |
| 7 | get all backup task id queries | MultiRow | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId |
| 8 | active node tracking for Log Backups | Timeline | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId |
| 9 | Backup Timelines from extension POV | CoBeTimeline | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId, queryFromC, queryToC, local_taskids |
| 10 | get log backup Task id queries | MultiRow | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId |
| 11 | Backup Chaining query | Graph | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId, queryFromC, queryToC |
| 12 | Recovery bird eye view | Timeline | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId |
| 13 | Pit view for pit ids | Timeline | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId, queryFromC, queryToC |
| 14 | view by service machine and ds | Timeline | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId, queryFromC, queryToC |
| 15 | get machines where recovery is done from hsr ds | MultiRow | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_logicalContainerId |
| 16 | get component restore timings | CoBeTimeline | https://mabprod1 | MABKustoProd1 | queryFrom, queryTo, local_subscriptionId, local_containerNames, queryFromC, queryToC |
