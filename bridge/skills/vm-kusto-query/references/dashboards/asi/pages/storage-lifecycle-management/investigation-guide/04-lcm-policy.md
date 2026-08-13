# LCM Policy

> Source: **Life Cycle Management Investigation Guide** dashboard, chapter **LCM Policy** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get LCM policy definition

_Widget purpose:_ LCM Policy

Cluster: `https://xstore.westcentralus.kusto.windows.net/` · Database: `xstore` · Type: `Table`
Source panel: `LCM Policy`

```kusto
ETWEventOLCMSchedulerActionStatsEventTableHourly
| where TIMESTAMP between (queryFrom .. queryTo)
| where AccountName == storageAccountName
| where Action == "AccountTasksDispatched"
| extend PolicyObj = parse_json(Policy)
| mv-expand Rule = PolicyObj.rules
| project TIMESTAMP, AccountName, PerformanceType, RuleName = tostring(Rule.name), PolicyObj
```

**Params:** `{queryFrom}`, `{queryTo}`, `{storageAccountName}`

**Signal filters seen in KQL:** `Action == "AccountTasksDispatched"`

---
