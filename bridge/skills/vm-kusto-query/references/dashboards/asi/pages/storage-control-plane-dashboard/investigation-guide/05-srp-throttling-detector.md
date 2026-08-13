# SRP Throttling Detector

> Source: **Storage Control Plane Dashboard Investigation Guide** dashboard, chapter **SRP Throttling Detector** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Detect SRP throttling Errors

_Widget purpose:_ SRP Throttling Detector

Cluster: `https://xstorepartners.kusto.windows.net/` · Database: `SRP` · Type: `IssueDetector`
Source panel: `SRP Throttling Detector`

```kusto
RegionalSRP_ServiceApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where account == accountName
| where httpStatusCode == 429
| summarize 429count = count()
| extend Severity = iff(429count > 0, "error", "information")
| extend Description = iff(429count > 0, strcat("There are", ['429count'], "throttling error detected in the given period."), "No SRP throttling error detected.")
| extend UriText = "Test"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{accountName}`

---
