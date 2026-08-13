# Counters

> Source: **CRP — VMs** dashboard, chapter **Counters** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Counters

### VM Counters

_Widget purpose:_ Counters

Cluster: `{{qAzCoreCluster}}` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Counters > Counters`

```kusto
let totalHours = datetime_diff('hour', qFrom, qTo);
let bucket = case(
    totalHours < 48, 5m,
    totalHours < 1000, 10m,
    totalHours < 1500, 20m,
    30m
);
let containerids = VmHealthRawStateEtwTable 
    | where PreciseTimeStamp between (qFrom .. qTo)
    | where VirtualMachineUniqueId == qVM
    | summarize by ContainerId
;
VmCounterFiveMinuteRoleInstanceCentralBondTable 
| where PreciseTimeStamp between (qFrom .. qTo)
| where VmId in(containerids)
| project PreciseTimeStamp, CounterName, SampleCount, AverageCounterValue, MinCounterValue, MaxCounterValue
| extend Counter = case (
    CounterName == 'Percentage CPU', 'Percentage CPU',
    CounterName endswith 'Current Pressure', 'Current Memory Pressure',
    CounterName endswith 'Physical Memory', 'Physical Memory GB',
    CounterName == 'Network In', 'Network In MB/sec',
    CounterName == 'Network Out', 'Network Out MB/sec',
    CounterName == 'Disk Read Bytes/sec', 'Disk Read MB/sec',
    CounterName == 'Disk Write Bytes/sec', 'Disk Write MB/sec',
    '')
| where isnotempty(Counter)
| summarize 
    AverageCPU = round(avgif(AverageCounterValue, Counter == 'Percentage CPU')), 
    MaxCPU = round(maxif(MaxCounterValue, Counter == 'Percentage CPU')), 
    AvgPhysicalMem = round(avgif(AverageCounterValue, Counter == 'Physical Memory GB') / 1024), 
    MaxPhysicalMem = round(maxif(MaxCounterValue, Counter == 'Physical Memory GB') / 1024),
    MinMemPressure = round(minif(MinCounterValue, Counter == 'Current Memory Pressure')), 
    AvgMemPressure = round(avgif(AverageCounterValue, Counter == 'Current Memory Pressure')), 
    MaxMemPressure = round(maxif(MaxCounterValue, Counter == 'Current Memory Pressure')), 
    AvgNetworkIn = round(avgif(AverageCounterValue, Counter == 'Network In MB/sec') / (1024 * 1024), 2),
    MaxNetworkIn = round(maxif(MaxCounterValue, Counter == 'Network In MB/sec') / (1024 * 1024), 2),
    AvgNetworkOut = round(avgif(AverageCounterValue, Counter == 'Network Out MB/sec') / (1024 * 1024), 2),
    MaxNetworkOut = round(maxif(MaxCounterValue, Counter == 'Network Out MB/sec') / (1024 * 1024), 2),
    MinDiskIORead = round(minif(MinCounterValue, Counter == 'Disk Read MB/sec') / (1024 * 1024), 2), 
    AvgDiskIORead = round(avgif(AverageCounterValue, Counter == 'Disk Read MB/sec') / (1024 * 1024), 2), 
    MaxDiskIORead = round(maxif(MaxCounterValue, Counter == 'Disk Read MB/sec') / (1024 * 1024), 2), 
    MinDiskIOWrite = round(minif(MinCounterValue, Counter == 'Disk Write MB/sec') / (1024 * 1024), 2), 
    AvgDiskIOWrite = round(avgif(AverageCounterValue, Counter == 'Disk Write MB/sec') / (1024 * 1024), 2), 
    MaxDiskIOWrite = round(maxif(MaxCounterValue, Counter == 'Disk Write MB/sec') / (1024 * 1024), 2)
    by bin(PreciseTimeStamp, bucket)
| extend AverageCPU = iff(isnan(AverageCPU), 0.0, AverageCPU)
| extend AvgPhysicalMem = iff(isnan(AvgPhysicalMem), 0.0, AvgPhysicalMem)
| extend AvgMemPressure = iff(isnan(AvgMemPressure), 0.0, AvgMemPressure)
| extend AvgNetworkIn = iff(isnan(AvgNetworkIn), 0.0, AvgNetworkIn)
| extend AvgNetworkOut = iff(isnan(AvgNetworkOut), 0.0, AvgNetworkOut)
| extend AvgDiskIORead = iff(isnan(AvgDiskIORead), 0.0, AvgDiskIORead)
| extend AvgDiskIOWrite = iff(isnan(AvgDiskIOWrite), 0.0, AvgDiskIOWrite)
| order by PreciseTimeStamp asc
| project    
    ['Average CPU %'] = AverageCPU, 
    ['Max CPU %'] = MaxCPU, 
    ['Avg Physical Mem MB'] = AvgPhysicalMem, 
    ['Max Physical Mem MB'] = MaxPhysicalMem, 
    ['Min MemPressure %'] = MinMemPressure, 
    ['Avg MemPressure %'] = AvgMemPressure, 
    ['Max MemPressure %'] = MaxMemPressure, 
    ['Avg Network In MB/sec'] = AvgNetworkIn, 
    ['Max Network In MB/sec'] = MaxNetworkIn, 
    ['Avg Network Out MB/sec'] = AvgNetworkOut, 
    ['Max Network Out MB/sec'] = MaxNetworkOut, 
    ['Min Disk IORead MB/sec'] = MinDiskIORead, 
    ['Avg Disk IORead MB/sec'] = AvgDiskIORead, 
    ['Max Disk IORead MB/sec'] = MaxDiskIORead, 
    ['Min Disk IOWrite MB/sec'] = MinDiskIOWrite, 
    ['Avg Disk IOWrite MB/sec'] = AvgDiskIOWrite, 
    ['Max Disk IOWrite MB/sec'] = MaxDiskIOWrite, 
    PreciseTimeStamp
```

**Params:** `{qVM}`, `{qAzCoreCluster}`, `{qFrom}`, `{qTo}`

---
