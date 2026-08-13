# EagleAI Networking Investigation Path

Use this reference when an Azure networking symptom needs topology awareness rather than only raw Kusto rows. The default Kusto investigation path for compute, storage, disks, host, CRP, and ARM telemetry remains `kusto` / `azuremcp`; `eagleai` is the networking-specialized path.

## When to choose `eagleai`

Use `eagleai` when the user asks about:

- End-to-end connectivity or topology: VM → Private Endpoint, VM → VM, VM → Public IP, VM → Storage/SQL private endpoint, cross-region path, latency/jitter path.
- Network policy/configuration reasoning: NSG effective rules, route tables, Private Link, Private Endpoint connection state, VNet/subnet/NIC relationships.
- Networking services: ExpressRoute, VPN/vWAN/Hub, Azure Front Door, Application Gateway, Load Balancer/SLB, DDoS/PCAP context, NVA/MSEE path.
- NetworkARG resource graph lookups: VNet/Subnet/NIC/NSG/PE/PIP/LB/FrontDoor/ExpressRoute/VirtualHub topology and properties.

Stay with `kusto` / `azuremcp` when the task is ordinary VM availability RCA, disk lifecycle, host hardware, service healing, CRP/ARM compute operation tracing, or storage account performance unless the conclusion depends on network topology.

## Tool signatures

The `eagleai` MCP exposes exactly these three tools:

| Tool | Signature | Use it for |
|---|---|---|
| `EagleAI` | `EagleAI(user_query: str)` | General networking entry point when the right sub-path is unclear. The service routes to RAG TSG, Kusto, or topology. |
| `execute_kusto_query` | `execute_kusto_query(query: str, cluster: str, database: str)` | Raw KQL when the cluster/database are known, especially NetworkARG (`cluster=eearg.westus2`, `database=AzureResourceGraph`). |
| `DiscoverTopology` | `DiscoverTopology(user_query: str)` | EagleEye topology / connectivity diagnosis: VM↔destination, ExpressRoute gateway, AFD edge, SQL/private endpoint, NSG rule analysis, Private Link, vWAN/Hub/NVA. |

For `EagleAI` and `DiscoverTopology`, the `user_query` must include:

1. Resource ARM IDs for source and destination where available (VM, NIC, VNet/Subnet, PE, PIP, ER circuit/gateway, AFD profile, LB/AppGW).
2. Absolute UTC time window or incident timestamp.
3. Symptom and scenario label: timeout, connection refused, latency spike, asymmetric routing, NSG deny, PE DNS/connection state, ExpressRoute flap, AFD 5xx, etc.

Good `DiscoverTopology` prompt shape:

```text
Check VM-to-PrivateEndpoint connectivity. Source VM ARM ID: /subscriptions/{Sub}/resourceGroups/{Rg}/providers/Microsoft.Compute/virtualMachines/{Vm}; destination PE ARM ID: /subscriptions/{Sub}/resourceGroups/{Rg}/providers/Microsoft.Network/privateEndpoints/{Pe}; destination FQDN/IP: {FqdnOrIp}; UTC window: {StartUtc}..{EndUtc}; symptom: TCP timeout from source VM to private endpoint service.
```

## NetworkARG (`eearg.westus2` / `AzureResourceGraph`)

Use NetworkARG when you need raw resource topology/properties and can express the lookup in KQL. Prefer `eagleai.execute_kusto_query` first because it is owned by the networking path; if `eagleai` is unavailable, run the same fully-qualified KQL through `kusto` / `azuremcp` against `https://eearg.westus2.kusto.windows.net`, database `AzureResourceGraph`.

### Resource by ARM ID

```kusto
let ResourceId = tolower('{ResourceArmId}');
cluster('eearg.westus2').database('AzureResourceGraph').Resources
| where tolower(id) == ResourceId
| project id, type, name, subscriptionId, resourceGroup, location, properties
| take 100
```

### NIC → subnet / VNet / public IP

```kusto
cluster('eearg.westus2').database('AzureResourceGraph').Resources
| where type =~ 'microsoft.network/networkinterfaces'
| where id =~ '{NicArmId}' or name =~ '{NicName}'
| mv-expand ipconfig = properties.ipConfigurations
| extend privateIp = tostring(ipconfig.properties.privateIPAddress),
         subnetId = tostring(ipconfig.properties.subnet.id),
         publicIpId = tostring(ipconfig.properties.publicIPAddress.id)
| project id, name, location, privateIp, subnetId, publicIpId, properties.networkSecurityGroup
| take 100
```

### Private Endpoint connection state

```kusto
cluster('eearg.westus2').database('AzureResourceGraph').Resources
| where type =~ 'microsoft.network/privateendpoints'
| where id =~ '{PrivateEndpointArmId}' or name =~ '{PrivateEndpointName}'
| mv-expand connection = properties.privateLinkServiceConnections
| extend targetResource = tostring(connection.properties.privateLinkServiceId),
         status = tostring(connection.properties.privateLinkServiceConnectionState.status),
         description = tostring(connection.properties.privateLinkServiceConnectionState.description)
| project id, name, location, targetResource, status, description
| take 100
```

### NSG rules by NSG ARM ID

```kusto
cluster('eearg.westus2').database('AzureResourceGraph').Resources
| where type =~ 'microsoft.network/networksecuritygroups'
| where id =~ '{NsgArmId}'
| mv-expand rule = properties.securityRules
| extend priority = toint(rule.properties.priority),
         direction = tostring(rule.properties.direction),
         access = tostring(rule.properties.access),
         protocol = tostring(rule.properties.protocol),
         src = tostring(rule.properties.sourceAddressPrefix),
         dst = tostring(rule.properties.destinationAddressPrefix),
         dstPort = tostring(rule.properties.destinationPortRange)
| project nsgId=id, ruleName=tostring(rule.name), priority, direction, access, protocol, src, dst, dstPort
| order by priority asc
```

### `execute_kusto_query` call shape

```jsonc
execute_kusto_query({
  query: "cluster('eearg.westus2').database('AzureResourceGraph').Resources | where type =~ 'microsoft.network/privateendpoints' | where subscriptionId =~ '{SubscriptionId}' | take 100",
  cluster: "eearg.westus2",
  database: "AzureResourceGraph"
})
```

## Interpretation and fallback

- `DiscoverTopology` returns a synthesized topology/connectivity report. Preserve its path, hop, NSG, route, latency, and deny/allow evidence in the final investigation ledger; do not pretend it returned raw table rows.
- `execute_kusto_query` returns raw Kusto rows. Show the fully-qualified KQL and summarize the rows as usual.
- If `eagleai` fails but raw NetworkARG is enough, retry the same KQL through `kusto` / `azuremcp` against `eearg.westus2.kusto.windows.net` / `AzureResourceGraph`.
- If topology diagnosis itself is required and `eagleai` is unavailable, state that the EagleEye topology path is unavailable, continue with NetworkARG + networking catalogs, and identify which topology assertions remain unverified.

For the larger ARM/networking table catalog and additional templates, read [`catalog-AzureNetworking.md`](catalog-AzureNetworking.md).
