# Builds

> Source: **Build Status** dashboard, chapter **Builds** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Service Build Saturation

_Widget purpose:_ Builds

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`
Source panel: `Builds`

```kusto
UsageKpiEvent
| project serviceBuild, RPTenant, PreciseTimeStamp
| where Build == "" or serviceBuild == Build
| summarize count=count(), firstSeen=min(PreciseTimeStamp), lastSeen=max(PreciseTimeStamp) by serviceBuild, RPTenant
| order by firstSeen desc
| extend StartTime = firstSeen, EndTime = lastSeen, Tooltip = ['count'], GroupBy = RPTenant
```

**Params:** `{Build}`

---
