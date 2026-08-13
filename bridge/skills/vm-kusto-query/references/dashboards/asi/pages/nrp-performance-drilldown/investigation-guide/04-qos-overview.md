# QOS Overview

> Source: **NRP - Nrp Performance Drilldown** dashboard, chapter **QOS Overview** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## QOS Overview

### QOS Overview

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `QOS Overview > QOS Overview`

```kusto
let qosLogs = QosEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where SubscriptionId == subscriptionId
| where Region == region
| extend valid = iff(operationId == "", iff(correlationId == "", true, CorrelationRequestId == correlationId), OperationId == operationId)
| where valid == true
| where OperationName !startswith "Get";
let logCount = qosLogs
| summarize count() by OperationId;
qosLogs
| join kind=inner logCount on OperationId
| extend isLast = iff(BackgroundTaskQos == 0, count_ == 1, true)
| where isLast == true
| summarize failures=sum(ErrorDetails != "" and ErrorCode != "RetryableError"), throttles=sum(ErrorCode == "RetryableError"), count(), percentiles(DurationInMilliseconds, 50, 99.9, 100) by OperationName
| extend sucessRate = 1 - (todouble(failures) + todouble(throttles)) / todouble(count_), failureRate = todouble(failures) / todouble(count_), throttleRate = todouble(throttles) / todouble(count_)
| project OperationName, count_, sucessRate, failureRate, throttleRate, percentile_DurationInMilliseconds_50, percentile_DurationInMilliseconds_99_9, percentile_DurationInMilliseconds_100
| order by sucessRate asc
```

**Params:** `{correlationId}`, `{operationId}`, `{region}`, `{subscriptionId}`, `{startTime}`, `{endTime}`

---
