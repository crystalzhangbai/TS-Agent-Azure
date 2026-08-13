# Extract SVD

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **Extract SVD** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Extract SVD

Cluster: `azcsupfollower2.centralus.kusto.windows.net` · Database: `crp_allprod` · Type: `ResourceGet` · Widget: `Card`
Source panel: `Extract SVD`

```kusto
GetUncompressedSvds(queryStart, queryEnd, queryOperationId)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryStart}`, `{queryEnd}`, `{queryOperationId}`

---
