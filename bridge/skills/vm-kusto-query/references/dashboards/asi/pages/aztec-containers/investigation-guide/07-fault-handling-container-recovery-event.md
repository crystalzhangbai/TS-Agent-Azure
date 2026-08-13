# Fault Handling Container Recovery Event

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Fault Handling Container Recovery Event** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Fault Handling Container Recovery Event

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Fault Handling Container Recovery Event`

```kusto
FaultHandlingContainerRecoveryEventEtwTable
| where PreciseTimeStamp between(global_startTime..global_endTime) and ContainerId == queryContainerId
| project PreciseTimeStamp,FaultDetails
| order by PreciseTimeStamp desc
```

**Params:** `{queryContainerId}`

---
