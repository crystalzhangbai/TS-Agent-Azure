# (top-level)

> Source: **Usage Statistics** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Global usage

_Widget purpose:_ Global usage by distinct Serial Console session

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `TimeSeries`

```kusto
ConnectorContainerActivity
| where ['time'] > queryFrom
| where ['time'] < queryTo
| summarize dcount(sessionId) by startofday(TIMESTAMP)
| render columnchart
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### Successful connection count by RP region

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `Table`

```kusto
ConnectorContainerActivity
| where TIMESTAMP > queryFrom
| where TIMESTAMP <= queryTo
| where cloudEnv == "prod"
| where message startswith "NodeInfo: "
| summarize CountByRpRegion = count() by rpRegion
| project rpRegion, CountByRpRegion
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `cloudEnv == "prod"` · `message startswith "NodeInfo: "`

---

### Successful connection count by VM location

Cluster: `azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `Table`

```kusto
ConnectorContainerActivity
| where TIMESTAMP > queryFrom
| where TIMESTAMP <= queryTo
| where cloudEnv == "prod"
| where message startswith "NodeInfo: "
| summarize CountByVMLocation = count() by vmLocation
| project vmLocation, CountByVMLocation
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `cloudEnv == "prod"` · `message startswith "NodeInfo: "`

---
