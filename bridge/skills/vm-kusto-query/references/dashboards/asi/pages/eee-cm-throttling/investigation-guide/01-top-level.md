# (top-level)

> Source: **EEE Compute Manager - Throttling** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### HighCostGet30Min

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `TimeSeries`

```kusto
ApiQosEvent
| where PreciseTimeStamp between (global_startTime..global_endTime)
| where subscriptionId =~ 'subscription_id'
| where region =~ 'crp_region'
| where operationName in ("VirtualMachines.GetVMs.GET",
                          "Subscriptions.GetVMs.GET",
                          "Subscriptions.GetAvailabilitySets.GET",
                          "ProximityPlacementGroups.ResourceOperation.GET",
                          "SpotEvictionRates.bulkQuery.POST",
                          "SpotPriceHistory.bulkQuery.POST")
| summarize count = count() by bin(PreciseTimeStamp, 30m), region
```

**Params:** `{subscription_id}`, `{crp_region}`

**Signal filters seen in KQL:** `subscriptionId =~ "subscription_id"` · `region =~ "crp_region"`

---
