# Peerings

> Source: **NRP - Virtual Networks** dashboard, chapter **Peerings** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VNet Peerings

### Virtual Network Peerings

_Widget purpose:_ VNet Peerings

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Peerings > VNet Peerings`

```kusto
let vnetResourceId = queryId;
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where type == "microsoft.network/virtualnetworks" and id =~ vnetResourceId and not(deleted) 
| take 1
| extend vnetPeerings = properties.virtualNetworkPeerings
| mv-expand vnetPeering = vnetPeerings
| project vnetPeering
| extend properties = vnetPeering.properties
| extend remoteVirtualNetworkId = tostring(properties.remoteVirtualNetwork.id)
| project 
    id = tostring(vnetPeering.id),
    name = tostring(vnetPeering.name),
    provisioningState = tostring(properties.provisioningState),
    peeringState = tostring(properties.peeringState),
    peeringSyncLevel = tostring(properties.peeringSyncLevel),
    remoteVirtualNetworkSub = tostring(split(remoteVirtualNetworkId, "/")[2]),
    remoteVirtualNetworkRG = tostring(split(remoteVirtualNetworkId, "/")[4]),
    remoteVirtualNetworkName = tostring(split(remoteVirtualNetworkId, "/")[8]),
    allowVirtualNetworkAccess = tostring(properties.allowVirtualNetworkAccess),
    allowForwardedTraffic = tostring(properties.allowForwardedTraffic),
    allowGatewayTransit = tostring(properties.allowGatewayTransit),
    useRemoteGateways = tostring(properties.useRemoteGateways),
    doNotVerifyRemoteGateways = tostring(properties.doNotVerifyRemoteGateways),
    remoteVirtualNetworkGreKey = tostring(properties.remoteVirtualNetworkGreKey),
    remoteVirtualNetworkRegionID = tostring(properties.remoteVirtualNetworkRegionID),
    remoteAddressSpaceAddressPrefixes = array_strcat(properties.remoteAddressSpace.addressPrefixes, ", "),
    remoteVirtualNetworkAddressSpaceAddressPrefixes = array_strcat(properties.remoteVirtualNetworkAddressSpace.addressPrefixes, ", "),
    remotePeeringUsesGateways = tostring(properties.remotePeeringUsesGateways),
    remoteVirtualNetworkResourceGuid = tostring(properties.remoteVirtualNetworkResourceGuid),
    remoteVirtualNetworkLocation = tostring(properties.remoteVirtualNetworkLocation),
    remoteGatewayPublicIPAddresses = tostring(properties.remoteGatewayPublicIPAddresses),
    routeServiceVips = tostring(properties.routeServiceVips),
    vnetPeering
```

**Params:** `{queryId}`

**Signal filters seen in KQL:** `type == "microsoft.network/virtualnetworks"`

---
