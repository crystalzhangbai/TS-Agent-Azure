# (top-level)

> Source: **Aztec Subscription Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Subscription"

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between (local_startDate..local_endDate)
| where subscriptionId =~ local_subscriptionId
| project subscriptionId
| limit 01
```

**Params:** `{local_endDate}`, `{local_startDate}`, `{local_subscriptionId}`

---
