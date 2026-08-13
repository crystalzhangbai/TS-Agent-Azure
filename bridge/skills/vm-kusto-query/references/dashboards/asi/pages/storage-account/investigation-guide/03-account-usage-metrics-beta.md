# Account Usage Metrics (Beta)

> Source: **Storage Account Investigation Guide** dashboard, chapter **Account Usage Metrics (Beta)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Usage Metrics

_Widget purpose:_ Account Usage Metrics (Beta)

Cluster: `azcore.centralus` · Database: `Xstore` · Type: `TimeSeries`
Source panel: `Account Usage Metrics (Beta)`

```kusto
let maxEst = cluster('azcore.centralus').database('Xstore').XAggAccountUsageMetric
| where TIMESTAMP between (queryFrom .. queryTo)
| where Tenant == tenant
| where AccountName == trim(@"[\s]+", accountName)
| where UsageCategory == usageType
| project TIMESTAMP, EstimatedAttemptedUsage
| summarize arg_max(EstimatedAttemptedUsage, *) by bin(TIMESTAMP,1m);
cluster('azcore.centralus').database('Xstore').XAggAccountUsageMetric
| where TIMESTAMP between (queryFrom .. queryTo)
| where Tenant == tenant
| where AccountName == trim(@"[\s]+", accountName)
| where UsageCategory == usageType
| summarize arg_max(MeasuredUsagePerSec, *) by bin(TIMESTAMP,1m)
| join maxEst on TIMESTAMP
| project TIMESTAMP, AccountName, UsageCategory, Tenant, 
Threshold = iff(usageType == 'Entities', TargetUsageThreshold/1000, TargetUsageThreshold*8/(1024*1024*1024)) , 
ThresholdinGbps_DCConfig = DefaultUsageThreshold*8/(1024*1024*1024), 
EstimatedAttemptedUsage = iff(usageType == 'Entities', EstimatedAttemptedUsage1/1000, EstimatedAttemptedUsage1*8/(1024*1024*1024)),
PeakMeasuredUsagePerMin = iff(usageType == 'Entities', MeasuredUsagePerSec/1000, MeasuredUsagePerSec*8/(1024*1024*1024)),
RawMeasuredUsagePerMin = RawMeasuredUsagePerSec*8/(1024*1024*1024)
| project TIMESTAMP, AccountName, UsageCategory, Tenant, Threshold, PeakMeasuredUsagePerMin, EstimatedAttemptedUsage
```

**Params:** `{queryFrom}`, `{queryTo}`, `{accountName}`, `{usageType}`, `{tenant}`

---
