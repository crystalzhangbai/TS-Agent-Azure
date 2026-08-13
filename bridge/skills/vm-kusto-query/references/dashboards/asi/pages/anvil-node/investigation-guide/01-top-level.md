# (top-level)

> Source: **Unhealthy Node Analysis - Node** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Node"

Cluster: `https://hawkeyekustocluster.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogNodeSnapshot
| where nodeId == local_nodeId
| take 1
| project PreciseTimeStamp, nodeState, nodeAvailabilityState, aliveContainerCount, containerCount, cmNodeChannelAggregatedHealthStatus, cmNodeWasChannelHealthStatus, hostingEnvironment, lastStateChangeTime = todatetime(lastStateChangeTime), faultInfo
```

**Params:** `{local_nodeId}`

---
