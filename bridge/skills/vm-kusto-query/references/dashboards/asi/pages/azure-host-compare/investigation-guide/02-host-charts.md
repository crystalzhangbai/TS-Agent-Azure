# Host Charts

> Source: **Azure Host Compare Investigation Guide** dashboard, chapter **Host Charts** (10 queries across 10 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Available Memory {{nodeId1}}

### Azure Host Node Available Memory

_Widget purpose:_ Available Memory {{nodeId1}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Available Memory {{nodeId1}}`

```kusto
let query = strcat(@"metricNamespace('HostAgent.Counters').metric('\\Memory\\Available MBytes').dimensions('NodeID','Cluster').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

## Available Memory {{nodeId2}}

### Azure Host Node Available Memory

_Widget purpose:_ Available Memory {{nodeId2}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Available Memory {{nodeId2}}`

```kusto
let query = strcat(@"metricNamespace('HostAgent.Counters').metric('\\Memory\\Available MBytes').dimensions('NodeID','Cluster').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

## Host CPU Node 1 ({{nodeId1}})

### Azure Host VP CPU

_Widget purpose:_ Host CPU Node 1 ({{nodeId1}})

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Host CPU Node 1 ({{nodeId1}})`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\Hyper-V Hypervisor Root Virtual Processor(_Total)\\% Total Run Time').dimensions('NodeID').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

## Host CPU Node 2 ({{nodeId2}})

### Azure Host VP CPU

_Widget purpose:_ Host CPU Node 2 ({{nodeId2}})

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Host CPU Node 2 ({{nodeId2}})`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\Hyper-V Hypervisor Root Virtual Processor(_Total)\\% Total Run Time').dimensions('NodeID').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

## Jitter Trend for {{nodeId1}}

### CPU Jitter (High granularity)

_Widget purpose:_ Jitter Trend for {{nodeId1}}

Cluster: `intmgmtshared.centralus.kusto.windows.net` · Database: `Fleet` · Type: `TimeSeries`
Source panel: `Host Charts > Jitter Trend for {{nodeId1}}`

```kusto
NodeCpuJitterBaseView_prod(startTime, endTime) 
| where  NodeId =~ nodeId 
| project Timestamp, nodeCpuJitterScoreV1 = CpuJitterScoreV1
| render timechart
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## Jitter Trend for {{nodeId2}}

### CPU Jitter (High granularity)

_Widget purpose:_ Jitter Trend for {{nodeId2}}

Cluster: `intmgmtshared.centralus.kusto.windows.net` · Database: `Fleet` · Type: `TimeSeries`
Source panel: `Host Charts > Jitter Trend for {{nodeId2}}`

```kusto
NodeCpuJitterBaseView_prod(startTime, endTime) 
| where  NodeId =~ nodeId 
| project Timestamp, nodeCpuJitterScoreV1 = CpuJitterScoreV1
| render timechart
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## Nonpaged Pool Bytes for {{nodeId1}}

### Azure Host Node NPP Bytes

_Widget purpose:_ Nonpaged Pool Bytes for {{nodeId1}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Nonpaged Pool Bytes for {{nodeId1}}`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\Memory\\Pool Nonpaged Bytes').dimensions('NodeID','Cluster').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

## Nonpaged Pool Bytes for {{nodeId2}}

### Azure Host Node NPP Bytes

_Widget purpose:_ Nonpaged Pool Bytes for {{nodeId2}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Nonpaged Pool Bytes for {{nodeId2}}`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\Memory\\Pool Nonpaged Bytes').dimensions('NodeID','Cluster').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

## Process Total Handle Count for {{nodeId1}}

### Azure Host Node Process Handle Count

_Widget purpose:_ Process Total Handle Count for {{nodeId1}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Process Total Handle Count for {{nodeId1}}`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\Process(_Total)\\Handle Count').dimensions('NodeID','Cluster').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---

## Process Total Handle Count for {{nodeId2}}

### Azure Host Node Process Handle Count

_Widget purpose:_ Process Total Handle Count for {{nodeId2}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Charts > Process Total Handle Count for {{nodeId2}}`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\Process(_Total)\\Handle Count').dimensions('NodeID','Cluster').samplingTypes('Average', 'Count') | where NodeID == '", nodeId, "'");
evaluate geneva_metrics_request("RDOS", query, startTime, endTime)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `NodeID == "", nodeId, ""`

---
