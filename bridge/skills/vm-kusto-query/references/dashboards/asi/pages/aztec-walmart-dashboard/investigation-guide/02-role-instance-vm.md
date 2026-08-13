# Role Instance / VM

> Source: **Aztec Walmart Dashboard Investigation Guide** dashboard, chapter **Role Instance / VM** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Role Instance / VM

### VMSnapshot

_Widget purpose:_ Role Instance / VM

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Role Instance / VM > Role Instance / VM`

```kusto
let SubscriptionFilter = iff(local_subscriptionId!= "", true, false);
let A = cluster('azcrpeus.kusto.windows.net').database('CommonDims').Dim_Subscription
| where  FriendlySubscriptionName contains "walmart" or TPName contains "walmart"
| where SubscriptionGuid == local_subscriptionId
| project SubscriptionGuid;
let B =  cluster('azcrpeus.kusto.windows.net').database('CommonDims').Dim_Subscription
| where  FriendlySubscriptionName contains "walmart" or TPName contains "walmart"
| project SubscriptionGuid;
let funcA = view(){
        A
    };
let funcB= view(){
        B
    };
let walmartSubscriptions = union (funcA() | where SubscriptionFilter), (funcB() | where not(SubscriptionFilter));
LogContainerSnapshot
| where PreciseTimeStamp between (startTime..endTime)
| where subscriptionId in (walmartSubscriptions)
| summarize max(PreciseTimeStamp) by roleInstanceName, containerId, availabilitySetName,virtualMachineUniqueId, tenantName, Tenant, Region
| extend LastSeen=max_PreciseTimeStamp
| project LastSeen,roleInstanceName, containerId,virtualMachineUniqueId,tenantName, Tenant, Region
| order by LastSeen desc
```

**Params:** `{startTime}`, `{endTime}`, `{local_subscriptionId}`

**Signal filters seen in KQL:** `FriendlySubscriptionName contains "walmart"`

---
