# (top-level)

> Source: **NRP - Firewall** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Firewall"

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `ResourceGet` · Widget: `Container`

```kusto
Resources
| where isnull(local_timestamp) or timestamp between(datetime_add("minute", -60, local_timestamp) .. datetime_add("minute", 60, local_timestamp))
| where type =~ "microsoft.network/azurefirewalls"
    and subscriptionId =~ local_subscriptionId
    and resourceGroup =~ local_resourceGroupName
    and name =~ local_name
| summarize arg_max(timestamp, *) by id
| extend provisioningState = tostring(properties.provisioningState)
| extend IpConfigurations = properties.ipConfigurations
| extend skuName = tostring(properties.sku.name)
| extend skuTier = tostring(properties.sku.tier)
| extend threatIntelMode = tostring(properties.threatIntelMode)
| extend AdditionalProperties = properties.additionalProperties
| extend networkRuleCollections = properties.networkRuleCollections
| extend applicationRuleCollections = properties.applicationRuleCollections
| extend natRuleCollections = properties.natRuleCollections
| extend virtualHubId = properties.virtualHub
| extend firewallPolicyId = properties.firewallPolicy
| extend ManagementIpConfiguration = properties.managementIpConfiguration
| extend hubPrivateIPAddress = tostring(properties.hubIPAddresses.privateIPAddress)
| extend hubPublicIPAddress = array_strcat(properties.hubIPAddresses.publicIPs.addresses, ", ")
| extend hubPublicIPs = array_strcat(properties.publicIPs.addresses, ", ")
| project 
    Name = name,
    GroupName = resourceGroup,
    SubscriptionId = subscriptionId,
    Region = location,
    provisioningState,
    IpConfigurations,
    skuName,
    skuTier,
    threatIntelMode,
    AdditionalProperties,
    networkRuleCollections, 
    applicationRuleCollections,
    natRuleCollections,
    virtualHubId,
    firewallPolicyId,
    ManagementIpConfiguration,
    hubPrivateIPAddress,
    hubPublicIPAddress,
    hubPublicIPs
```

**Params:** `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_name}`, `{local_timestamp}`

**Signal filters seen in KQL:** `type =~ "microsoft.network/azurefirewalls"`

---
