# Role Instances / VMs

> Source: **Aztec Subscription Investigation Guide** dashboard, chapter **Role Instances / VMs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Subscription RoleInstance List

_Widget purpose:_ Role Instances / VMs

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`
Source panel: `Role Instances / VMs`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between (local_startDate..local_endDate)
| where subscriptionId =~ local_subscriptionId
| summarize max(PreciseTimeStamp) by roleInstanceName, availabilitySetName,virtualMachineUniqueId,AvailabilityZone,Region
| extend LastSeen=max_PreciseTimeStamp
| project LastSeen,roleInstanceName,availabilitySetName,virtualMachineUniqueId,AvailabilityZone,Region
| order by LastSeen desc
```

**Params:** `{local_subscriptionId}`, `{local_endDate}`, `{local_startDate}`

---
