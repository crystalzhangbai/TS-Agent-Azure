# Networking

> Source: **CRP — VMs** dashboard, chapter **Networking** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### CRP-SingleVM-NetworkProfile

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Single` · Widget: `Column`
Source panel: `Networking`

```kusto
let networkCardList = 
range index from 1 to 1 step 1
| extend NetworkProfile=todynamic(local_networkProfile).networkInterfaces
| mv-expand NetworkProfile
| extend networkCard=tostring(NetworkProfile.id)
| project-reorder networkCard
;
let networkProfileDetails = cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where (type =~ 'microsoft.network/networkInterfaces' or type =~'microsoft.compute/virtualmachinescalesets/virtualmachines/networkinterfaces') and not(partial)
| where id in~ (networkCardList)
| summarize arg_max(timestamp, *) by id
| extend 
    isPrimaryNic=tobool(properties.primary),
    macAddress=tostring(properties.macAddress),
    accelaratedNetworking=iff(tobool(properties.enableAcceleratedNetworking),"Enabled","Disabled"),
    vnetEncryptionSupported=iff(tobool(properties.vnetEncryptionSupported),"Yes","No"),
    enableIPForwarding=iff(tobool(properties.enableIPForwarding),"Enabled","Disabled"),
    disableTcpStateTracking=iff(tobool(properties.disableTcpStateTracking),"Enabled","Disabled"),
    allowPort25Out=iff(tobool(properties.allowPort25Out),"Allowed","Blocked"),
    nsgUri=tostring(properties.networkSecurityGroup.id)
| extend ipConfigs=properties.ipConfigurations, nsgName=extract('(.+)\\/(?i)networkSecurityGroups\\/(.+$)',2, tostring(nsgUri))
| mv-expand ipConfigs
| extend subnetId=ipConfigs.properties.subnet.id
| extend
    vnetUri=extract('(.+)\\/(?i)subnets\\/(.+$)',1, tostring(subnetId)),
    subnetName=extract('(.+)\\/(?i)subnets\\/(.+$)',2, tostring(subnetId)),
    nicUri=id, nicName=name, nicState=iff(not(deleted),'Active','Deleted'),
    isPrimaryIp=tobool(ipConfigs.properties.primary),
    privateIpAllocationMode=tostring(ipConfigs.properties.privateIPAllocationMethod),
    ipAddress=tostring(ipConfigs.properties.privateIPAddress)
| extend primaryIpAddress=iff(isPrimaryIp,ipAddress, "")
| summarize ipAddresses=make_list(ipAddress), take_any(*) by id
| order by nicName asc
| extend nicDetails=bag_pack_columns(subnetName, subnetId, nicName, nicUri, nicState, nsgUri, nsgName, isPrimaryNic, macAddress, accelaratedNetworking, vnetEncryptionSupported, enableIPForwarding, disableTcpStateTracking, allowPort25Out, primaryIpAddress, ipAddresses)
| summarize nicDetails=make_list(nicDetails) by vnetUri
| extend vnetName=extract('\\/(?i)virtualNetworks\\/(.+$)',1, tostring(vnetUri))
;
networkProfileDetails
```

**Params:** `{local_networkProfile}`

---

## NICs

### CRP-SingleVM-NetworkProfile-Expand

_Widget purpose:_ NICs

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Networking > NICs`

```kusto
range index from 1 to 1 step 1
| mv-expand nicDetails=data
| extend subnetName=tostring(nicDetails.subnetName), subnetId=tostring(nicDetails.subnetId), nicName=tostring(nicDetails.nicName), nicUri=tostring(nicDetails.nicUri), nicState=tostring(nicDetails.nicState),
    nsgUri=tostring(nicDetails.nsgUri), nsgName=tostring(nicDetails.nsgName), isPrimaryNic=tostring(nicDetails.isPrimaryNic), macAddress=tostring(nicDetails.macAddress), accelaratedNetworking=tostring(nicDetails.accelaratedNetworking),
    vnetEncryptionSupported=tostring(nicDetails.vnetEncryptionSupported), enableIPForwarding=tostring(nicDetails.enableIPForwarding), disableTcpStateTracking=tostring(nicDetails.disableTcpStateTracking), allowPort25Out=tostring(nicDetails.allowPort25Out),
    primaryIpAddress=tostring(nicDetails.primaryIpAddress), ipAddresses=strcat_array(nicDetails.ipAddresses,',')
| project-away index
```

**Params:** `{data}`

---
