# Subnets

> Source: **NRP - Virtual Networks** dashboard, chapter **Subnets** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Subnets

### Virtual Network Subnets

_Widget purpose:_ Subnets

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Subnets > Subnets`

```kusto
let vnetResourceId = queryVNetResourceId;
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where type == "microsoft.network/virtualnetworks" and id =~ vnetResourceId and not(deleted) and isnotempty(properties)
| top 1 by timestamp desc
| mv-expand Subnet = properties.subnets
| parse Subnet.id with "/subscriptions/" subSubId "/resourceGroups/" subRg "/providers/Microsoft.Network/virtualNetworks/" subVnet "/subnets/" *
| extend networkSecurityGroupId = tostring(Subnet.properties.networkSecurityGroup.id)
| parse networkSecurityGroupId with "/subscriptions/" nsgSubscriptionId "/resourceGroups/" nsgResourceGroupName "/providers/Microsoft.Network/networkSecurityGroups/" networkSecurityGroupName 
| extend routeTableId = tostring(Subnet.properties.routeTable.id)
| parse routeTableId with "/subscriptions/" rtSubscriptionId "/resourceGroups/" rtResourceGroupName "/providers/Microsoft.Network/routeTables/" routeTableName
| extend privateEndpointId = tostring(Subnet.properties.privateEndpoints[0].id)
| extend hasPrivateEndpoints = tobool(iif(isempty(privateEndpointId), false, true))
| project 
    PreciseTimeStamp = timestamp,
    name = tostring(Subnet.name), 
    subSubId, 
    subRg, 
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
    hasPrivateEndpoints
```

**Params:** `{queryVNetResourceId}`

**Signal filters seen in KQL:** `type == "microsoft.network/virtualnetworks"`

---
