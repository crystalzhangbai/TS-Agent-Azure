# Config Audits

> Source: **Serial Console Home** dashboard, chapter **Config Audits** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### WIP Trivy Config Audits

Cluster: `https://azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `TimeSeries`
Source panel: `Config Audits`

```kusto
external_table("TrivyDevMichaelGira")
| where Namespace == 'prometheus' and Name == 'trivy_resource_configaudits'
| where TimeGenerated > queryFrom
| where TimeGenerated <= queryTo
| summarize ConfigAudits = sum(Val) by Time = TimeGenerated
| order by Time desc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `Namespace == "prometheus"`

---
