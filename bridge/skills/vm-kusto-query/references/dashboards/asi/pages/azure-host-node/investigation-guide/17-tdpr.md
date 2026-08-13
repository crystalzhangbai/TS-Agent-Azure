# TDPR

> Source: **Azure Host — Azure Host Node** dashboard, chapter **TDPR** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Deployment EG

### Azure Host EG Telemetry 

_Widget purpose:_ IaasVmOperations

Cluster: `egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `Table`
Source panel: `TDPR > Deployment EG > Deployment EG > IaasVmOperations`

```kusto
IaasVmOperations
| where StartTime between (startTime .. endTime) and NodeId == nodeId
| project StartTime, OperationName, ContainerId, OsBlobUri, OsDiskStorageAccountType, NodeId, PrefetchDurationInSeconds, VmBootDurationInSeconds, ProvisioningDurationInSeconds, EgId, FailureSignature, E2EDurationInSeconds
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Host Storage IFX

### Azure VM IFX Table

_Widget purpose:_ IFX Tables

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `TDPR > Host Storage IFX > IFX Tables`

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
