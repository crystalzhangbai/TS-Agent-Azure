# TDPR

> Source: **Azure VM Compare Investigation Guide** dashboard, chapter **TDPR** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Comparing the IFX Functions

### Azure Host VM Compare IFX Tables

_Widget purpose:_ Comparing the IFX Functions

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `TDPR > Comparing the IFX Functions`

```kusto
let operations = cluster("https://egpublic.westus.kusto.windows.net").database("eg").TDPR_OperationName2TeamServiceMap
| where Service == "StorageClient"
| distinct OperationName;
let nodeId1 = toscalar(database('AzureCP').MycroftContainerSnapshot | where PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h)) and ContainerId == containerId1 | distinct NodeId);
let nodeId2 = toscalar(database('AzureCP').MycroftContainerSnapshot | where PreciseTimeStamp between ((queryParam3 - 1h) .. (queryParam4 + 1h)) and ContainerId == containerId2 | distinct NodeId);
let allOperationsWithContainer = cluster('azcore.centralus.kusto.windows.net').database('Fa').IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and OperationName in (operations) and NodeId == nodeId1
        and  * contains containerId1;
let rootoperationIds = allOperationsWithContainer | distinct RootOperationId;
let activityIds = allOperationsWithContainer | distinct ActivityId;
let parentActivityIds = allOperationsWithContainer | distinct ParentActivityId;
let allOperationsWithContainer2 = cluster('azcore.centralus.kusto.windows.net').database('Fa').IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryParam3 .. queryParam4) and OperationName in (operations) and NodeId == nodeId2
        and  * contains containerId2;
let rootoperationIds2 = allOperationsWithContainer2 | distinct RootOperationId;
let activityIds2 = allOperationsWithContainer2 | distinct ActivityId;
let parentActivityIds2 = allOperationsWithContainer2 | distinct ParentActivityId;
cluster('azcore.centralus.kusto.windows.net').database('Fa').IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId in (nodeId1) and OperationName in (operations) and 
        (
            * contains containerId1
            or RootOperationId in (rootoperationIds)
            or ActivityId in (activityIds) or ActivityId in (parentActivityIds) or 
            ((ParentActivityId in (parentActivityIds) or ParentActivityId in (activityIds)) and ParentActivityId != "00000000-0000-0000-0000-000000000000")
            or (ParentActivityId == "00000000-0000-0000-0000-000000000000" and * contains containerId1)
        )
| project PreciseTimeStamp, OperationName, DurationInMs = DurationIn100ns / 10000.0
| summarize TotalTimeInMS = sum(DurationInMs) by OperationName
| join kind=fullouter(
    cluster('azcore.centralus.kusto.windows.net').database('Fa').IfxOperationV2v1EtwTable
    | where PreciseTimeStamp between (queryParam3 .. queryParam4) and NodeId in (nodeId2) and OperationName in (operations) and 
            (
                * contains containerId2
                or RootOperationId in (rootoperationIds2)
                or ActivityId in (activityIds2) or ActivityId in (parentActivityIds2) or 
                ((ParentActivityId in (parentActivityIds2) or ParentActivityId in (activityIds)) and ParentActivityId != "00000000-0000-0000-0000-000000000000")
                or (ParentActivityId == "00000000-0000-0000-0000-000000000000" and * contains containerId2)
            )
    | project PreciseTimeStamp, OperationName, DurationInMs = DurationIn100ns / 10000.0
    | summarize TotalTimeInMS = sum(DurationInMs) by OperationName
) on OperationName
| extend OperationName = case(isempty(OperationName), OperationName1, OperationName )
| project OperationName, TotalTimeInMS_VM1 = TotalTimeInMS, TotalTimeInMS_VM2 = TotalTimeInMS1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId1}`, `{queryParam3}`, `{queryParam4}`, `{containerId2}`

**Signal filters seen in KQL:** `Service == "StorageClient"`

---
