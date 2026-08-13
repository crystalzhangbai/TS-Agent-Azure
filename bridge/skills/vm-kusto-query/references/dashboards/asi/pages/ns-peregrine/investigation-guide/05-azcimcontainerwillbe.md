# AzCiMContainerWillBe

> Source: **NodeService - NodeService_Peregrine** dashboard, chapter **AzCiMContainerWillBe** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AzCiMContainerWillBe

Cluster: `hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `AzCiMContainerWillBe`

```kusto
AzCiMContainerWillBe
| where PreciseTimeStamp between (queryFrom..queryTo)
| where PhysicalContainerId == containerId
| project PreciseTimeStamp, WillBe
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
