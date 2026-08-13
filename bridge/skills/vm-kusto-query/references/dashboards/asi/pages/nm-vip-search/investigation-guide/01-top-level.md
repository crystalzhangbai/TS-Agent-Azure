# (top-level)

> Source: **Network Manager - VIP Search** dashboard, chapter **(top-level)** (10 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "VIP Search"

Cluster: `aznwsdn.kusto.windows.net` · Database: `nsmplus` · Type: `ResourceGet` · Widget: `Container`

```kusto
let startTime = datetime_add('hour', -24, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 72, local_PreciseTimeStamp);
let VipInfo = cluster('azurecm.kusto.windows.net').database('AzureCM').DCMNMLBEngineClientGoalStateInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where publicIPAddress == local_publicIPAddress
| where vipConfig has local_TenantName
| top 1 by PreciseTimeStamp desc
| extend TenantName = local_TenantName
| extend IsSpanned = extract(@"IsSpanned:([^\s\]]+)", 1, vipConfig)
| extend IsSpanned = iff(IsSpanned == "", "False", IsSpanned)
| project PreciseTimeStamp, TenantName, publicIPAddress, IsSpanned, goalStateId, vipConfig;
cluster('azurecm.kusto.windows.net').database('AzureCM').DCMNMLBEngineClientGoalStateInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where publicIPAddress == local_publicIPAddress and goalStateId == toscalar(VipInfo | project goalStateId)
| top 1 by PreciseTimeStamp desc
| extend TenantName = local_TenantName
| extend IsSpanned = toscalar(VipInfo | project IsSpanned)
| project PreciseTimeStamp, Region, Tenant, TenantName, IsSpanned, goalStateId, state, numOfTries, message, vipConfig, publicIPAddress
```

**Params:** `{local_PreciseTimeStamp}`, `{local_TenantName}`, `{local_publicIPAddress}`, `{local_Tenant}`

---

### NsmQosOps

_Widget purpose:_ Requests received by NSM

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `CoBeTimeline`

```kusto
let startTime = datetime_add('hour', -120, timestamp);
let endTime = datetime_add('hour', 1, timestamp);
DCMNMQOSInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where additionalMessage contains queryTenantName or message contains queryTenantName
| where operation !in ('QueryAllAllocatedRootSnatResources', 'GetVipAllocationStatus', 'PopulateLBSettingsApplianceIdsUntransacted')
| extend Health = iff(success, 'Healthy', 'Unhealthy')
| extend StartTime = datetime_add('Millisecond', 0 - toint(todouble(duration)), PreciseTimeStamp)
| summarize arg_max(PreciseTimeStamp, *) by ActivityId
| extend StartTime = iff(isnull(StartTime), PreciseTimeStamp, StartTime)
| project EventId = ActivityId, StartTime, EndTime = PreciseTimeStamp, EventName = operation, Health,
Properties = tostring(pack('message', message, 'additionalMessage',additionalMessage))
```

**Params:** `{timestamp}`, `{queryTenantName}`

---

### GetResourceGroup

_Widget purpose:_ Resource Group Information

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`

```kusto
let startTime = datetime_add('day', -10, timestamp);
let endTime = datetime_add('hour', 1, timestamp);
VMApiQosEvent
| where PreciseTimeStamp between (startTime..endTime) 
| where fabricTenantName == queryTenantName
| top 1 by PreciseTimeStamp desc
| extend StartTime = datetime_add('hour', -4, PreciseTimeStamp);
```

**Params:** `{timestamp}`, `{queryTenantName}`

---

### VIP State

_Widget purpose:_ State Timelines

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
DCMNMLBEngineClientGoalStateInfoEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Tenant == queryTenant
| where publicIPAddress == queryPublicIpAddress
| project PreciseTimeStamp, state
| order by PreciseTimeStamp asc
| extend PrevTime = prev(PreciseTimeStamp)
| extend NextTime = next(PreciseTimeStamp)
| extend PrevState = prev(state)
| extend NextState = next(state)
| where 
    isnull(PrevTime) or 
    isnull(NextTime) or 
    (state != PrevState or state != NextState) 
| extend StartTime = PreciseTimeStamp
| extend EndTime = next(PreciseTimeStamp)
| project StartTime, EndTime, Content = state
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 1, StartTime), EndTime)
```

**Params:** `{queryPublicIpAddress}`, `{queryTenant}`, `{queryFrom}`, `{queryTo}`

---

### RNMRequest

Cluster: `aznwsdn.kusto.windows.net` · Database: `aznwmds` · Type: `Table`

```kusto
let startTime = datetime_add('hour', -72, timestamp);
let endTime = datetime_add('hour', 4, timestamp);
let LoadBalancerInstanceId = materialize( ServiceExecutionEvent
| where PreciseTimeStamp between (startTime .. endTime)
| where Region endswith queryRegion
| where Message has queryTenantName
| where Message contains "CreateOrUpdateLoadBalancer"
| extend LoadBalancerInstanceId =  extract('LoadBalancerInstanceId:([0-9a-z-]+)', 1, Message)
| project LoadBalancerInstanceId);
let continuationIds = materialize (ServiceExecutionEvent
| where PreciseTimeStamp between (startTime .. endTime)
| where Region endswith queryRegion
| where Message has queryTenantName
    or Message has_any (LoadBalancerInstanceId)
| where ContinuationId != 'null' 
| summarize arg_max(PreciseTimeStamp, *) by ContinuationId
| top 1000 by PreciseTimeStamp desc
| distinct ContinuationId
);
ServiceExecutionEvent
| where PreciseTimeStamp between (startTime .. endTime)
| where Region endswith queryRegion
| where ContinuationId in (continuationIds)
    or Message has queryTenantName
    or Message has_any (LoadBalancerInstanceId) // LB instance ID
| project PreciseTimeStamp, OpName, Message, ContinuationId, EventType, RnmPartitionId, UserIdentity
| top 1000 by PreciseTimeStamp desc
```

**Params:** `{timestamp}`, `{queryTenantName}`, `{queryRegion}`

**Signal filters seen in KQL:** `Message contains "CreateOrUpdateLoadBalancer"` · `ContinuationId != "null"`

---

### VipLifeCycle

Cluster: `aznwsdn.kusto.windows.net` · Database: `aznwmds` · Type: `Table`

```kusto
let startTime = datetime_add('day', -10, timestamp);
let endTime = datetime_add('hour', 1, timestamp);
ResourceLifeCycleEvent
| where PreciseTimeStamp between (startTime .. endTime)
| where Region endswith queryRegion
| where Resource == queryVip
| top 1000 by PreciseTimeStamp desc
```

**Params:** `{timestamp}`, `{queryVip}`, `{queryRegion}`

---

### VipOwnershipSnapshot

Cluster: `aznwsdn.kusto.windows.net` · Database: `aznwmds` · Type: `Table`

```kusto
let startTime = datetime_add('day', -30, timestamp);
let endTime = datetime_add('hour', 1, timestamp);
VipOwnershipSnapshotEvent
| where PreciseTimeStamp between (startTime .. endTime)
| where Region endswith queryRegion
| where IPAddress == queryVip
| top 100 by PreciseTimeStamp desc
```

**Params:** `{timestamp}`, `{queryVip}`, `{queryRegion}`

---

### RNM ResourceRelease

Cluster: `aznwsdn.kusto.windows.net` · Database: `aznwmds` · Type: `Table`

```kusto
let startTime = datetime_add('hour', -24, timestamp);
let endTime = datetime_add('hour', 4, timestamp);
ResourceReleaseEvent
| where PreciseTimeStamp between (startTime..endTime) 
| where Region endswith queryRegion
| where Message contains queryTenantName
| extend serviceId = extract(@'service: ([^\s]+) ', 1, Message)
| extend serviceId = iff(serviceId == '', extract(@'ServiceId: ([^\s]+) ', 1, Message), serviceId)
| extend fabricId = extract(@'Cleanup of resource in fabric ([^\s]+) exceeded', 1, Message)
| project PreciseTimeStamp, RnmPartitionId, Message, PendingComponent, serviceId, fabricId
| top 1000 by PreciseTimeStamp desc
```

**Params:** `{timestamp}`, `{queryRegion}`, `{queryTenantName}`

---

### Frontend

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`

```kusto
let startTime = datetime_add('hour', -120, timestamp);
let endTime = datetime_add('hour', 4, timestamp);
let CRPResourceGroup = materialize  (
cluster('azcrp').database('crp_allprod').VMApiQosEvent
| where PreciseTimeStamp between (startTime..endTime) 
| where fabricTenantName == queryTenantName
| top 1 by PreciseTimeStamp desc);
FrontendOperationEtwEvent
| where PreciseTimeStamp between (startTime..endTime) 
| where HttpMethod != 'GET'
| where ResourceGroup in ((CRPResourceGroup | project resourceGroupName)) and SubscriptionId in ((CRPResourceGroup | project subscriptionId))
| top 200 by PreciseTimeStamp desc
| project PreciseTimeStamp, Tenant, Role, RoleInstance, ClientOperationId, Message
```

**Params:** `{timestamp}`, `{queryTenantName}`

**Signal filters seen in KQL:** `HttpMethod != "GET"`

---

### NsmPlusVipGS

Cluster: `aznwsdn.kusto.windows.net` · Database: `nsmplus` · Type: `Table`

```kusto
let startTime = datetime_add('day', -10, timestamp);
let endTime = datetime_add('hour', 1, timestamp);
SlbGoalStateInfo
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant contains queryRegion
| where vip == queryVip
| project PreciseTimeStamp, status, vipConfiguration
| sort by PreciseTimeStamp desc
```

**Params:** `{timestamp}`, `{queryVip}`, `{queryRegion}`

---
