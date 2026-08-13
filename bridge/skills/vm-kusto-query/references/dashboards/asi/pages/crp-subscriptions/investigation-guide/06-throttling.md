# Throttling

> Source: **CRP Subscriptions Investigation Guide** dashboard, chapter **Throttling** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Subscription Throttling

Cluster: `azcrp` · Database: `crp_allprod` · Type: `TimeSeries`
Source panel: `Throttling`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between (global_startTime..global_endTime)
| where subscriptionId =~ trim(" ", querySubscriptionId)
| where operationName in ("VirtualMachines.GetVMs.GET",
                          "Subscriptions.GetVMs.GET",
                          "Subscriptions.GetAvailabilitySets.GET",
                          "ProximityPlacementGroups.ResourceOperation.GET",
                          "SpotEvictionRates.bulkQuery.POST",
                          "SpotPriceHistory.bulkQuery.POST")
| summarize 
    Ok2xxs = countif(httpStatusCode in (200, 202)), 
    Throttled429s = countif(httpStatusCode == 429), 
    NotFound404s = countif(httpStatusCode == 404), 
    InternalServerError500s = countif(httpStatusCode >= 500) by bin(PreciseTimeStamp, 30m)
| order by PreciseTimeStamp asc
```

**Params:** `{querySubscriptionId}`

---
