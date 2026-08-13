# Timeline of Startup Table

> Source: **Azure Host — Azure Host Node** dashboard, chapter **Timeline of Startup Table** (5 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Node Health

_Widget purpose:_ Timeline of Startup Table

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Timeline of Startup Table`

```kusto
cluster('azurecm').database('AzureCM').
LogNodeSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeId == nodeid
| extend Health = case(nodeState == "Ready", "Healthy", nodeState == "Unhealthy", "Unhealthy", nodeState in ("HumanInvestigate", "PoweringOn"), "Unhealthy",  "Neutral")
| project StartTime = PreciseTimeStamp, Content = nodeAvailabilityState, Health
| summarize argmax(StartTime, Content, Health) by bin(StartTime, 60s)
| project-away max_StartTime
| project StartTime, Content = max_StartTime_Content, Health = max_StartTime_Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### NodeWorkflow Timeline

_Widget purpose:_ Timeline of Startup Table

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Timeline of Startup Table`

```kusto
cluster('azurecm.kusto.windows.net').database('AzureCM').
NodeWorkflowDurationDetails
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeId == nodeid
| extend StartTime = PreciseTimeStamp
| extend Content = workflowStep
| extend EndTime = StartTime + toreal(workflowDuration) * 1s
| project StartTime, EndTime, nodeId, Content, workflowDuration, agentStatus, configuredTimeoutSeconds, retryAttemptCount, lastAttemptStatusCode
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### Agent Start Operations Details

_Widget purpose:_ Timeline of Startup Table

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Timeline of Startup Table`

```kusto
cluster('azcore.centralus').database('Fa').
AgentStartOperationsPerformanceEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == nodeid
| extend duration = EndTime - StartTime
| project Cluster, NodeId, PreciseTimeStamp, StartTime, EndTime, duration, Content = Operation, AgentPackage
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### Container Workflow Details

_Widget purpose:_ Timeline of Startup Table

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Timeline of Startup Table`

```kusto
cluster('azurecm').database('AzureCM').
ContainerWorkflowDurationDetails
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeId == nodeid
| extend EndTime = PreciseTimeStamp + toreal(workflowDuration) * 1s
| project StartTime = PreciseTimeStamp, EndTime, nodeId, Content = workflowStep, workflowDuration, agentStatus, configuredTimeoutSeconds, retryAttemptCount, lastAttemptStatusCode
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

---

### IFxOperationV2 Table

_Widget purpose:_ Timeline of Startup Table

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Timeline of Startup Table`

```kusto
cluster('azcore.centralus').database('Fa').
IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == nodeid
| extend Time = DurationIn100ns/10000000.0
| extend StartTime = TIMESTAMP-(Time*1s)
| extend Time = DurationIn100ns/10000000.0
| extend StartTime = TIMESTAMP-(Time*1s)
| project StartTime, EndTime=TIMESTAMP, Content = OperationName, NodeId, Region, ResultType, Time, ResultSignature, ContextInCsv, RoleBuildNumber //, ActivityId, ParentActivityId, RootOperationId
| order by StartTime asc  
| where RoleBuildNumber contains "HostAgent"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

**Signal filters seen in KQL:** `RoleBuildNumber contains "HostAgent"`

---
