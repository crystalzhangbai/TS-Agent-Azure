# VM Counters — Shoebox

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Counters** (26 queries, part 6 of 7).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values.

---

## Shoebox

### Azure Host VM Shoebox Read MBytes Sec

_Widget purpose:_ Per Disk (LUN) Read MBytes/sec Average by minute

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk Bandwidth > Disk Bandwidth > Per Disk (LUN) Read MBytes/sec Average by minute`

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `MBPS`

```kusto
let counter = "Read Bytes/Sec";
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_osdisk, startTime, endTime);
let dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_datadisk, startTime, endTime);
let tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_tempdisk, startTime, endTime);
union theSchema, osDiskMetrics
| extend LUN = "OS Disk"
| union dataDiskMetrics
| union ( tempDiskMetrics | extend LUN = "Temp" )
| where isnotempty(TimestampUtc)
| extend BPS = column_ifexists("Max",0)
| project TimestampUtc, tostring(LUN), MBPS = BPS / 1000000.00
```

**Params:** `{startTime}`, `{endTime}`, `{shoeboxAccount}`, `{vmId}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Write Bytes Sec

_Widget purpose:_ Per Disk (LUN) Write MBytes/sec Average by minute

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk Bandwidth > Disk Bandwidth > Per Disk (LUN) Write MBytes/sec Average by minute`

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `MBPS`

```kusto
let counter = "Write Bytes/sec";
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_osdisk, startTime, endTime);
let dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_datadisk, startTime, endTime);
let tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_tempdisk, startTime, endTime);
union theSchema, osDiskMetrics
| extend LUN = "OS Disk"
| union dataDiskMetrics
| union ( tempDiskMetrics | extend LUN = "Temp" )
| where isnotempty(TimestampUtc)
| extend BPS = column_ifexists("Max",0)
| project TimestampUtc, tostring(LUN), MBPS = BPS / 1000000.00
```

**Params:** `{startTime}`, `{endTime}`, `{shoeboxAccount}`, `{vmId}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Burst BPS Credit

_Widget purpose:_ Per Disk (LUN) Burst BPS Credits Percentage

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk Bursting > Disk Bursting > Per Disk (LUN) Burst BPS Credits Percentage`

**Output columns:** `TimestampUtc`, `LUN`, `Average`

```kusto
let counter = "Used Burst BPS Credits Percentage";
let query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
evaluate geneva_metrics_request(shoeboxAccount, query_datadisk, startTime, endTime)
| project TimestampUtc, LUN = column_ifexists("LUN", ""), Average = tolong(column_ifexists("Average", 0))
| union(
    evaluate geneva_metrics_request(shoeboxAccount, query_osdisk, startTime, endTime)
    | project TimestampUtc, LUN = "OSDisk", Average = tolong(column_ifexists("Average", 0))
)
| where isnotempty(TimestampUtc)
```

**Params:** `{startTime}`, `{endTime}`, `{shoeboxAccount}`, `{vmId}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Disk Bursting IO Credits

_Widget purpose:_ Per Disk (LUN) Burst IO Credits Percentage

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk Bursting > Disk Bursting > Per Disk (LUN) Burst IO Credits Percentage`

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `Average`

```kusto
let counter = "Used Burst IO Credits Percentage";
let query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
evaluate geneva_metrics_request(shoeboxAccount, query_datadisk, startTime, endTime)
| project TimestampUtc, LUN = column_ifexists("LUN", ""), Average = tolong(column_ifexists("Average", 0))
| union(
    evaluate geneva_metrics_request(shoeboxAccount, query_osdisk, startTime, endTime)
    | project TimestampUtc, LUN = "OSDisk", Average = tolong(column_ifexists("Average", 0))
)
| where isnotempty(TimestampUtc)
| project TimestampUtc, tostring(LUN), Average
```

**Params:** `{startTime}`, `{endTime}`, `{shoeboxAccount}`, `{vmId}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Cache Hit

_Widget purpose:_ Per Disk (LUN) Cache Hit Percentage (per 5 mins)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk Cache Hit > Disk Cache Hit > Per Disk (LUN) Cache Hit Percentage (per 5 mins)`

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `Average`

```kusto
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Premium Data Disk Cache Read Hit').dimensions('ResourceId', 'LUN').samplingTypes('Average', 'Count') | where ResourceId == '", vmId, "'");
let query_osdisk = strcat(@"metricNamespace('Shoebox').metric('Premium OS Disk Cache Read Hit').dimensions('ResourceId').samplingTypes('Average', 'Count') | where ResourceId == '", vmId, "'");
let osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_osdisk, startTime, endTime);
let dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_datadisk, startTime, endTime);
union theSchema, osDiskMetrics
| extend LUN = "OS Disk"
| union dataDiskMetrics
| where isnotempty(TimestampUtc)
| extend Count = column_ifexists("Count",0)
| where Count > 0
| extend Average = column_ifexists("Average",0)
| project TimestampUtc, tostring(LUN), Average
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Read IOPS

