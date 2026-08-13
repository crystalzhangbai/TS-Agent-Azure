# Services on Node

> Source: EEE RDOS Start Hub dashboard (8 queries).

Use when investigating: **host agent processes (PfAgent, PilotFish, ApSvcMgr, ApLauncher, Wire Service, Node Service) crashing or stopped**. Agent failures often precede or cause container faults.

---

### Node WasChannel Health Status

_Purpose:_ Services on Node

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where nodeId == queryNodeId
| project StartTime = PreciseTimeStamp, Content = cmNodeWasChannelHealthStatus
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = case(Content == "Unhealthy", "Unhealthy", Content in ("Unresponsive", "Unknown"), "Degraded", Content == "Healthy",  "Healthy", "Neutral")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Node WillBe Channel Health Status

_Purpose:_ Services on Node

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where nodeId == queryNodeId
| project StartTime = PreciseTimeStamp, Content = cmNodeWillBeChannelHealthStatus
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = case(Content == "Unhealthy", "Unhealthy", Content in ("Unresponsive", "Unknown"), "Degraded", Content == "Healthy",  "Healthy", "Neutral")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### PfAgent Status

_Purpose:_ Services on Node

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`

```kusto
PFClientBootstrapAvailability
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where Id == queryNodeId
| project StartTime = PreciseTimeStamp, Content = iif(PfAgentUp == "True", "Up", "Down")
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = iif(Content == "Up", "healthy", "Unhealthy")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### PilotFish State

_Purpose:_ Services on Node

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`

```kusto
cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotHistoryV1
| where PreciseTimeStamp between(starttime .. endtime)
| where ResourceId == nodeid
| order by PreciseTimeStamp asc
| project PreciseTimeStamp, Tenant, ResourceId, LifecycleState, PfState, PfRepairState, HealthSummary, FaultCode, FaultDescription
| extend flag = case (prev(PfState) <> PfState, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp
| extend EndTime = case (isnotempty(next(PreciseTimeStamp)), next(PreciseTimeStamp), endtime)
| extend Content = strcat (PfState, " ", PfRepairState)
| extend Health = case (PfState == "H", "Healthy", 
    PfState in ("D", "C", "F"), "Unhealthy",
    "Degraded")
| project StartTime, EndTime, Content, Health, PfState
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

---

### ApSvcMgr Status

_Purpose:_ Services on Node

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`

```kusto
PFClientBootstrapAvailability
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where Id == queryNodeId
| project StartTime = PreciseTimeStamp, Content = iif(ApSvcMgrUp == "True", "Up", "Down")
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = iif(Content == "Up", "healthy", "Unhealthy")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### ApLauncher Status

_Purpose:_ Services on Node

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`

```kusto
PFClientBootstrapAvailability
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where Id == queryNodeId
| project StartTime = PreciseTimeStamp, Content = iif(ApLauncherUp == "True", "Up", "Down")
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Health = iif(Content == "Up", "healthy", "Unhealthy")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Node Service Status

_Purpose:_ Services on Node

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
NodeServiceEventEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project StartTime = PreciseTimeStamp, Content = strcat("PID: " , tostring(Pid)), Pid
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| extend flag = case (Content <> next(Content), "changed", flag)
| where flag <> ""
| extend EndTime = iif (isnotempty(next(StartTime)), iif (Content == next(Content), next(StartTime), StartTime), StartTime)
| extend StartTime = iif(Content == prev(Content), prev(StartTime), StartTime)
| distinct *
| project StartTime, EndTime, Content, Pid
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### WireService Status

_Purpose:_ Services on Node

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
WireserverHeartbeatEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, Status, Pid
| sort by PreciseTimeStamp asc
| serialize 
| extend prevTime = case (isnotempty(prev(PreciseTimeStamp)), prev(PreciseTimeStamp), queryFrom)
| extend prevDiff = PreciseTimeStamp - prevTime
| extend Health = case ( (prevDiff >= 62s and prevDiff != 0s and isnotempty(prev(PreciseTimeStamp))), "Unhealthy", "Healthy")
| extend flag = case (Health <> prev(Health), "changed" , "")
| where flag <> ""
| extend Content = Health
| extend StartTime  = case (isnotempty(prevTime), prevTime, queryFrom)
| extend EndTime = case (isnotempty(next(StartTime )), next(StartTime), queryTo)
| project StartTime , EndTime, Content, prevDiff, Pid
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---
