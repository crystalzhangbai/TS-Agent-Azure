# Cluster Information Queries

> These queries gather cluster configuration and context. Run them early in troubleshooting.

## 4.1 Basic Cluster Info (ManagedClusterSnapshot)

**Database**: `AKSprod`

```kql
cluster('akshuba.centralus').database('AKSprod').ManagedClusterSnapshot
| where PreciseTimeStamp > ago(2d)
| where clusterName == '{Cluster name}'
| take 1
| project 
    // Basic Info
    PreciseTimeStamp,
    clusterName,
    ccpNamespace = namespace,
    location,
    provisioningState,
    clusterNodeCount,
    // Kubernetes Version
    kubernetesVersion = tostring(todynamic(orchestratorProfile).orchestratorVersion),
    // SKU
    sku_tier = tostring(todynamic(sku).tier),
    // Outbound
    outboundType,
    // Underlay
    UnderlayName,
    // Power State
    powerState = tostring(todynamic(powerState).code),
    // Addons
    addonProfiles
```

**⚠️ Important Filtering Notes:**
- **Use `clusterName == '{exact name}'` for fastest queries** - exact match is faster than `contains`
- Use `take 1` for quick lookups (faster than `top 1 by ... desc`)
- Use `namespace` to get CCP namespace (NOT `ccpNamespace` - doesn't exist in this table)
- For network config details, extend with: `| extend logd = todynamic(tostring(log)) | extend kubeConfig = logd.orchestratorProfile.kubernetesConfig`

**Important Steps:**
1. **Save the returned `ccpNamespace` value** - this is the CCP namespace identifier for control plane log filtering
2. **Format and present** cluster information to the user in a readable format
3. The `ccpNamespace` is **critical** for filtering control plane logs in `AKSccplogs` database

**Example Output Format:**
```
## Cluster Information
| Field | Value |
|-------|-------|
| Cluster Name | aks-eas-hkg-uat |
| CCP Namespace | 60f91b7f0e54ba0001719c52 |
| Location | eastasia |
| Provisioning State | Succeeded |
| Kubernetes Version | 1.33.4 |
| SKU Tier | Paid |
| Node Count | 143 |
| Power State | Running |

## Network Configuration
| Field | Value |
|-------|-------|
| Network Plugin | azure |
| Network Policy | azure |
| Cluster Subnet | 10.161.128.0/19 |
| Service CIDR | 10.164.96.0/19 |
| DNS Service IP | 10.164.96.10 |
| Max Pods | 30 |
| Outbound Type | loadBalancer |

## Enabled Addons
- azurepolicy ✅
- image-cleaner ✅
- keda ✅
- workload-identity ✅
- omsagent ❌
```

**Retrieving Additional Details:**

For security profile, autoscaler settings, or certificates:

```kql
cluster('akshuba.centralus').database('AKSprod').ManagedClusterSnapshot
| where PreciseTimeStamp > ago(7d)
| where clusterName == '{Cluster name}'
| take 1
| extend logd = todynamic(tostring(log))
| project 
    clusterName,
    // Security
    securityProfile = logd.securityProfile,
    aadProfile = logd.aadProfile,
    // Autoscaler
    autoScalerProfile = logd.autoScalerProfile,
    isAutoscalingCluster = logd.isAutoscalingCluster,
    // Certificates
    certificateProfile = logd.certificateProfile,
    // API Server
    apiServerAuthorizedIPRanges = logd.apiServerAuthorizedIPRanges,
    // Private cluster
    privateClusterEnabled = tostring(logd.orchestratorProfile.kubernetesConfig.privateCluster.enabled)
```

**Note on Dynamic Fields:**
- The `log` field contains the full cluster configuration as a JSON string
- Parse with `todynamic(tostring(log))` to access nested fields
- Network configuration is at `log.orchestratorProfile.kubernetesConfig`

---

## 4.2 Comprehensive Cluster Information (Multi-Table Join)

For complete cluster context including control plane wrapper details, network configuration, and availability zones.

**Database**: `AKSprod`

> **Default time range**: `ago(2h)` for optimal performance. Adjust if needed for historical analysis.

```kql
// Set query parameters - default to last 2 hours for performance
let qCCP = '{ccpNamespace}';
let qFrom = ago(2h);  // Adjust for historical analysis: datetime('2026-01-20T10:00:00Z')
let qTo = now();      // Adjust for historical analysis: datetime('2026-01-20T12:00:00Z')

// Get Control Plane Wrapper details
let cpws = cluster('akshuba.centralus').database('AKSprod').ControlPlaneWrapperSnapshot
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| order by PreciseTimeStamp desc
| take 1
| extend networkProfile = parse_json(networkProfile)
| extend openVPNProfile = todynamic(openVPNProfile)
| extend tunnelVersion = iff(konnectivityProfile.enabled == true, "konnectivity", 
    iif(openVPNProfile.enabled == true, "openvpn", 
    iff(privateConnectProfile == "na", "v1", "none")))
| extend cloudProviderProfile = todynamic(cloudProviderProfile)
| extend ccpPrivateLinkProfile = privateLinkProfile
| project 
    cluster_id,
    subscriptionID,
    resourceGroupName = resourceGroup,
    clusterName = name,
    ccpNamespace = namespace,
    fqdnIP = ip,
    fqdn = apiServerServiceAccountIssuerFQDN,
    provisioningState,
    tunnelVersion,
    // Network Profile
    networkPlugin = tostring(networkProfile.networkPlugin),
    networkPolicy = tostring(networkProfile.networkPolicy),
    ipMasqAgent = networkProfile.ipMasqAgent,
    isAzureCNI = iff(networkProfile.networkPlugin == "kubenet", false, true),
    isCiliumDataplane = (networkProfile.ebpfDataplane == 1),
    podCIDR = tostring(networkProfile.podCIDR),
    podCIDRs = networkProfile.pod_cidrs,
    serviceCIDR = tostring(networkProfile.serviceCIDR),
    serviceCIDRs = networkProfile.serviceCIDRs,
    kubeDnsServiceIP = tostring(networkProfile.kubeDnsServiceIP),
    vnetCIDRs = networkProfile.vnetCIDRs,
    // Cloud Provider Profile
    cpwSubnetName = tostring(cloudProviderProfile.subnetName),
    cpwVnetName = tostring(cloudProviderProfile.vnetName),
    cpwVnetResourceGroup = tostring(cloudProviderProfile.resourceGroup),
    cpwSecurityGroupName = tostring(cloudProviderProfile.securityGroupName),
    cpwRouteTableName = tostring(cloudProviderProfile.routeTableName),
    loadBalancerSku = tostring(cloudProviderProfile.loadBalancerSku),
    kubeResourceGroup = tostring(cloudProviderProfile.resourceGroup),
    // Private Link
    ccpPrivateLinkProfile
;

// Get Managed Cluster details
let mcs = cluster('akshuba.centralus').database('AKSprod').ManagedClusterSnapshot
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| order by PreciseTimeStamp desc
| take 1
| extend LoadBalancerProfile = parse_json(LoadBalancerProfile)
| extend orchestratorProfile = parse_json(orchestratorProfile)
| extend hostedMasterProfile = parse_json(hostedMasterProfile)
| extend autoUpgradeProfile = parse_json(autoUpgradeProfile)
| extend managedClusterSKUTier = iff(isempty(sku.tier), "free", tolower(tostring(sku.tier)))
| project 
    cluster_id,
    k8sCurrentVersion = tostring(orchestratorProfile.orchestratorVersion),
    AksNodeResourceGroup = nodeResourceGroup,
    clusterBirthdate = createdTime,
    clusterNodeCount,
    managedClusterSKUTier,
    UnderlayName,
    powerState = tostring(todynamic(powerState).code),
    outboundType,
    // Network details from MCS
    networkPluginMode = tostring(orchestratorProfile.kubernetesConfig.networkPluginMode),
    dockerBridgeSubnet = tostring(orchestratorProfile.kubernetesConfig.dockerBridgeSubnet),
    dnsPrefix = tostring(hostedMasterProfile.dnsPrefix),
    hostedMasterSubnet = tostring(hostedMasterProfile.subnet),
    maxPodsPerNode = toint(orchestratorProfile.kubernetesConfig.kubeletConfig["--max-pods"]),
    // Load Balancer
    managedOutboundIPCount = LoadBalancerProfile.managedOutboundIPs.desiredCount,
    effectiveOutboundIPs = LoadBalancerProfile.effectiveOutboundIPs,
    allocatedOutboundPorts = coalesce(tostring(LoadBalancerProfile.allocatedOutboundPorts), "0"),
    slbBackendPoolType = tostring(LoadBalancerProfile.backendPoolType),
    outboundRuleIdleTimeout = tostring(orchestratorProfile.kubernetesConfig.outboundRuleIdleTimeoutInMinutes),
    // CNI Version
    cniVersion = tostring(orchestratorProfile.kubernetesConfig.azureCNIVersion),
    // Upgrade Profile
    upgradeChannel = tostring(coalesce(tostring(autoUpgradeProfile.upgradeChannel), "none")),
    nodeOSUpgradeChannel = toint(coalesce(toint(autoUpgradeProfile.NodeOSUpgradeChannel), 0)),
    // Security
    isAAD = not(aadProfile == "na"),
    isMSICluster = isnotempty(MSIProfile),
    isAutoscalingCluster,
    // Private cluster
    privateLinkProfile,
    privateDNSZone,
    // Fleet
    fleetMembershipProfile,
    fleetProfile,
    // Addons
    addonProfiles,
    extensionAddonProfiles
;

// Get Agent Pool details (for availability zones)
let aps = cluster('akshuba.centralus').database('AKSprod').AgentPoolSnapshot
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| summarize maxAvailabilityZones = max(iff(availabilityZones == "na", 0, array_length(todynamic(availabilityZones)))) by cluster_id
;

// Join all tables
cpws
| join kind=leftouter (mcs) on cluster_id
| join kind=leftouter (aps) on cluster_id
| extend isPrivateCluster = iif(ccpPrivateLinkProfile == "na", false, true)
| extend isCustomVnet = isnotempty(cpwVnetResourceGroup)
| extend numberOfAvailabilityZones = maxAvailabilityZones
| extend nodeOSUpgradeChannelName = case(
    nodeOSUpgradeChannel == 0, "Unspecified",
    nodeOSUpgradeChannel == 1, "Unmanaged",
    nodeOSUpgradeChannel == 2, "None",
    nodeOSUpgradeChannel == 3, "SecurityPatch",
    nodeOSUpgradeChannel == 4, "NodeImage",
    "Unknown")
| extend isCiliumEnterprise = (extensionAddonProfiles has "CiliumEnterprise")
| extend privateLinkServiceID = tostring(todynamic(ccpPrivateLinkProfile).privateLinkServiceID)
| extend enablePrivateCluster = tobool(todynamic(ccpPrivateLinkProfile).enablePrivateCluster)
| extend privateLinkIP = tostring(todynamic(ccpPrivateLinkProfile).ip)
| extend fleet_resourceId = iff(fleetProfile == "na", 
    tolower(tostring(todynamic(fleetMembershipProfile).fleetResourceId)), 
    tolower(tostring(todynamic(fleetProfile).fleetResourceId)))
| project 
    // Identity
    ccpNamespace, clusterName, subscriptionID, resourceGroupName, AksNodeResourceGroup,
    // State
    provisioningState, powerState, k8sCurrentVersion, managedClusterSKUTier, clusterBirthdate, clusterNodeCount,
    // Infrastructure
    UnderlayName, tunnelVersion, numberOfAvailabilityZones,
    // Network
    networkPlugin, networkPolicy, networkPluginMode, isAzureCNI, isCiliumDataplane, isCiliumEnterprise,
    podCIDR, serviceCIDR, kubeDnsServiceIP, maxPodsPerNode,
    cpwVnetName, cpwSubnetName, cpwVnetResourceGroup, cpwSecurityGroupName, cpwRouteTableName,
    // Load Balancer
    loadBalancerSku, outboundType, slbBackendPoolType, managedOutboundIPCount, allocatedOutboundPorts,
    // Private Cluster
    isPrivateCluster, enablePrivateCluster, privateLinkIP, privateDNSZone,
    // Identity & Security
    isAAD, isMSICluster, isAutoscalingCluster, isCustomVnet,
    // Upgrade
    upgradeChannel, nodeOSUpgradeChannelName,
    // Fleet
    fleet_resourceId,
    // Addons
    addonProfiles
```

**Key Information from This Query:**

| Category | Fields |
|----------|--------|
| **Identity** | ccpNamespace, clusterName, subscriptionID, resourceGroupName |
| **State** | provisioningState, powerState, k8sCurrentVersion, SKU tier |
| **Network** | networkPlugin, networkPolicy, isCiliumDataplane, podCIDR, serviceCIDR |
| **Private Cluster** | isPrivateCluster, privateLinkIP, privateDNSZone |
| **Load Balancer** | loadBalancerSku, outboundType, slbBackendPoolType |
| **Upgrade** | upgradeChannel, nodeOSUpgradeChannel |
| **Fleet** | fleet_resourceId (if cluster is part of a Fleet) |

---

## 4.3 Network-Focused Query

For detailed network troubleshooting, use this query to get all networking-related configuration:

**Database**: `AKSprod`

> **Default time range**: `ago(2h)` for optimal performance. Adjust if needed for historical analysis.

```kql
// Set query parameters - default to last 2 hours for performance
let qCCP = '{ccpNamespace}';
let qFrom = ago(2h);  // Adjust for historical analysis: datetime('2026-01-20T10:00:00Z')
let qTo = now();      // Adjust for historical analysis: datetime('2026-01-20T12:00:00Z')

let cpws = cluster('akshuba.centralus').database('AKSprod').ControlPlaneWrapperSnapshot
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| order by PreciseTimeStamp desc
| take 1
| extend networkProfile = parse_json(networkProfile)
| extend isAzureCNI = iff(networkProfile.networkPlugin == "kubenet", false, true)
| extend isCiliumDataplane = (networkProfile.ebpfDataplane == 1)
| project 
    cluster_id, 
    fqdnIP = ip, 
    fqdn = apiServerServiceAccountIssuerFQDN, 
    networkPlugin = tostring(networkProfile.networkPlugin), 
    networkPolicy = tostring(networkProfile.networkPolicy), 
    ipMasqAgent = networkProfile.ipMasqAgent, 
    isAzureCNI,
    isCiliumDataplane,
    podCIDR = tostring(networkProfile.podCIDR), 
    podCIDRs = networkProfile.pod_cidrs, 
    subnetMask = toint(coalesce(tostring(split(networkProfile.podCIDR, "/")[1]), "0")), 
    cpwSubnetName = tostring(todynamic(cloudProviderProfile).subnetName), 
    cpwVnetName = tostring(todynamic(cloudProviderProfile).vnetName), 
    cpwVnetResourceGroup = tostring(todynamic(cloudProviderProfile).resourceGroup), 
    vnetCIDRs = networkProfile.vnetCIDRs, 
    cpwSecurityGroupName = tostring(todynamic(cloudProviderProfile).securityGroupName), 
    cpwRouteTableName = tostring(todynamic(cloudProviderProfile).routeTableName), 
    loadBalancerSku = tostring(todynamic(cloudProviderProfile).loadBalancerSku), 
    serviceCIDR = tostring(networkProfile.serviceCIDR), 
    serviceCIDRs = networkProfile.serviceCIDRs, 
    kubeDnsServiceIP = tostring(networkProfile.kubeDnsServiceIP), 
    kubeResourceGroup = tostring(todynamic(cloudProviderProfile).resourceGroup),
    privateLinkProfile
;

let mcs = cluster('akshuba.centralus').database('AKSprod').ManagedClusterSnapshot
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| order by PreciseTimeStamp desc
| take 1
| extend LoadBalancerProfile = parse_json(LoadBalancerProfile)
| extend orchestratorProfile = parse_json(orchestratorProfile)
| project 
    cluster_id, 
    k8sCurrentVersion = tostring(orchestratorProfile.orchestratorVersion), 
    AksNodeResourceGroup = nodeResourceGroup, 
    networkPluginModeFromMcs = tostring(orchestratorProfile.kubernetesConfig.networkPluginMode), 
    dockerBridgeSubnet = tostring(orchestratorProfile.kubernetesConfig.dockerBridgeSubnet),
    hostedMasterSubnet = tostring(todynamic(hostedMasterProfile).subnet), 
    managedOutboundIPCount = LoadBalancerProfile.managedOutboundIPs.desiredCount, 
    effectiveOutboundIPs = LoadBalancerProfile.effectiveOutboundIPs, 
    allocatedOutboundPorts = coalesce(tostring(LoadBalancerProfile.allocatedOutboundPorts), "0"),
    outboundRuleIdleTimeout = tostring(orchestratorProfile.kubernetesConfig.outboundRuleIdleTimeoutInMinutes), 
    outboundType, 
    customerProvidedKubenetRouteTableID = tostring(CustomerProvidedKubenetRouteTableID),
    natGatewayProfile, 
    cniVersion = tostring(orchestratorProfile.kubernetesConfig.azureCNIVersion),
    azureCNIURLLinux = tostring(orchestratorProfile.kubernetesConfig.azureCNIURLLinux), 
    isCiliumEnterprise = (extensionAddonProfiles has "CiliumEnterprise"), 
    privateDNSZone
;

let aps = cluster('akshuba.centralus').database('AKSprod').AgentPoolSnapshot
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP
| take 1
| extend vnetSubnetID = iff(vnetSubnetID != "na", vnetSubnetID, "")
| project 
    cluster_id, 
    maxPodsPerNode = tostring(todynamic(kubernetesConfig).kubeletConfig["--max-pods"]), 
    customerVnetSubnetID = vnetSubnetID, 
    containerRuntimeVersion = tostring(todynamic(kubernetesConfig).containerRuntime), 
    podSubnetId
;

cpws
| join kind=leftouter (mcs) on cluster_id
| join kind=leftouter (aps) on cluster_id
| extend isCustomVnet = isnotempty(customerVnetSubnetID)
| extend vnetResourceId = case(
    isnotempty(customerVnetSubnetID), tostring(split(customerVnetSubnetID, "/subnets/")[0]),
    strcat("/subscriptions/", tostring(split(cluster_id, "/")[2]), "/resourceGroups/", cpwVnetResourceGroup, "/providers/Microsoft.Network/virtualNetworks/", cpwVnetName)
)
| extend networkPluginMode = iff(isnotempty(podSubnetId) and podSubnetId != "na", "podsubnet", networkPluginModeFromMcs)
| extend networkPluginMode = iff(isempty(networkPluginModeFromMcs) and isempty(podSubnetId), "legacy", networkPluginMode)
| extend privateLinkServiceID = tostring(todynamic(privateLinkProfile).privateLinkServiceID)
| extend enablePrivateCluster = tobool(todynamic(privateLinkProfile).enablePrivateCluster)
| extend privateLinkIP = tostring(todynamic(privateLinkProfile).ip)
| project
    // API Server
    fqdnIP, fqdn,
    // Network Plugin
    networkPlugin, networkPolicy, networkPluginMode, isAzureCNI, isCiliumDataplane, isCiliumEnterprise,
    // IP Ranges
    podCIDR, podCIDRs, serviceCIDR, serviceCIDRs, kubeDnsServiceIP, subnetMask, vnetCIDRs,
    // VNet
    isCustomVnet, vnetResourceId, cpwVnetName, cpwSubnetName, cpwVnetResourceGroup, customerVnetSubnetID,
    podSubnetId, cpwSecurityGroupName, cpwRouteTableName, customerProvidedKubenetRouteTableID,
    // Load Balancer & Outbound
    loadBalancerSku, outboundType, managedOutboundIPCount, effectiveOutboundIPs, allocatedOutboundPorts, outboundRuleIdleTimeout, natGatewayProfile,
    // Private Cluster
    enablePrivateCluster, privateLinkIP, privateLinkServiceID, privateDNSZone,
    // Container Runtime
    containerRuntimeVersion, maxPodsPerNode, cniVersion, azureCNIURLLinux, dockerBridgeSubnet
```

**Network Troubleshooting Fields:**

| Category | Key Fields | Use For |
|----------|------------|---------|
| **Plugin** | networkPlugin, networkPolicy, networkPluginMode | CNI type issues |
| **Cilium** | isCiliumDataplane, isCiliumEnterprise | Cilium-specific issues |
| **IP Ranges** | podCIDR, serviceCIDR, subnetMask | IP exhaustion, routing |
| **Custom VNet** | isCustomVnet, customerVnetSubnetID, cpwVnetResourceGroup | BYO VNet issues |
| **Pod Subnet** | podSubnetId, networkPluginMode | Azure CNI Overlay/Pod Subnet |
| **Private Cluster** | enablePrivateCluster, privateLinkIP, privateDNSZone | Private endpoint issues |
| **Outbound** | outboundType, natGatewayProfile, effectiveOutboundIPs | Egress issues |

---

## 4.4 List Cluster Node Pools

**Database**: `AKSprod`

> **Default time range**: `ago(2h)` for optimal performance.

```kql
let qFrom = ago(2h);
let qTo = now();
let qCCP = '{ccpNamespace}';

cluster('akshuba.centralus').database('AKSprod').AgentPoolSnapshot
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id =~ qCCP
| summarize arg_max(PreciseTimeStamp, *) by name
| project 
    nodePoolName = name,
    vmSize,
    nodeCount = size,
    osSku,
    osType,
    orchestratorVersion,
    mode,
    availabilityProfile,
    availabilityZones,
    enableAutoScaling,
    minCount,
    maxCount,
    maxPods = tostring(todynamic(kubernetesConfig).kubeletConfig["--max-pods"]),
    provisioningState,
    powerState = tostring(todynamic(powerState).code),
    vnetSubnetID,
    podSubnetId,
    nodeImageVersion = tostring(split(tostring(todynamic(agentPoolVersionProfile).nodeImageReference.id), "/")[-1])
| order by mode asc, nodePoolName asc
```

**Node Pool Fields:**

| Field | Description |
|-------|-------------|
| `nodeCount` | Current number of nodes (from `size` field) |
| `mode` | System or User node pool |
| `enableAutoScaling` | Whether autoscaler is enabled |
| `minCount/maxCount` | Autoscaler bounds |
| `nodeImageVersion` | Node image version (e.g., `202601.13.0`) |
| `provisioningState` | Pool provisioning status |

---

## 4.5 List Individual Cluster Nodes

**Database**: `AKSccplogs`

> **Default time range**: `ago(2h)` for optimal performance.

```kql
let qFrom = ago(2h);
let qTo = now();
let qCCP = '{ccpNamespace}';

cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id =~ qCCP and objectRef.resource == 'nodes'
| where verb in ('patch', 'update') and level !in ('Metadata')
| extend node = tostring(objectRef.name)
| summarize take_any(responseObject) by node
| extend metadata = responseObject.metadata
| extend status = responseObject.status
| extend created = todatetime(metadata.creationTimestamp)
| extend vmSize = tostring(metadata.labels['node.kubernetes.io/instance-type'])
| extend pool = coalesce(
    tostring(metadata.labels['kubernetes.azure.com/agentpool']), 
    tostring(metadata.labels['agentpool'])
)
| extend kubeletVersion = tostring(status.nodeInfo.kubeletVersion)
| extend containerRuntime = tostring(status.nodeInfo.containerRuntimeVersion)
| extend osImage = tostring(status.nodeInfo.osImage)
| extend kernelVersion = tostring(status.nodeInfo.kernelVersion)
| extend architecture = tostring(status.nodeInfo.architecture)
| mv-apply address = coalesce(status.addresses, dynamic([{"type": "InternalIP","address":""}])) on 
(
    where address.type == "InternalIP" | project internal_ip = tostring(address.address)
)
| mv-apply condition = coalesce(status.conditions, dynamic([])) on
(
    where condition.type == "Ready" | project readyStatus = tostring(condition.status), readyReason = tostring(condition.reason)
)
| extend allocatable_cpu = tostring(status.allocatable.cpu)
| extend allocatable_memory = tostring(status.allocatable.memory)
| extend allocatable_pods = tostring(status.allocatable.pods)
| project 
    node, 
    pool, 
    vmSize, 
    internal_ip, 
    readyStatus,
    readyReason,
    created, 
    kubeletVersion, 
    containerRuntime, 
    osImage, 
    kernelVersion,
    architecture,
    allocatable_cpu,
    allocatable_memory,
    allocatable_pods
| order by pool asc, node asc
| take 100
```

**Node Fields:**

| Field | Description |
|-------|-------------|
| `node` | Node name (includes VMSS instance ID) |
| `pool` | Node pool name |
| `internal_ip` | Node's internal IP address |
| `readyStatus` | True/False/Unknown |
| `readyReason` | KubeletReady, KubeletNotReady, etc. |
| `kubeletVersion` | Kubelet version (e.g., v1.33.6) |
| `containerRuntime` | Container runtime (e.g., containerd://1.7.30-1) |
| `osImage` | OS image (e.g., Ubuntu 22.04.5 LTS) |
| `kernelVersion` | Linux kernel version |
| `allocatable_*` | Allocatable resources (cpu, memory, pods) |

---

## 4.6 List Unhealthy Pods

**Database**: `AKSccplogs`

> **Default time range**: `ago(2h)` for optimal performance. Expand if needed.

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(2h);  // Adjust for historical analysis
let qTo = now();

cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP and requestObject has 'terminated'
| mv-expand cs = requestObject.status.containerStatuses
| where cs.lastState.terminated.reason !in ('', 'Completed')
| project 
    PreciseTimeStamp, 
    pod = tostring(objectRef.name),
    ns = tostring(objectRef.namespace),
    container = tostring(cs.name),
    reason = tostring(cs.lastState.terminated.reason),
    exitCode = tostring(cs.lastState.terminated.exitCode),
    restartCount = toint(cs.restartCount),
    image = tostring(cs.image),
    startedAt = todatetime(cs.lastState.terminated.startedAt),
    finishedAt = todatetime(cs.lastState.terminated.finishedAt),
    message = tostring(cs.lastState.terminated.message)
| summarize 
    LastTerminated = arg_max(coalesce(finishedAt, PreciseTimeStamp), *) 
    by pod, container
| order by LastTerminated desc
| take 100
```

**Common Termination Reasons:**

| Reason | Exit Code | Description |
|--------|-----------|-------------|
| `OOMKilled` | 137 | Container exceeded memory limit |
| `Error` | 1, 143 | Application error or graceful shutdown |
| `ContainerCannotRun` | varies | Container failed to start |
| `CrashLoopBackOff` | varies | Repeated crashes (check restartCount) |

**Summarize by Reason (for overview):**

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(2h);
let qTo = now();

cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp between(qFrom .. qTo)
| where cluster_id == qCCP and requestObject has 'terminated'
| mv-expand cs = requestObject.status.containerStatuses
| where cs.lastState.terminated.reason !in ('', 'Completed')
| extend reason = tostring(cs.lastState.terminated.reason)
| extend ns = tostring(objectRef.namespace)
| summarize 
    PodCount = dcount(tostring(objectRef.name)),
    TotalRestarts = sum(toint(cs.restartCount)),
    FirstSeen = min(PreciseTimeStamp),
    LastSeen = max(PreciseTimeStamp)
  by reason, ns
| order by PodCount desc
```

---

## 4.7 Check Overlay Components Health

**Database**: `AKSprod`

> **Default time range**: `ago(2h)` for optimal performance.

```kql
let qCCP = '{ccpNamespace}';
let qFrom = ago(2h);  // Adjust for historical analysis
let qTo = now();

// Collect general warnings (non-event logs)
let general = cluster('akshuba.centralus').database('AKSprod').OverlaymgrEvents
| where PreciseTimeStamp between (qFrom .. qTo)
| where id == qCCP
| where isempty(eventObjectName) and isempty(eventReason) and level != 'info'
| extend StartTime = todatetime(logPreciseTime)
| extend Pod = '', Reason = 'General Warnings', Message = msg, Kind = ''
| project StartTime, Pod, Kind, Reason, Message, level
| summarize 
    Message = make_set(Message), 
    Pod = strcat('remove-', rand(1000)),
    Kind = any(Kind),  
    Reason = any(Reason),
    Level = any(level)
    by bin(StartTime, 5m) 
| extend Message = array_strcat(Message, '\n')
| project StartTime, Pod, Kind, Reason, Message, Level
;

// Collect component events and union with general warnings
cluster('akshuba.centralus').database('AKSprod').OverlaymgrEvents
| where PreciseTimeStamp between (qFrom .. qTo)
| where id == qCCP
| where eventReason !in ('Pulling', 'Pulled', 'Created', 'na')
| where isnotempty(eventObjectName) and isnotempty(eventReason)
| extend StartTime = todatetime(logPreciseTime)
| extend Pod = eventObjectName, Reason = eventReason, Message = eventMessage, Kind = eventKind
| project StartTime, Pod, Kind, Reason, Message, Level = level
| union (general)
| summarize MinTime = min(StartTime), Messages = make_set(Message) by Pod, Kind, Reason, Level, bin(StartTime, 10m)
| extend Pod = iff(Pod startswith 'remove-', 'N/A', Pod)
| extend Messages = array_strcat(Messages, '\n')
| extend Level = case (
    Level != 'info', Level,
    Reason in ('Failed', 'Killing', 'Unhealthy', 'BackOff', 'FailedKillPod', 'General Warnings', 'FailedMount'), 'warning',
    'info'
)
| project MinTime, Pod, Kind, Reason, Message = Messages, Level
| order by MinTime desc
| take 100
```

**Overlay Component Events:**

| Reason | Level | Description |
|--------|-------|-------------|
| `Unhealthy` | warning | Readiness/liveness probe failed |
| `Killing` | warning | Container being terminated |
| `FailedMount` | warning | Volume mount failed (configmap, secret) |
| `BackOff` | warning | Container in crash loop |
| `Started` | info | Container started successfully |

**Key Components to Monitor:**

| Component | Description |
|-----------|-------------|
| `kube-apiserver-*` | Kubernetes API server pods |
| `kube-api-proxy-*` | API server proxy (envoy) |
| `kube-controller-manager-*` | Controller manager |
| `kube-scheduler-*` | Scheduler |
| `etcd-*` | Etcd cluster pods |
| `konnectivity-*` | Konnectivity tunnel |
| `*-helmrelease` | Helm release status for addons |

**Filter by Warning/Error Only:**

```kql
// Add this filter before final project to see only issues:
| where Level in ('warning', 'error')
```
