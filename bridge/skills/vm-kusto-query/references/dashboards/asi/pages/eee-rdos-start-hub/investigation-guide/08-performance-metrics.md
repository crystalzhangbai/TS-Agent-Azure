# Performance Metrics

> Source: EEE RDOS Start Hub dashboard (4 queries).

Use when investigating: **host CPU saturation, host memory pressure, container IO performance**. These return time-series for the resource consumption side of incidents.

---

### EEERDOSHostMemoryPerformance

_Purpose:_ Host Available Memory (MB)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`

```kusto
let query = strcat(@"metricNamespace('HostAgent.Counters').metric('\\Memory\\Available MBytes').dimensions('NodeID').samplingTypes('Average', 'Count') | where NodeID == '", queryNodeId, "'");
evaluate geneva_metrics_request("RDOS", query, queryFrom, queryTo)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `NodeID == "", queryNodeId, ""`

---

### HostCPUPerformance

_Purpose:_ Host CPU Utilization (%)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`

```kusto
let query = strcat(@"metricNamespace('OS.Counters').metric('\\Hyper-V Hypervisor Root Virtual Processor(_Total)\\% Total Run Time').dimensions('NodeID').samplingTypes('Average', 'Count') | where NodeID == '", queryNodeId, "'");
evaluate geneva_metrics_request("RDOS", query, queryFrom, queryTo)
| where column_ifexists("Count", 0) > 0
| project TimestampUtc = column_ifexists("TimestampUtc", 0), Average = column_ifexists("Average", 0)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `NodeID == "", queryNodeId, ""`

---

### ContainerPerformance

_Purpose:_ Performance Metrics (Node View)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (starttime .. endtime)
| where VmId == containerid
| project PreciseTimeStamp, Cluster, TenantId, NodeId, VmId, RoleId, RoleInstanceId, CounterName, SampleCount, AverageCounterValue, MinCounterValue, MaxCounterValue
| summarize sum(AverageCounterValue) by PreciseTimeStamp, CounterName
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{containerid}`

---

### Container Performance Shoebox

_Purpose:_ Performance Metrics (Shoebox View)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').VmShoeboxCounterTable
| where PreciseTimeStamp between (starttime .. endtime)
| where NodeId  == nodeid
| where VmId == containerid
| project PreciseTimeStamp, Cluster, RoleInstanceId, VmResourceType, MDMCounterName, MDMAccountName, DurationInMinutes, AverageValue
| project PreciseTimeStamp, MDMCounterName, AverageValue
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`, `{containerid}`

---
