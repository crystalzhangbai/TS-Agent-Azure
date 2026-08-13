# Host Tables

> Source: **Azure Host Compare Investigation Guide** dashboard, chapter **Host Tables** (5 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## HighCPU Table

### Azure Host HighCPUTable

_Widget purpose:_ HighCPU Table for {{nodeId1}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > HighCPU Table > HighCPU Table for {{nodeId1}}`

```kusto
HighCpuCounterNodeTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, CounterName, CounterValue
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

### Azure Host HighCPUTable

_Widget purpose:_ HighCPU Table for {{nodeId2}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > HighCPU Table > HighCPU Table for {{nodeId2}}`

```kusto
HighCpuCounterNodeTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| project PreciseTimeStamp, CounterName, CounterValue
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

---

## Windows Event Table

### Azure Host Compare Windows Event Comparison

_Widget purpose:_ Windows Events Count

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > Windows Event Table > Comparison > Windows Events Count`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId ==  nodeId1
| summarize CountInNode1 = count() by ProviderName, EventId
| join kind=fullouter (
    cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
    | where PreciseTimeStamp between (Time2From .. Time2To) and NodeId ==  nodeId2
    | summarize CountInNode2 = count() by ProviderName, EventId
) on ProviderName, EventId
| extend level = case(CountInNode1 != CountInNode2, "warning", "info")
| sort by level desc
| extend ProviderName = case(isempty(ProviderName), ProviderName1, ProviderName),
         EventId = case(isempty(EventId), EventId1, EventId)
| project-away ProviderName1, EventId1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId1}`, `{Time2From}`, `{Time2To}`, `{nodeId2}`

---

### Azure Host WindowsEventTable

_Widget purpose:_ Host Events {{nodeId1}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > Windows Event Table > Events > Host Events {{nodeId1}}`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where EventId !in ('0','3095') 
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project TimeCreated = todatetime(TimeCreated), Id = EventId, ProviderName, Message = Description, level
| sort by TimeCreated asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Azure Host WindowsEventTable

_Widget purpose:_ Host Events {{nodeId2}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Host Tables > Windows Event Table > Events > Host Events {{nodeId2}}`

```kusto
WindowsEventTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId
| where EventId !in ('0','3095') 
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project TimeCreated = todatetime(TimeCreated), Id = EventId, ProviderName, Message = Description, level
| sort by TimeCreated asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---
