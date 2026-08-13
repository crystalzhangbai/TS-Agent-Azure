# VMStartTimedOut

> Source: **Resource URI** dashboard, chapter **VMStartTimedOut** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Container Unknown Duration

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Table`
Source panel: `VMStartTimedOut`

```kusto
let containers = materialize(cluster('azcore.centralus').database('AzureCP').MycroftContainerSnapshot
| where PreciseTimeStamp between((queryFrom)..(queryTo))
| where SubscriptionId =~ subId
| where RoleInstanceName == strcat("_", resName) | distinct ContainerId);
let containerDetails = materialize(cluster('azcore.centralus').database('AzureCP').MycroftContainerSnapshot
| where PreciseTimeStamp between((queryFrom)..(queryTo))
| where ContainerId in~ (containers) 
| join 
( 
  macro-expand isfuzzy=true entity_group [cluster('azcore.centralus.kusto.windows.net')] as X ( 
 X.database('AzureCP').MycroftContainerHealthSnapshot
| where PreciseTimeStamp between((queryFrom)..(queryTo))
  | where ContainerId in~ (containers)
  | where ContainerState == "ContainerStateUnknown"
  | summarize StartTime = arg_min( PreciseTimeStamp, ContainerId), EndTime= arg_max(PreciseTimeStamp, ContainerId) by ContainerId)
) on $left.ContainerId == $right.ContainerId
);
containerDetails 
| project ContainerId, NodeId, CreationTime, VirtualMachineUniqueId, UnknownDuration = EndTime - StartTime | where UnknownDuration > 1m
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`, `{resName}`

**Signal filters seen in KQL:** `ContainerState == "ContainerStateUnknown"`

---
