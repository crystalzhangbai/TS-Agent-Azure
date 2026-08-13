# AzCiMContainerWas

> Source: **Peregrine_ContainerEvents** dashboard, chapter **AzCiMContainerWas** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AzCiMContainerWas

Cluster: `hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `AzCiMContainerWas`

```kusto
AzCiMContainerWas
| where PhysicalContainerId ==  containerId
| where PreciseTimeStamp between (queryFrom..queryTo)
| project PreciseTimeStamp, Was
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
