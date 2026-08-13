# Availability Sets

> Source: **Aztec Subscription Investigation Guide** dashboard, chapter **Availability Sets** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Subscription AvailabilitySet List

_Widget purpose:_ Availability Sets

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Availability Sets`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between (local_startDate..local_endDate)
| where subscriptionId =~ local_subscriptionId
| summarize max(PreciseTimeStamp) by availabilitySetName,tenantName,AvailabilityZone,Region
| extend LastSeen=max_PreciseTimeStamp
| project LastSeen,availabilitySetName,tenantName,AvailabilityZone,Region
| order by LastSeen desc
```

**Params:** `{local_subscriptionId}`, `{local_startDate}`, `{local_endDate}`

---