_Widget purpose:_ Per Disk (LUN) Read IOPS by minute

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk IOPS > Disk IOPS > Per Disk (LUN) Read IOPS by minute`

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `ReadIOPS`

```kusto
let counter = "Read Operations/Sec";
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_osdisk, startTime, endTime);
let dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_datadisk, startTime, endTime);
let tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_tempdisk, startTime, endTime);
union theSchema, osDiskMetrics
| extend LUN = "OS Disk"
| union dataDiskMetrics
| union ( tempDiskMetrics | extend LUN = "Temp" )
| where isnotempty(TimestampUtc)
| extend Max = column_ifexists("Max",0)
| project TimestampUtc, tostring(LUN), ReadIOPS = Max
```

**Params:** `{startTime}`, `{endTime}`, `{shoeboxAccount}`, `{vmId}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Write IOPS

_Widget purpose:_ Per Disk (LUN) Write IOPS by minute

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk IOPS > Disk IOPS > Per Disk (LUN) Write IOPS by minute`

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `WriteIOPS`

```kusto
let counter = "Write Operations/Sec";
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_osdisk, startTime, endTime);
let dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_datadisk, startTime, endTime);
let tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_tempdisk, startTime, endTime);
union theSchema, osDiskMetrics
| extend LUN = "OS Disk"
| union dataDiskMetrics
| union ( tempDiskMetrics | extend LUN = "Temp" )
| where isnotempty(TimestampUtc)
| extend Max = column_ifexists("Max",0)
| project TimestampUtc, tostring(LUN), WriteIOPS = Max
```

**Params:** `{startTime}`, `{endTime}`, `{shoeboxAccount}`, `{vmId}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Disk Latency

_Widget purpose:_ Disk Latency 

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk Latency (Preview) > Disk Latency `

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `Latency`

```kusto
let counter = "Latency";
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_osdisk, startTime, endTime);
let dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_datadisk, startTime, endTime);
let tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_tempdisk, startTime, endTime);
union theSchema, osDiskMetrics
| extend LUN = "OS Disk"
| union dataDiskMetrics
| union ( tempDiskMetrics | extend LUN = "Temp" )
| where isnotempty(TimestampUtc)
| extend Latency = column_ifexists("Max",0)
| project TimestampUtc, tostring(LUN), Latency
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Queue Depth

_Widget purpose:_ Per Disk (LUN) Queue Depth Average by minute

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk QD > Disk QD > Per Disk (LUN) Queue Depth Average by minute`

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `QD`

```kusto
let counter = "Queue Depth";
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_osdisk, startTime, endTime);
let dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_datadisk, startTime, endTime);
let tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_tempdisk, startTime, endTime);
union theSchema, osDiskMetrics
| extend LUN = "OS Disk"
| union dataDiskMetrics
| union ( tempDiskMetrics | extend LUN = "Temp" )
| where isnotempty(TimestampUtc)
| extend Max = column_ifexists("Max",0)
| project TimestampUtc, tostring(LUN), QD = Max
```

**Params:** `{startTime}`, `{endTime}`, `{shoeboxAccount}`, `{vmId}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### DiskBurstBPSMetrics

_Widget purpose:_ Disk Burst BPS Percentage Counters (Uncached)

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Burst BPS Percentage Counters (Uncached)`

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `Average`

```kusto
let theSchema = datatable (TimestampUtc: datetime,  i_MetricName: real, LUN: string, Average: real) [];
let counterBps = "Used Burst BPS Credits Percentage";
let query_osdiskbpsconsumed = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counterBps, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let query_datadiskbpsconsumed = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counterBps, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let osDiskMetricsBps = evaluate geneva_metrics_request(shoeboxAccount, query_osdiskbpsconsumed, startTime, endTime);
let dataDiskMetricsBps = evaluate geneva_metrics_request(shoeboxAccount, query_datadiskbpsconsumed, startTime, endTime);
union theSchema, osDiskMetricsBps, dataDiskMetricsBps
| where isnotempty(TimestampUtc)
| extend Average = column_ifexists("Average",0)
| project TimestampUtc, tostring(LUN), Average
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### DiskBurstIOPSMetrics

_Widget purpose:_ Disk Burst IOPS Percentage Counters (Uncached)

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Burst IOPS Percentage Counters (Uncached)`

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `Average`

```kusto
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let counterIops = "Used Burst IO Credits Percentage";
let query_osdiskiopsconsumed = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counterIops, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let query_datadiskiopsconsumed = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counterIops, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let osDiskMetricsIops = evaluate geneva_metrics_request(shoeboxAccount, query_osdiskiopsconsumed, startTime, endTime);
let dataDiskMetricsIops = evaluate geneva_metrics_request(shoeboxAccount, query_datadiskiopsconsumed, startTime, endTime);
union theSchema, osDiskMetricsIops, dataDiskMetricsIops
//| extend LUN = "OS Disk"
| where isnotempty(TimestampUtc)
| extend Average = column_ifexists("Average",0)
| project TimestampUtc, tostring(LUN), Average
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Disk Bandwidth Consumed Percentage

