# (top-level)

> Source: **NRP - Subnets** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Subnets"

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `ResourceGet` · Widget: `Container`

```kusto
let vnetResourceId = strcat(
    "/subscriptions/", local_subscriptionId, 
    "/resourceGroups/", local_resourceGroupName, 
    "/providers/Microsoft.Network/virtualNetworks/", local_virtualNetworkName);
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where type == "microsoft.network/virtualnetworks" and id =~ vnetResourceId and not(deleted) and isnotempty(properties)
| summarize arg_max(timestamp, properties) by id
| mv-expand Subnet = properties.subnets
| project Subnet, subnetName = tostring(Subnet.name), id, timestamp
| where subnetName =~ local_subnetName
| extend networkSecurityGroupId = tostring(Subnet.properties.networkSecurityGroup.id)
| parse networkSecurityGroupId with "/subscriptions/" nsgSubscriptionId "/resourceGroups/" nsgResourceGroupName "/providers/Microsoft.Network/networkSecurityGroups/" networkSecurityGroupName 
| extend routeTableId = tostring(Subnet.properties.routeTable.id)
| parse routeTableId with "/subscriptions/" rtSubscriptionId "/resourceGroups/" rtResourceGroupName "/providers/Microsoft.Network/routeTables/" routeTableName
| extend privateEndpointId = tostring(Subnet.properties.privateEndpoints[0].id)
| parse privateEndpointId with "/subscriptions/" peSub "/resourceGroups/" peRt "/providers/Microsoft.Network/privateEndpoints/" peName
| extend hasPrivateEndpoints = tobool(iif(isempty(privateEndpointId), false, true))
| extend ipConfigurations = Subnet.properties.ipConfigurations
| extend natGateway = tostring(Subnet.properties.natGateway.id)
| project 
    PreciseTimeStamp = timestamp,
    id = tostring(Subnet.id), 
    name = tostring(Subnet.name), 
    subscriptionId = local_subscriptionId,
    resourceGroupName = local_resourceGroupName,
    virtualNetworkName = local_virtualNetworkName,
    vnetResourceId = id,
    reconciliationState = tostring(Subnet.reconciliationState), 
    lastModifiedTime = todatetime(Subnet.lastModifiedTime),
    createdTime = todatetime(Subnet.createdTime),
    provisioningState = tostring(Subnet.properties.provisioningState),
    addressPrefixes = coalesce(Subnet.properties.addressPrefixes, Subnet.properties.addressPrefix),
    isSqlGTEnabledNow = tobool(Subnet.properties.isSqlGTEnabledNow),
    isStorageGTEnabledNow = tobool(Subnet.properties.isStorageGTEnabledNow),
    isSqlGTEnabledEver = tobool(Subnet.properties.isSqlGTEnabledEver),
    isStorageGTEnabledEver = tobool(Subnet.properties.isStorageGTEnabledEver),
    isAddressPrefixesSet = tobool(Subnet.properties.isAddressPrefixesSet),
    networkSecurityGroupId,
    networkSecurityGroupName,
    nsgSubscriptionId,
    nsgResourceGroupName,
    routeTableId,
    routeTableName,
    rtSubscriptionId,
    rtResourceGroupName,
    privateEndpointNetworkPolicies = tostring(Subnet.properties.privateEndpointNetworkPolicies),
    privateLinkServiceNetworkPolicies = tostring(Subnet.properties.privateLinkServiceNetworkPolicies),
    subnetTrafficTag = tolong(Subnet.properties.subnetTrafficTag),
    ipAddressOwnerDict = Subnet.properties.ipAddressOwnerDict,
    privateEndpointId,
    hasPrivateEndpoints,
    ipConfigurations,
    natGateway,
    peSub,
    peRt,
    peName
```

**Params:** `{local_subnetName}`, `{local_subscriptionId}`, `{local_resourceGroupName}`, `{local_virtualNetworkName}`

**Signal filters seen in KQL:** `type == "microsoft.network/virtualnetworks"`

---

### Subnet Features

_Widget purpose:_ Subnet - {{name}}

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `FeatureList` · Widget: `Card`

```kusto
Resources
| where timestamp between((queryTimestampHint-15m)..(queryTimestampHint+15m)) and type == "microsoft.network/virtualnetworks"
| where id =~ queryVNetResourceId
| top 1 by timestamp
| mv-expand Subnet = properties.subnets
| project 
    Subnet, 
    subnetName = tostring(Subnet.name), 
    virtualNetworkName = name,
    isAddressPrefixesSet = tobool(isnotempty(Subnet.properties.addressPrefix)),
    privateEndpointNetworkPolicies = tostring(Subnet.properties.privateEndpointNetworkPolicies),
    privateLinkServiceNetworkPolicies = tostring(Subnet.properties.privateLinkServiceNetworkPolicies)
| where subnetName =~ querySubnetName
| project features = pack(
    "AddressPrefixesSet", isAddressPrefixesSet,
    "PrivateEndpointNetworkPolicies", iif(privateEndpointNetworkPolicies == "Enabled", true, false),
    "PrivateLinkServiceNetworkPolicies", iif(privateLinkServiceNetworkPolicies == "Enabled", true, false)
)
| mv-expand bagexpansion=array features
| project FeatureName = tostring(features[0]), State = iif(tobool(features[1]), "Enabled", "Disabled");
```

**Params:** `{queryVNetResourceId}`, `{querySubnetName}`, `{queryTimestampHint}`

---

### Subnet Private Endpoints

_Widget purpose:_ Private Endpoints

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `Table`

```kusto
let vnetResourceId = strcat(
    "/subscriptions/", qSubId, 
    "/resourceGroups/", qRG, 
    "/providers/Microsoft.Network/virtualNetworks/", qVnetName);
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where id =~ vnetResourceId and type == "microsoft.network/virtualnetworks" 
| where not(deleted) and isnotempty(properties)
| top 1 by timestamp desc
| mv-expand Subnet = properties.subnets
| project Subnet, subnetName = tostring(Subnet.name), id, timestamp
| where subnetName =~ qSubnetName
| mv-expand pEndpoint = Subnet.properties.privateEndpoints
| project id = tolower(tostring(pEndpoint.id))
| join kind=inner (
    cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
    | where type == 'microsoft.network/privateendpoints' and not(deleted) and not(partial)
    | extend id = tolower(id)
) on id
| summarize arg_max(timestamp, properties) by id, name, resourceGroup, subscriptionId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{qSubnetName}`, `{qSubId}`, `{qRG}`, `{qVnetName}`

**Signal filters seen in KQL:** `type == "microsoft.network/privateendpoints"`

---
