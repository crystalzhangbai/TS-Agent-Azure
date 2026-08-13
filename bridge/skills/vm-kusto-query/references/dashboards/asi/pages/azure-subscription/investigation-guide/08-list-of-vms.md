# List of VMs

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **List of VMs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## List of VMs that were running during the selected time

### Azure Host Subscription VMs

_Widget purpose:_ List of VMs that were running during the selected time

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `List of VMs > List of VMs that were running during the selected time`

```kusto
let containerList = LogContainerSnapshot
| where PreciseTimeStamp between (startTime..endTime) and subscriptionId == subId
| distinct creationTime = todatetime(creationTime), roleInstanceName, containerType, containerId, nodeId, tipNodeSessionId, virtualMachineUniqueId, Tenant, Region;
containerList | join kind = leftouter (
    LogTipNodeSessionSnapShot
    | where tipNodeSessionId in ((containerList | distinct tipNodeSessionId))
    | project PreciseTimeStamp, createdBy, tipNodeSessionId, nodeList
    | summarize arg_max(PreciseTimeStamp, *) by tipNodeSessionId
    | project tipNodeSessionId, createdBy
) on tipNodeSessionId
| project-away tipNodeSessionId1
| sort by creationTime desc
```

**Params:** `{startTime}`, `{endTime}`, `{subId}`

---
