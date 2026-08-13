# (top-level)

> Source: **NRP - Private Endpoint** dashboard, chapter **(top-level)** (9 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Private Endpoint"

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `ResourceGet` · Widget: `Container`

```kusto
let idMatch = strcat("/subscriptions/", local_subscriptionId, "/resourceGroups/", local_resourceGroup, "/providers/Microsoft.Network/privateEndpoints/", local_name);
Resources
| where isempty(local_timestamp) or timestamp between(datetime_add('day', -1, local_timestamp) .. datetime_add('hour', 1, local_timestamp))
| where resourceGroup =~ local_resourceGroup and subscriptionId =~ local_subscriptionId
| where type == "microsoft.network/privateendpoints" and not(partial)
| where id =~ idMatch and not(deleted)
| top 1 by timestamp desc
| extend resourceGuid = properties.resourceGuid
| extend provisioningState = tostring(properties.provisioningState)
| extend subnet = tostring(properties.subnet.id)
| parse subnet with "/subscriptions/" subSub "/resourceGroups/" subRg "/providers/Microsoft.Network/virtualNetworks/" subVnet "/subnets/" subName
| extend ipConfigurations = properties.ipConfigurations
| extend networkInterfaces = properties.networkInterfaces
| extend privateLinkServiceConnections = properties.privateLinkServiceConnections
| extend manualPrivateLinkServiceConnections = properties.manualPrivateLinkServiceConnections
| extend customNetworkInterfaceName = tostring(properties.customNetworkInterfaceName)
| extend customDnsConfigs = properties.customDnsConfigs
| extend privateDnsZoneGroups = properties.privateDnsZoneGroups
| project-away properties
```

**Params:** `{local_name}`, `{local_resourceGroup}`, `{local_subscriptionId}`, `{local_timestamp}`, `{globalFrom}`, `{globalTo}`

**Signal filters seen in KQL:** `type == "microsoft.network/privateendpoints"`

---

### NRP PE Operations Logs - QosEtwEvent

_Widget purpose:_ NRP Logs for PE Operations

Cluster: `nrp` · Database: `mdsnrp` · Type: `MultiRow` · Widget: `Card`

```kusto
QosEtwEvent
| where SubscriptionId == subscriptionIdParam and ResourceGroup == resourceGroupParam and ResourceType == 'privateEndpoints' and ResourceName == resourceNameParam
| where HttpMethod != "GET"
| summarize arg_max(TIMESTAMP, Region, ResourceName, OperationName, ErrorDetails) by OperationId
```

**Params:** `{subscriptionIdParam}`, `{resourceGroupParam}`, `{resourceNameParam}`

**Signal filters seen in KQL:** `HttpMethod != "GET"`

---

### NRP PE Operations Logs -FrontendOperationEtwEvent

_Widget purpose:_ NRP Operation Details

Cluster: `nrp` · Database: `mdsnrp` · Type: `MultiRow` · Widget: `Card`

```kusto
cluster("nrp").database("mdsnrp").FrontendOperationEtwEvent
| where OperationId == OperationIdParam
| where OperationName == OperationNameParam
| where Message contains "error" or Message contains "exception" // comment out this line to get full logs
| where TIMESTAMP >= TimeStampParam - 1d and TIMESTAMP <= TimeStampParam + 1d // edit to match your desired timeframe
| where ResourceGroup == ResourceGroupParam and ResourceName == ResourceNameParam
| project TIMESTAMP, EventCode, Message, OperationName, OperationId, ResourceName, ResourceGroup, CorrelationRequestId
| order by TIMESTAMP asc
```

**Params:** `{OperationIdParam}`, `{OperationNameParam}`, `{TimeStampParam}`, `{ResourceGroupParam}`, `{ResourceNameParam}`, `{local_timestamp}`

**Signal filters seen in KQL:** `Message contains "error"`

---

### Private Endpoint IPs

_Widget purpose:_ Network Interfaces

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `Table`

```kusto
let privateEndpointId = strcat('/subscriptions/', qSub, '/resourceGroups/', qRg, '/providers/Microsoft.Network/privateEndpoints/', qName);
let private_endpoint_to_nic_id = cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where id =~ privateEndpointId and type == 'microsoft.network/privateendpoints' 
| where not(deleted) and not(partial)
| summarize arg_max(timestamp, properties) by id, name, resourceGroup, subscriptionId
| mv-expand nic = properties.networkInterfaces
| extend nic_id = tostring(nic.id)
| project pe_id = id, pe_name = name, pe_rg = resourceGroup, pe_sub = subscriptionId, nic_id
;
let nic_ids = private_endpoint_to_nic_id | distinct nic_id
; 
private_endpoint_to_nic_id
| join kind=inner (
    cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
    | where id has_any(nic_ids) and type == "microsoft.network/networkinterfaces"
    | where not(deleted) and not(partial)
    | summarize arg_max(timestamp, properties) by id, name, resourceGroup, subscriptionId
    | extend nic_id = id, nic_name = name, nic_rg = resourceGroup, nic_sub = subscriptionId
) on nic_id
| mv-expand ipConfig = properties.ipConfigurations
| extend ipAddress = tostring(ipConfig.properties.privateIPAddress)
| project pe_id, pe_name, pe_rg, pe_sub, nic_id, nic_name, nic_rg, nic_sub, ipAddress
```

**Params:** `{queryFrom}`, `{queryTo}`, `{qSub}`, `{qRg}`, `{qName}`

---

### Find Vnet Id

_Widget purpose:_ VNet Id

Cluster: `nrpbi.westus` · Database: `mdsnrpbi` · Type: `Single` · Widget: `Card`

```kusto
let VNetName = split(ArmUriParam, "/")[8];
let VNetUriFragment = strcat("/virtualNetworks/", VNetName);
NRP_Entities
| where isempty(local_timestamp) or TimeStamp between(datetime_add('day', -1, local_timestamp) .. datetime_add('hour', 1, local_timestamp))
| where SubscriptionId == SubscriptionIdParam
| where Location == LocationParam
| where Key has VNetUriFragment
| extend JsonValue = parse_json(JsonValue)
| where EntityType == 'virtualNetworks'
| summarize arg_max(TimeStamp, *) by Key
| project VNetId = ResourceGuid, DcmtRegion
```

**Params:** `{SubscriptionIdParam}`, `{LocationParam}`, `{ArmUriParam}`, `{local_timestamp}`

**Signal filters seen in KQL:** `EntityType == "virtualNetworks"`

---

### Grab all the resources tied to PE

_Widget purpose:_ Resources tied to this PE

Cluster: `nrpbi.westus` · Database: `mdsnrpbi` · Type: `MultiRow` · Widget: `Card`

```kusto
NRP_Entities
| where TimeStamp > ago(26h)
| where EntityType != 'children'
| where isnotempty(JsonValue)
| where Key has KeyParam or JsonValue contains KeyParam
| extend JsonValue = parse_json(JsonValue)
| extend JsonName = tostring(JsonValue.name)
| summarize arg_max(TimeStamp, *) by Key
| project TimeStamp, ResourceGuid, EntityType, Key, ResourceName = JsonName
```

**Params:** `{KeyParam}`

**Signal filters seen in KQL:** `EntityType != "children"`

---

### Get all resources tied to PE (name-only)

_Widget purpose:_ Resources tied to this PE

Cluster: `nrpbi.westus` · Database: `mdsnrpbi` · Type: `Single` · Widget: `Card`

```kusto
let projectedTable = NRP_Entities
| where TimeStamp > ago(26h)
| where EntityType != 'children'
| where isnotempty(JsonValue)
| where Key has KeyParam or JsonValue contains KeyParam
| extend JsonValue = parse_json(JsonValue)
| extend JsonName = tostring(JsonValue.name)
| summarize arg_max(TimeStamp, *) by Key
| project TimeStamp, ResourceGuid, EntityType, Key, ResourceName = JsonName;
projectedTable
| summarize ResourceNameArray = make_list(ResourceName)
```

**Params:** `{KeyParam}`

**Signal filters seen in KQL:** `EntityType != "children"`

---

### FullResourceLogs

_Widget purpose:_ Resources tied to this PE

Cluster: `nrp` · Database: `mdsnrp` · Type: `MultiRow` · Widget: `Card`

```kusto
QosEtwEvent
| where SubscriptionId == subscriptionIdParam and ResourceGroup == resourceGroupParam and ResourceName has_any(resourceNameParamArray)
// | where CorrelationRequestId == correlationRequestIdParam
| where HttpMethod != "GET"
| project TIMESTAMP, OperationId, Region, ResourceName, OperationName, ErrorDetails, CorrelationRequestId, ParentOperationId
```

**Params:** `{subscriptionIdParam}`, `{resourceGroupParam}`, `{resourceNameParamArray}`

**Signal filters seen in KQL:** `HttpMethod != "GET"`

---

### RNM NSMPlus State Propagation

_Widget purpose:_ PrivateLinkEvents table for RNM->NSM+ state propagation

Cluster: `Aznwsdn` · Database: `aznwmds` · Type: `MultiRow` · Widget: `Card`

```kusto
let region = strcat("PROD_", DCMTRegionParam);
let vnetId = VNetIdParam;
PrivateLinkEvents
| where isempty(local_timestamp) or TIMESTAMP between(datetime_add('day', -1, local_timestamp) .. datetime_add('hour', 1, local_timestamp))
| where Region =~ region
| where Message contains "Adding name records"
| where Message contains vnetId
| project PreciseTimeStamp, Message
| order by PreciseTimeStamp asc
```

**Params:** `{DCMTRegionParam}`, `{VNetIdParam}`, `{local_timestamp}`

**Signal filters seen in KQL:** `Message contains "Adding name records"`

---
