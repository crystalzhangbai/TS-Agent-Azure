# Exposed Secrets

> Source: **Serial Console Home** dashboard, chapter **Exposed Secrets** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### WIP Trivy Exposed Secrets

Cluster: `https://azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `TimeSeries`
Source panel: `Exposed Secrets`

```kusto
external_table("TrivyDevMichaelGira")
| where Namespace == 'prometheus' and Name == 'trivy_image_exposedsecrets'
| where TimeGenerated > queryFrom
| where TimeGenerated <= queryTo
| summarize ExposedSecrets = sum(Val) by Time = TimeGenerated
| order by Time desc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `Namespace == "prometheus"`

---
