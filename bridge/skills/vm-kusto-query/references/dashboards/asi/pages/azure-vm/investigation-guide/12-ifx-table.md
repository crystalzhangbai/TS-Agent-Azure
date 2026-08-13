# IFX Table

> Source: **Azure Host - Azure VM** dashboard, chapter **IFX Table** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## IFX Table for the Container Operations

### Azure VM IFX Table

_Widget purpose:_ IFX Table for the Container Operations

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `IFX Table > IFX Table for the Container Operations`

**Tables:** `TDPR_OperationName2TeamServiceMap`, `IfxOperationV2v1EtwTable`
**Output columns:** `PreciseTimeStamp`, `OperationName`, `DurationInMs`, `RootOperationId`, `ActivityId`, `ParentActivityId`

```kusto
let operations = cluster("https://egpublic.westus.kusto.windows.net").database("eg").TDPR_OperationName2TeamServiceMap
| where Service == "StorageClient"
| distinct OperationName;
let allOperationsWithContainer = cluster('azcore.centralus.kusto.windows.net').database('Fa').IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and OperationName in (operations)
        and  * contains containerId;
let rootoperationIds = allOperationsWithContainer | distinct RootOperationId;
let activityIds = allOperationsWithContainer | distinct ActivityId;
let parentActivityIds = allOperationsWithContainer | distinct ParentActivityId;
cluster('azcore.centralus.kusto.windows.net').database('Fa').IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and OperationName in (operations) and 
        (
            * contains containerId
            or RootOperationId in (rootoperationIds)
            or ActivityId in (activityIds) or ActivityId in (parentActivityIds) or 
            ((ParentActivityId in (parentActivityIds) or ParentActivityId in (activityIds)) and ParentActivityId != "00000000-0000-0000-0000-000000000000")
            or (ParentActivityId == "00000000-0000-0000-0000-000000000000" and * contains containerId)
        )
| project PreciseTimeStamp, OperationName, DurationInMs = DurationIn100ns / 10000.0, RootOperationId, ActivityId, ParentActivityId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`, `{nodeId}`

**Signal filters seen in KQL:** `Service == "StorageClient"`

---
