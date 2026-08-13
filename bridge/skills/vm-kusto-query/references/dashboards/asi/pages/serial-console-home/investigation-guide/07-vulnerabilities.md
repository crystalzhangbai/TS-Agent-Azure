# Vulnerabilities

> Source: **Serial Console Home** dashboard, chapter **Vulnerabilities** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Vulnerabilities by Severity

### WIP Trivy Vulernabilities by Severity

_Widget purpose:_ Vulnerabilities by Severity

Cluster: `https://azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `CategoryChart`
Source panel: `Vulnerabilities > Vulnerabilities by Severity`

```kusto
let latestTime = toscalar(external_table("TrivyDevMichaelGira")
    | where Namespace == 'prometheus' and Name == 'trivy_image_vulnerabilities'
    | summarize max(TimeGenerated)
);
external_table("TrivyDevMichaelGira")
| where Namespace == 'prometheus' and Name == 'trivy_image_vulnerabilities' and TimeGenerated == latestTime
| project Val, Image=Tags.image_repository, Severity=tostring(Tags.severity), Namespace=Tags.namespace
| summarize Sum = sum(Val) by Severity
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `Namespace == "prometheus"`

---

## Vulnerabilities by Time

### WIP Trivy Vulnerabilities

_Widget purpose:_ Vulnerabilities by Time

Cluster: `https://azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `TimeSeries`
Source panel: `Vulnerabilities > Vulnerabilities by Time`

```kusto
external_table("TrivyDevMichaelGira")
| where Namespace == 'prometheus'
| where Name == 'trivy_image_vulnerabilities'
| where TimeGenerated > queryFrom
| where TimeGenerated <= queryTo
| summarize ImageVulnerabilities = sum(Val) by Time = TimeGenerated
| order by Time desc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `Namespace == "prometheus"` · `Name == "trivy_image_vulnerabilities"`

---
