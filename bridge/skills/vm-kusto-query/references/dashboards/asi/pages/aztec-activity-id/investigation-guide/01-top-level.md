# (top-level)

> Source: **Aztec ActivityId Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "ActivityId"

Cluster: `AzureCM` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
CommonWebOperationStart
| where ActivityId =~ local_ActivityId
| take 1
| extend ActivityId=local_ActivityId
| project AvailabilityZone, ClientType, CloudName, DataCenterName, Region, Tenant, ActivityId, RelatedActivityId
```

**Params:** `{local_ActivityId}`, `{local_startDate}`, `{local_endDate}`, `{globalFrom}`, `{globalTo}`

---
