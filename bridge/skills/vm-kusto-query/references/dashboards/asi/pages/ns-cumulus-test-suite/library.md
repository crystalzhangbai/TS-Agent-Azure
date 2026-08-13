# NodeService — CumulusTestSuite: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T13:12:40.042Z.
> Total: 4 unique KQL queries across 1 panels (4 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 4

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "CumulusTestSuite" | ResourceGet | azcore.centralus | HACumulus | globalFrom, globalTo, local_TestSuiteId |
| 2 | CRP Logs | Table | azcrp | crp_allprod | _startTime, _endTime, _resourceGroup, _cpAvailabilityZone, _clusterName |
| 3 | Node ASI link | Table | ? | ? | _startTime, _endTime, _nodeId |
| 4 | EG Query | Table | executiongraph | eg | rgName |
