# (top-level)

> Source: **CRP CorrelationId Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Correlation Id"

Cluster: `azcrp` · Database: `crp_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
ApiQosEvent
| where correlationId =~ local_correlationId
| take 1
| project PreciseTimeStamp, correlationId
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_correlationId}`, `{local_endDate}`, `{local_startDate}`

---
