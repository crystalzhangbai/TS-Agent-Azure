# TDPR

> Source: **Azure Host Compare Investigation Guide** dashboard, chapter **TDPR** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## {{nodeId1}} TDPR Stats

### Azure Host TDPR

_Widget purpose:_ {{nodeId1}} TDPR Stats

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `TDPR > {{nodeId1}} TDPR Stats`

```kusto
let operations = cluster("https://egpublic.westus.kusto.windows.net").database("eg").TDPR_OperationName2TeamServiceMap
| where Service == "StorageClient"
| distinct OperationName;
cluster('azcore.centralus.kusto.windows.net').database('Fa').IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and OperationName in (operations)
| project PreciseTimeStamp, OperationName, DurationInMs = DurationIn100ns / 10000.0, RootOperationId, ActivityId, ParentActivityId
| summarize sum(DurationInMs) by bin(PreciseTimeStamp, 1m), OperationName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

**Signal filters seen in KQL:** `Service == "StorageClient"`

---

## {{nodeId2}} TDPR Stats

### Azure Host TDPR

_Widget purpose:_ {{nodeId2}} TDPR Stats

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `TDPR > {{nodeId2}} TDPR Stats`

```kusto
let operations = cluster("https://egpublic.westus.kusto.windows.net").database("eg").TDPR_OperationName2TeamServiceMap
| where Service == "StorageClient"
| distinct OperationName;
cluster('azcore.centralus.kusto.windows.net').database('Fa').IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == nodeId and OperationName in (operations)
| project PreciseTimeStamp, OperationName, DurationInMs = DurationIn100ns / 10000.0, RootOperationId, ActivityId, ParentActivityId
| summarize sum(DurationInMs) by bin(PreciseTimeStamp, 1m), OperationName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

**Signal filters seen in KQL:** `Service == "StorageClient"`

---
