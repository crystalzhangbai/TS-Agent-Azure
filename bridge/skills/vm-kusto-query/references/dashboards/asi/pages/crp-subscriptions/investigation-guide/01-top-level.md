# (top-level)

> Source: **CRP Subscriptions Investigation Guide** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Subscriptions"

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
Subscription
| where SubscriptionId =~ local_subscriptionId
| top 1 by PreciseTimeStamp desc
```

**Params:** `{local_subscriptionId}`

---

### Query Sub from CommonDims

_Widget purpose:_ Subscription - {{subscriptionId}}

Cluster: `customerdomrptwus3prod.westus3` · Database: `customerdomdata` · Type: `Single` · Widget: `Card`

```kusto
ObserveCustomerModel 
| where SubscriptionGuid == querySubId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`

---

### Subscription Availability Zones

_Widget purpose:_ Availability Zones

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Table`

```kusto
Subscription
| where SubscriptionId =~ querySubscriptionId
| top 1 by PreciseTimeStamp desc
| extend AvailabilityZoneMappings = parse_json(AvailabilityZoneMappings)
| mv-expand AvailabilityZoneMappings
| project AvailabilityZoneMappings
| extend LogicalZone = tostring(AvailabilityZoneMappings.LogicalZone),
    PhysicalZone = tostring(AvailabilityZoneMappings.PhysicalZone)
| extend b = bag_remove_keys(AvailabilityZoneMappings, dynamic(["LogicalZone", "PhysicalZone"]))
| project PhysicalZone, LogicalZone, OtherDetails = AvailabilityZoneMappings
| order by PhysicalZone asc
```

**Params:** `{querySubscriptionId}`

---
