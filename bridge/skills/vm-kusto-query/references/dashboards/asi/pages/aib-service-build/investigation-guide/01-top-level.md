# (top-level)

> Source: **serviceBuild** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "serviceBuild"

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `ResourceGet` · Widget: `Container`

```kusto
UsageKpiEvent
| where serviceBuild ==  local_serviceBuild
| take 1
| project serviceBuild
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_serviceBuild}`

---

### Service Build Saturation

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

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

### Daily Build Success Rate

_Widget purpose:_ Daily Builds - {{ binTime }}

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `TimeSeries`

```kusto
AsyncQoSEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
// | where not(IsAIBSubscription(subscriptionID))
| where iff(build != "", serviceBuild == build, true)
| summarize
    callCount=todouble(count()),
    clientFailures=countif(resultType == 1),
    serverFailures=countif(resultType == 2),
    // failures=countif(resultType != 0),
    failedSubs=dcountif(subscriptionID, resultType != 0)
    by bin(PreciseTimeStamp, binTime)
| extend successRate = round(((callCount - clientFailures - serverFailures) * 100 ) / (callCount - clientFailures), 2)
| project PreciseTimeStamp, successRate, clientFailures, serverFailures
```

**Params:** `{queryFrom}`, `{queryTo}`, `{binTime}`, `{build}`

---
