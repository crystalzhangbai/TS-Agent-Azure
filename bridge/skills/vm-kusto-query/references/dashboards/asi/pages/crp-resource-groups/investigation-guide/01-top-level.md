# (top-level)

> Source: **CRP Resource Groups Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Resource Groups"

Cluster: `azcrp` · Database: `crp_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
union VMApiQosEvent, VmssVMApiQosEvent
| where subscriptionId == local_subscriptionId and resourceGroupName =~ local_resourceGroupName
| take 1
| project subscriptionId, resourceGroupName
```

**Params:** `{local_subscriptionId}`, `{local_resourceGroupName}`

---
