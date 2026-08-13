# MeteredUsageEvent 

> Source: **CRP — VMs** dashboard, chapter **MeteredUsageEvent ** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query MeteredUsageEvent

_Widget purpose:_ MeteredUsageEvent 

Cluster: `azcrp` · Database: `monetaprod` · Type: `Table`
Source panel: `MeteredUsageEvent `

```kusto
MeteredUsageEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where resourceUri =~ queryResourceId
| extend payload = parse_json(additionalInfo)
| project PreciseTimeStamp, meterId, UsageType = payload["UsageType"], ImageType = payload["ImageType"], ConsumedQuantity = payload["ConsumedQuantity"], VCPUs = payload["VCPUs"], ServiceType = payload["ServiceType"], additionalInfo, resourceUri
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryResourceId}`

---
