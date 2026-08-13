# VM VMSS CRUD Hub — Resource URI: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:18:41.893Z.
> Total: 16 unique KQL queries across 9 panels (16 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 7

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "Resource URI" | ResourceGet | azcore.centralus | Crp | globalFrom, globalTo, local_resourceGroupName, local_resourceName, local_ResourceURI, local_subscriptionId |
| 2 | Failover Issue Detector Query | IssueDetector | azcore.centralus | Crp | queryFrom, queryTo, subId, rgName, resName |
| 3 | NeworkingInternalOperationError Detector  | IssueDetector | azcore.centralus | Crp | queryFrom, queryTo, subId, rgName, resName |
| 4 | Slow Extensions | IssueDetector | azcore.centralus | Crp | queryFrom, queryTo, subId, rgName, resName |
| 5 | VMStartTimedOut Detector | IssueDetector | azcore.centralus | Crp | queryFrom, queryTo, subId, rgName, resName |
| 6 | Failures / Slow operations | Timeline | azcore.centralus | Crp | queryFrom, queryTo, subId, rgName, resName |
| 7 | Active Azsm/Fabric Tenants | Timeline | azcore.centralus | Crp | queryFrom, queryTo, subId, resName, rgName |

### CRP Operation Premption flow
Path: `CRP Operation Premption flow`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | PreemptedOperations V2 | Table | azcore.centralus | Crp | queryFrom, ResURI |

### CRP Operation Premption flow > CRP Operation Preemption Timeline
Path: `CRP Operation Premption flow > CRP Operation Preemption Timeline`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Operations - StartTime | Timeline | azcrp | crp_allprod | queryFrom, ResURI |
| 2 | Operations - Lifecycle until preemption | Timeline | azcore.centralus | Crp | queryFrom, ResURI |

### Fabric Failover
Path: `Fabric Failover`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Failovers | Timeline | azcore.centralus | Crp | queryFrom, queryTo, subId, rgName, resName |

### NetworkingInternalOperationError
Path: `NetworkingInternalOperationError`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | statemachinevents | Table | azcore.centralus | Crp | queryFrom, queryTo, subid, rgName, resName |

### NetworkingInternalOperationError > Automated query
Path: `NetworkingInternalOperationError > Automated query`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | NIOE | Single | azcore.centralus | Crp | queryFrom, queryTo, subid, rgName, resName |

### NetworkingInternalOperationError > RNM release notification
Path: `NetworkingInternalOperationError > RNM release notification`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | RnmOperationEvents | Table | azcore.centralus | Crp | queryFrom, queryTo, subid, rgName, resName |

### Slow Extensions
Path: `Slow Extensions`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Slow Extensions v2 | Table | azcore.centralus | Crp | queryFrom, queryTo, ResURI |

### VMStartTimedOut
Path: `VMStartTimedOut`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Container Unknown Duration | Table | azcore.centralus | AzureCP | queryFrom, queryTo, subId, resName |
