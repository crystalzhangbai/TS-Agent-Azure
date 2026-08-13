# Subnets

> Source: **NRP - Resource Groups** dashboard, chapter **Subnets** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Resource Group Subnets

### Subscription Subnets

_Widget purpose:_ Resource Group Subnets

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Subnets > Resource Group Subnets`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where type == "microsoft.network/virtualnetworks" and subscriptionId =~ querySubscriptionId 
| where isempty(queryOptionalResourceGroupName) or resourceGroup =~ queryOptionalResourceGroupName
| extend virtualNetworkName = name
| summarize arg_max(timestamp, properties, resourceGroup, deleted) by virtualNetworkName, id, deleted
| mv-expand Subnet = properties.subnets
| project Subnet, Name = virtualNetworkName, virtualNetworkName, subnetName = tostring(Subnet.name), key = id, PreciseTimeStamp = timestamp, resourceGroup, deleted
| extend networkSecurityGroupId = tostring(Subnet.properties.networkSecurityGroup.id)
| extend routeTableId = tostring(Subnet.properties.routeTable.id)
| parse networkSecurityGroupId with "/subscriptions/" nsgSubscriptionId "/resourceGroups/" nsgResourceGroupName "/providers/Microsoft.Network/networkSecurityGroups/" networkSecurityGroupName 
| parse routeTableId with "/subscriptions/" rtSubscriptionId "/resourceGroups/" rtResourceGroupName "/providers/Microsoft.Network/routeTables/" routeTableName
| extend privateEndpointId = tostring(Subnet.properties.privateEndpoints[0].id)
| extend hasPrivateEndpoints = tobool(iif(isempty(privateEndpointId), false, true))
| project PreciseTimeStamp,
    name = tostring(Subnet.name), 
    subscriptionId = querySubscriptionId,
    resourceGroupName = resourceGroup,
    deleted, 
    virtualNetworkName,
    vnetResourceId = key,
    reconciliationState = tostring(Subnet.reconciliationState), 
    lastModifiedTime = todatetime(Subnet.lastModifiedTime),
    createdTime = todatetime(Subnet.createdTime),
    provisioningState = tostring(Subnet.properties.provisioningState),
    addressPrefixes = array_strcat(Subnet.properties.addressPrefixes, ", "),
    isSqlGTEnabledNow = tobool(Subnet.properties.isSqlGTEnabledNow),
    isStorageGTEnabledNow = tobool(Subnet.properties.isStorageGTEnabledNow),
    isSqlGTEnabledEver = tobool(Subnet.properties.isSqlGTEnabledEver),
    isStorageGTEnabledEver = tobool(Subnet.properties.isStorageGTEnabledEver),
    isAddressPrefixesSet = tobool(Subnet.properties.isAddressPrefixesSet),
    networkSecurityGroupId,
    networkSecurityGroupName,
    routeTableId,
    routeTableName,
    privateEndpointNetworkPolicies = tostring(Subnet.properties.privateEndpointNetworkPolicies),
    privateLinkServiceNetworkPolicies = tostring(Subnet.properties.privateLinkServiceNetworkPolicies),
    subnetTrafficTag = tolong(Subnet.properties.subnetTrafficTag),
    ipAddressOwnerDict = Subnet.properties.ipAddressOwnerDict,
    rtSubscriptionId,
    rtResourceGroupName,
    nsgSubscriptionId,
    nsgResourceGroupName,
    privateEndpointId,
    hasPrivateEndpoints
| order by virtualNetworkName asc, name asc
```

**Params:** `{querySubscriptionId}`, `{queryOptionalResourceGroupName}`, `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `type == "microsoft.network/virtualnetworks"`

---
