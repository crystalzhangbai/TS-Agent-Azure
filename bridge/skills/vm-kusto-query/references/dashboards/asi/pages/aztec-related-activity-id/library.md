# Aztec — RelatedActivityId: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T11:19:27.219Z.
> Total: 6 unique KQL queries across 5 panels (6 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "RelatedActivityId" | ResourceGet | AzureCM | AzureCM | local_RelatedActivityId, local_startDate, local_endDate |
| 2 | RelatedActivityId CRP QoS Get | Single | azcrp | crp_allprod | local_startDate, local_RelatedActivityId |

### Allocation Activity > Compute Allocation Activity
Path: `Allocation Activity > Compute Allocation Activity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Compute Allocation Activity - ActivityId | Table | azcrp | crp_allprod | queryActivityId, queryOperationTime |

### CommonWebOperationEnd > CommonWebOperationEnd
Path: `CommonWebOperationEnd > CommonWebOperationEnd`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RelatedActivityId CommonWebOperationEnd | Table | AzureCM | AzureCM | local_RelatedActivityId, queryOperationTime |

### CommonWebOperationStart > CommonWebOperationStart
Path: `CommonWebOperationStart > CommonWebOperationStart`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RelatedActivityId CommonWebOperationStart | Table | AzureCM | AzureCM | queryOperationTime, local_RelatedActivityId |

### GatewayServiceTraceEvent > GatewayServiceTraceEvent
Path: `GatewayServiceTraceEvent > GatewayServiceTraceEvent`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RelatedActivityId GatewayServiceTraceEvent | Table | AzureCM | AzureCM | local_RelatedActivityId, queryOperationTime |
