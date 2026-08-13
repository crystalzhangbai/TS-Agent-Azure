# (top-level)

> Source: **Network Manager - Mizar Validation** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Mizar Validation"

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
let startTime = datetime_add('hour', -48, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 24, local_PreciseTimeStamp);
DCMNMQOSInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant == local_Tenant
| where operation == 'BatchUpdateNetworkResource-Allocation'
| where additionalMessage contains local_TenantName
| top 1 by PreciseTimeStamp asc 
| extend TenantName = extract(@'Tenant Name: ([a-z0-9\-]+)', 1, additionalMessage)
| extend ContainerInstanceId = extract_all(@'ContainerId:\s+([a-z0-9\-]+)', additionalMessage)
| extend InterfaceId = extract_all(@'InterfaceId:\s+([a-z0-9\-]+)', additionalMessage)
| extend InterfaceName = extract_all(@'InterfaceName:\s+([A-Za-z0-9\-]+)', additionalMessage)
| extend MacAddress = extract_all(@'MacAddress:\s+([a-z0-9\-]+)', additionalMessage)
| project Region, Tenant, TenantName, ContainerInstanceId, InterfaceId, MacAddress, success, message
```

**Params:** `{local_PreciseTimeStamp}`, `{local_Tenant}`, `{local_TenantName}`

**Signal filters seen in KQL:** `operation == "BatchUpdateNetworkResource-Allocation"`

---

### LogNetworkInterface

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
let startTime = datetime_add('hour', -48, timestamp);
let endTime = datetime_add('hour', 24, timestamp);
let targets = DCMNMQOSInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where operation == 'BatchUpdateNetworkResource-Allocation'
| where additionalMessage contains queryTenantName
| top 1 by PreciseTimeStamp asc 
| extend TenantName = extract(@'Tenant Name: ([a-z0-9\-]+)', 1, additionalMessage)
| extend ContainerInstanceId = extract_all(@'ContainerId:\s+([a-z0-9\-]+)', additionalMessage)
| extend InterfaceId = extract_all(@'InterfaceId:\s+([a-z0-9\-]+)', additionalMessage)
| extend MacAddress = extract_all(@'MacAddress:\s+([a-z0-9\-]+)', additionalMessage)
| project TenantName, ContainerInstanceId, InterfaceId, MacAddress, Tenant, Region;
let nicIds = NetworkServiceManagerEvents
| where PreciseTimeStamp between (startTime .. endTime)
| where TaskName != "ChangedSetting"
| where Message has_any (( targets | project TenantName)) or Message has_any ((targets | project ContainerInstanceId)) or Message has_any (( targets | project InterfaceId)) 
| where TaskName == "LogNetworkInterfacePersistedForContainerInterface"
| extend nicId = extract(@'nicId="([a-z0-9\-]+)"', 1, Message)
| distinct nicId;
let compartmentsId = NetworkServiceManagerEvents
| where PreciseTimeStamp between (startTime .. endTime)
| where TaskName != "ChangedSetting"
| where Message has_any (( targets | project InterfaceId)) and Message contains "/compartments/"
| extend nicId = extract(@'nicId="([a-z0-9\-]+)"', 1, Message)
| extend compartmentsId = extract(@'compartments/([a-z0-9\-]+)', 1, Message)
| distinct compartmentsId;
let ContainerIds = NetworkServiceManagerEvents
| where PreciseTimeStamp between (startTime .. endTime)
| where TaskName != "ChangedSetting"
| where Message has_any ((targets | project TenantName)) or Message has_any ((targets | project ContainerInstanceId)) or Message has_any ((targets | project InterfaceId)) 
      or Message has_any (nicIds)
| where TaskName == "LogMerlinNetworkInterfaceInstanceConfigAddToPublish"
| where Message has "ContainerId"
| extend ContainerId = extract(@'\\"ContainerId\\": ([a-z0-9\-]+)', 1, Message)
| distinct ContainerId;
NetworkServiceManagerEvents
| where PreciseTimeStamp between (startTime .. endTime)
| where TaskName != "ChangedSetting"
| where Message has_any ((targets | project TenantName)) or Message has_any ((targets | project ContainerInstanceId)) or Message has_any ((targets | project InterfaceId)) 
      or Message has_any (nicIds) or Message has_any (ContainerIds) or Message has_any (compartmentsId)
| project PreciseTimeStamp, TaskName, Message
| sort by PreciseTimeStamp asc
```

**Params:** `{timestamp}`, `{queryTenantName}`

**Signal filters seen in KQL:** `operation == "BatchUpdateNetworkResource-Allocation"` · `TaskName != "ChangedSetting"` · `TaskName == "LogNetworkInterfacePersistedForContainerInterface"` · `TaskName == "LogMerlinNetworkInterfaceInstanceConfigAddToPublish"` · `Message has "ContainerId"`

---

### NicInstanceStateMachine

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
let startTime = datetime_add('hour', -48, timestamp);
let endTime = datetime_add('hour', 24, timestamp);
let targets = DCMNMQOSInfoEtwTable
| where PreciseTimeStamp between (startTime .. endTime)
| where operation == 'BatchUpdateNetworkResource-Allocation'
| where additionalMessage contains queryTenantName
| top 1 by PreciseTimeStamp asc 
| extend InterfaceId = extract_all(@'InterfaceId:\s+([a-z0-9\-]+)', additionalMessage)
| project Tenant, InterfaceId;
NetworkServiceManagerMessages
| where PreciseTimeStamp between (startTime .. endTime)
| where Tenant in ((targets | project Tenant))
| project PreciseTimeStamp, data = parse_json(text)
| where data.category == 'StateMachine'
| where data.id has_any ((targets | project InterfaceId))
| top 1000 by PreciseTimeStamp desc
```

**Params:** `{timestamp}`, `{queryTenantName}`

**Signal filters seen in KQL:** `operation == "BatchUpdateNetworkResource-Allocation"` · `data.category == "StateMachine"`

---
