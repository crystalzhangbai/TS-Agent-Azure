# (top-level)

> Source: **Build Status** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Build Timeline

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Timeline`

```kusto
FrontEndQoSEvents
| where TIMESTAMP between(queryFrom .. queryTo)
| where case( cloud == "public", RPTenant == "prod", cloud == "ussec", RPTenant == "secprod", cloud == "usnat", RPTenant == "natprod", true )
| project serviceBuild, RPTenant, PreciseTimeStamp, RPSector
| summarize requests=count(), firstSeen=min(PreciseTimeStamp), lastSeen=max(PreciseTimeStamp) by serviceBuild, RPSector
| extend Content = RPSector, StartTime = firstSeen, EndTime = lastSeen, Tooltip = tostring(requests), GroupBy = serviceBuild
| project GroupBy, Content, StartTime, EndTime, Tooltip
| extend Health="Neutral"
| order by StartTime desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{Build}`, `{cloud}`

---