_Widget purpose:_ Per Disk (LUN) Bandwidth Consumed Percentage by minute (Uncached)

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Percentage > Per Disk (LUN) Bandwidth Consumed Percentage by minute (Uncached)`

**Output columns:** `TimestampUtc`, `tostring(LUN)`, `Average`

```kusto
let counter = "Bandwidth Consumed Percentage";
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let query_datadiskbandwidthconsumed = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let query_osdiskbandwidthconsumed = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_osdiskbandwidthconsumed, startTime, endTime);
let dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_datadiskbandwidthconsumed, startTime, endTime);
union theSchema, osDiskMetrics
| extend LUN = "OS Disk"
| union dataDiskMetrics
| where isnotempty(TimestampUtc)
| extend Average = column_ifexists("Average",0)
| project TimestampUtc, tostring(LUN), Average
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Disk IOPS Consumed Percentage

_Widget purpose:_ Per Disk (LUN) IOPS Consumed Percentage by minute (Uncached)

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Disk Used Percentage > Disk Percentage > Per Disk (LUN) IOPS Consumed Percentage by minute (Uncached)`

**Output columns:** `TimestampUtc`, `tostring(LUN)`

```kusto
let counter = "IOPS Consumed Percentage";
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let query_datadiskiopsconsumed = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_osdiskiopsconsumed = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_osdiskiopsconsumed, startTime, endTime);
let dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_datadiskiopsconsumed, startTime, endTime);
union theSchema, osDiskMetrics
| extend LUN = "OS Disk"
| union dataDiskMetrics
| where isnotempty(TimestampUtc)
| extend Max = column_ifexists("Max",0)
| project TimestampUtc, tostring(LUN), Max
```

**Params:** `{startTime}`, `{endTime}`, `{shoeboxAccount}`, `{vmId}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Insights

_Widget purpose:_ Shoebox Insights

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `VM Counters > Shoebox > Shoebox > Info > Shoebox Insights`

**Output columns:** `PreciseTimeStamp`, `Message`, `EventName`, `level`

```kusto
StorageClientInsightsForContainer2(containerId, nodeId, startTime, endTime)
| where Message contains "shoebox"
| project PreciseTimeStamp, Message, EventName, level = case(EventName contains "Update", "warning", "error")
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

**Signal filters seen in KQL:** `Message contains "shoebox"`

---

### Azure Host VM Shoebox Inbound Flows

_Widget purpose:_ Inbound Flows

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Networking > Networking > Inbound Flows`

**Output columns:** `TimestampUtc`

```kusto
let counter = "Inbound Flows";
let query = strcat(@"metricNamespace('Shoebox').metric('", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let mdmMetrics = evaluate geneva_metrics_request(shoeboxAccount, query, startTime, endTime);
mdmMetrics
| where isnotempty(TimestampUtc)
| extend Max = column_ifexists("Max",0)
| project TimestampUtc, Max
```

**Params:** `{vmId}`, `{shoeboxAccount}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Network InOut Bytes

_Widget purpose:_ Network In (Megabits per second)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Networking > Networking > Network In (Megabits per second)`

**Output columns:** `TimestampUtc1`

```kusto
let query_vmnetworkin = strcat(@"metricNamespace('Shoebox').metric('Network In Total').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_vmnetworkout = strcat(@"metricNamespace('Shoebox').metric('Network Out Total').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
evaluate geneva_metrics_request(shoeboxAccount, query_vmnetworkin, startTime, endTime)
| project TimestampUtc, NetworkIn = column_ifexists("Max",0) * 1.33 * 0.0000001
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmnetworkout, startTime, endTime)
    | project TimestampUtc, NetworkOut = column_ifexists("Max",0) * 1.33 * 0.0000001
) on TimestampUtc
| project-away TimestampUtc1
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Network InOut Bytes

_Widget purpose:_ Network Out (Megabits per second)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Networking > Networking > Network Out (Megabits per second)`

**Output columns:** `TimestampUtc1`

```kusto
let query_vmnetworkin = strcat(@"metricNamespace('Shoebox').metric('Network In Total').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_vmnetworkout = strcat(@"metricNamespace('Shoebox').metric('Network Out Total').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
evaluate geneva_metrics_request(shoeboxAccount, query_vmnetworkin, startTime, endTime)
| project TimestampUtc, NetworkIn = column_ifexists("Max",0) * 1.33 * 0.0000001
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmnetworkout, startTime, endTime)
    | project TimestampUtc, NetworkOut = column_ifexists("Max",0) * 1.33 * 0.0000001
) on TimestampUtc
| project-away TimestampUtc1
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Outbound Flows

_Widget purpose:_ Outbound Flows

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > Networking > Networking > Outbound Flows`

**Output columns:** `TimestampUtc`

