# Gateway Health Check Failure Percentage

> Source: **Serial Console Home** dashboard, chapter **Gateway Health Check Failure Percentage** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Gateway To RP Healthcheck

_Widget purpose:_ Gateway Health Check Failure Percentage

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `TimeSeries`
Source panel: `Gateway Health Check Failure Percentage`

```kusto
let totalCount = HttpAccessLog
| where activitytimestamp > queryFrom
| where activitytimestamp <= queryTo
| where log contains "/healthcheck HTTP/1.1"
| summarize total_count = count() by RPTenant, total_time_bin=bin(activitytimestamp, 1h);
let healthyCount = HttpAccessLog
| where activitytimestamp > queryFrom
| where activitytimestamp <= queryTo
| where log contains "/healthcheck HTTP/1.1\" 200 2"
| summarize healthy_count = count() by RPTenant, healthy_time_bin=bin(activitytimestamp, 1h);
totalCount
| join kind=inner healthyCount on $left.total_time_bin == $right.healthy_time_bin, RPTenant
| extend ratio = (1.0 - round(1.0 * healthy_count/total_count, 3))*100
| project RPTenant, ratio, healthy_time_bin
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `log contains "/healthcheck HTTP/1.1"` · `log contains "/healthcheck HTTP/1.1\"`

---
