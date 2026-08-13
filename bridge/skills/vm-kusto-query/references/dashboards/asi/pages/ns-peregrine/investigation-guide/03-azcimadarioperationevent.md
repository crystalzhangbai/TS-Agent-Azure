# AzCiMadariOperationEvent

> Source: **NodeService - NodeService_Peregrine** dashboard, chapter **AzCiMadariOperationEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AzCiMMadariOperationEvent

Cluster: `hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `AzCiMadariOperationEvent`

```kusto
AzCiMMadariOperationEvent
| where PreciseTimeStamp between (queryFrom..queryTo)
| where * contains containerId
| project PreciseTimeStamp, Result
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