```kusto
let counter = "Outbound Flows";
let query = strcat(@"metricNamespace('Shoebox').metric('", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let mdmMetrics = evaluate geneva_metrics_request(shoeboxAccount, query, startTime, endTime);
mdmMetrics
| where isnotempty(TimestampUtc)
| extend Max = column_ifexists("Max",0)
| project TimestampUtc, Max
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox CPU Credits

_Widget purpose:_ CPU Credits

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > VM CPU > CPU Credits`

**Output columns:** `TimestampUtc`, `CPUCredits`

```kusto
let query_cpu_credits = strcat(@"metricNamespace('Shoebox').metric('CPU Credits Remaining').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
evaluate geneva_metrics_request(shoeboxAccount, query_cpu_credits, startTime, endTime)
| project TimestampUtc, CPUCredits = column_ifexists("Average",0)
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Disk Consumed Percentage

_Widget purpose:_ CPU Percentage

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > VM CPU > CPU Percentage`

**Output columns:** `TimestampUtc1`, `TimestampUtc2`, `TimestampUtc3`, `TimestampUtc4`

```kusto
let query_vmcachediops = strcat(@"metricNamespace('Shoebox').metric('VM Cached IOPS Consumed Percentage').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_vmuncachediops = strcat(@"metricNamespace('Shoebox').metric('VM UnCached IOPS Consumed Percentage').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_vmcachedband = strcat(@"metricNamespace('Shoebox').metric('VM Cached Bandwidth Consumed Percentage').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_vmuncachedband = strcat(@"metricNamespace('Shoebox').metric('VM UnCached Bandwidth Consumed Percentage').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_cpu = strcat(@"metricNamespace('Shoebox').metric('Percentage CPU').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
evaluate geneva_metrics_request(shoeboxAccount, query_cpu, startTime, endTime)
| project TimestampUtc, AvgCPU = column_ifexists("Average",0), MaxCPU = column_ifexists("Max",0)
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmcachediops, startTime, endTime)
    | project TimestampUtc, VMCachedIOPSPercentage = column_ifexists("Max",0)
) on TimestampUtc
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmuncachediops, startTime, endTime)
    | project TimestampUtc, VMUnCachedIOPSPercentage = column_ifexists("Max",0)
) on TimestampUtc
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmcachedband, startTime, endTime)
    | project TimestampUtc, VMCachedMBPSPercentage = column_ifexists("Max",0)
) on TimestampUtc
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmuncachedband, startTime, endTime)
    | project TimestampUtc, VMUnCachedMBPSPercentage = column_ifexists("Max",0)
) on TimestampUtc
| where isnotempty(TimestampUtc)
| project-away TimestampUtc1, TimestampUtc2, TimestampUtc3, TimestampUtc4
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox VM Burst Consumed Percentage

_Widget purpose:_ VM Burst Percentage Counters

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > VM Disk Limits > VM Percentage > VM Burst Percentage Counters`

**Aggregations:** `summarize LocalBurstBPSPercentage = max(LocalBurstBPSPercentage), LocalBurstIOPSPercentage by bin(TimestampUtc, 5m)`
**Output columns:** `TimestampUtc`, `RemoteBurstIOPSPercentage`

```kusto
let query_vmremoteiops = strcat(@"metricNamespace('Shoebox').metric('VM Remote Used Burst IO Credits Percentage').dimensions('ResourceId').samplingTypes('Average', 'Count') | where ResourceId == '", vmId, "'");
let query_vmremotbps = strcat(@"metricNamespace('Shoebox').metric('VM Remote Used Burst BPS Credits Percentage').dimensions('ResourceId').samplingTypes('Average', 'Count') | where ResourceId == '", vmId, "'");
let query_vmlocaliops = strcat(@"metricNamespace('Shoebox').metric('VM Local Used Burst IO Credits Percentage').dimensions('ResourceId').samplingTypes('Average', 'Count') | where ResourceId == '", vmId, "'");
let query_vmlocalbps = strcat(@"metricNamespace('Shoebox').metric('VM Local Used Burst BPS Credits Percentage').dimensions('ResourceId').samplingTypes('Average', 'Count') | where ResourceId == '", vmId, "'");
evaluate geneva_metrics_request(shoeboxAccount, query_vmremoteiops, startTime, endTime)
| extend Count = column_ifexists("Count",0)
| where Count > 0
| project TimestampUtc, RemoteBurstIOPSPercentage = column_ifexists("Average",0)
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmremotbps, startTime, endTime)
    | extend Count = column_ifexists("Count",0)
    | where Count > 0
    | project TimestampUtc, RemoteBurstBPSPercentage = column_ifexists("Average",0)
) on TimestampUtc
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmlocaliops, startTime, endTime)
    | extend Count = column_ifexists("Count",0)
    | where Count > 0
    | project TimestampUtc, LocalBurstIOPSPercentage = column_ifexists("Average",0)
) on TimestampUtc
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmlocalbps, startTime, endTime)
    | extend Count = column_ifexists("Count",0)
    | where Count > 0
    | project TimestampUtc, LocalBurstBPSPercentage = column_ifexists("Average",0)
) on TimestampUtc
| extend TimestampUtc = case(isnotempty(TimestampUtc1), TimestampUtc1,isnotempty(TimestampUtc2), TimestampUtc2,isnotempty(TimestampUtc3), TimestampUtc3,TimestampUtc)
| summarize LocalBurstBPSPercentage = max(LocalBurstBPSPercentage), LocalBurstIOPSPercentage = max(LocalBurstIOPSPercentage), 
            RemoteBurstBPSPercentage = max(RemoteBurstBPSPercentage), RemoteBurstIOPSPercentage = max(RemoteBurstIOPSPercentage) by bin(TimestampUtc, 5m)
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Disk Consumed Percentage

_Widget purpose:_ VM Shoebox Percentage Counters

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > VM Disk Limits > VM Percentage > VM Shoebox Percentage Counters`

