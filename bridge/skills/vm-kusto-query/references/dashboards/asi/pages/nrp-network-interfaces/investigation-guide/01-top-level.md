# (top-level)

> Source: **NRP - Network Interfaces** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Network Interfaces"

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `ResourceGet` · Widget: `Container`

```kusto
Resources
| where (isempty(local_timestamp) or isnull(local_timestamp) or timestamp between((local_timestamp-1h)..(local_timestamp+1h))) 
    and type in ("microsoft.network/networkinterfaces", "microsoft.compute/virtualmachinescalesets/virtualmachines/networkinterfaces")
| where subscriptionId =~ local_subscriptionId and resourceGroup =~ local_resourceGroupName and name =~ local_name
| top 1 by timestamp desc
| extend IpConfigurations = properties.ipConfigurations
| extend DnsSettings = properties.dnsSettings
| extend HostedWorkloads = properties.hostedWorkloads
| extend 
    nsgName = tostring(split(properties.networkSecurityGroup.id, "/")[-1]), 
    nsgSub = tostring(split(properties.networkSecurityGroup.id, "/")[2]), 
    nsgRg = tostring(split(properties.networkSecurityGroup.id, "/")[4])
| extend dnsServers = array_strcat(parse_json(DnsSettings.dnsServers), ", ")
| extend appliedDnsServers = array_strcat(parse_json(DnsSettings.appliedDnsServers), ", ")
| extend oldInternalDnsNameLabels = array_strcat(parse_json(DnsSettings.oldInternalDnsNameLabels), ", ")
| extend internalDomainNameSuffix = array_strcat(parse_json(DnsSettings.internalDomainNameSuffix), ", ")
```

**Params:** `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_name}`, `{local_timestamp}`

---

### NIC IP Configurations

_Widget purpose:_ IP Configurations

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `Table`

```kusto
Resources
| where timestamp between(queryFrom..queryTo) 
    and subscriptionId == querySubscriptionId 
    and resourceGroup =~ queryResourceGroupName 
    and name =~ queryNICName
| top 1 by timestamp desc
| extend IpConfigurations = properties.ipConfigurations
| mv-expand IpConfigurations
| project IpConfigurations
| extend properties = IpConfigurations.properties
| extend subnetId = tostring(properties.subnet.id)
| project name = tostring(IpConfigurations.name),
    groupName = tostring(IpConfigurations.groupName),
    subscriptionId = tostring(IpConfigurations.subscriptionId),
    provisioningState = tostring(properties.provisioningState),
    privateIPAddress = tostring(properties.privateIPAddress),
    privateIPAllocationMethod = tostring(properties.privateIPAllocationMethod),
    publicIPAddress = tostring(properties.publicIPAddress.id),
    subnetId,
    subnetSub = tostring(split(subnetId, "/")[2]),
    subnetRG = tostring(split(subnetId, "/")[4]),
    subnetVNet = tostring(split(subnetId, "/")[8]),
    subnetName = tostring(split(subnetId, "/")[10]),
    previousSubnetIPAddresses = properties.previousSubnetIPAddresses,
    previousAllocationGoalsPrivateIPs = properties.previousAllocationGoalsPrivateIPs,
    primary = tobool(properties.primary),
    allocationId = tostring(properties.allocationId),
    rnmIpConfigurationId = tostring(properties.rnmIpConfigurationId),
    rnmIpConfigurationVersion = tolong(properties.rnmIpConfigurationVersion),
    privateIPAddressVersion = tostring(properties.privateIPAddressVersion),
    isInUseWithService = tobool(properties.isInUseWithService),
    IpConfigurations,
    loadBalancerBackendAddressPools = properties.loadBalancerBackendAddressPools,
    loadBalancerBackendPoolAddresses = properties.loadBalancerBackendPoolAddresses,
    loadBalancerInboundNatRules = properties.loadBalancerInboundNatRules,
    allocationCommittedPrivateIP = properties.allocationCommittedPrivateIP,
    allocationGoalPrivateIP = properties.allocationGoalPrivateIP
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryNICName}`, `{queryFrom}`, `{queryTo}`

---

### Get Network Security Group

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Single` · Widget: `Container`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where isnotempty(queryNSGName) and (resourceGroup =~ queryResourceGroupName and subscriptionId =~ querySubscriptionId)
| where type == "microsoft.network/networksecuritygroups" and not(partial)
| where name =~ queryNSGName
| top 1 by timestamp desc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryNSGName}`

**Signal filters seen in KQL:** `type == "microsoft.network/networksecuritygroups"`

---
