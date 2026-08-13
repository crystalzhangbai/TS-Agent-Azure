# (top-level)

> Source: **Azure Dedicated Host - Host Groups** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Host Groups"

Cluster: `azcsupfollower.centralus.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogDedicatedHostSnapshot
| where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and assert(isnotempty(local_subscriptionId) or isnotempty(local_hostName), "Either a container Id or VM Id must be specified")
| where (isempty(local_subscriptionId) or hostName == local_hostName)
| summarize arg_max(PreciseTimeStamp, PreciseTimeStamp, dedicatedHostId, nodeId, creationDate, hostName, lifecycleState, stateChangeTime, RegionFriendlyName) by nodeId
| distinct PreciseTimeStamp, dedicatedHostId, nodeId, creationDate, hostName, lifecycleState, stateChangeTime, RegionFriendlyName
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_hostName}`, `{local_subscriptionId}`

---
