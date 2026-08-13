# RemoteDataAccess RPC Latencies

> Source: **NRP - ReadOperationService** dashboard, chapter **RemoteDataAccess RPC Latencies** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ReadOperationService RPC Latency

_Widget purpose:_ RemoteDataAccess RPC Latencies

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `RemoteDataAccess RPC Latencies`

```kusto
let serverSideRequests = FrontendOperationEtwEvent
| where Region == "useast2euap"
| where SourceAssemblyFileVersion contains_cs ".rc"
| where PreciseTimeStamp between(queryFrom..queryTo)
| where EventCode == "RemoteDataAccessServerDuration"
| where OperationName == "RemoteDataAccessService"
| parse Message with "RemoteDataAccessServer completed: "repositoryOperation" for requestId "requestId" in "serverExecutionTime:timespan 
| project PreciseTimeStamp, ServerRole=RoleInstance, repositoryOperation, requestId, serverExecutionTime;
let clientSideRequests = FrontendReadOperationEtwEvent
| where Region == "useast2euap"
| where SourceAssemblyFileVersion contains_cs ".readoperations"
| where PreciseTimeStamp between(queryFrom..queryTo)
| where EventCode == "RemoteDataAccessClientDuration"
| parse Message with "RemoteDataClient completed: "clientRepositoryOperation" for requestId "requestId" in "clientExecutionTime:timespan ", attempts: "*
| project PreciseTimeStamp, ClientRole=RoleInstance, clientRepositoryOperation, requestId, clientExecutionTime;
serverSideRequests
| join clientSideRequests on requestId
| extend networkingOverhead = (clientExecutionTime - serverExecutionTime) / 1ms
| project PreciseTimeStamp1, repositoryOperation, requestId, clientExecutionTime, serverExecutionTime, networkingOverhead, ServerRole, ClientRole
| summarize percentiles=percentiles(networkingOverhead, 50, 75, 95, 99, 99.9), samples=count() by repositoryOperation
| project-rename p50=percentiles, p75=percentile_networkingOverhead_75, p95=percentile_networkingOverhead_95, p99=percentile_networkingOverhead_99, p99_9=percentile_networkingOverhead_99_9
| order by p99 desc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `Region == "useast2euap"` · `EventCode == "RemoteDataAccessServerDuration"` · `OperationName == "RemoteDataAccessService"` · `EventCode == "RemoteDataAccessClientDuration"`

---
