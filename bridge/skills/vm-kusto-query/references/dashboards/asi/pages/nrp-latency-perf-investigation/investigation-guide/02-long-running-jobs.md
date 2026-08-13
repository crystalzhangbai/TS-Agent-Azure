# Long Running Jobs

> Source: **NRP - Latency and Performance Investigation Dashboard** dashboard, chapter **Long Running Jobs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Long Running Jobs

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Long Running Jobs`

```kusto
cluster('nrp').database('mdsnrp').BatchTransactionManagerEvent
| where TIMESTAMP between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subscriptionId
| where Message contains "Long execution duration execution job id"
| parse Message with "Long execution duration execution job id: " LongRunningJobId ", duration: " ExecutionDuration
| extend jobDuration = toint(ExecutionDuration)
| project PreciseTimeStamp, JobId, JobName, Message, jobDuration
| summarize avg(jobDuration) by bin(PreciseTimeStamp, 1s), JobName, JobId
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subscriptionId}`

**Signal filters seen in KQL:** `Message contains "Long execution duration execution job id"`

---