**Output columns:** `TimestampUtc1`, `TimestampUtc2`, `TimestampUtc3`, `TimestampUtc4`

```kusto
let query_vmcachediops = strcat(@"metricNamespace('Shoebox').metric('VM Cached IOPS Consumed Percentage').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_vmuncachediops = strcat(@"metricNamespace('Shoebox').metric('VM UnCached IOPS Consumed Percentage').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_vmcachedband = strcat(@"metricNamespace('Shoebox').metric('VM Cached Bandwidth Consumed Percentage').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_vmuncachedband = strcat(@"metricNamespace('Shoebox').metric('VM UnCached Bandwidth Consumed Percentage').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
let query_cpu = strcat(@"metricNamespace('Shoebox').metric('Percentage CPU').dimensions('ResourceId').samplingTypes('Average','Max') | where ResourceId == '", vmId, "'");
evaluate geneva_metrics_request(shoeboxAccount, query_cpu, startTime, endTime)
| project TimestampUtc, AvgCPU = column_ifexists("Average",0), MaxCPU = column_ifexists("Max",0)
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmcachediops, startTime, endTime)
    | project TimestampUtc, VMCachedIOPSPercentage = column_ifexists("Max",0)
) on TimestampUtc
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmuncachediops, startTime, endTime)
    | project TimestampUtc, VMUnCachedIOPSPercentage = column_ifexists("Max",0)
) on TimestampUtc
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmcachedband, startTime, endTime)
    | project TimestampUtc, VMCachedMBPSPercentage = column_ifexists("Max",0)
) on TimestampUtc
| join kind=fullouter(
    evaluate geneva_metrics_request(shoeboxAccount, query_vmuncachedband, startTime, endTime)
    | project TimestampUtc, VMUnCachedMBPSPercentage = column_ifexists("Max",0)
) on TimestampUtc
| where isnotempty(TimestampUtc)
| project-away TimestampUtc1, TimestampUtc2, TimestampUtc3, TimestampUtc4
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox VM Disk IOPS

_Widget purpose:_ VM Total IOPS (by minute avg)

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > VM IO Stats > VM IO Stats > VM Total IOPS (by minute avg)`

**Tables:** `OsBlobCacheConfigTableV2`, `OsUltraSSDHealthSignalEvent`
**Aggregations:** `summarize Average = sum(Average) by TimestampUtc, IO` · `summarize Average = sum(Average) by TimestampUtc, IO = "Total IO Operations/Sec"`
**Output columns:** `TimestampUtc`, `tostring(LUN)`, `Average`, `IO`

