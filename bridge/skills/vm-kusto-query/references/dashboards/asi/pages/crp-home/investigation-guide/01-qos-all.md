# QoS - All

> Source: **CRP Home Investigation Guide** dashboard, chapter **QoS - All** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### QoS - All

Cluster: `azcrp` · Database: `crp_allprod` · Type: `TimeSeries`
Source panel: `QoS - All`

```kusto
ApiQosEvent
| where PreciseTimeStamp between (qFrom .. qTo)
| project PreciseTimeStamp, operationName, operationId, resultType, RPTenant, region
| summarize 
    Requests = dcount(operationId),
    UnexpectedFailures = dcountif(operationId, resultType == 2) 
    by bin(PreciseTimeStamp, 1m)
| extend QoS = (100 - round((toreal(UnexpectedFailures) / Requests) * 100, 4))
```

**Params:** `{qFrom}`, `{qTo}`

---
