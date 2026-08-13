# Region level

> Source: **NRP - DELETE VMScaleSet operation drilldown** dashboard, chapter **Region level** (5 queries across 5 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Latency

### Latency

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Region level > Latency`

```kusto
WriteOperationResponseEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region == region
| where OperationName =~ "DeleteVmScaleSetOperation"
| summarize percentiles(DurationInMillisecond, 50, 90 ) by bin(PreciseTimeStamp, 10m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

**Signal filters seen in KQL:** `OperationName =~ "DeleteVmScaleSetOperation"`

---

## Sub lock duration

### DeleteVmssSubLockRegion

_Widget purpose:_ Sub lock duration

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Region level > Sub lock duration`

```kusto
let location = region;
let startTime = queryFrom;
let endTime = queryTo;
let regex="Operation (.+) \\((.+)\\) released lock (.+) after (\\d+) ms";
let dvmss=WriteOperationResponseEtwEvent
| where PreciseTimeStamp between (startTime..endTime)
| where Region == location
| where OperationName in ("DeleteVMScaleSetOperation")
| where HttpStatusCode == "Accepted"
| distinct OperationId;
//dvmss;
let subLock=FrontendOperationEtwEvent
| where Region == location
| where PreciseTimeStamp between (startTime..endTime)
| where OperationName in ("DeleteVMScaleSetOperation")
| where EventCode == "LockReleased"
| extend cou = OperationId in (dvmss)
| extend LockName=extract(regex, 3, Message)
| extend LockDuration=toint(extract(regex, 4, Message))
| where LockName == SubscriptionId
| summarize sum(LockDuration) by bin(PreciseTimeStamp, 5m)
| render timechart;
subLock;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

**Signal filters seen in KQL:** `HttpStatusCode == "Accepted"` · `EventCode == "LockReleased"`

---

## Success rate

### DeleteVmssSuccess

_Widget purpose:_ Success rate

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Region level > Success rate`

```kusto
WriteOperationResponseEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region == region
| where OperationName =~ "DeleteVmScaleSetOperation"
| extend isSuccess = iff(HttpStatusCode  == "Accepted", 1, 0)
| extend fail = iff(HttpStatusCode  != "Accepted", 1, 0)
| summarize count(), sum(isSuccess), sum(fail) by bin(PreciseTimeStamp, 10m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

**Signal filters seen in KQL:** `OperationName =~ "DeleteVmScaleSetOperation"`

---

## Top Subscriptions

### DeleteVmssTopSubs

_Widget purpose:_ Top Subscriptions

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Region level > Top Subscriptions`

```kusto
let location = region;
let startTime = queryFrom;
let endTime = queryTo;
let dvmss=WriteOperationResponseEtwEvent
| where PreciseTimeStamp between (startTime..endTime)
| where Region == location
| where OperationName in ("DeleteVMScaleSetOperation")
| where ResourceName !startswith "pps-vm"
| where HttpStatusCode == "Accepted"
| summarize count() by SubscriptionId
| order by count_ desc 
| take 10;
dvmss;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

**Signal filters seen in KQL:** `HttpStatusCode == "Accepted"`

---

## Transaction stats (KB)

### DeleteVmssTransactionStatsRegion

_Widget purpose:_ Transaction stats (KB)

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Region level > Transaction stats (KB)`

```kusto
KvsTransactionEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where OperationName in ("DeleteVMScaleSetOperation")
| project PreciseTimeStamp, ReadCount, ReadSize, AddCount, AddSize, ReadDuration, CommitDuration, UpdateCount, UpdateSize, OperationId
| summarize readSizeKb = sum(ReadSize)/1000, addSizeKb = sum(AddSize)/1000, updateSizeKb = sum(UpdateSize)/1000 by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

---
