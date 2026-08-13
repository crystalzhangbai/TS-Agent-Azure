# Resource Groups

> Source: **CRP Subscriptions Investigation Guide** dashboard, chapter **Resource Groups** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Resource Groups

### Resource Groups

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Resource Groups > Resource Groups`

```kusto
union VMApiQosEvent, VmssVMApiQosEvent
| where PreciseTimeStamp >= global_startTime and PreciseTimeStamp <= global_endTime
| where subscriptionId == querySubscriptionId
| distinct resourceGroupName, MonitoringApplication
| project resourceGroupName, region = MonitoringApplication
| order by resourceGroupName asc
```

**Params:** `{querySubscriptionId}`

---