```kusto
// let read_counter = "Read Operations/Sec";
// let write_counter = "Write Operations/Sec";
// let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real, IO:string) [];
// let read_query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", read_counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let read_query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", read_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let read_query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", read_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let read_dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_datadisk, startTime, endTime) | extend IO = read_counter;
// let read_osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_osdisk, startTime, endTime) | extend IO = read_counter;
// let read_tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_tempdisk, startTime, endTime) | extend IO = read_counter;
// let write_query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", write_counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let write_query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", write_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let write_query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", write_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let write_dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_datadisk, startTime, endTime) | extend IO = write_counter;
// let write_osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_osdisk, startTime, endTime) | extend IO = write_counter;
// let write_tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_tempdisk, startTime, endTime) | extend IO = write_counter;
// let readwrite = union theSchema, read_osDiskMetrics, write_osDiskMetrics
// | extend LUN = "OS Disk"
// | union read_dataDiskMetrics, write_dataDiskMetrics, read_tempDiskMetrics, write_tempDiskMetrics
// | where isnotempty(TimestampUtc)
// | project TimestampUtc, tostring(LUN), Average, IO
// | extend Average = column_ifexists("Average",0)
// | summarize Average = sum(Average) by TimestampUtc, IO;
// let total = readwrite | summarize Average = sum(Average) by TimestampUtc, IO = "Total IO Operations/Sec";
// readwrite
// | union total
//
let GetVMLimits = (nodeId:string, containerId:string, startTime:datetime, endTime:datetime) {
    OsBlobCacheConfigTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId 
    and (EntityType == 3 and UserData contains "XioSettingsNetworkThrottle" and UserData contains containerId)
    | summarize arg_max(PreciseTimeStamp, *) by EntityId, EntityConfig, UserData
    | extend UserData = case(UserData contains "Hardware" and UserData !endswith "}}", strcat(UserData, "}"), UserData)
    | extend EntityConfig = parse_json(EntityConfig), UserData = parse_json(UserData).user_data
    | extend IOPS = tolong(EntityConfig.max_iops), 
             BPS = tolong(EntityConfig.max_bps), 
             BPSMultiplier = tolong(EntityConfig.bps_multiplier), 
             BurstIOPS = tolong(EntityConfig.burst_iops), 
             BurstBPS = tolong(EntityConfig.burst_bps), 
             IopsDirectDriveMultiplier = tolong(UserData.IopsDirectDriveMultiplier),
             BpsDirectDriveMultiplier = tolong(UserData.BpsDirectDriveMultiplier)
    | extend BPS = iff(isnotempty(BPSMultiplier), BPS * BPSMultiplier/100, BPS)
    | extend DDIOPS = iff(isnotempty(IopsDirectDriveMultiplier), IOPS * IopsDirectDriveMultiplier / 100, IOPS), 
             DDBPS = iff(isnotempty(BpsDirectDriveMultiplier), BPS * BpsDirectDriveMultiplier / 100, BPS),
             BurstDDIOPS = iff(isnotempty(IopsDirectDriveMultiplier), BurstIOPS * IopsDirectDriveMultiplier / 100, BurstIOPS), 
             BurstDDBPS = iff(isnotempty(BpsDirectDriveMultiplier), BurstBPS * BpsDirectDriveMultiplier / 100, BurstBPS)
    | project IOPS, BPS, BurstIOPS, BurstBPS, DDIOPS, DDBPS, BurstDDIOPS, BurstDDBPS, ContainerId = tostring(split(UserData.Tag, "Throttle")[1])
    | join kind = leftouter (
        OsUltraSSDHealthSignalEvent
        | where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId and ContainerId =~ containerId
        | summarize DDDiskCount = dcount(BlobPath) by ContainerId
    ) on ContainerId
    | project ContainerId,
              IOPSProvisionedLimit = iff(isnull(DDDiskCount) or DDDiskCount == 0, IOPS, DDIOPS), 
              IOPSBurstLimit = iff(isnull(DDDiskCount) or DDDiskCount == 0, BurstIOPS, BurstDDIOPS),
              MBPSProvisionedLimit = iff(isnull(DDDiskCount) or DDDiskCount == 0, BPS, DDBPS) / 1000000, 
              MBPSBurstLimit = iff(isnull(DDDiskCount) or DDDiskCount == 0, BurstBPS, BurstDDBPS) / 1000000
};
let read_counter = "Read Operations/Sec";
let write_counter = "Write Operations/Sec";
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real, IO:string) [];
let read_query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", read_counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let read_query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", read_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let read_query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", read_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let read_dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_datadisk, startTime, endTime) | extend IO = read_counter;
let read_osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_osdisk, startTime, endTime) | extend IO = read_counter;
let read_tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_tempdisk, startTime, endTime) | extend IO = read_counter;
let write_query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", write_counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let write_query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", write_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let write_query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", write_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let write_dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_datadisk, startTime, endTime) | extend IO = write_counter;
let write_osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_osdisk, startTime, endTime) | extend IO = write_counter;
let write_tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_tempdisk, startTime, endTime) | extend IO = write_counter;
let readwrite = union theSchema, read_osDiskMetrics, write_osDiskMetrics
| extend LUN = "OS Disk"
| union read_dataDiskMetrics, write_dataDiskMetrics, read_tempDiskMetrics, write_tempDiskMetrics
| where isnotempty(TimestampUtc)
| project TimestampUtc, tostring(LUN), Average, IO
| extend Average = column_ifexists("Average",0)
| summarize Average = sum(Average) by TimestampUtc, IO;
let total = readwrite | summarize Average = sum(Average) by TimestampUtc, IO = "Total IO Operations/Sec";
let ProvisionedLimit = readwrite | extend ContainerId = containerId 
| join kind = leftouter GetVMLimits(nodeId, containerId, startTime, endTime) on ContainerId
| summarize Average = avg(IOPSProvisionedLimit) by TimestampUtc, IO = "IOPSProvisionedLimit";
let BurstLimit = readwrite | extend ContainerId = containerId 
| join kind = leftouter GetVMLimits(nodeId, containerId, startTime, endTime) on ContainerId
| summarize Average = avg(IOPSBurstLimit) by TimestampUtc, IO = "IOPSBurstLimit";
union readwrite, total, ProvisionedLimit, BurstLimit
```

