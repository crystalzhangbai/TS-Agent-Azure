# (top-level)

> Source: **Network Manager - NsmQosInfo Search** dashboard, chapter **(top-level)** (6 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "NsmQosInfo Search"

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
let startTime = datetime_add('day', -1, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 1, local_PreciseTimeStamp);
DCMNMQOSInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where additionalMessage contains local_TenantName or message contains local_TenantName
| where operation !startswith "Get"
| extend TenantName = local_TenantName
| project PreciseTimeStamp, Tenant, operation, success, additionalMessage, message, duration, Region, TenantName
| top 1 by PreciseTimeStamp desc
```

**Params:** `{local_PreciseTimeStamp}`, `{local_TenantName}`

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
