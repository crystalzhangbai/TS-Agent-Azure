# (top-level)

> Source: **NodeService - CumulusTestSuite** dashboard, chapter **(top-level)** (4 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "CumulusTestSuite"

Cluster: `azcore.centralus.kusto.windows.net` · Database: `HACumulus` · Type: `ResourceGet` · Widget: `Container`

```kusto
let testDetails = CumulusV2TestAssertionSnapshot
| where TestSuiteId == local_TestSuiteId
| where Description startswith_cs "Resource group"
| take 1
| project TestSuiteId, Description
| parse Description with "Resource group (" ResourceGroupName ") should be available" *
| project TestSuiteId, ResourceGroupName
| union (print "" | project TestSuiteId = "677895fbbf57b59d44da8ed9")
| sort by ResourceGroupName desc | take 1
| join kind=inner (
  CumulusV2TestSuiteStatusSnapshot
  | where TestSuiteId == local_TestSuiteId
  | summarize StartTime=max(StartTime), EndTime=max(EndTime), arg_max(PreciseTimeStamp, TipNodeSessionIds) by TestSuiteId
) on TestSuiteId
| project TestSuiteId, ResourceGroupName, StartTime, EndTime, TipNodeSessionId=tostring(parse_json(TipNodeSessionIds)[0]);
let _tipNodeSessionId = testDetails | project TipNodeSessionId;
let _startTime = testDetails | project StartTime;
let _endTime = testDetails | project EndTime;
testDetails
| join kind=inner ( 
  database('AzureCP').MycroftNodeSnapshot
  | where TipNodeSessionId == toscalar(_tipNodeSessionId)
  | where PreciseTimeStamp > toscalar(_startTime) - 1h and PreciseTimeStamp < toscalar(_endTime) + 1h
) on TipNodeSessionId
| take 1
| project TestSuiteId, ResourceGroupName, StartTime, EndTime, TipNodeSessionId, NodeId, ClusterName, Region, AvailabilityZone, CPAvailabilityZone=Tenant
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_TestSuiteId}`

---

### CRP Logs

_Widget purpose:_ CRP Logs (For debugging VM deployment)

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `Table`

```kusto
let crpEvents = VMApiQosEvent
| where PreciseTimeStamp > _startTime and PreciseTimeStamp < _endTime
| where resourceGroupName == _resourceGroup
| where operationName == "VirtualMachines.ResourceOperation.PUT"
| project fabricTenantName, subscriptionId, correlationId, operationId, errorDetails
| parse errorDetails with "Constraints applied: " Constraints "." *
| extend hasError=errorDetails != ""
| project-away errorDetails;
let crpLogs = crpEvents 
| project LogType="VMApiQosEvent", Message=pack_all();
let fabricTenantName = crpEvents | project fabricTenantName;
let constraints = crpEvents | project Constraints;
let _activityId = crpEvents | project ActivityId=operationId;
let azSMLogs = cluster('azcore.centralus.kusto.windows.net').database('AzureCP').AzSMAllocationScoreStatus
| where PreciseTimeStamp between (_startTime .. _endTime)
| where tenantName in (fabricTenantName)
| where activityId in (_activityId)
| where Tenant == _cpAvailabilityZone
| summarize arg_max(PreciseTimeStamp,*) by tenantName, Tenant
| project PreciseTimeStamp, Tenant, tenantName, isAllocationSuccessful, allocationScoreCookie, aztmRejectionReason, scoreResultMessage
| project LogType="AzSMAllocationScoreStatus", Message=pack_all();
let allocationLogs = ComputeAllocationActivity
| where PreciseTimeStamp between (_startTime .. _endTime)
| where activityId in (_activityId)
| where computeStamp =~ _clusterName
| where errorCode != ""
| distinct errorCode, errorType, resultDetails
| project LogType="ComputeAllocationActivity", Message=pack_all();
crpLogs
| union allocationLogs
| union azSMLogs
```

**Params:** `{_startTime}`, `{_endTime}`, `{_resourceGroup}`, `{_cpAvailabilityZone}`, `{_clusterName}`

**Signal filters seen in KQL:** `operationName == "VirtualMachines.ResourceOperation.PUT"`

---

### Node ASI link

_Widget purpose:_ Links to Node/Container page (For debugging host level issues during VM deployment)

Cluster: `?` · Database: `?` · Type: `Table`

```kusto
return [{"Node ASI Link": "https://asi.azure.ms/services/NodeService/pages/NodeService_NodeView?NodeId=" + data["_nodeId"] + "&TimeOfFault=" + data["_endTime"]}];
```

**Params:** `{_startTime}`, `{_endTime}`, `{_nodeId}`

---

### EG Query

_Widget purpose:_ EG links

Cluster: `executiongraph.kusto.windows.net` · Database: `eg` · Type: `Table`

```kusto
IaasVmOperations
| where ResourceGroupName contains rgName
| project OperationName, FailureSignature, EgUrl
```

**Params:** `{rgName}`

---