**Params:** `{startTime}`, `{endTime}`, `{shoeboxAccount}`, `{vmId}`, `{containerId}`, `{nodeId}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox VM MBPS

_Widget purpose:_ VM Total MBytes/Sec (by minute avg)

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > VM IO Stats > VM IO Stats > VM Total MBytes/Sec (by minute avg)`

**Tables:** `OsBlobCacheConfigTableV2`, `OsUltraSSDHealthSignalEvent`
**Aggregations:** `summarize Average = sum(Average) by TimestampUtc, IO // | extend Average = Average / 10000` · `summarize Average = sum(Average) by TimestampUtc, IO = "Total MBytes/Sec"`
**Output columns:** `TimestampUtc`, `tostring(LUN)`, `Average`, `IO`

```kusto
let read_counter = "Read Bytes/Sec";
let write_counter = "Write Bytes/Sec";
// let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real, IO:string) [];
// let read_query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", read_counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let read_query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", read_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let read_query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", read_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let read_dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_datadisk, startTime, endTime) | extend IO = read_counter;
// let read_osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_osdisk, startTime, endTime) | extend IO = read_counter;
// let read_tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_tempdisk, startTime, endTime) | extend IO = read_counter;
// let write_query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", write_counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let write_query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", write_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let write_query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", write_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
// let write_dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_datadisk, startTime, endTime) | extend IO = write_counter;
// let write_osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_osdisk, startTime, endTime) | extend IO = write_counter;
// let write_tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_tempdisk, startTime, endTime) | extend IO = write_counter;
// let readwrite = union theSchema, read_osDiskMetrics, write_osDiskMetrics
// | extend LUN = "OS Disk"
// | union read_dataDiskMetrics, write_dataDiskMetrics, read_tempDiskMetrics, write_tempDiskMetrics
// | where isnotempty(TimestampUtc)
// | project TimestampUtc, tostring(LUN), Average, IO
// | extend Average = column_ifexists("Average",0)
// | summarize Average = sum(Average) by TimestampUtc, IO
// | extend Average = Average / 1000000.00, IO = replace_string(IO, "Bytes", "MBytes");
// let total = readwrite | summarize Average = sum(Average) by TimestampUtc, IO = "Total MBytes/Sec";
// readwrite | union total
//
let GetVMLimits = (nodeId:string, containerId:string, startTime:datetime, endTime:datetime) {
    OsBlobCacheConfigTableV2
    | where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId 
    and (EntityType == 3 and UserData contains "XioSettingsNetworkThrottle" and UserData contains containerId)
    | summarize arg_max(PreciseTimeStamp, *) by EntityId, EntityConfig, UserData
    | extend UserData = case(UserData contains "Hardware" and UserData !endswith "}}", strcat(UserData, "}"), UserData)
    | extend EntityConfig = parse_json(EntityConfig), UserData = parse_json(UserData).user_data
    | extend IOPS = tolong(EntityConfig.max_iops), 
             BPS = tolong(EntityConfig.max_bps), 
             BPSMultiplier = tolong(EntityConfig.bps_multiplier), 
             BurstIOPS = tolong(EntityConfig.burst_iops), 
             BurstBPS = tolong(EntityConfig.burst_bps), 
             IopsDirectDriveMultiplier = tolong(UserData.IopsDirectDriveMultiplier),
             BpsDirectDriveMultiplier = tolong(UserData.BpsDirectDriveMultiplier)
    | extend BPS = iff(isnotempty(BPSMultiplier), BPS * BPSMultiplier/100, BPS)
    | extend DDIOPS = iff(isnotempty(IopsDirectDriveMultiplier), IOPS * IopsDirectDriveMultiplier / 100, IOPS), 
             DDBPS = iff(isnotempty(BpsDirectDriveMultiplier), BPS * BpsDirectDriveMultiplier / 100, BPS),
             BurstDDIOPS = iff(isnotempty(IopsDirectDriveMultiplier), BurstIOPS * IopsDirectDriveMultiplier / 100, BurstIOPS), 
             BurstDDBPS = iff(isnotempty(BpsDirectDriveMultiplier), BurstBPS * BpsDirectDriveMultiplier / 100, BurstBPS)
    | project IOPS, BPS, BurstIOPS, BurstBPS, DDIOPS, DDBPS, BurstDDIOPS, BurstDDBPS, ContainerId = tostring(split(UserData.Tag, "Throttle")[1])
    | join kind = leftouter (
        OsUltraSSDHealthSignalEvent
        | where PreciseTimeStamp between (startTime..endTime) and NodeId =~ nodeId and ContainerId =~ containerId
        | summarize DDDiskCount = dcount(BlobPath) by ContainerId
    ) on ContainerId
    | project ContainerId,
              IOPSProvisionedLimit = iff(isnull(DDDiskCount) or DDDiskCount == 0, IOPS, DDIOPS), 
              IOPSBurstLimit = iff(isnull(DDDiskCount) or DDDiskCount == 0, BurstIOPS, BurstDDIOPS),
              MBPSProvisionedLimit = iff(isnull(DDDiskCount) or DDDiskCount == 0, BPS, DDBPS) / 1000000, 
              MBPSBurstLimit = iff(isnull(DDDiskCount) or DDDiskCount == 0, BurstBPS, BurstDDBPS) / 1000000
};
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real, IO:string) [];
let read_query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", read_counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let read_query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", read_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let read_query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", read_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let read_dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_datadisk, startTime, endTime) | extend IO = read_counter;
let read_osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_osdisk, startTime, endTime) | extend IO = read_counter;
let read_tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, read_query_tempdisk, startTime, endTime) | extend IO = read_counter;
let write_query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", write_counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let write_query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", write_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let write_query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", write_counter, "').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
let write_dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_datadisk, startTime, endTime) | extend IO = write_counter;
let write_osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_osdisk, startTime, endTime) | extend IO = write_counter;
let write_tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, write_query_tempdisk, startTime, endTime) | extend IO = write_counter;
let readwrite = union theSchema, read_osDiskMetrics, write_osDiskMetrics
| extend LUN = "OS Disk"
| union read_dataDiskMetrics, write_dataDiskMetrics, read_tempDiskMetrics, write_tempDiskMetrics
| where isnotempty(TimestampUtc)
| project TimestampUtc, tostring(LUN), Average, IO
| extend Average = column_ifexists("Average",0)
| summarize Average = sum(Average) by TimestampUtc, IO
| extend Average = Average / 1000000.00, IO = replace_string(IO, "Bytes", "MBytes");
let total = readwrite | summarize Average = sum(Average) by TimestampUtc, IO = "Total MBytes/Sec";
let ProvisionedLimit = readwrite | extend ContainerId = containerId 
| join kind = leftouter GetVMLimits(nodeId, containerId, startTime, endTime) on ContainerId
| summarize Average = avg(MBPSProvisionedLimit) by TimestampUtc, IO = "MBPSProvisionedLimit";
let BurstLimit = readwrite | extend ContainerId = containerId 
| join kind = leftouter GetVMLimits(nodeId, containerId, startTime, endTime) on ContainerId
| summarize Average = avg(MBPSBurstLimit) by TimestampUtc, IO = "MBPSBurstLimit";
union readwrite, total, ProvisionedLimit, BurstLimit
```

