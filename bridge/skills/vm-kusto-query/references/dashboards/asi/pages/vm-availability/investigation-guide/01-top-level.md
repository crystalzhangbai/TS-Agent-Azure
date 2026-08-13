# (top-level)

> Source: **EEE RDOS — VM Availability** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "VM Availability"

_Widget purpose:_ VM Availability - ContainerId: {{containerId}}, NodeId: {{nodeId}}

Cluster: `azcore.centralus` · Database: `azurecp` · Type: `ResourceGet` · Widget: `Container`

```kusto
// print cluster = local_cluster, Tenant = local_cluster, tenantName = local_tenantname, containerId = local_containerid, nodeId = local_nodeid, vmid = local_vmid, virtualMachineUniqueId=local_vmid, roleInstanceName = local_roleInstanceName
// | extend vmid = iff(isnotempty(vmid), vmid, "nodata")
MycroftContainerSnapshot
| where PreciseTimeStamp between ((globalFrom - 6h) .. (globalTo + 6h))
// containerId is unique, we dont need the role instance name also.
| where ContainerId == local_containerId and RoleInstanceName has local_roleInstanceName
| where isnotempty(RoleInstanceName)
| top 1 by PreciseTimeStamp
| project azsmCluster = Cluster, cluster = ClusterName, Tenant = ClusterName, tenantname = TenantName, tenantName = TenantName, containerid = ContainerId, containerId = ContainerId, nodeid = NodeId, nodeId = NodeId, vmid=VirtualMachineUniqueId, virtualMachineUniqueId = VirtualMachineUniqueId, roleInstanceName = RoleInstanceName, subscriptionId = SubscriptionId, creationTime = todatetime(CreationTime), additionalContainerProperties = AdditionalContainerProperties, containerType = ContainerType, billingType = BillingContext, priority = Priority, tenantOwners = ContainerLifeCycleOwner, Region, RegionFriendlyName
| extend Dummy = "***"
```

**Params:** `{local_containerId}`, `{local_nodeId}`, `{local_roleInstanceName}`, `{local_Tenant}`, `{local_tenantName}`, `{local_virtualMachineUniqueId}`, `{globalFrom}`, `{globalTo}`

---

### OverlakeNodeMap

_Widget purpose:_ VM Availability - ContainerId: {{containerId}}, NodeId: {{nodeId}}

Cluster: `overlakedata.southcentralus.kusto.windows.net` · Database: `overlake-syslog` · Type: `Single` · Widget: `Container`

```kusto
let QueryFilterByNodeId = cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMap_Latest
| where NodeId =~ queryNodeId;
QueryFilterByNodeId
| summarize count()
| extend OverlakeState = iff(count_ == 0, "Not Enabled", "Enabled")
| project OverlakeState, NodeId = tolower(queryNodeId)
| join kind=leftouter (QueryFilterByNodeId) on NodeId
| project OverlakeState, Cluster, NodeId, SocNodeId, hostMachineName, AvailabilityZone, Region, SocOSVersion, FWVersion
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### GetShoeboxAccount

_Widget purpose:_ VM Availability - ContainerId: {{containerId}}, NodeId: {{nodeId}}

Cluster: `azurecm` · Database: `AzureCM` · Type: `Single` · Widget: `Container`

```kusto
cluster('azurecm.kusto.windows.net').database('AzureCM').LogClusterSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Tenant =~ queryCluster
| project shoeboxMdmAccountName
| take 1
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryCluster}`

---
