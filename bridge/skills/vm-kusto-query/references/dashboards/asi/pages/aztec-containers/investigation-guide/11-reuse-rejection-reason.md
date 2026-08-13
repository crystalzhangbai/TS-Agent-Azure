# Reuse Rejection Reason

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Reuse Rejection Reason** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Reuse Rejection Reason

### Container Reuse Rejection Reason

_Widget purpose:_ Reuse Rejection Reason

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Reuse Rejection Reason > Reuse Rejection Reason`

```kusto
AllocatorContainerReuseRejectionReason
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where rejectedContainerId == queryContainerId
| project PreciseTimeStamp,rejectedContainerId,reason
```

**Params:** `{queryContainerId}`

---
