# (top-level)

> Source: **NRP - Private Link Service** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Private Link Service"

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `ResourceGet` · Widget: `Container`

```kusto
Resources
| where isempty(local_timestamp) or timestamp between((local_timestamp-6h)..(local_timestamp+6h))
| where 
    type == "microsoft.network/privatelinkservices" and
    subscriptionId =~ local_subId and
    resourceGroup =~ local_groupName and
    name =~ local_name
| top 1 by timestamp desc
| extend 
    LoadBalancerFrontendIpConfigurations = properties.loadBalancerFrontendIpConfigurations,
    IpConfigurations = properties.ipConfigurations,
    PrivateEndpointConnections = properties.privateEndpointConnections,
    PrivateEndpointConnectionProxies = properties.privateEndpointConnectionProxies,
    NetworkInterfaces = properties.networkInterfaces,
    Json = properties
| project 
    PreciseTimeStamp = timestamp, 
    Name = name, 
    GroupName = resourceGroup, 
    SubscriptionId = subscriptionId, 
    key = id,
    CreatedTime = timestamp, 
    ProvisioningState = properties.provisioningState, 
    Fqdns = properties.fqdns, 
    Alias = properties.alias, 
    EnableProxyProtocol = properties.enableProxyProtocol, 
    LoadBalancerFrontendIpConfigurations, 
    IpConfigurations, 
    PrivateEndpointConnections, 
    PrivateEndpointConnectionProxies, 
    NetworkInterfaces, 
    Json
```

**Params:** `{local_groupName}`, `{local_subId}`, `{local_name}`, `{local_timestamp}`, `{globalFrom}`, `{globalTo}`

**Signal filters seen in KQL:** `type == "microsoft.network/privatelinkservices"`

---
