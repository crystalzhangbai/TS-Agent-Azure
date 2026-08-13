# Sla Measurement Event

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Sla Measurement Event** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Sla Measurement Event

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Sla Measurement Event`

```kusto
TMMgmtSlaMeasurementEventEtwTable
| where PreciseTimeStamp between(global_startTime..global_endTime) and ContainerID == queryContainerId
| project PreciseTimeStamp, Context, RoleInstanceName, EntityState, Detail0
| order by PreciseTimeStamp desc
```

**Params:** `{queryContainerId}`

---
