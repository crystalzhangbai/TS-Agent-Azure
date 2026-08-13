# Put Vmss sub lock duration ms (COU vs non-COU) per 5 mins

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Put Vmss sub lock duration ms (COU vs non-COU) per 5 mins** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssLockDurationCouVsNonCOU

_Widget purpose:_ Put Vmss sub lock duration ms (COU vs non-COU) per 5 mins

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Put Vmss sub lock duration ms (COU vs non-COU) per 5 mins`

```kusto
let sub = subId;
let startTime = queryFrom;
let endTime = queryTo;
let regex="Operation (.+) \\((.+)\\) released lock (.+) after (\\d+) ms";
let qosStats = QosEtwEvent
| where PreciseTimeStamp between (startTime..endTime)
| where Region == region
| where SubscriptionId == sub
| where OperationName in ("PutVMScaleSetOperation")
| extend hasBkTask = iif(BackgroundTaskQos, 1, 0)
| extend Success = iif(Success, 1, 0)
| summarize retryCnt=count()-sum(hasBkTask), hasBkTask=max(hasBkTask), PreciseTimeStamp=max(PreciseTimeStamp), Accepted=max(Success) by ClientOperationId;
FrontendOperationEtwEvent
| where Region == region
| where SubscriptionId == sub
| where PreciseTimeStamp between (startTime..endTime)
| where OperationName in ("PutVMScaleSetOperation")
| where EventCode == "LockReleased"
| extend cou = ClientOperationId in (qosStats | where Accepted == 1 and hasBkTask == 0 | project ClientOperationId)
| extend LockName=extract(regex, 3, Message)
| extend LockDuration=toint(extract(regex, 4, Message))
| where LockName == sub
| summarize Duration=sum(LockDuration), couLockDuration=sumif(LockDuration, cou) by PreciseTimeStamp = bin(PreciseTimeStamp, 5m)
//| extend couLockDurationPc=1.0*couLockDuration/Duration
//| summarize avg(couLockDurationPc)
| project PreciseTimeStamp, Duration, lockDurationNoBgTaskOps = couLockDuration
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

**Signal filters seen in KQL:** `EventCode == "LockReleased"`

---

### PutVmssSubLockCouVsNonCouPerRes

_Widget purpose:_ Put Vmss sub lock duration ms (COU vs non-COU) per 5 mins

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `MultiRow` · Widget: `TimeSeries`
Source panel: `Put Vmss sub lock duration ms (COU vs non-COU) per 5 mins`

```kusto
let sub = subId;
let startTime = queryFrom;
let endTime = queryTo;
let location = region;
let regex="Operation (.+) \\((.+)\\) released lock (.+) after (\\d+) ms";
let qosStats = QosEtwEvent
| where PreciseTimeStamp between (startTime..endTime)
| where Region == location
| where SubscriptionId == sub
| where OperationName in ("PutVMScaleSetOperation")
| extend hasBkTask = iif(BackgroundTaskQos, 1, 0)
| where ResourceGroup =~ resourceGroup and ResourceName =~ resourceName
| extend Success = iif(Success, 1, 0)
| summarize retryCnt=count()-sum(hasBkTask), hasBkTask=max(hasBkTask), PreciseTimeStamp=max(PreciseTimeStamp), Accepted=max(Success) by ClientOperationId;
FrontendOperationEtwEvent
| where Region == location
| where SubscriptionId == sub
| where PreciseTimeStamp between (startTime..endTime)
| where OperationName in ("PutVMScaleSetOperation")
| where ResourceGroup =~ resourceGroup and ResourceName =~ resourceName
| where EventCode == "LockReleased"
| extend cou = ClientOperationId in (qosStats | where Accepted == 1 and hasBkTask == 0 | project ClientOperationId)
| extend LockName=extract(regex, 3, Message)
| extend LockDuration=toint(extract(regex, 4, Message))
| where LockName == sub
| summarize Duration=sum(LockDuration), couLockDuration=sumif(LockDuration, cou) by PreciseTimeStamp = bin(PreciseTimeStamp, 5m)
| project PreciseTimeStamp, Duration, couLockDuration
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`, `{resourceGroup}`, `{resourceName}`

**Signal filters seen in KQL:** `EventCode == "LockReleased"`

---
