# Insights

> Source: **CRP — Scale Sets** dashboard, chapter **Insights** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### GetVMSSImpactEvents

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `Insights`

```kusto
GetVMSSImpactEvents(queryBegin, queryEnd, querySubId, queryResourceGroupName, queryVmssName)
```

**Params:** `{querySubId}`, `{queryResourceGroupName}`, `{queryVmssName}`, `{queryBegin}`, `{queryEnd}`

---