**Params:** `{startTime}`, `{endTime}`, `{shoeboxAccount}`, `{vmId}`, `{containerId}`, `{nodeId}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Total QD

_Widget purpose:_ VM QD (Total QD cumulative of all disks attached to VM by minute)

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > VM IO Stats > VM QD (Total QD cumulative of all disks attached to VM by minute)`

**Aggregations:** `summarize QD = sum(QD) by TimestampUtc`
**Output columns:** `TimestampUtc`, `tostring(LUN)`, `QD`

```kusto
let counter = "Queue Depth";
let theSchema = datatable (TimestampUtc: datetime, LUN: string, Average: real) [];
let query_datadisk = strcat(@"metricNamespace('Shoebox').metric('Data Disk ", counter, "').dimensions('ResourceId', 'LUN').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_osdisk = strcat(@"metricNamespace('Shoebox').metric('OS Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let query_tempdisk = strcat(@"metricNamespace('Shoebox').metric('Temp Disk ", counter, "').dimensions('ResourceId').samplingTypes('Max') | where ResourceId == '", vmId, "'");
let osDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_osdisk, startTime, endTime);
let dataDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_datadisk, startTime, endTime);
let tempDiskMetrics = evaluate geneva_metrics_request(shoeboxAccount, query_tempdisk, startTime, endTime);
union theSchema, osDiskMetrics
| extend LUN = "OS Disk"
| union dataDiskMetrics, tempDiskMetrics
| where isnotempty(TimestampUtc)
| extend Max = column_ifexists("Max",0)
| project TimestampUtc, tostring(LUN), QD = Max
| summarize QD = sum(QD) by TimestampUtc
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---

### Azure Host VM Shoebox Memory 

_Widget purpose:_ Available Memory Bytes

Cluster: `azcore.centralus` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Counters > Shoebox > Shoebox > VM Memory > VM Memory > Available Memory Bytes`

**Output columns:** `TimestampUtc`, `Bytes`

```kusto
let query_memory = strcat(@"metricNamespace('Shoebox').metric('Available Memory Bytes').dimensions('ResourceId').samplingTypes('Average') | where ResourceId == '", vmId, "'");
evaluate geneva_metrics_request(shoeboxAccount, query_memory, startTime, endTime)
| project TimestampUtc, Bytes = column_ifexists("Average",0)
| extend MB = round(toreal(Bytes) / (1024 * 1024))
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`, `{shoeboxAccount}`

**Signal filters seen in KQL:** `ResourceId == "", vmId, ""`

---
