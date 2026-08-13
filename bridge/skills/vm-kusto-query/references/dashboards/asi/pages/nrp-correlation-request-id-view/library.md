# NRP — CorrelationRequestIdView: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:54.053Z.
> Total: 9 unique KQL queries across 9 panels (9 widget refs).

## Page inputs (URL params)


## Panels

### Activity
Path: `Activity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | correl_activity | TimeSeries | nrp | mdsnrp | queryFrom, queryTo, correllationId, subscriptionId, region, resourceGroup_query_ |

### correlId
Path: `correlId`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | correlId | Timeline | https://nrp | mdsnrp | queryFrom, queryTo, region, correlationId, operationId, bin_size_sec, minDurationToShow_sec, subscriptionId, show_only_errs, show_only_locks, show_only_operationNames, resourceGroupName_, Tables |

### correlId > Activity
Path: `correlId > Activity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | correlActivity | TimeSeries | nrp | mdsnrp | qk, starttime, endtime |

### correlId > ARMHttpIncomingOutgoing
Path: `correlId > ARMHttpIncomingOutgoing`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | ARM_Correl | Table | nrp | mdsnrp | queryFrom, queryTo, test, qk, ignore_200 |

### correlId > CRP_ApiQosEvent
Path: `correlId > CRP_ApiQosEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | crp_apiqos | Table | nrp | mdsnrp | queryFrom, queryTo, qk, ignore_200 |

### correlId > FE_query
Path: `correlId > FE_query`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | fe_popup | Table | https://nrp | mdsnrp | queryFrom, queryTo, qk, min_step_dur, maxLevel, tid_query_, min_Sequence, max_Sequence, show_only_locks, show_only_errs |

### correlId > Request
Path: `correlId > Request`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | GetRequestBody | Table | nrp | mdsnrp | queryFrom, queryTo, qk, QueryWithOperationId |

### correlId > TID_Timeline
Path: `correlId > TID_Timeline`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | FE_Tid_query | Timeline | https://nrp | mdsnrp | queryFrom, queryTo, qk, errors, select_locks |

### NRPQosErrors
Path: `NRPQosErrors`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | qos_errs | Table | nrp | mdsnrp | queryFrom, queryTo, correlationId, subscriptionId, region, resourceGroupName, ignoreSuccess |
