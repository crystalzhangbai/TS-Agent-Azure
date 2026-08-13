# NRP and Control Path Runner Succeed Rate

> Source: **NRP - Vnet Encryption** dashboard, chapter **NRP and Control Path Runner Succeed Rate** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### RunnerSucceed

_Widget purpose:_ NRP and Control Path Runner Succeed Rate

Cluster: `aznwsdn.kusto.windows.net` · Database: `aznwmds` · Type: `Table`
Source panel: `NRP and Control Path Runner Succeed Rate`

```kusto
RunnersDeployMetric
| where (Timestamp > startTime and Timestamp < endTime)
| where SubscriptionId == "c51a6f0a-b599-46bc-8484-6cb32b0ac038"
| where (RunnerInstanceName contains "NrpCreateVM" and RunnerInstanceName contains "encrypted") or RunnerInstanceName contains "encryption"
| project RunnerName, RunnerInstanceName, Timestamp, Metric, MetricName, Region, SubscriptionId
| extend Region = tolower(Region)
| summarize Failure = countif(Metric == 2), Pass = countif(Metric == 1) by RunnerInstanceName, Timestamp, Region
| summarize PassRate = sum(Pass) * 1.0 / (sum(Pass)+sum(Failure)) by RunnerInstanceName, Region
| project RunnerInstanceName, Region, PassRate
| extend SuccessRate = round(PassRate, 4) * 100.0
| project RunnerInstanceName, Region, SuccessRate
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `SubscriptionId == "c51a6f0a-b599-46bc-8484-6cb32b0ac038"`

---
