# (top-level)

> Source: **Network Manager - TDPR** dashboard, chapter **(top-level)** (5 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "TDPR"

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
let startTime = datetime_add('hour', -24, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 1, local_PreciseTimeStamp);
DCMNMAgentProgrammingDurationEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where nodeId == local_nodeId
| extend ContainerId = local_ContainerId
| extend MacAddress = local_MacAddress
| where interfaceId contains ContainerId and interfaceId contains MacAddress
| project PreciseTimeStamp, Tenant, RoleInstance, nodeId, ContainerId, MacAddress, interfaceId, programmingDelayInSeconds, message
| top 1 by PreciseTimeStamp desc
```

**Params:** `{local_PreciseTimeStamp}`, `{local_Tenant}`, `{local_nodeId}`, `{local_ContainerId}`, `{local_MacAddress}`

---

### TDPR_NMAgentProgrammingDuration

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
let startTime = datetime_add('hour', -24, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 1, local_PreciseTimeStamp);
DCMNMAgentProgrammingDurationEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where nodeId == local_nodeId
| extend ContainerId = local_ContainerId
| extend MacAddress = local_MacAddress
| where interfaceId contains ContainerId and interfaceId contains MacAddress
| project PreciseTimeStamp, Tenant, RoleInstance, nodeId, ContainerId, MacAddress, interfaceId, programmingDelayInSeconds, message
| top 100 by PreciseTimeStamp desc
```

**Params:** `{local_PreciseTimeStamp}`, `{local_Tenant}`, `{local_nodeId}`, `{local_ContainerId}`, `{local_MacAddress}`

---

### TDPR_DCMNMQOSInfoEtw

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
let startTime = datetime_add('hour', -2, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 2, local_PreciseTimeStamp);
let target = cluster("azurecm").database("AzureCM").DCMNMQOSInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where operation == 'BatchUpdateNetworkResource-Allocation'
| where additionalMessage contains "Tenant Name"
| where additionalMessage has local_ContainerId
| top 1 by PreciseTimeStamp desc
| extend TenantName = extract(@'Tenant Name: ([a-z0-9\-]+)', 1, additionalMessage)
| extend NetworkServiceInstanceId = extract(@'NetworkServiceInstanceId: ([a-z0-9\-]+)', 1, additionalMessage)
| project TenantName, NetworkServiceInstanceId;
let TenantName = target | distinct TenantName;
let NetworkServiceInstanceId = target | distinct NetworkServiceInstanceId;
cluster("azurecm").database("AzureCM").DCMNMQOSInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where additionalMessage has local_ContainerId 
    or additionalMessage has_any (TenantName)
    or additionalMessage has_any (NetworkServiceInstanceId)
    or message has_any (NetworkServiceInstanceId)
| project PreciseTimeStamp, Region, Tenant, operation, success, additionalMessage, message, duration
| top 100 by PreciseTimeStamp desc
```

**Params:** `{local_PreciseTimeStamp}`, `{local_Tenant}`, `{local_ContainerId}`

**Signal filters seen in KQL:** `operation == "BatchUpdateNetworkResource-Allocation"` · `additionalMessage contains "Tenant Name"`

---

### TDPR_DCMNMRegionalNetworkConfigurationQoS

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
let startTime = datetime_add('hour', -5, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 5, local_PreciseTimeStamp);
let target = cluster("azurecm").database("AzureCM").DCMNMQOSInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where operation == 'BatchUpdateNetworkResource-Allocation'
| where additionalMessage contains "Tenant Name"
| where additionalMessage has local_ContainerId
| top 1 by PreciseTimeStamp desc
| extend TenantName = extract(@'Tenant Name: ([a-z0-9\-]+)', 1, additionalMessage)
| extend NetworkServiceInstanceId = extract(@'NetworkServiceInstanceId: ([a-z0-9\-]+)', 1, additionalMessage)
| project TenantName, NetworkServiceInstanceId;
let TenantName = target | distinct TenantName;
let NetworkServiceInstanceId = target | distinct NetworkServiceInstanceId;
DCMNMRegionalNetworkConfigurationQoSEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where Configuration has_any (TenantName) 
    or Configuration has_any (NetworkServiceInstanceId)
    or Configuration contains local_ContainerId 
| project PreciseTimeStamp, SequenceEvent, Configuration, ConfigurationType, ConfigurationId
| top 1000 by PreciseTimeStamp asc
```

**Params:** `{local_PreciseTimeStamp}`, `{local_Tenant}`, `{local_ContainerId}`

**Signal filters seen in KQL:** `operation == "BatchUpdateNetworkResource-Allocation"` · `additionalMessage contains "Tenant Name"`

---

### TDPR_DCMNMRegionalNetworkConfigurationFailure

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
let startTime = datetime_add('hour', -5, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 5, local_PreciseTimeStamp);
let target = cluster("azurecm").database("AzureCM").DCMNMQOSInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where operation == 'BatchUpdateNetworkResource-Allocation'
| where additionalMessage contains "Tenant Name"
| where additionalMessage has local_ContainerId
| top 1 by PreciseTimeStamp desc
| extend TenantName = extract(@'Tenant Name: ([a-z0-9\-]+)', 1, additionalMessage)
| extend NetworkServiceInstanceId = extract(@'NetworkServiceInstanceId: ([a-z0-9\-]+)', 1, additionalMessage)
| project TenantName, NetworkServiceInstanceId;
let TenantName = target | distinct TenantName;
let NetworkServiceInstanceId = target | distinct NetworkServiceInstanceId;
DCMNMRegionalNetworkConfigurationFailureEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where * contains local_ContainerId
    or Message has_any (TenantName)
    or Message has_any (NetworkServiceInstanceId)
| top 1000 by PreciseTimeStamp asc
| project PreciseTimeStamp, Region, Tenant, ConfigurationType, Message
```

**Params:** `{local_PreciseTimeStamp}`, `{local_Tenant}`, `{local_ContainerId}`

**Signal filters seen in KQL:** `operation == "BatchUpdateNetworkResource-Allocation"` · `additionalMessage contains "Tenant Name"`

---
