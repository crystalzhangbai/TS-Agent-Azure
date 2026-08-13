# (top-level)

> Source: **CRP — VMs** dashboard, chapter **(top-level)** (9 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "VMs"

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
union 
    cluster('azcrpbifollower').database('bi_allprod').VMScaleSetVMInstance,
    cluster('azcrpbifollower').database('bi_allprod').VM
| where PreciseTimeStamp between (globalFrom .. globalTo) and ResourceGroupName =~ local_resourceGroupName
| where SubscriptionId =~ local_subscriptionId
| extend VMId = coalesce(VMId, VMScaleSetVMInstanceId)
| extend VMName = coalesce(VMName, tolower(strcat(VMScaleSetName, "_", InstanceIdString)))
| where VMName =~ local_resourceName
| where isempty(local_VMId) or VMId =~ local_VMId
| extend VMGeoLocation = coalesce(VMGeoLocation, Region)
| extend 
    SubscriptionId = tolower(SubscriptionId), 
    ResourceGroupName= tolower(ResourceGroupName), 
    ResourceName = tolower(VMName), 
    VMName = tolower(VMName), 
    VMId = tolower(VMId), 
    VirtualMachineUniqueId = tolower(VMId)
| summarize SnapshotTime = arg_max(PreciseTimeStamp, *) by VirtualMachineUniqueId
| extend ArmResourceId = iif(isempty(VMScaleSetName),
    strcat("/subscriptions/", SubscriptionId, "/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Compute/virtualMachines/", VMName),
    strcat("/subscriptions/", SubscriptionId, "/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Compute/virtualMachineScaleSets/", VMScaleSetName, "/virtualMachines/",InstanceIdString))
| extend queryVMResourceId = ArmResourceId
| extend jarvisActionGetVM = strcat('https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=',
  'Public',
  '&managementOpen=false&selectedNodeType=3&extension=CRP&group=VM%20Operations&operationId=GetVM&operationName=GET%20VM&inputMode=single&params=',
  '{"smecrpregion":"', VMGeoLocation, 
  '","wellknownsubscriptionid":"', local_subscriptionId,
  '","smeresourcegroupnameparameter":"', local_resourceGroupName, 
  '","smevmnameparameter":"', local_resourceName, 
  '","smegetvmoptionparameter":"VM%20model%20and%20InstanceView"}&actionEndpoint=Production&genevatraceguid=44e06030-1571-4814-a7db-9f2bbe317e8c')
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_resourceGroupName}`, `{local_resourceName}`, `{local_subscriptionId}`, `{local_VMId}`

---

### Get AzCoreSpoke

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Single` · Widget: `Container`

```kusto
cluster("azcore.centralus").database("Fa").VmHealthRawStateEtwTable 
| where PreciseTimeStamp between (qFrom .. qTo) and VirtualMachineUniqueId == qVM 
| take 1
| project AzCoreCluster
```

**Params:** `{qFrom}`, `{qTo}`, `{qVM}`

---

### Query VM Placement History

_Widget purpose:_ CRP VM Placement History since {{globalFrom}}

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Table`

```kusto
union
cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').VMScaleSetVMInstance,
cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').VM
| where PreciseTimeStamp between (queryFrom .. now())
| where SubscriptionId == querySubId
| where ResourceGroupName =~ queryResourceGroup
| extend VMGeoLocation = coalesce(VMGeoLocation, Region)
| extend VMId = coalesce(VMId, VMScaleSetVMInstanceId)
| extend VMName = coalesce(VMName, tolower(strcat(VMScaleSetName, "_", InstanceIdString)))
| where VMName =~ queryVMName
| extend VMTimeCreated = coalesce(VMTimeCreated, TimeCreated)
| summarize by VMId, VMTimeCreated
| join kind=leftouter (cluster("azcsupfollower.kusto.windows.net").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp between (queryFrom .. now())
| where subscriptionId == querySubId
| extend containerCreationTime = todatetime(creationTime)
| summarize FirstSeen = min(PreciseTimeStamp), LastSeen = arg_max(PreciseTimeStamp, *) by containerCreationTime, roleInstanceName, Tenant, tenantName, containerId, nodeId, virtualMachineUniqueId, containerType, Region) on $left.VMId == $right.virtualMachineUniqueId
| extend OSType = parse_json(features).["Fabric.OSType"]
| where FirstSeen < queryTo or containerCreationTime < queryTo
| order by VMTimeCreated asc, containerCreationTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`, `{queryResourceGroup}`, `{queryVMName}`

---

### CRP-SingleVM-NetworkProfile

_Widget purpose:_ Details - CRP BI

Cluster: `argwus2nrpone.westus2.kusto.windows.net` · Database: `AzureResourceGraph` · Type: `Single` · Widget: `Card`

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

### VMAllocationInfo

_Widget purpose:_ Goal State - CRP BI

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Single` · Widget: `Card`

```kusto
union cluster("azcrpbifollower").database("bi_allprod").VMAllocationInfo,
    cluster("azcrpbifollower").database("bi_allprod").VMScaleSetVMInstanceAllocationInfo
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where SubscriptionId =~ querySubId
| where ResourceGroupName =~ queryRGName
| extend VMName = coalesce(VMName, tolower(strcat(VMScaleSetName, "_", InstanceIdString)))
| where VMName =~ queryResourceName
| extend Error = parse_json(iif(Error startswith "H4sIAAAAAAA", gzip_decompress_from_base64_string(Error), Error))
| top 1 by PreciseTimeStamp desc
| extend opStartTime = LastGoalSeekingCompletionTime - 1d
| extend opEndTime = LastGoalSeekingCompletionTime + 1m
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRGName}`, `{querySubId}`, `{queryResourceName}`

---

### Query VM Extension

Cluster: `Azcrpbifollower` · Database: `bi_allprod` · Type: `Table`

```kusto
TenantModelVMExtension
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where VMId == queryVMId
| summarize SnapshotTimes = arg_max(PreciseTimeStamp, *)  by Id, TimeCreated
| order by Name asc, TimeCreated asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVMId}`

---

### Query VMs in AvailabilitySet

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Table`

```kusto
VM
| where PreciseTimeStamp between(queryFrom .. now())
| where AvailabilitySetKey =~ queryAvailabilitySetKey
| summarize LastSeen = max(PreciseTimeStamp) by VMId = tolower(VMId), VMName = tolower(VMName), VMTimeCreated,ResourceGroupName =  tolower(ResourceGroupName), SubscriptionId = tolower(SubscriptionId)
| order by VMTimeCreated
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryAvailabilitySetKey}`

---

### query Communications in AlbnTargets

Cluster: `Icmcluster` · Database: `ACM.Publisher` · Type: `Table`

```kusto
AlbnTargets_Expanded
| where PublishDateTime between (queryFrom .. queryTo)
| where Subscription == querySubId
| project CommunicationId, PublishDateTime
| join cluster('Icmcluster').database("ACM.Backend").PublishRequest on CommunicationId
| where CommunicationDateTime between (queryFrom .. queryTo)
| order by CommunicationDateTime desc
| project CommunicationId, PublishDateTime, CommunicationDateTime, CommunicationType, Title, IncidentId, RichTextMessage, AdditionalProperties
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`

---

### Examine VM by ContainerId

Cluster: `Azcsupfollower` · Database: `AzureCM` · Type: `Filter` · Widget: `Row`

```kusto
cluster('Azcsupfollower').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where virtualMachineUniqueId == queryVmId
| summarize  LastSeen = arg_max(PreciseTimeStamp, *) by containerId, creationTime
| extend Value  = containerId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`

---
