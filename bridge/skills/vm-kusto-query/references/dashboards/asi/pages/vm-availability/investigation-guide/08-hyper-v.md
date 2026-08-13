# Hyper-V

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Hyper-V** (7 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Hyper-V

### Hyper-V Event Timeline

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Hyper-V > Hyper-V > Hyper-V Event > Hyper-V Event > Hyper-V Event Timeline`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
| where ProviderName contains "Hyper-V"
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by TimeCreated asc
| extend StartTime = TimeCreated, EndTime = datetime_add("Minute", 1, TimeCreated)
| extend GroupBy = strcat(ProviderName, " - ", EventId ), Content = ""
| extend Health = case (Level == 1, "Unhealthy", Level == 2, "Unhealthy", Level == 3, "Degraded", "Healthy")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ProviderName contains "Hyper-V"`

---

### Hyper-V Events

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V > Hyper-V > Hyper-V Event > Hyper-V Event > Hyper-V Events`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between(starttime .. endtime)
| where NodeId == nodeid
| where ProviderName contains "Hyper-V"
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by TimeCreated asc
| extend level = case (Level == 1, "critical", 
    Level == 2, "error", 
    Level == 3, "warning", 
    "info")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`, `{containerid}`

**Signal filters seen in KQL:** `ProviderName contains "Hyper-V"`

---

### VMSS Table

_Widget purpose:_ Hyper-V Worker Event

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V > Hyper-V > Hyper-V Worker > Worker > Hyper-V Worker Event`

```kusto
let hypervvmid = toscalar(cluster('azcore.centralus.kusto.windows.net').database('Fa').OsHyperVWorkerAdminEventTable
| where PreciseTimeStamp between (starttime .. endtime)
| where VmName == containerid
| top 1 by PreciseTimeStamp
| project VmId);
cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVWorkerTable
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId == nodeid
| where Message contains hypervvmid
| extend Context = parse_json(Message).Context, Operation = parse_json(Message).Operation, microseconds = todouble(parse_json(Message).Seconds) * 1000 * 1000, VmId = parse_json(Message).VmId
| project PreciseTimeStamp, Level, TaskName, Context, Operation, microseconds, Message, NodeId, VmId
| extend level = case (Level == 1, "critical",
      Level == 2, "error", 
      Level == 3, "warning",
      "info")
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{containerid}`, `{nodeid}`

---

### Hyper-V Worker Timeline

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Hyper-V > Hyper-V > Hyper-V Worker > Worker > Hyper-V Worker Timeline`

```kusto
let hypervvmid = toscalar(cluster('azcore.centralus.kusto.windows.net').database('Fa').OsHyperVWorkerAdminEventTable
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId == nodeid
| where VmName == containerid
| top 1 by PreciseTimeStamp
| project VmId);
cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVWorkerTable
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId == nodeid
| where isnotempty(hypervvmid) and Message contains hypervvmid
| where TaskName contains "TimeSpent"
| extend Context = parse_json(Message).Context, Operation = parse_json(Message).Operation, microseconds = todouble(parse_json(Message).Seconds) * 1000 * 1000, VmId = parse_json(Message).VmId
| extend EndTime = PreciseTimeStamp, StartTime = datetime_add("microsecond", - toint(microseconds), PreciseTimeStamp )
| extend Content = "", GroupBy = strcat(Context, " / ", Operation)
| extend Health = case (microseconds / 1000 / 1000 > 600, "Unhealthy", "Healthy")
| project StartTime, EndTime, Level, TaskName, Context, Operation, microseconds, Message, NodeId, VmId, Content, Health, GroupBy
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`, `{containerid}`

**Signal filters seen in KQL:** `TaskName contains "TimeSpent"`

---

### Query HyperVAnalyticEvents

Cluster: `Azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V > Hyper-V > HyperVAnalyticEvents`

```kusto
cluster('azcore.centralus').database('Fa').HyperVAnalyticEvents()
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventMessage !contains "Ignored"
| project PreciseTimeStamp, Level, EventId, ChannelName, EventMessage, Message
| extend level = case(Level == 1, "fatal", Level == 2, "error", Level == 3, "warning", "info")
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query HyperVStorageStackTable

_Widget purpose:_ HyperVStorageStackTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V > Hyper-V > HyperVHyperVAnalyticEventsStorageStackTable > HyperVStorageStackTable`

```kusto
cluster('azcore.centralus').database('Fa').HyperVStorageStackTable()
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, ProviderName, EventId, TaskName, ChannelName, EventMessage, Message, Level
| extend level = case(Level == 1, "fatal", Level == 2, "error", Level == 3, "warning", "info")
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Query HyperVVmmsTable

_Widget purpose:_ HyperVVmmsTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Hyper-V > Hyper-V > HyperVVmmsTable > HyperVVmmsTable`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVVmmsTable()
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| where EventMessage !contains "ignored"
| project PreciseTimeStamp, ProviderName, ChannelName, EventId, TaskName, EventMessage, Message, Level
| extend level = case(Level == 1, "fatal", Level == 2, "error", Level == 3, "warning", "info")
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---
