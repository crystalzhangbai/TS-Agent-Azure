# Monthly Active Users

> Source: **NRP - NRP BYOIP** dashboard, chapter **Monthly Active Users** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Monthly Calls for Create/Delete CustomIPPRefix

_Widget purpose:_ Monthly Active Users

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Monthly Active Users`

```kusto
WriteOperationResponseEtwEvent
| where TIMESTAMP > ago(90d)
| where Region == region
| where OperationName contains "CustomIpPrefix"
| summarize ct = count() by bin(TIMESTAMP, 30d)
| summarize CustomIpPrefix = sum(ct)/1.0 by bin(TIMESTAMP, 30d)
| project TIMESTAMP, CustomIpPrefix
```

**Params:** `{region}`

**Signal filters seen in KQL:** `OperationName contains "CustomIpPrefix"`

---
