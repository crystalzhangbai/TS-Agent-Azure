# (top-level)

> Source: **NRP - Customer Write Operations** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Customer Write Operations"

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `ResourceGet` · Widget: `Container`

```kusto
print("")
| project startTime = local_startDate, endTime = local_endDate, SubscriptionId = local_SubscriptionId, resourceGroup = local_resourceGroup;
```

**Params:** `{local_SubscriptionId}`, `{local_resourceGroup}`, `{local_startDate}`, `{local_endDate}`

---

### CustomerWriteOperations

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `CoBeTimeline`

```kusto
NRPCustomerWriteOperations(subId, startTime, endTime, resourceGroup);
```

**Params:** `{subId}`, `{resourceGroup}`, `{startTime}`, `{endTime}`

---
